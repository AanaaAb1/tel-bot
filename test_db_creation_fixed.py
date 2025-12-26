#!/usr/bin/env python3
"""
Test script to verify database table creation and model consistency
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database.base import Base
from app.database.session import engine
from app.models import Question, Course, Chapter

print("Testing database schema creation...")
print("Question model columns:")
print([column.name for column in Question.__table__.columns])

print("\nCreating tables...")
try:
    # Drop existing tables first to ensure clean schema
    print("Dropping existing tables...")
    Base.metadata.drop_all(bind=engine)
    
    print("Creating tables with fresh schema...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully!")
    
    # Check if explanation column exists in the database
    from sqlalchemy import inspect
    inspector = inspect(engine)
    columns = inspector.get_columns('questions')
    column_names = [col['name'] for col in columns]
    print(f"Actual database columns: {column_names}")
    
    if 'explanation' in column_names:
        print("✅ explanation column exists in database")
    else:
        print("❌ explanation column missing from database")
        
except Exception as e:
    print(f"Error creating tables: {e}")
    import traceback
    traceback.print_exc()
