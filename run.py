#!/usr/bin/env python3
"""
SmartTest Bot - Main Entry Point
Fixed version with proper event loop handling
"""

import asyncio
import logging
import os
import signal
import sys
import time
from pathlib import Path

# Add app to path
sys.path.append(str(Path(__file__).parent))

# Import configuration
try:
    from app.config.constants import ADMIN_IDS, PAYMENT_STATUSES, USER_LEVELS
    print("✅ Constants loaded successfully")
    print(f"👥 Admin IDs: {ADMIN_IDS}")
    print(f"💰 Payment statuses: {PAYMENT_STATUSES}")
    print(f"📚 User levels: {USER_LEVELS}")
except Exception as e:
    print(f"❌ Failed to load constants: {e}")
    sys.exit(1)

# Import database
from app.database.session import Base, engine, SessionLocal
from app.database.models import User, Course, Chapter, Question, Payment, PracticeSession

# Import handlers
from app.handlers.start_handler import start_handler
from app.handlers.help_handler import help_handler
from app.handlers.menu_handler_fixed import menu_handler
from app.handlers.register_handler_updated import register_handler
from app.handlers.profile_handler_fixed import profile_handler
from app.handlers.materials_handler import materials_handler
from app.handlers.practice_handler import practice_handler
from app.handlers.course_handler_fixed import course_handler
from app.handlers.course_handler_admin_fixed import course_admin_handler
from app.handlers.chapter_selection_handler_fixed import chapter_selection_handler
from app.handlers.radio_question_handler import radio_question_handler
from app.handlers.payment_handler_fixed import payment_handler
from app.handlers.admin_handler_fixed import admin_handler
from app.handlers.admin_question_handler_fixed import admin_question_handler
from app.handlers.stream_course_handler import stream_course_handler

# Import keyboards
from app.keyboards.menu_keyboard import get_main_menu_keyboard
from app.keyboards.admin_keyboard import get_admin_keyboard

# Import services
from app.services.user_service import UserService
from app.services.course_service import CourseService
from app.services.chapter_service import ChapterService
from app.services.question_service import QuestionService
from app.services.payment_service import PaymentService
from app.services.practice_service import PracticeService

# Import utilities
from app.utils.process_manager import ProcessManager
from app.config.settings import BOT_TOKEN

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Global variables
app = None
db = None
process_manager = None

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    logging.info("Received shutdown signal, cleaning up...")
    global app, db, process_manager
    
    if process_manager:
        process_manager.cleanup()
    
    if db:
        db.close()
    
    if app:
        # Clean shutdown
        pass
    
    sys.exit(0)

def cleanup_processes():
    """Clean up any existing bot processes"""
    global process_manager
    process_manager = ProcessManager()
    process_manager.cleanup()
    logging.info("Cleaned up existing bot processes")

async def initialize_database():
    """Initialize the database"""
    global db
    try:
        logging.info("Initializing database...")
        Base.metadata.create_all(bind=engine)
        db = SessionLocal()
        logging.info("Database initialized successfully")
        return True
    except Exception as e:
        logging.error(f"Database initialization failed: {e}")
        return False

async def validate_bot_token():
    """Validate the bot token"""
    if not BOT_TOKEN:
        logging.error("BOT_TOKEN is not set")
        return False
    
    if len(BOT_TOKEN) < 45:
        logging.error(f"BOT_TOKEN appears to be invalid (length: {len(BOT_TOKEN)})")
        return False
    
    logging.info("Bot token validation passed (length: {})".format(len(BOT_TOKEN)))
    return True

async def create_application():
    """Create the bot application"""
    global app
    try:
        from telegram.ext import ApplicationBuilder
        
        logging.info("Building application...")
        app = ApplicationBuilder().token(BOT_TOKEN).build()
        logging.info("Application built successfully")
        
        logging.info("Initializing application...")
        await app.initialize()
        
        # Verify bot token and get bot info
        logging.info("Verifying bot token...")
        bot_info = await app.bot.get_me()
        logging.info(f"Bot token verified successfully - Bot: @{bot_info.username}")
        logging.info(f"Bot initialized successfully with ID: {bot_info.id}")
        
        return app
        
    except Exception as e:
        logging.error(f"Application creation failed: {e}")
        return None

def register_handlers(app):
    """Register all handlers with the application"""
    try:
        # Command handlers
        app.add_handler(start_handler)
        app.add_handler(help_handler)
        app.add_handler(register_handler)
        app.add_handler(menu_handler)
        app.add_handler(profile_handler)
        
        # Callback query handlers (in order)
        app.add_handler(practice_handler)
        app.add_handler(course_handler)
        app.add_handler(course_admin_handler)
        app.add_handler(chapter_selection_handler)
        app.add_handler(radio_question_handler)
        app.add_handler(payment_handler)
        app.add_handler(admin_handler)
        app.add_handler(admin_question_handler)
        app.add_handler(stream_course_handler)
        app.add_handler(materials_handler)
        
        logging.info("✅ Profile handlers registered successfully")
        logging.info("Bot application built successfully with all handlers")
        
    except Exception as e:
        logging.error(f"Handler registration failed: {e}")
        raise

async def main():
    """Main function"""
    global app, db
    
    try:
        # Setup signal handlers
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Get current process PID
        pid = os.getpid()
        logging.info(f"Current process PID: {pid}")
        
        # Clean up existing processes
        cleanup_processes()
        
        # Initialize database
        if not await initialize_database():
            logging.error("Failed to initialize database")
            return False
        
        # Validate bot token
        if not await validate_bot_token():
            logging.error("Bot token validation failed")
            return False
        
        # Create application
        app = await create_application()
        if not app:
            logging.error("Failed to create application")
            return False
        
        # Register handlers
        register_handlers(app)
        
        # Start polling with the FIX
        logging.info("Starting bot polling...")
        print("🚀 Bot is running! Press Ctrl+C to stop.")
        
        # THIS IS THE CRITICAL FIX - close_loop=False prevents event loop conflicts
        await app.run_polling(
            allowed_updates=['message', 'callback_query', 'poll'],
            drop_pending_updates=True,
            timeout=30,
            close_loop=False,  # ← THIS FIXES THE EVENT LOOP ISSUE
            bootstrap_retries=3
        )
        
        return True
        
    except KeyboardInterrupt:
        logging.info("Bot shutdown by user")
        return True
    except Exception as e:
        logging.error(f"Bot startup failed: {e}")
        import traceback
        logging.error(traceback.format_exc())
        return False
    finally:
        if app:
            logging.info("Stopping application...")
            await app.stop()
            await app.shutdown()
        
        if db:
            db.close()

if __name__ == "__main__":
    logging.info("Starting Smart Test Exam...")
    logging.info(f"Using bot token: {BOT_TOKEN[:10]}...")
    
    # Check if we're in an existing event loop
    try:
        loop = asyncio.get_running_loop()
        logging.warning("Event loop already running - this might cause issues")
    except RuntimeError:
        # No running loop, we can use asyncio.run()
        pass
    
    # Run the main function
    result = asyncio.run(main())
    
    if result:
        logging.info("Bot completed successfully")
    else:
        logging.error("Bot failed")
        sys.exit(1)
