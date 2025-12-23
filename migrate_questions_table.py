#!/usr/bin/env python3
import sqlite3
import sys
import os

def migrate_questions_table():
    """Add missing columns to questions table to match the updated model"""
    
    # Connect to database
    conn = sqlite3.connect('data/bot.db')
    cursor = conn.cursor()
    
    try:
        # Check current schema
        cursor.execute("PRAGMA table_info(questions);")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        print("Current questions table schema:")
        for col in columns:
            print(f"  {col[1]} ({col[2]})")
        print()
        
        # List of columns to add
        columns_to_add = [
            ('correct_answer', 'VARCHAR(10)'),
            ('course', 'VARCHAR(100)'),
            ('difficulty', 'VARCHAR(20)'),
            ('created_at', 'DATETIME DEFAULT CURRENT_TIMESTAMP')
        ]
        
        # Add missing columns
        for col_name, col_type in columns_to_add:
            if col_name not in column_names:
                try:
                    cursor.execute(f"ALTER TABLE questions ADD COLUMN {col_name} {col_type};")
                    print(f"✅ Added column: {col_name} ({col_type})")
                except sqlite3.Error as e:
                    print(f"❌ Failed to add column {col_name}: {e}")
            else:
                print(f"ℹ️ Column {col_name} already exists")
        
        # Commit changes
        conn.commit()
        print("\n✅ Migration completed successfully!")
        
        # Verify new schema
        cursor.execute("PRAGMA table_info(questions);")
        new_columns = cursor.fetchall()
        
        print("\nUpdated questions table schema:")
        for col in new_columns:
            print(f"  {col[1]} ({col[2]})")
            
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    print("🔧 Migrating questions table...")
    migrate_questions_table()
    print("Migration script completed.")
