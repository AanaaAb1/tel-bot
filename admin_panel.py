#!/usr/bin/env python3
"""
SmartTest Admin Panel Web Interface
Web-based administration for Telegram Bot Database
"""

import sys
import os
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import json

# Database imports
from app.database.session import SessionLocal, engine
from app.models.course import Course
from app.models.chapter import Chapter
from app.models.question import Question
from app.models.user import User
from app.models.payment import Payment

from app.database.base import Base

# Configuration
app = Flask(__name__)
app.secret_key = 'your-secret-key-here-change-in-production'
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS

# Login Manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Create admin user if not exists
def create_admin_user():
    """Create default admin user"""
    db = SessionLocal()
    try:
        # Check if admin exists
        admin = db.query(User).filter_by(username='admin').first()
        if not admin:
            admin_user = User(
                username='admin',
                email='admin@smarttest.com',
                password_hash=generate_password_hash('admin123'),
                full_name='Administrator',
                user_level='admin',
                is_approved=True,
                created_at=datetime.utcnow()
            )
            db.add(admin_user)
            db.commit()
            print("✅ Admin user created: admin / admin123")
        else:
            print("✅ Admin user already exists")
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
    finally:
        db.close()

@login_manager.user_loader
def load_user(user_id):
    """Load user by ID"""
    db = SessionLocal()
    try:
        user = db.query(User).get(int(user_id))
        return user
    finally:
        db.close()

# Routes

