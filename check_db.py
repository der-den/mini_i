#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3

def check_database(db_file):
    """Check the structure of the SQLite database"""
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    # Check tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print("Tables in database:")
    for table in tables:
        print(f"- {table[0]}")
    
    # Check columns in tabelle1
    cursor.execute("PRAGMA table_info(tabelle1)")
    columns = cursor.fetchall()
    print("\nColumns in tabelle1:")
    for col in columns:
        print(f"- {col[1]} ({col[2]})")
    
    # Check row count
    cursor.execute("SELECT COUNT(*) FROM tabelle1")
    row_count = cursor.fetchone()[0]
    print(f"\nNumber of rows in tabelle1: {row_count}")
    
    # Sample data
    cursor.execute("SELECT * FROM tabelle1 LIMIT 3")
    rows = cursor.fetchall()
    print("\nSample data (first 3 rows):")
    for row in rows:
        print(row)
    
    conn.close()

if __name__ == "__main__":
    check_database("inventory.db")
