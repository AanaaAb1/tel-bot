#!/usr/bin/env python3
"""
Database Migration Script for Profile and Referral System
This script adds the new referral columns to the existing users table.
"""

import sqlite3
import os
from datetime import datetime

def migrate_database():
    """Add referral columns to the users table"""
    print("🔄 Starting database migration for referral system...")
    
    # Get database path
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'bot.db')
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found at {db_path}")
        return False
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print(f"📂 Connected to database: {db_path}")
        
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(users)")
        existing_columns = [row[1] for row in cursor.fetchall()]
        
        print(f"📋 Current columns in users table: {existing_columns}")
        
        # Define new columns to add
        new_columns = [
            ("referral_code", "VARCHAR(8)"),  # Remove UNIQUE constraint
            ("referred_by_id", "INTEGER"),
            ("total_referrals", "INTEGER DEFAULT 0"),
            ("total_commission", "INTEGER DEFAULT 0"),
            ("is_referral_active", "BOOLEAN DEFAULT 1")
        ]
        
        columns_to_add = []
        for column_name, column_type in new_columns:
            if column_name not in existing_columns:
                columns_to_add.append(f"{column_name} {column_type}")
                print(f"➕ Will add column: {column_name}")
            else:
                print(f"✅ Column already exists: {column_name}")
        
        if not columns_to_add:
            print("✅ All referral columns already exist. No migration needed.")
            conn.close()
            return True
        
        # Add new columns
        for column_def in columns_to_add:
            alter_query = f"ALTER TABLE users ADD COLUMN {column_def}"
            cursor.execute(alter_query)
            print(f"✅ Added column: {column_def}")
        
        # Commit changes
        conn.commit()
        print("💾 Migration completed successfully!")
        
        # Verify the changes
        cursor.execute("PRAGMA table_info(users)")
        updated_columns = [row[1] for row in cursor.fetchall()]
        print(f"📋 Updated columns: {updated_columns}")
        
        # Create referrals table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS referrals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                referrer_id INTEGER NOT NULL,
                referred_id INTEGER NOT NULL,
                status VARCHAR DEFAULT 'PENDING',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                completed_at DATETIME,
                commission_earned INTEGER DEFAULT 30,
                commission_paid BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (referrer_id) REFERENCES users (id),
                FOREIGN KEY (referred_id) REFERENCES users (id),
                UNIQUE(referrer_id, referred_id)
            )
        """)
        print("✅ Referrals table created/verified")
        
        conn.commit()
        conn.close()
        
        print("🎉 Database migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False

if __name__ == "__main__":
    print("🚀 Profile & Referral System - Database Migration")
    print("=" * 50)
    
    success = migrate_database()
    
    if success:
        print("\n✅ Migration completed successfully!")
        print("🚀 You can now restart the bot to use the referral system.")
    else:
        print("\n❌ Migration failed. Please check the error messages above.")
    
    print("\n" + "=" * 50)
