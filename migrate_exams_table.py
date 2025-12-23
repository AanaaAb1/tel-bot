#!/usr/bin/env python3
"""
Database Migration: Add missing columns to exams table
This script adds the missing time_limit and total_marks columns to the exams table.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import sqlite3

def migrate_exams_table():
    """Add missing columns to exams table"""
    
    print("🔧 Starting database migration for exams table...")
    
    # Database file path
    db_path = "data/bot.db"
    
    # Check if database file exists
    if not os.path.exists(db_path):
        print(f"❌ Database file not found: {db_path}")
        return False
    
    # Connect to SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check current columns in exams table
        cursor.execute("PRAGMA table_info(exams)")
        columns = {row[1]: row[2] for row in cursor.fetchall()}
        
        print(f"📋 Current exams table columns: {list(columns.keys())}")
        
        # Add missing columns if they don't exist
        migrations = []
        
        if "time_limit" not in columns:
            print("➕ Adding time_limit column...")
            cursor.execute("ALTER TABLE exams ADD COLUMN time_limit INTEGER")
            migrations.append("time_limit")
        
        if "total_marks" not in columns:
            print("➕ Adding total_marks column...")
            cursor.execute("ALTER TABLE exams ADD COLUMN total_marks INTEGER")
            migrations.append("total_marks")
        
        if "created_at" not in columns:
            print("➕ Adding created_at column...")
            cursor.execute("ALTER TABLE exams ADD COLUMN created_at DATETIME")
            migrations.append("created_at")
        
        # Commit changes
        conn.commit()
        
        # Verify the changes
        cursor.execute("PRAGMA table_info(exams)")
        updated_columns = {row[1]: row[2] for row in cursor.fetchall()}
        
        print(f"✅ Migration completed successfully!")
        print(f"📋 Updated exams table columns: {list(updated_columns.keys())}")
        
        if migrations:
            print(f"🆕 Added columns: {', '.join(migrations)}")
        else:
            print("ℹ️ No columns needed to be added - all columns already exist")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        conn.rollback()
        return False
    
    finally:
        conn.close()

def verify_migration():
    """Verify the migration was successful"""
    print("\n🔍 Verifying migration...")
    
    try:
        # Try to import and query the exam model
        from app.database.session import SessionLocal
        from app.models.exam import Exam
        from app.models.course import Course
        
        db = SessionLocal()
        
        # Try to query exams to ensure the model works
        exams = db.query(Exam).limit(1).all()
        print("✅ Database model queries working correctly")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Exam Table Migration")
    print("=" * 50)
    
    # Run migration
    success = migrate_exams_table()
    
    if success:
        # Verify migration
        verify_migration()
        print("\n🎉 Migration completed successfully!")
        print("✅ The bot should now work without database schema errors")
    else:
        print("\n❌ Migration failed!")
        sys.exit(1)
