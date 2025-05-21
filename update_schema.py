#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3

def update_database_schema(db_file):
    """
    Update the database schema to add the last_scanned field
    """
    print(f"Updating database schema for {db_file}")
    
    # Connect to SQLite database
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    # Check if column already exists
    cursor.execute("PRAGMA table_info(tabelle1)")
    columns = [col[1] for col in cursor.fetchall()]
    
    # Add last_scanned column if it doesn't exist
    if 'last_scanned' not in columns:
        print("Adding 'last_scanned' column...")
        cursor.execute("ALTER TABLE tabelle1 ADD COLUMN last_scanned DATE")
        print("Column 'last_scanned' added successfully")
    else:
        print("Column 'last_scanned' already exists")
    
    # Commit changes and close connection
    conn.commit()
    conn.close()
    
    print("Database schema updated successfully")

if __name__ == "__main__":
    update_database_schema("inventory.db")
