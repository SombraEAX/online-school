#!/usr/bin/env python3
import sqlite3
import os

db_paths = ['instance/users.db', 'users.db']
db_path = None
for path in db_paths:
    if os.path.exists(path):
        db_path = path
        break

if not db_path:
    print('Database not found')
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("PRAGMA table_info(landing_page)")
columns = [col[1] for col in cursor.fetchall()]

if 'topics_section_description' not in columns:
    cursor.execute("ALTER TABLE landing_page ADD COLUMN topics_section_description TEXT")
    print('Added topics_section_description column')
else:
    print('Column already exists')

conn.commit()
conn.close()
