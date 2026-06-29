#!/usr/bin/env python3
"""Script to recreate the database with an updated schema"""
import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db

db_path = os.path.join(os.path.dirname(__file__), 'users.db')

# Delete old database
if os.path.exists(db_path):
    os.remove(db_path)
    print(f"Deleted old database: {db_path}")

# Create new database with updated schema
with app.app_context():
    db.create_all()
    print("Database created successfully!")
    
    # Check article table structure
    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    columns = [col['name'] for col in inspector.get_columns('article')]
    print(f"Columns in article table: {columns}")
    
    if 'media_path' in columns:
        print("SUCCESS: column media_path created!")
    else:
        print("ERROR: column media_path NOT created!")
        sys.exit(1)
