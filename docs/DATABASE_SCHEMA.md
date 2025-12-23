# Database Schema for Telegram Exam Bot

## Overview
This document describes the database schema for the Telegram Exam Bot application. The database uses SQLite and is managed with SQLAlchemy ORM.

## Tables

### Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER UNIQUE NOT NULL,
    full_name TEXT NOT NULL,
    username TEXT,
    join_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    level TEXT,
    stream TEXT,
    payment_status TEXT DEFAULT 'NOT_PAID',
    access TEXT DEFAULT 'LOCKED'
);
```

**Fields:**
- `id`: Primary key, auto-increment
- `telegram_id`: Unique Telegram user ID
- `full_name`: User's full name
- `username`: Telegram username (optional)
- `join_time`: When user joined the bot
- `level`: Academic level (Remedial/Freshman)
- `stream`: Academic stream (Natural/Social)
- `payment_status`: Payment status (NOT_PAID/PENDING/APPROVED/REJECTED)
- `access`: Access status (LOCKED/UNLOCKED)

### Payments Table
```sql
CREATE TABLE payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    proof TEXT,
    status TEXT DEFAULT 'PENDING',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id)
);
```

**Fields:**
- `id`: Primary key, auto-increment
- `user_id`: Foreign key to users table
- `proof`: Payment proof
- `status`: Payment status (PENDING/APPROVED/REJECTED)
- `created_at`: Timestamp of payment creation

### Courses Table
```sql
CREATE TABLE courses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT
);
```

**Fields:**
- `id`: Primary key, auto-increment
- `name`: Course name
- `description`: Course description

### Exams Table
```sql
CREATE TABLE exams (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    total_questions INTEGER,
    FOREIGN KEY(course_id) REFERENCES courses(id)
);
```

**Fields:**
- `id`: Primary key, auto-increment
- `course_id`: Foreign key to courses table
- `name`: Exam name
- `total_questions`: Total number of questions in the exam

### Questions Table
```sql
CREATE TABLE questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    exam_id INTEGER NOT NULL,
    text TEXT NOT NULL,
    option_a TEXT,
    option_b TEXT,
    option_c TEXT,
    option_d TEXT,
    correct_option TEXT,
    FOREIGN KEY(exam_id) REFERENCES exams(id)
);
```

**Fields:**
- `id`: Primary key, auto-increment
- `exam_id`: Foreign key to exams table
- `text`: Question text
- `option_a/b/c/d`: Answer options
- `correct_option`: Correct answer (A/B/C/D)

### Answers Table
```sql
CREATE TABLE answers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    question_id INTEGER NOT NULL,
    selected_option TEXT,
    is_correct BOOLEAN,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id),
    FOREIGN KEY(question_id) REFERENCES questions(id)
);
```

**Fields:**
- `id`: Primary key, auto-increment
- `user_id`: Foreign key to users table
- `question_id`: Foreign key to questions table
- `selected_option`: User's selected answer
- `is_correct`: Whether answer is correct
- `timestamp`: Timestamp of the answer

### Results Table
```sql
CREATE TABLE results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    exam_id INTEGER NOT NULL,
    score INTEGER,
    percentage REAL,
    completed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id),
    FOREIGN KEY(exam_id) REFERENCES exams(id)
);
```

**Fields:**
- `id`: Primary key, auto-increment
- `user_id`: Foreign key to users table
- `exam_id`: Foreign key to exams table
- `score`: Exam score
- `percentage`: Score percentage
- `completed_at`: Completion timestamp

## Relationships
- Users can have multiple payments and results
- Courses have multiple exams
- Exams have multiple questions
- Questions have multiple answers
- Answers belong to users and questions
- Results belong to users and exams

### SQLAlchemy ORM Relationships
- `User.payments` → Payment.user
- `User.answers` → Answer.user  
- `User.results` → Result.user
- `Course.exams` → Exam.course
- `Exam.questions` → Question.exam
- `Exam.results` → Result.exam
- `Question.answers` → Answer.question

## Indexes
- Unique index on users.telegram_id
- Foreign key indexes on all FK columns

## Data Types
- INTEGER: For IDs and boolean flags
- TEXT: For string fields
- REAL: For floating point numbers
- DATETIME: For timestamps

## Constraints
- telegram_id must be unique
- All foreign keys enforce referential integrity