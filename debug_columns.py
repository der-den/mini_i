#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3

def debug_columns():
    """Debug the column access in the database"""
    print("Debugging column access...")
    
    # Connect to the database
    conn = sqlite3.connect('inventory.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get column information
    print("\nColumn information from PRAGMA:")
    cursor.execute("PRAGMA table_info(tabelle1)")
    columns = cursor.fetchall()
    for col in columns:
        print(f"Column: {col[0]} - {col[1]} ({col[2]})")
    
    # Get a sample row
    print("\nSample row:")
    cursor.execute("SELECT * FROM tabelle1 LIMIT 1")
    row = cursor.fetchone()
    
    # Print row as dictionary
    print("\nRow as dictionary:")
    row_dict = dict(row)
    for key, value in row_dict.items():
        print(f"{key}: {value}")
    
    # Try accessing by column name
    print("\nAccessing by column name:")
    for col in [col[1] for col in columns]:
        try:
            print(f"{col}: {row[col]}")
        except Exception as e:
            print(f"Error accessing {col}: {e}")
    
    # Close connection
    conn.close()

if __name__ == "__main__":
    debug_columns()
