#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd
import sqlite3
import os

def analyze_excel_file(excel_file):
    """
    Analyze the Excel file structure and print information about its sheets and columns
    """
    print(f"Analyzing Excel file: {excel_file}")
    
    # Read the Excel file
    xls = pd.ExcelFile(excel_file)
    
    # Get sheet names
    sheet_names = xls.sheet_names
    print(f"Found {len(sheet_names)} sheets: {', '.join(sheet_names)}")
    
    # Analyze each sheet
    tables_info = []
    
    for sheet in sheet_names:
        print(f"\nSheet: {sheet}")
        df = pd.read_excel(excel_file, sheet_name=sheet)
        
        # Get column information
        print(f"Number of rows: {len(df)}")
        print(f"Number of columns: {len(df.columns)}")
        print("Columns:")
        
        columns_info = []
        for col in df.columns:
            # Determine data type
            dtype = df[col].dtype
            sample = df[col].iloc[0] if not df[col].empty else None
            
            # Map pandas dtype to SQLite type
            if pd.api.types.is_integer_dtype(dtype):
                sql_type = "INTEGER"
            elif pd.api.types.is_float_dtype(dtype):
                sql_type = "REAL"
            elif pd.api.types.is_datetime64_dtype(dtype):
                sql_type = "TIMESTAMP"
            else:
                sql_type = "TEXT"
                
            print(f"  - {col} ({sql_type}): {dtype}, Sample: {sample}")
            columns_info.append({
                "name": col,
                "dtype": str(dtype),
                "sql_type": sql_type,
                "sample": sample
            })
        
        tables_info.append({
            "sheet_name": sheet,
            "columns": columns_info,
            "row_count": len(df)
        })
    
    return tables_info

def generate_schema(tables_info):
    """
    Generate a SQLite schema based on the Excel structure
    """
    schema = []
    
    for table in tables_info:
        table_name = table["sheet_name"].replace(" ", "_").lower()
        columns = []
        
        # Add id column as primary key
        columns.append("id INTEGER PRIMARY KEY AUTOINCREMENT")
        
        for col in table["columns"]:
            # Clean column name (remove spaces, special chars)
            col_name = col["name"].replace(" ", "_").lower()
            col_name = ''.join(c for c in col_name if c.isalnum() or c == '_')
            
            # Skip if empty column name after cleaning
            if not col_name:
                continue
                
            columns.append(f"{col_name} {col['sql_type']}")
        
        create_table = f"CREATE TABLE {table_name} (\n  " + ",\n  ".join(columns) + "\n);"
        schema.append(create_table)
    
    return schema

def write_schema_to_file(schema, output_file):
    """
    Write the generated schema to a file
    """
    with open(output_file, 'w') as f:
        f.write("\n\n".join(schema))
    print(f"Schema written to {output_file}")

def create_database(excel_file, db_file, schema):
    """
    Create SQLite database and import data from Excel
    """
    # Connect to SQLite database (will create if it doesn't exist)
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    # Execute schema to create tables
    for create_table in schema:
        cursor.execute(create_table)
    
    # Read Excel file and import data
    xls = pd.ExcelFile(excel_file)
    
    for sheet in xls.sheet_names:
        table_name = sheet.replace(" ", "_").lower()
        df = pd.read_excel(excel_file, sheet_name=sheet)
        
        # Clean column names
        df.columns = [
            ''.join(c for c in col.replace(" ", "_").lower() if c.isalnum() or c == '_')
            for col in df.columns
        ]
        
        # Import data
        df.to_sql(table_name, conn, if_exists='append', index=False)
        print(f"Imported {len(df)} rows into table {table_name}")
    
    conn.commit()
    conn.close()
    print(f"Database created at {db_file}")

if __name__ == "__main__":
    excel_file = "Asservatenliste.xlsx"
    db_file = "inventory.db"
    schema_file = "db_schema.txt"
    
    # Analyze Excel file
    tables_info = analyze_excel_file(excel_file)
    
    # Generate schema
    schema = generate_schema(tables_info)
    
    # Write schema to file
    write_schema_to_file(schema, schema_file)
    
    # Create database and import data
    create_database(excel_file, db_file, schema)
