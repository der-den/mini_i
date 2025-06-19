#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3
import pandas as pd
import argparse
import os
import sys
from datetime import datetime

def get_db_connection(db_path):
    """Stellt eine Verbindung zur Datenbank her"""
    conn = sqlite3.connect(db_path)
    # Dictionary-Cursor verwenden, um Spaltennamen zu erhalten
    conn.row_factory = sqlite3.Row
    return conn

def get_header_mapping():
    """Lädt die Header-Mapping-Datei, falls vorhanden"""
    header_file = 'header_mapping.json'
    if os.path.exists(header_file):
        try:
            import json
            with open(header_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Warnung: Konnte Header-Mapping nicht laden: {e}")
    
    # Standard-Mapping
    return {
        'id': 'ID',
        'az_pol': 'AZ POL',
        'place_status': 'Place Status',
        'ass_number': 'Ass. Number',
        'type': 'Type',
        'vendor': 'Vendor',
        'model': 'Model',
        'model_desc': 'Description',
        'status': 'Status',
        'serial': 'Serial',
        'barcode': 'Barcode',
        'seized_by': 'Seized By',
        'status_hint': 'Status Hint',
        'storage': 'Storage',
        'storage_sub': 'Storage Sub',
        'last_scanned': 'Last Scanned'
    }

def export_to_excel(db_path, output_file, query=None, sheet_name='Inventar'):
    """
    Exportiert Daten aus der SQLite-Datenbank in eine Excel-Datei
    
    Args:
        db_path (str): Pfad zur SQLite-Datenbank
        output_file (str): Pfad zur Ausgabe-Excel-Datei
        query (str, optional): Benutzerdefinierte SQL-Abfrage
        sheet_name (str, optional): Name des Excel-Tabellenblatts
    """
    try:
        # Verbindung zur Datenbank herstellen
        conn = get_db_connection(db_path)
        
        # SQL-Abfrage ausführen
        if query is None:
            query = "SELECT * FROM tabelle1"
        
        # Daten in ein DataFrame laden
        df = pd.read_sql_query(query, conn)
        
        # Verbindung schließen
        conn.close()
        
        if df.empty:
            print("Keine Daten gefunden.")
            return False
        
        # Header-Mapping laden und anwenden
        header_mapping = get_header_mapping()
        df = df.rename(columns={col: header_mapping.get(col, col) for col in df.columns})
        
        # Datum formatieren
        if 'Last Scanned' in df.columns:
            # Konvertiere Datum in ein lesbares Format
            df['Last Scanned'] = pd.to_datetime(df['Last Scanned'], errors='coerce').dt.strftime('%d.%m.%Y')
        
        # In Excel-Datei exportieren
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            # Automatische Spaltenbreite anpassen
            worksheet = writer.sheets[sheet_name]
            for i, col in enumerate(df.columns):
                max_len = max(
                    df[col].astype(str).map(len).max(),  # Längster Eintrag
                    len(str(col))  # Länge der Spaltenüberschrift
                ) + 2  # Etwas Platz hinzufügen
                worksheet.column_dimensions[chr(65 + i)].width = min(max_len, 50)  # Maximal 50 Zeichen breit
        
        print(f"Daten erfolgreich in '{output_file}' exportiert.")
        print(f"Anzahl der exportierten Datensätze: {len(df)}")
        return True
    
    except Exception as e:
        print(f"Fehler beim Export: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Exportiert Daten aus der SQLite-Datenbank in eine Excel-Datei')
    parser.add_argument('--db', default='inventory.db', help='Pfad zur SQLite-Datenbank (Standard: inventory.db)')
    parser.add_argument('--out', default=None, help='Pfad zur Ausgabe-Excel-Datei (Standard: inventory_DATUM.xlsx)')
    parser.add_argument('--sheet', default='Inventar', help='Name des Excel-Tabellenblatts (Standard: Inventar)')
    parser.add_argument('--query', default=None, help='Benutzerdefinierte SQL-Abfrage (Standard: SELECT * FROM tabelle1)')
    parser.add_argument('--filter', default=None, help='Einfacher Suchfilter (wird auf mehrere Felder angewendet)')
    parser.add_argument('--storage', action='store_true', help='Nur Einträge mit Storage anzeigen')
    parser.add_argument('--az', default=None, help='Nach Aktenzeichen filtern')
    
    args = parser.parse_args()
    
    # Überprüfen, ob die Datenbank existiert
    if not os.path.exists(args.db):
        print(f"Fehler: Datenbank '{args.db}' nicht gefunden.")
        sys.exit(1)
    
    # Standard-Ausgabedatei mit Datum generieren, wenn nicht angegeben
    if args.out is None:
        current_date = datetime.now().strftime('%Y%m%d')
        args.out = f"inventory_{current_date}.xlsx"
    
    # SQL-Abfrage erstellen
    query = args.query
    if query is None:
        query = "SELECT * FROM tabelle1 WHERE 1=1"
        params = []
        
        # Filter anwenden
        if args.filter:
            search_conditions = [
                "az_pol LIKE ?", 
                "place_status LIKE ?", 
                "type LIKE ?", 
                "vendor LIKE ?", 
                "model LIKE ?", 
                "model_desc LIKE ?", 
                "status_hint LIKE ?"
            ]
            search_query = " OR ".join(search_conditions)
            query += f" AND ({search_query})"
            
            # Suchparameter für jedes Feld hinzufügen
            for _ in range(len(search_conditions)):
                params.append(f"%{args.filter}%")
        
        if args.storage:
            query += " AND storage IS NOT NULL"
        
        if args.az:
            query += " AND az_pol = ?"
            params.append(args.az)
        
        # Parameter in die Abfrage einfügen
        conn = get_db_connection(args.db)
        query = conn.execute(query, params).fetchall()
        conn.close()
    
    # Export durchführen
    success = export_to_excel(args.db, args.out, query, args.sheet)
    if not success:
        sys.exit(1)

if __name__ == '__main__':
    main()
