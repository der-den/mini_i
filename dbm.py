#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, redirect, url_for, flash, abort
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField, SelectField, IntegerField, DateField, TextAreaField
from wtforms.validators import Optional, DataRequired
import sqlite3
import os
import math
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
bootstrap = Bootstrap(app)

# Database connection helper
def get_db_connection():
    conn = sqlite3.connect('inventory.db')
    # Use dictionary cursor to preserve column names
    conn.row_factory = sqlite3.Row
    return conn

# Search form
class SearchForm(FlaskForm):
    search = StringField('Search', validators=[Optional()])
    has_storage = BooleanField('Has Storage')
    submit = SubmitField('Search')

# Edit form for detail page
# Funktion zum Abrufen aller eindeutigen place_status-Werte aus der Datenbank
def get_place_status_options():
    conn = get_db_connection()
    # Hole alle eindeutigen place_status-Werte, sortiert
    result = conn.execute('SELECT DISTINCT place_status FROM tabelle1 WHERE place_status IS NOT NULL ORDER BY place_status').fetchall()
    conn.close()
    
    # Extrahiere die Werte und erstelle eine Liste von Tupeln (value, label)
    options = [(row['place_status'], row['place_status']) for row in result]
    
    # Füge eine leere Option hinzu
    options.insert(0, ('', '-- Bitte wählen --'))
    
    return options

# Funktion zum Abrufen aller eindeutigen type-Werte aus der Datenbank
def get_type_options():
    conn = get_db_connection()
    # Hole alle eindeutigen type-Werte, sortiert
    result = conn.execute('SELECT DISTINCT type FROM tabelle1 WHERE type IS NOT NULL ORDER BY type').fetchall()
    conn.close()
    
    # Extrahiere die Werte und erstelle eine Liste von Tupeln (value, label)
    options = [(row['type'], row['type']) for row in result]
    
    # Füge eine leere Option hinzu
    options.insert(0, ('', '-- Bitte wählen --'))
    
    return options

class EditForm(FlaskForm):
    az_pol = StringField('AZ POL', validators=[DataRequired()])
    place_status = SelectField('Place Status', validators=[Optional()], choices=[])
    ass_number = StringField('Ass. Number', validators=[Optional()])
    type = SelectField('Type', validators=[Optional()], choices=[])
    vendor = StringField('Vendor', validators=[Optional()])
    model = StringField('Model', validators=[Optional()])
    model_desc = TextAreaField('Description', validators=[Optional()])
    status = TextAreaField('Status', validators=[Optional()])
    serial = StringField('Serial', validators=[Optional()])
    barcode = IntegerField('Barcode', validators=[Optional()])
    seized_by = StringField('Seized By', validators=[Optional()])
    status_hint = TextAreaField('Status Hint', validators=[Optional()])
    storage = IntegerField('Storage', validators=[Optional()])
    storage_sub = StringField('Storage Sub', validators=[Optional()])
    last_scanned = DateField('Last Scanned', validators=[Optional()], format='%Y-%m-%d')
    submit = SubmitField('Save Changes')

# Header mapping for table columns
def get_header_mapping():
    # Try to load from file
    header_file = 'header_mapping.json'
    if os.path.exists(header_file):
        try:
            with open(header_file, 'r') as f:
                return json.load(f)
        except:
            pass
    
    # Default mapping
    default_mapping = {
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
        'storage_sub': 'Storage Sub'
    }
    
    # Save default mapping
    with open(header_file, 'w') as f:
        json.dump(default_mapping, f, indent=4)
    
    return default_mapping

@app.route('/', methods=['GET', 'POST'])
def index():
    form = SearchForm()
    page = request.args.get('page', 1, type=int)
    per_page = 50  # Items per page
    
    conn = get_db_connection()
    
    # Base query
    query = "SELECT * FROM tabelle1 WHERE 1=1"
    params = []
    
    # Apply search filters if form is submitted
    if form.validate_on_submit() or request.args.get('search_param') == '1':
        # Get values from form or URL parameters
        search_term = form.search.data or request.args.get('search', '')
        has_storage = form.has_storage.data or request.args.get('has_storage') == 'True'
        az_pol_filter = request.args.get('az_pol', '')
        
        # Add filters to query
        if search_term:
            # Search across multiple fields
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
            
            # Add search parameters for each field
            for _ in range(len(search_conditions)):
                params.append(f"%{search_term}%")
                
            form.search.data = search_term
            
        if has_storage:
            query += " AND storage IS NOT NULL"
            form.has_storage.data = has_storage
            
        # Filter nach Aktenzeichen, wenn angegeben
        if az_pol_filter:
            query += " AND az_pol = ?"
            params.append(az_pol_filter)
    
    # Count total results for pagination
    count_query = f"SELECT COUNT(*) FROM ({query})"
    total_count = conn.execute(count_query, params).fetchone()[0]
    total_pages = math.ceil(total_count / per_page)
    
    # Add pagination to query
    query += " ORDER BY id LIMIT ? OFFSET ?"
    offset = (page - 1) * per_page
    params.extend([per_page, offset])
    
    # Execute query
    items = conn.execute(query, params).fetchall()
    
    # Get column names for table headers
    columns = [column[1] for column in conn.execute("PRAGMA table_info(tabelle1)").fetchall()]
    
    # Exclude the last_scanned column from the list view
    if 'last_scanned' in columns:
        columns.remove('last_scanned')
    
    # Get header mapping
    header_mapping = get_header_mapping()
    
    conn.close()
    
    return render_template(
        'index.html', 
        items=items, 
        columns=columns, 
        header_mapping=header_mapping,
        form=form,
        page=page, 
        total_pages=total_pages,
        total_count=total_count,
        search_active=bool(request.args.get('search_param'))
    )

