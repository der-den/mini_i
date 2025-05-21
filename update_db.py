#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3

def update_database_schema(db_file):
    """
    Update the database schema to add new columns
    """
    print(f"Updating database schema for {db_file}")
    
    # Connect to SQLite database
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    # Check if columns already exist
    cursor.execute("PRAGMA table_info(tabelle1)")
    columns = [col[1] for col in cursor.fetchall()]
    
    # Add storage column if it doesn't exist
    if 'storage' not in columns:
        print("Adding 'storage' column...")
        cursor.execute("ALTER TABLE tabelle1 ADD COLUMN storage INTEGER")
    else:
        print("Column 'storage' already exists")
    
    # Add storage_sub column if it doesn't exist
    if 'storage_sub' not in columns:
        print("Adding 'storage_sub' column...")
        cursor.execute("ALTER TABLE tabelle1 ADD COLUMN storage_sub TEXT")
    else:
        print("Column 'storage_sub' already exists")
    
    # Commit changes and close connection
    conn.commit()
    conn.close()
    
    print("Database schema updated successfully")

if __name__ == "__main__":
    update_database_schema("inventory.db")
