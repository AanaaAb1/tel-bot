#!/usr/bin/env python3
"""
Comprehensive System Diagnostic
"""

import sys
import os
import traceback
from pathlib import Path

def test_imports():
    """Test all required imports"""
    print("=" * 60)
    print("IMPORT TESTING")
    print("=" * 60)
    
    imports_to_test = [
        ('flask', 'Flask web framework'),
        ('flask_login', 'Flask-Login extension'),
        ('werkzeug.security', 'Werkzeug security utilities'),
        ('sqlalchemy', 'SQLAlchemy ORM'),
        ('datetime', 'DateTime utilities'),
        ('json', 'JSON utilities'),
    ]
    
    results = {}
    
    for module_name, description in imports_to_test:
        try:
            if module_name == 'flask':
                import flask
                results[module_name] = f"✅ {description} - Version: {flask.__version__}"
            elif module_name == 'flask_login':
                import flask_login
                results[module_name] = f"✅ {description} - Version: {flask_login.__version__}"
            elif module_name == 'werkzeug.security':
                import werkzeug.security
                results[module_name] = f"✅ {description}"
            elif module_name == 'sqlalchemy':
                import sqlalchemy
                results[module_name] = f"✅ {description} - Version: {sqlalchemy.__version__}"
            elif module_name == 'datetime':
                import datetime
                results[module_name] = f"✅ {description}"
            elif module_name == 'json':
                import json
                results[module_name] = f"✅ {description}"
        except ImportError as e:
            results[module_name] = f"❌ {description} - Import Error: {e}"
        except Exception as e:
            results[module_name] = f"⚠️ {description} - Error: {e}"
    
    for module_name, result in results.items():
        print(result)
    
    return results

def test_database_imports():
    """Test database-related imports"""
    print("\n" + "=" * 60)
    print("DATABASE IMPORT TESTING")
    print("=" * 60)
    
    database_imports = [
        ('app.database.session', 'SessionLocal'),
        ('app.database.base', 'Base'),
        ('app.models.user', 'User'),
        ('app.models.course', 'Course'),
        ('app.models.chapter', 'Chapter'),
        ('app.models.question', 'Question'),
        ('app.models.payment', 'Payment'),
    ]
    
    results = {}
    
    for module_path, description in database_imports:
        try:
            if module_path == 'app.database.session':
                from app.database.session import SessionLocal
                results[module_path] = f"✅ {description} - Import successful"
            elif module_path == 'app.database.base':
                from app.database.base import Base
                results[module_path] = f"✅ {description} - Import successful"
            elif module_path == 'app.models.user':
                from app.models.user import User
                results[module_path] = f"✅ {description} - Import successful"
            elif module_path == 'app.models.course':
                from app.models.course import Course
                results[module_path] = f"✅ {description} - Import successful"
            elif module_path == 'app.models.chapter':
                from app.models.chapter import Chapter
                results[module_path] = f"✅ {description} - Import successful"
            elif module_path == 'app.models.question':
                from app.models.question import Question
                results[module_path] = f"✅ {description} - Import successful"
            elif module_path == 'app.models.payment':
                from app.models.payment import Payment
                results[module_path] = f"✅ {description} - Import successful"
        except ImportError as e:
            results[module_path] = f"❌ {description} - Import Error: {e}"
        except Exception as e:
            results[module_path] = f"⚠️ {description} - Error: {e}"
    
    for module_path, result in results.items():
        print(result)
    
    return results

def test_database_connection():
    """Test database connection"""
    print("\n" + "=" * 60)
    print("DATABASE CONNECTION TESTING")
    print("=" * 60)
    
    try:
        from app.database.session import SessionLocal, engine
        from app.database.base import Base
        
        # Test database creation
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully")
        
        # Test session
        db = SessionLocal()
        print("✅ Database session created successfully")
        
        # Test basic query
        from app.models.user import User
        user_count = db.query(User).count()
        print(f"✅ Database query successful - User count: {user_count}")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        traceback.print_exc()
        return False

def test_template_files():
    """Test template files existence"""
    print("\n" + "=" * 60)
    print("TEMPLATE FILES TESTING")
    print("=" * 60)
    
    template_files = [
        'templates/base.html',
        'templates/admin/login.html',
        'templates/admin/dashboard.html',
        'templates/admin/courses.html',
        'templates/admin/course_form.html',
        'templates/admin/chapters.html',
        'templates/admin/chapter_form.html',
        'templates/admin/questions.html',
        'templates/admin/question_form.html',
        'templates/admin/users.html',
        'templates/admin/payments.html',
    ]
    
    results = {}
    
    for template_file in template_files:
        file_path = Path(template_file)
        if file_path.exists():
            results[template_file] = f"✅ {template_file} - Exists"
        else:
            results[template_file] = f"❌ {template_file} - Missing"
    
    for template_file, result in results.items():
        print(result)
    
    return results

def test_flask_app_creation():
    """Test Flask app creation"""
    print("\n" + "=" * 60)
    print("FLASK APP CREATION TESTING")
    print("=" * 60)
    
    try:
        from flask import Flask
        from flask_login import LoginManager
        from werkzeug.security import generate_password_hash
        
        app = Flask(__name__)
        app.secret_key = 'test-secret-key'
        
        # Test Flask-Login
        login_manager = LoginManager()
        login_manager.init_app(app)
        
        print("✅ Flask app created successfully")
        print("✅ Flask-Login initialized successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Flask app creation error: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all diagnostic tests"""
    print("🔍 COMPREHENSIVE SYSTEM DIAGNOSTIC")
    print("=" * 60)
    
    # Test imports
    import_results = test_imports()
    
    # Test database imports
    db_import_results = test_database_imports()
    
    # Test database connection
    db_connection_result = test_database_connection()
    
    # Test template files
    template_results = test_template_files()
    
    # Test Flask app creation
    flask_app_result = test_flask_app_creation()
    
    # Summary
    print("\n" + "=" * 60)
    print("DIAGNOSTIC SUMMARY")
    print("=" * 60)
    
    print(f"📦 Import Tests: {sum(1 for r in import_results.values() if '✅' in r)}/{len(import_results)} passed")
    print(f"🗄️ Database Import Tests: {sum(1 for r in db_import_results.values() if '✅' in r)}/{len(db_import_results)} passed")
    print(f"🔗 Database Connection: {'✅ Passed' if db_connection_result else '❌ Failed'}")
    print(f"🎨 Template Tests: {sum(1 for r in template_results.values() if '✅' in r)}/{len(template_results)} passed")
    print(f"🌐 Flask App Creation: {'✅ Passed' if flask_app_result else '❌ Failed'}")
    
    # Determine if admin panel can run
    all_essential_tests_passed = (
        sum(1 for r in import_results.values() if '✅' in r) >= 5 and  # Most imports work
        sum(1 for r in db_import_results.values() if '✅' in r) >= 4 and  # Most DB imports work
        db_connection_result and  # DB connection works
        flask_app_result  # Flask app works
    )
    
    print(f"\n🚀 Admin Panel Status: {'✅ CAN RUN' if all_essential_tests_passed else '❌ CANNOT RUN'}")
    
    return all_essential_tests_passed

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Diagnostic failed with error: {e}")
        traceback.print_exc()
        sys.exit(1)