@app.route('/detail/<int:id>', methods=['GET', 'POST'])
def detail(id):
    conn = get_db_connection()
    
    # Get the item by ID
    item = conn.execute('SELECT * FROM tabelle1 WHERE id = ?', (id,)).fetchone()
    if item is None:
        conn.close()
        abort(404)
    
    # Create form and populate with data
    form = EditForm()
    
    # Lade die place_status- und type-Optionen aus der Datenbank
    form.place_status.choices = get_place_status_options()
    form.type.choices = get_type_options()
    
    # If form is submitted and valid, update the database
    if form.validate_on_submit():
        # Prepare update data
        data = (
            form.az_pol.data,
            form.place_status.data,
            form.ass_number.data,
            form.type.data,
            form.vendor.data,
            form.model.data,
            form.model_desc.data,
            form.status.data,
            form.serial.data,
            form.barcode.data,
            form.seized_by.data,
            form.status_hint.data,
            form.storage.data,
            form.storage_sub.data,
            form.last_scanned.data.strftime('%Y-%m-%d') if form.last_scanned.data else None,
            id
        )
        
        # Update the database
        conn.execute(
            '''
            UPDATE tabelle1 SET 
                az_pol = ?, 
                place_status = ?, 
                ass_number = ?, 
                type = ?, 
                vendor = ?, 
                model = ?, 
                model_desc = ?, 
                status = ?, 
                serial = ?, 
                barcode = ?, 
                seized_by = ?, 
                status_hint = ?,
                storage = ?,
                storage_sub = ?,
                last_scanned = ?
            WHERE id = ?
            ''', data
        )
        conn.commit()
        flash('Item updated successfully')
        return redirect(url_for('detail', id=id))
    
    # For GET request, populate form with existing data
    elif request.method == 'GET':
        form.az_pol.data = item['az_pol']
        form.place_status.data = item['place_status']
        form.ass_number.data = item['ass_number']
        form.type.data = item['type']
        form.vendor.data = item['vendor']
        form.model.data = item['model']
        form.model_desc.data = item['model_desc']
        form.status.data = item['status']
        form.serial.data = item['serial']
        form.barcode.data = item['barcode']
        form.seized_by.data = item['seized_by']
        form.status_hint.data = item['status_hint']
        form.storage.data = item['storage']
        form.storage_sub.data = item['storage_sub']
        
        # Handle date field
        if item['last_scanned']:
            try:
                from datetime import datetime
                form.last_scanned.data = datetime.strptime(item['last_scanned'], '%Y-%m-%d')
            except (ValueError, TypeError):
                form.last_scanned.data = None
    
    # Get header mapping for field labels
    header_mapping = get_header_mapping()
    
    conn.close()
    # Verwende das Aktenzeichen als Titel für die Detailseite
    title = item['az_pol']
    return render_template('detail.html', form=form, item=item, id=id, header_mapping=header_mapping, title=title)

@app.route('/scanner', methods=['GET', 'POST'])
def scanner():
    error = None
    success = None
    
    if request.method == 'POST':
        barcode = request.form.get('barcode', '').strip()
        
        # Validiere den Barcode
        if len(barcode) != 12 or not barcode.isdigit():
            error = 'Der Barcode muss genau 12 Ziffern enthalten.'
        else:
            # Suche nach dem Barcode in der Datenbank
            # Entferne die letzte Ziffer (Prüfziffer) und führende Nullen
            # Beispiel: 000292565683 -> 29256568
            barcode_transformed = int(barcode[:-1])
            
            conn = get_db_connection()
            item = conn.execute('SELECT id FROM tabelle1 WHERE barcode = ?', (barcode_transformed,)).fetchone()
            conn.close()
            
            if item:
                # Wenn gefunden, leite zur Detailseite weiter und öffne in neuem Tab via JavaScript
                success = f'Barcode {barcode} gefunden! Öffne Detailseite...'
                return render_template('scanner.html', 
                                      success=success, 
                                      item_id=item['id'],
                                      redirect_script=True,
                                      title='Scanner')
            else:
                error = f'Barcode {barcode} wurde nicht in der Datenbank gefunden.'
    
    return render_template('scanner.html', error=error, success=success, title='Scanner')

