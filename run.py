#!/usr/bin/env python3
"""
Bot startup using consolidated dispatcher system
Uses dispatcher_fixed.py to prevent duplicate handler registrations
"""

import sys
import logging
import signal
import subprocess
import asyncio
from pathlib import Path

# Add app to path
sys.path.append(str(Path(__file__).parent))

from telegram.ext import ApplicationBuilder
from app.config.settings import BOT_TOKEN
from app.bot.dispatcher_fixed import register_handlers

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def signal_handler(signum, frame):
    """Handle graceful shutdown"""
    logger.info(f"🛑 Received signal {signum}, shutting down gracefully...")
    sys.exit(0)

def init_db():
    """Initialize database tables"""
    try:
        from app.database.base import Base
        from app.database.session import engine
        from app.models.user import User
        from app.models.payment import Payment
        from app.models.course import Course
        from app.models.question import Question
        from app.models.exam import Exam
        from app.models.answer import Answer
        from app.models.result import Result
        
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database initialized successfully")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        sys.exit(1)

def main():
    """Main bot startup function"""
    
    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        logger.info("🚀 Starting Smart Test Exam (Working Version)...")
        logger.info(f"🔑 Using bot token: {BOT_TOKEN[:20]}...")
        
        # Clean up any existing bot processes first (but not current process)
        try:
            import os
            current_pid = os.getpid()
            logger.info(f"🧹 Current process PID: {current_pid}")
            
            # Get list of running python processes that might be bots
            result = subprocess.run(["pgrep", "-f", "python.*run.py"], 
                                  capture_output=True, text=True, check=False)
            if result.stdout:
                pids = result.stdout.strip().split('\n')
                for pid in pids:
                    pid = pid.strip()
                    if pid and pid != str(current_pid):
                        try:
                            logger.info(f"🗑️ Killing process {pid}")
                            subprocess.run(["kill", pid], check=False)
                        except:
                            pass
            
            # Clean up other bot instances
            for pattern in ["python.*working_bot.py", "python.*simple_bot.py"]:
                result = subprocess.run(["pgrep", "-f", pattern], 
                                      capture_output=True, text=True, check=False)
                if result.stdout:
                    pids = result.stdout.strip().split('\n')
                    for pid in pids:
                        pid = pid.strip()
                        if pid:
                            try:
                                logger.info(f"🗑️ Killing process {pid}")
                                subprocess.run(["kill", pid], check=False)
                            except:
                                pass
                                
            logger.info("🧹 Cleaned up existing bot processes")
        except Exception as e:
            logger.warning(f"⚠️ Process cleanup warning: {e}")
        
        # Initialize database
        logger.info("💾 Initializing database...")
        init_db()
        
        # Build application with custom API configuration
        from app.config.settings import TELEGRAM_API_BASE_URL
        
        # Configure application with custom API base URL
        if TELEGRAM_API_BASE_URL and TELEGRAM_API_BASE_URL != "https://api.telegram.org":
            app = ApplicationBuilder().token(BOT_TOKEN).base_url(TELEGRAM_API_BASE_URL).build()
            logger.info(f"🔗 Using custom API endpoint: {TELEGRAM_API_BASE_URL}")
        else:
            app = ApplicationBuilder().token(BOT_TOKEN).build()
            logger.info("🔗 Using default Telegram API endpoint")
        
        # Register all handlers using consolidated dispatcher
        register_handlers(app)
        
        logger.info("✅ Bot application built successfully with all handlers")
        
        # Start polling
        logger.info("📡 Starting bot polling...")
        app.run_polling(
            allowed_updates=['message', 'callback_query', 'poll'],
            drop_pending_updates=True,
            timeout=30
        )
        
    except Exception as e:
        logger.error(f"❌ Bot startup failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    # Run the main function directly since app.run_polling() handles the event loop
    main()

