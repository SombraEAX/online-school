#!/usr/bin/env python3
"""
Database migration script to add 'price' column to courses table
"""

import sqlite3
import os

def migrate_database():
    # Check both possible locations for the database
    db_paths = ['users.db', 'instance/users.db']
    db_path = None
    
    for path in db_paths:
        if os.path.exists(path):
            db_path = path
            break
    
    if not db_path:
        print("Database file not found!")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if the column already exists
        cursor.execute("PRAGMA table_info(course)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'price' in columns:
            print("Column 'price' already exists in courses table")
            return
        
        # Add the price column
        cursor.execute("ALTER TABLE course ADD COLUMN price NUMERIC")
        
        # Commit the changes
        conn.commit()
        print("Successfully added 'price' column to courses table")
        
        # Verify the column was added
        cursor.execute("PRAGMA table_info(course)")
        columns = [column[1] for column in cursor.fetchall()]
        print(f"Current columns in course table: {columns}")
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    migrate_database()
