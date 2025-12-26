#!/usr/bin/env python3
"""
Test Admin Panel Navigation Improvements

This test verifies that the admin panel navigation has been properly implemented
and that all pages are connected with proper breadcrumb navigation and sidebar links.
"""

import os
import sys
import time
import subprocess
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def start_admin_panel():
    """Start the admin panel server"""
    print("🚀 Starting admin panel server...")
    
    try:
        # Change to project directory
        os.chdir(project_root)
        
        # Start the admin panel
        process = subprocess.Popen(
            [sys.executable, "start_admin_panel.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait for server to start
        time.sleep(3)
        
        return process
        
    except Exception as e:
        print(f"❌ Error starting admin panel: {e}")
        return None

def test_navigation_templates():
    """Test that all navigation templates are properly configured"""
    print("\n📋 Testing Navigation Templates...")
    
    templates_dir = project_root / "templates"
    base_template = templates_dir / "base.html"
    courses_template = templates_dir / "admin" / "courses.html"
    chapters_template = templates_dir / "admin" / "chapters.html"
    questions_template = templates_dir / "admin" / "questions.html"
    
    tests = []
    
    # Test base template has breadcrumb block
    try:
        with open(base_template, 'r') as f:
            content = f.read()
            has_breadcrumb_block = "{% block breadcrumb %}" in content
            has_chapters_link = "Chapters" in content
            has_questions_link = "Questions" in content
            has_navigation_hint = "showQuestionsHint" in content
            
            tests.append(("Base Template - Breadcrumb Block", has_breadcrumb_block))
            tests.append(("Base Template - Chapters Link", has_chapters_link))
            tests.append(("Base Template - Questions Link", has_questions_link))
            tests.append(("Base Template - Navigation Hint", has_navigation_hint))
            
    except Exception as e:
        tests.append(("Base Template - Read Error", False))
    
    # Test chapters template has breadcrumb
    try:
        with open(chapters_template, 'r') as f:
            content = f.read()
            has_breadcrumb = "{% block breadcrumb %}" in content
            has_course_link = "course.name" in content
            
            tests.append(("Chapters Template - Breadcrumb", has_breadcrumb))
            tests.append(("Chapters Template - Course Context", has_course_link))
            
    except Exception as e:
        tests.append(("Chapters Template - Read Error", False))
    
    # Test questions template has breadcrumb
    try:
        with open(questions_template, 'r') as f:
            content = f.read()
            has_breadcrumb = "{% block breadcrumb %}" in content
            has_course_and_chapter = "course.name" in content and "chapter.name" in content
            
            tests.append(("Questions Template - Breadcrumb", has_breadcrumb))
            tests.append(("Questions Template - Full Context", has_course_and_chapter))
            
    except Exception as e:
        tests.append(("Questions Template - Read Error", False))
    
    # Print results
    for test_name, result in tests:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} {test_name}")
    
    return all(result for _, result in tests)

def test_navigation_structure():
    """Test the navigation structure and links"""
    print("\n🔗 Testing Navigation Structure...")
    
    templates_dir = project_root / "templates"
    base_template = templates_dir / "base.html"
    
    try:
        with open(base_template, 'r') as f:
            content = f.read()
        
        # Check for expected navigation elements
        checks = [
            ("Dashboard link", "url_for('dashboard')" in content),
            ("Courses link", "url_for('courses')" in content),
            ("Users link", "url_for('users')" in content),
            ("Payments link", "url_for('payments')" in content),
            ("Breadcrumb block", "{% block breadcrumb %}" in content),
            ("JavaScript navigation hint", "showQuestionsHint" in content),
            ("Active state detection", "request.endpoint" in content)
        ]
        
        for check_name, result in checks:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"  {status} {check_name}")
        
        return all(result for _, result in checks)
        
    except Exception as e:
        print(f"❌ Error testing navigation structure: {e}")
        return False

def test_breadcrumb_implementation():
    """Test breadcrumb implementation in specific templates"""
    print("\n🍞 Testing Breadcrumb Implementation...")
    
    templates_dir = project_root / "templates"
    
    # Test chapters breadcrumb
    chapters_template = templates_dir / "admin" / "chapters.html"
    try:
        with open(chapters_template, 'r') as f:
            chapters_content = f.read()
        
        chapters_breadcrumbs = [
            ("Dashboard link", "url_for('dashboard')" in chapters_content),
            ("Courses link", "url_for('courses')" in chapters_content),
            ("Course name display", "{{ course.name }}" in chapters_content),
            ("Breadcrumb HTML", "<nav aria-label=\"breadcrumb\"" in chapters_content)
        ]
        
        print("  📚 Chapters Template:")
        for check_name, result in chapters_breadcrumbs:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"    {status} {check_name}")
            
    except Exception as e:
        print(f"  ❌ Error testing chapters breadcrumb: {e}")
    
    # Test questions breadcrumb
    questions_template = templates_dir / "admin" / "questions.html"
    try:
        with open(questions_template, 'r') as f:
            questions_content = f.read()
        
        questions_breadcrumbs = [
            ("Dashboard link", "url_for('dashboard')" in questions_content),
            ("Courses link", "url_for('courses')" in questions_content),
            ("Chapters link", "url_for('chapters'" in questions_content),
            ("Course name display", "{{ course.name }}" in questions_content),
            ("Chapter name display", "{{ chapter.name }}" in questions_content)
        ]
        
        print("  ❓ Questions Template:")
        for check_name, result in questions_breadcrumbs:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"    {status} {check_name}")
            
    except Exception as e:
        print(f"  ❌ Error testing questions breadcrumb: {e}")

def test_file_structure():
    """Test that all required template files exist"""
    print("\n📁 Testing File Structure...")
    
    templates_dir = project_root / "templates"
    admin_dir = templates_dir / "admin"
    
    required_files = [
        ("base.html", templates_dir / "base.html"),
        ("dashboard.html", admin_dir / "dashboard.html"),
        ("courses.html", admin_dir / "courses.html"),
        ("chapters.html", admin_dir / "chapters.html"),
        ("questions.html", admin_dir / "questions.html"),
        ("users.html", admin_dir / "users.html"),
        ("payments.html", admin_dir / "payments.html"),
        ("login.html", admin_dir / "login.html")
    ]
    
    all_exist = True
    for file_name, file_path in required_files:
        exists = file_path.exists()
        status = "✅ PASS" if exists else "❌ FAIL"
        print(f"  {status} {file_name}")
        if not exists:
            all_exist = False
    
    return all_exist

def main():
    """Main test function"""
    print("🧪 Admin Panel Navigation Test Suite")
    print("=" * 50)
    
    # Test file structure
    files_ok = test_file_structure()
    
    # Test navigation templates
    templates_ok = test_navigation_templates()
    
    # Test navigation structure
    structure_ok = test_navigation_structure()
    
    # Test breadcrumb implementation
    test_breadcrumb_implementation()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    total_tests = 4
    passed_tests = sum([files_ok, templates_ok, structure_ok])
    
    print(f"✅ Tests Passed: {passed_tests}/{total_tests}")
    print(f"❌ Tests Failed: {total_tests - passed_tests}/{total_tests}")
    
    if passed_tests == total_tests:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Admin panel navigation is properly implemented")
        print("✅ Breadcrumb navigation is working")
        print("✅ Sidebar navigation is complete")
        print("✅ Navigation flow is connected")
        return True
    else:
        print(f"\n⚠️  SOME TESTS FAILED ({total_tests - passed_tests} failures)")
        print("🔧 Please review the failed tests above")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