@app.route('/auto_scanner', methods=['GET', 'POST'])
def auto_scanner():
    error = None
    success = None
    storage = request.form.get('storage', '')
    storage_sub = request.form.get('storage_sub', '')
    item_data = None
    
    if request.method == 'POST':
        barcode = request.form.get('barcode', '').strip()
        
        # Validiere den Barcode
        if len(barcode) != 12 or not barcode.isdigit():
            error = 'Der Barcode muss genau 12 Ziffern enthalten.'
        elif not storage:
            error = 'Storage ist ein Pflichtfeld.'
        else:
            # Suche nach dem Barcode in der Datenbank
            # Entferne die letzte Ziffer (Prüfziffer) und führende Nullen
            # Beispiel: 000292565683 -> 29256568
            barcode_transformed = int(barcode[:-1])
            
            conn = get_db_connection()
            # Hole zusätzliche Informationen (AZ, Spurnummer, Typ, Vendor)
            item = conn.execute('SELECT id, az_pol, ass_number, type, vendor FROM tabelle1 WHERE barcode = ?', 
                               (barcode_transformed,)).fetchone()
            
            if item:
                # Aktualisiere den Datensatz mit den neuen Storage-Werten
                try:
                    # Aktualisiere auch das last_scanned Feld mit dem aktuellen Datum
                    from datetime import date
                    today = date.today().strftime('%Y-%m-%d')
                    
                    conn.execute(
                        '''
                        UPDATE tabelle1 SET 
                            storage = ?, 
                            storage_sub = ?,
                            last_scanned = ?
                        WHERE id = ?
                        ''', (storage, storage_sub, today, item['id'])
                    )
                    conn.commit()
                    success = f'Barcode {barcode} gefunden und Lagerort aktualisiert!'
                    
                    # Speichere die Artikeldaten für die Anzeige
                    item_data = {
                        'id': item['id'],
                        'az_pol': item['az_pol'],
                        'ass_number': item['ass_number'],
                        'type': item['type'],
                        'vendor': item['vendor']
                    }
                except Exception as e:
                    error = f'Fehler beim Aktualisieren des Datensatzes: {str(e)}'
            else:
                error = f'Barcode {barcode} wurde nicht in der Datenbank gefunden.'
            
            conn.close()
    
    return render_template('auto_scanner.html', 
                          error=error, 
                          success=success, 
                          storage=storage, 
                          storage_sub=storage_sub, 
                          item_data=item_data,
                          title='Auto-Scanner')

@app.route('/add_new', methods=['GET', 'POST'])
def add_new():
    # Erstelle ein neues Formular für den neuen Eintrag
    form = EditForm()
    
    # Lade die place_status- und type-Optionen aus der Datenbank
    form.place_status.choices = get_place_status_options()
    form.type.choices = get_type_options()
    
    # Ändere den Submit-Button-Text
    form.submit.label.text = 'Eintrag hinzufügen'
    
    # Wenn das Formular abgesendet und gültig ist, füge den neuen Eintrag hinzu
    if form.validate_on_submit():
        conn = get_db_connection()
        
        try:
            # Bereite die Daten für den neuen Eintrag vor
            data = (
                form.az_pol.data,
                form.place_status.data,
                form.ass_number.data,
                form.type.data,
                form.vendor.data,
                form.model.data,
                form.model_desc.data,
                form.status.data,
                form.serial.data,
                form.barcode.data,
                form.seized_by.data,
                form.status_hint.data,
                form.storage.data,
                form.storage_sub.data,
                form.last_scanned.data.strftime('%Y-%m-%d') if form.last_scanned.data else None
            )
            
            # Füge den neuen Eintrag in die Datenbank ein
            cursor = conn.execute(
                '''
                INSERT INTO tabelle1 (
                    az_pol, place_status, ass_number, type, vendor, model, model_desc,
                    status, serial, barcode, seized_by, status_hint, storage, storage_sub, last_scanned
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', data
            )
            
            # Hole die ID des neu eingefügten Eintrags
            new_id = cursor.lastrowid
            
            conn.commit()
            flash('Neuer Eintrag erfolgreich hinzugefügt!')
            
            # Leite zur Detailseite des neuen Eintrags weiter
            return redirect(url_for('detail', id=new_id))
        
        except Exception as e:
            flash(f'Fehler beim Hinzufügen des Eintrags: {str(e)}', 'error')
        
        finally:
            conn.close()
    
    # Für GET-Anfragen oder wenn das Formular nicht gültig ist, zeige das Formular an
    return render_template('add_new.html', form=form, title='Neu hinzufügen')

if __name__ == '__main__':
    app.run(debug=True)
