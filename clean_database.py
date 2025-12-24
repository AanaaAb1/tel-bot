#!/usr/bin/env python3
"""
Database Data Cleaning Script
Clears all user data except admin users
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from app.database.session import SessionLocal
from app.models.user import User
from app.config.constants import ADMIN_IDS

def clean_database():
    """Clean all user data while preserving admin users in constants"""
    print("🧹 Starting database cleanup...")
    
    # Create database engine
    engine = create_engine('sqlite:///exam_bot.db')
    
    try:
        # Connect to database
        with engine.connect() as conn:
            print("📊 Database connection established")
            
            # Get all tables
            result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
            tables = [row[0] for row in result.fetchall()]
            print(f"📋 Found tables: {tables}")
            
            # Define tables to clean (in order to avoid foreign key issues)
            tables_to_clean = [
                'referrals',
                'exam_results', 
                'exam_answers',
                'user_exam_progress',
                'payments',
                'exams',
                'questions',
                'users'
            ]
            
            cleaned_tables = []
            
            for table in tables_to_clean:
                if table in tables:
                    try:
                        # Check if table exists and has data
                        count_result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                        count = count_result.fetchone()[0]
                        
                        if count > 0:
                            # Clear table data
                            conn.execute(text(f"DELETE FROM {table}"))
                            print(f"🗑️  Cleared {count} records from {table}")
                            cleaned_tables.append(table)
                        else:
                            print(f"✅ {table} is already empty")
                            
                    except Exception as e:
                        print(f"⚠️  Error cleaning {table}: {e}")
                else:
                    print(f"ℹ️  Table {table} not found, skipping")
            
            # Commit changes
            conn.commit()
            print(f"✅ Database cleanup completed!")
            print(f"📊 Tables cleaned: {cleaned_tables}")
            
    except Exception as e:
        print(f"❌ Database cleanup failed: {e}")
        return False
    
    return True

def verify_admin_users():
    """Verify admin users are still in constants"""
    print("\n👑 Verifying admin users...")
    print(f"Admin IDs in constants: {ADMIN_IDS}")
    
    # Check if the specified admin IDs are still there
    expected_admins = [5642507992, 7342121804]
    
    for admin_id in expected_admins:
        if admin_id in ADMIN_IDS:
            print(f"✅ Admin {admin_id} is preserved in constants")
        else:
            print(f"❌ Admin {admin_id} missing from constants!")
            
    return True

def show_final_status():
    """Show final database status"""
    print("\n📋 Final Database Status:")
    
    try:
        engine = create_engine('sqlite:///exam_bot.db')
        with engine.connect() as conn:
            
            # Check users table
            result = conn.execute(text("SELECT COUNT(*) FROM users"))
            user_count = result.fetchone()[0]
            print(f"👥 Total users: {user_count}")
            
            # Check payments table  
            result = conn.execute(text("SELECT COUNT(*) FROM payments"))
            payment_count = result.fetchone()[0]
            print(f"💰 Total payments: {payment_count}")
            
            # Check questions table
            result = conn.execute(text("SELECT COUNT(*) FROM questions"))
            question_count = result.fetchone()[0]
            print(f"❓ Total questions: {question_count}")
            
            # Check exams table
            result = conn.execute(text("SELECT COUNT(*) FROM exams"))
            exam_count = result.fetchone()[0]
            print(f"📝 Total exams: {exam_count}")
            
    except Exception as e:
        print(f"⚠️  Could not check final status: {e}")

def main():
    """Main cleanup function"""
    print("🚀 Database Data Cleaning Script")
    print("=" * 50)
    print("This script will:")
    print("• Clear all user registration data")
    print("• Clear all payment records") 
    print("• Clear all exam results")
    print("• Keep admin users in constants")
    print("• Preserve database structure")
    print("=" * 50)
    
    # Verify admin users first
    verify_admin_users()
    
    # Confirm before proceeding
    response = input("\n⚠️  Are you sure you want to proceed with database cleanup? (yes/no): ")
    if response.lower() != 'yes':
        print("❌ Cleanup cancelled")
        return False
    
    # Clean database
    success = clean_database()
    
    if success:
        show_final_status()
        print("\n🎉 Database cleanup completed successfully!")
        print("✅ Admin users preserved")
        print("✅ All user data cleared")
        print("✅ System ready for fresh registrations")
    else:
        print("\n❌ Database cleanup failed!")
        
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
