#!/usr/bin/env python3
"""Migration to add media_path, media_type and disable_link_preview columns to article table"""

import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'users.db')

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check existing columns
cursor.execute("PRAGMA table_info(article)")
columns = [row[1] for row in cursor.fetchall()]
print(f"Existing columns: {columns}")

# Add new columns if they don't exist
if 'media_path' not in columns:
    cursor.execute("ALTER TABLE article ADD COLUMN media_path VARCHAR(500)")
    print("Added column media_path")

if 'media_type' not in columns:
    cursor.execute("ALTER TABLE article ADD COLUMN media_type VARCHAR(10)")
    print("Added column media_type")

if 'disable_link_preview' not in columns:
    cursor.execute("ALTER TABLE article ADD COLUMN disable_link_preview BOOLEAN DEFAULT 0")
    print("Added column disable_link_preview")

conn.commit()
conn.close()
print("Migration completed successfully!")