@app.route('/')
def index():
    """Home page"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Admin login"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        db = SessionLocal()
        try:
            user = db.query(User).filter_by(username=username).first()
            if user and check_password_hash(user.password_hash, password) and user.user_level == 'admin':
                login_user(user)
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid credentials or insufficient permissions', 'error')
        finally:
            db.close()
    
    return render_template('admin/login.html')

@app.route('/logout')
@login_required
def logout():
    """Logout"""
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    """Admin dashboard"""
    db = SessionLocal()
    try:
        # Get statistics
        total_courses = db.query(Course).count()
        total_chapters = db.query(Chapter).count()
        total_questions = db.query(Question).count()
        total_users = db.query(User).count()
        total_payments = db.query(Payment).count()
        pending_payments = db.query(Payment).filter_by(status='pending').count()
        
        # Recent activity
        recent_users = db.query(User).order_by(User.created_at.desc()).limit(5).all()
        recent_payments = db.query(Payment).order_by(Payment.created_at.desc()).limit(5).all()
        
        stats = {
            'total_courses': total_courses,
            'total_chapters': total_chapters,
            'total_questions': total_questions,
            'total_users': total_users,
            'total_payments': total_payments,
            'pending_payments': pending_payments
        }
        
        return render_template('admin/dashboard.html', 
                             stats=stats, 
                             recent_users=recent_users, 
                             recent_payments=recent_payments)
    finally:
        db.close()

# Courses Management

@app.route('/courses')
@login_required
def courses():
    """Manage courses"""
    db = SessionLocal()
    try:
        courses = db.query(Course).all()
        course_data = []
        
        for course in courses:
            chapters_count = db.query(Chapter).filter_by(course_id=course.id).count()
            questions_count = db.query(Question).join(Chapter).filter(Chapter.course_id == course.id).count()
            
            course_data.append({
                'id': course.id,
                'name': course.name,
                'code': course.code,
                'description': course.description,
                'chapters_count': chapters_count,
                'questions_count': questions_count,
                'created_at': course.created_at
            })
        
        return render_template('admin/courses.html', courses=course_data)
    finally:
        db.close()

@app.route('/courses/add', methods=['GET', 'POST'])
@login_required
def add_course():
    """Add new course"""
    if request.method == 'POST':
        name = request.form['name']
        code = request.form['code']
        description = request.form['description']
        
        db = SessionLocal()
        try:
            # Check if course code already exists
            existing = db.query(Course).filter_by(code=code).first()
            if existing:
                flash('Course code already exists', 'error')
                return render_template('admin/course_form.html', course=None)
            
            # Create new course
            course = Course(
                name=name,
                code=code,
                description=description,
                created_at=datetime.utcnow()
            )
            db.add(course)
            db.commit()
            flash('Course added successfully', 'success')
            return redirect(url_for('courses'))
        finally:
            db.close()
    
    return render_template('admin/course_form.html', course=None)

@app.route('/courses/edit/<int:course_id>', methods=['GET', 'POST'])
@login_required
def edit_course(course_id):
    """Edit course"""
    db = SessionLocal()
    try:
        course = db.query(Course).get(course_id)
        if not course:
            flash('Course not found', 'error')
            return redirect(url_for('courses'))
        
        if request.method == 'POST':
            course.name = request.form['name']
            course.code = request.form['code']
            course.description = request.form['description']
            db.commit()
            flash('Course updated successfully', 'success')
            return redirect(url_for('courses'))
        
        return render_template('admin/course_form.html', course=course)
    finally:
        db.close()

@app.route('/courses/delete/<int:course_id>', methods=['POST'])
@login_required
def delete_course(course_id):
    """Delete course"""
    db = SessionLocal()
    try:
        course = db.query(Course).get(course_id)
        if course:
            # Delete related chapters and questions
            chapters = db.query(Chapter).filter_by(course_id=course.id).all()
            for chapter in chapters:
                db.query(Question).filter_by(chapter_id=chapter.id).delete()
                db.delete(chapter)
            db.delete(course)
            db.commit()
            flash('Course deleted successfully', 'success')
        else:
            flash('Course not found', 'error')
    finally:
        db.close()
    
    return redirect(url_for('courses'))

# Chapters Management

@app.route('/courses/<int:course_id>/chapters')
@login_required
def chapters(course_id):
    """Manage chapters for a course"""
    db = SessionLocal()
    try:
        course = db.query(Course).get(course_id)
        if not course:
            flash('Course not found', 'error')
            return redirect(url_for('courses'))
        
        chapters = db.query(Chapter).filter_by(course_id=course_id).all()
        chapter_data = []
        
        for chapter in chapters:
            questions_count = db.query(Question).filter_by(chapter_id=chapter.id).count()
            chapter_data.append({
                'id': chapter.id,
                'name': chapter.name,
                'description': chapter.description,
                'questions_count': questions_count,
                'created_at': chapter.created_at
            })
        
        return render_template('admin/chapters.html', course=course, chapters=chapter_data)
    finally:
        db.close()

@app.route('/courses/<int:course_id>/chapters/add', methods=['GET', 'POST'])
@login_required
def add_chapter(course_id):
    """Add new chapter"""
    db = SessionLocal()
    try:
        course = db.query(Course).get(course_id)
        if not course:
            flash('Course not found', 'error')
            return redirect(url_for('courses'))
        
        if request.method == 'POST':
            name = request.form['name']
            description = request.form['description']
            
            chapter = Chapter(
                name=name,
                description=description,
                course_id=course_id,
                created_at=datetime.utcnow()
            )
            db.add(chapter)
            db.commit()
            flash('Chapter added successfully', 'success')
            return redirect(url_for('chapters', course_id=course_id))
        
        return render_template('admin/chapter_form.html', course=course, chapter=None)
    finally:
        db.close()

@app.route('/courses/<int:course_id>/chapters/edit/<int:chapter_id>', methods=['GET', 'POST'])
@login_required
def edit_chapter(course_id, chapter_id):
    """Edit chapter"""
    db = SessionLocal()
    try:
        course = db.query(Course).get(course_id)
        chapter = db.query(Chapter).get(chapter_id)
        
        if not course or not chapter or chapter.course_id != course_id:
            flash('Chapter not found', 'error')
            return redirect(url_for('chapters', course_id=course_id))
        
        if request.method == 'POST':
            chapter.name = request.form['name']
            chapter.description = request.form['description']
            db.commit()
            flash('Chapter updated successfully', 'success')
            return redirect(url_for('chapters', course_id=course_id))
        
        return render_template('admin/chapter_form.html', course=course, chapter=chapter)
    finally:
        db.close()

@app.route('/courses/<int:course_id>/chapters/delete/<int:chapter_id>', methods=['POST'])
@login_required
def delete_chapter(course_id, chapter_id):
    """Delete chapter"""
    db = SessionLocal()
    try:
        chapter = db.query(Chapter).get(chapter_id)
        if chapter and chapter.course_id == course_id:
            # Delete related questions
            db.query(Question).filter_by(chapter_id=chapter.id).delete()
            db.delete(chapter)
            db.commit()
            flash('Chapter deleted successfully', 'success')
        else:
            flash('Chapter not found', 'error')
    finally:
        db.close()
    
    return redirect(url_for('chapters', course_id=course_id))

# Questions Management

@app.route('/chapters/<int:chapter_id>/questions')
@login_required
def questions(chapter_id):
    """Manage questions for a chapter"""
    db = SessionLocal()
    try:
        chapter = db.query(Chapter).get(chapter_id)
        if not chapter:
            flash('Chapter not found', 'error')
            return redirect(url_for('courses'))
        
        course = db.query(Course).get(chapter.course_id)
        questions = db.query(Question).filter_by(chapter_id=chapter_id).all()
        
        return render_template('admin/questions.html', 
                             course=course, 
                             chapter=chapter, 
                             questions=questions)
    finally:
        db.close()

@app.route('/chapters/<int:chapter_id>/questions/add', methods=['GET', 'POST'])
@login_required
def add_question(chapter_id):
    """Add new question"""
    db = SessionLocal()
    try:
        chapter = db.query(Chapter).get(chapter_id)
        if not chapter:
            flash('Chapter not found', 'error')
            return redirect(url_for('courses'))
        
        course = db.query(Course).get(chapter.course_id)
        
        if request.method == 'POST':
            question_text = request.form['question_text']
            option_a = request.form['option_a']
            option_b = request.form['option_b']
            option_c = request.form['option_c']
            option_d = request.form['option_d']
            correct_answer = request.form['correct_answer']
            difficulty = request.form['difficulty']
            explanation = request.form['explanation']
            
            question = Question(
                course_id=course.id,
                chapter_id=chapter_id,
                question_text=question_text,
                option_a=option_a,
                option_b=option_b,
                option_c=option_c,
                option_d=option_d,
                correct_answer=correct_answer,
                difficulty=difficulty,
                explanation=explanation,
                created_at=datetime.utcnow()
            )
            db.add(question)
            db.commit()
            flash('Question added successfully', 'success')
            return redirect(url_for('questions', chapter_id=chapter_id))
        
        return render_template('admin/question_form.html', 
                             course=course, 
                             chapter=chapter, 
                             question=None)
    finally:
        db.close()

@app.route('/chapters/<int:chapter_id>/questions/edit/<int:question_id>', methods=['GET', 'POST'])
@login_required
def edit_question(chapter_id, question_id):
    """Edit question"""
    db = SessionLocal()
    try:
        chapter = db.query(Chapter).get(chapter_id)
        question = db.query(Question).get(question_id)
        
        if not chapter or not question or question.chapter_id != chapter_id:
            flash('Question not found', 'error')
            return redirect(url_for('questions', chapter_id=chapter_id))
        
        course = db.query(Course).get(chapter.course_id)
        
        if request.method == 'POST':
            question.question_text = request.form['question_text']
            question.option_a = request.form['option_a']
            question.option_b = request.form['option_b']
            question.option_c = request.form['option_c']
            question.option_d = request.form['option_d']
            question.correct_answer = request.form['correct_answer']
            question.difficulty = request.form['difficulty']
            question.explanation = request.form['explanation']
            db.commit()
            flash('Question updated successfully', 'success')
            return redirect(url_for('questions', chapter_id=chapter_id))
        
        return render_template('admin/question_form.html', 
                             course=course, 
                             chapter=chapter, 
                             question=question)
    finally:
        db.close()

@app.route('/chapters/<int:chapter_id>/questions/delete/<int:question_id>', methods=['POST'])
@login_required
def delete_question(chapter_id, question_id):
    """Delete question"""
    db = SessionLocal()
    try:
        question = db.query(Question).get(question_id)
        if question and question.chapter_id == chapter_id:
            db.delete(question)
            db.commit()
            flash('Question deleted successfully', 'success')
        else:
            flash('Question not found', 'error')
    finally:
        db.close()
    
    return redirect(url_for('questions', chapter_id=chapter_id))

# Users Management

@app.route('/users')
@login_required
def users():
    """Manage users"""
    db = SessionLocal()
    try:
        users = db.query(User).all()
        return render_template('admin/users.html', users=users)
    finally:
        db.close()

@app.route('/users/<int:user_id>/approve', methods=['POST'])
@login_required
def approve_user(user_id):
    """Approve user"""
    db = SessionLocal()
    try:
        user = db.query(User).get(user_id)
        if user:
            user.is_approved = True
            db.commit()
            flash('User approved successfully', 'success')
        else:
            flash('User not found', 'error')
    finally:
        db.close()
    
    return redirect(url_for('users'))

@app.route('/users/<int:user_id>/reject', methods=['POST'])
@login_required
def reject_user(user_id):
    """Reject user"""
    db = SessionLocal()
    try:
        user = db.query(User).get(user_id)
        if user:
            user.is_approved = False
            db.commit()
            flash('User rejected successfully', 'success')
        else:
            flash('User not found', 'error')
    finally:
        db.close()
    
    return redirect(url_for('users'))

# Payments Management

@app.route('/payments')
@login_required
def payments():
    """Manage payments"""
    db = SessionLocal()
    try:
        payments = db.query(Payment).all()
        return render_template('admin/payments.html', payments=payments)
    finally:
        db.close()

@app.route('/payments/<int:payment_id>/approve', methods=['POST'])
@login_required
def approve_payment(payment_id):
    """Approve payment"""
    db = SessionLocal()
    try:
        payment = db.query(Payment).get(payment_id)
        if payment:
            payment.status = 'approved'
            payment.approved_at = datetime.utcnow()
            db.commit()
            flash('Payment approved successfully', 'success')
        else:
            flash('Payment not found', 'error')
    finally:
        db.close()
    
    return redirect(url_for('payments'))

@app.route('/payments/<int:payment_id>/reject', methods=['POST'])
@login_required
def reject_payment(payment_id):
    """Reject payment"""
    db = SessionLocal()
    try:
        payment = db.query(Payment).get(payment_id)
        if payment:
            payment.status = 'rejected'
            db.commit()
            flash('Payment rejected successfully', 'success')
        else:
            flash('Payment not found', 'error')
    finally:
        db.close()
    
    return redirect(url_for('payments'))

# API Routes for AJAX

@app.route('/api/courses/<int:course_id>/stats')
@login_required
def course_stats(course_id):
    """Get course statistics"""
    db = SessionLocal()
    try:
        chapters_count = db.query(Chapter).filter_by(course_id=course_id).count()
        questions_count = db.query(Question).join(Chapter).filter(Chapter.course_id == course_id).count()
        
        return jsonify({
            'chapters_count': chapters_count,
            'questions_count': questions_count
        })
    finally:
        db.close()

@app.route('/api/chapters/<int:chapter_id>/stats')
@login_required
def chapter_stats(chapter_id):
    """Get chapter statistics"""
    db = SessionLocal()
    try:
        questions_count = db.query(Question).filter_by(chapter_id=chapter_id).count()
        easy_count = db.query(Question).filter_by(chapter_id=chapter_id, difficulty='Easy').count()
        intermediate_count = db.query(Question).filter_by(chapter_id=chapter_id, difficulty='Intermediate').count()
        advanced_count = db.query(Question).filter_by(chapter_id=chapter_id, difficulty='Advanced').count()
        
        return jsonify({
            'total_questions': questions_count,
            'easy_questions': easy_count,
            'intermediate_questions': intermediate_count,
            'advanced_questions': advanced_count
        })
    finally:
        db.close()

if __name__ == '__main__':
    # Create database tables
    Base.metadata.create_all(bind=engine)
    
    # Create admin user
    create_admin_user()
    
    # Run the application
    print("🚀 Starting SmartTest Admin Panel...")
    print("📱 Admin Panel URL: http://localhost:5000")
    print("👤 Default Admin: admin / admin123")
    print("🛑 Press Ctrl+C to stop")
    
    app.run(debug=True, host='0.0.0.0', port=5000)

