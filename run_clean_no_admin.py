import logging
import signal
import sys
import time
import asyncio
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters, PollAnswerHandler
from telegram.error import Conflict, InvalidToken, TelegramError
from app.config.settings import BOT_TOKEN, WEBHOOK_URL
from app.handlers.start_handler import start
from app.handlers.register_handler import register, handle_registration_callback
from app.handlers.onboarding_handler import onboarding
from app.handlers.menu_handler_no_admin import menu
from app.handlers.materials_handler import materials_menu, course_materials, request_material
from app.handlers.help_handler import help_handler, help_callback
from app.handlers.payment_handler import submit_payment, receive_payment_proof
from app.handlers.profile_handler_fixed import profile_menu, copy_referral_code, copy_invitation_link, view_referral_history
from app.handlers.exam_handler_fixed import start_exam
from app.handlers.course_handler_fixed import select_course, start_exam_selected
from app.handlers.practice_handler_fixed import (
    start_practice,
    practice_by_course,
    practice_course_selected,
    practice_by_chapter,
    practice_course_for_chapter,
    practice_chapter_selected
)
from app.handlers.question_handler import answer_question, show_detailed_result
from app.handlers.radio_question_handler import handle_poll_answer
from app.utils.process_manager import cleanup_existing_bot, is_bot_running

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global app reference for graceful shutdown
global_app = None

async def clear_webhook_completely():
    """Completely clear webhook and pending updates with verification"""
    try:
        bot = Bot(token=BOT_TOKEN)
        
        # Get current webhook info
        webhook_info = await bot.get_webhook_info()
        logger.info(f"Current webhook info: {webhook_info.url if webhook_info.url else 'No webhook set'}")
        
        if webhook_info.url:
            # Delete webhook and drop pending updates
            await bot.delete_webhook(drop_pending_updates=True)
            logger.info("Webhook deleted with pending updates dropped")
        
        # Wait for Telegram to process the cleanup
        await asyncio.sleep(3)
        
        # Verify webhook is cleared
        webhook_info = await bot.get_webhook_info()
        if not webhook_info.url:
            logger.info("✅ Webhook successfully cleared and verified")
            return True
        else:
            logger.warning("⚠️  Webhook may still be active after cleanup attempt")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error clearing webhook: {e}")
        return False

async def ensure_clean_state():
    """Ensure bot starts in a completely clean state"""
    logger.info("🧹 Ensuring clean bot state...")
    
    # Step 1: Clear webhook completely
    webhook_cleared = await clear_webhook_completely()
    
    # Step 2: Process cleanup
    logger.info("🗑️  Cleaning up existing processes...")
    cleanup_existing_bot()
    
    # Step 3: Additional wait for Telegram servers
    await asyncio.sleep(5)
    
    # Step 4: Verify no processes are running
    if is_bot_running():
        logger.warning("⚠️  Bot still appears to be running after cleanup")
        # Force cleanup
        import psutil
        for proc in psutil.process_iter(['pid', 'cmdline']):
            try:
                cmdline = ' '.join(proc.info.get('cmdline', []))
                if 'run.py' in cmdline and proc.pid != psutil.Process().pid:
                    logger.info(f"🔪 Force killing process {proc.pid}")
                    proc.kill()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
    
    logger.info("✅ Clean state verification completed")
    return webhook_cleared

# simple /start handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Bot is running!")

def signal_handler(signum, frame):
    """Handle graceful shutdown"""
    logger.info("Received shutdown signal, stopping bot...")
    if global_app:
        try:
            # Try to stop gracefully
            if hasattr(global_app, 'updater') and global_app.updater:
                global_app.updater.stop()
            if hasattr(global_app, 'stop'):
                global_app.stop()
        except Exception as e:
            logger.warning(f"Error during graceful shutdown: {e}")
    sys.exit(0)

def setup_signal_handlers():
    """Setup signal handlers for graceful shutdown"""
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

def register_clean_handlers(app):
    """Register ONLY non-admin handlers to prevent recursion"""
    # Basic commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("register", register))
    app.add_handler(CommandHandler("help", help_handler))

    # Registration callbacks
    app.add_handler(CallbackQueryHandler(handle_registration_callback, pattern="^(level_|stream_)"))
    app.add_handler(CallbackQueryHandler(onboarding, pattern="^(level_|stream_)"))
    
    # Question answering
    app.add_handler(CallbackQueryHandler(answer_question, pattern="^ans_"))
    
    # Payment handling
    app.add_handler(CallbackQueryHandler(submit_payment, pattern="submit_payment"))
    
    # Profile handlers - Specific patterns first
    app.add_handler(CallbackQueryHandler(profile_menu, pattern="^profile$"))
    app.add_handler(CallbackQueryHandler(copy_referral_code, pattern="^copy_code_"))
    app.add_handler(CallbackQueryHandler(copy_invitation_link, pattern="^copy_link_"))
    app.add_handler(CallbackQueryHandler(view_referral_history, pattern="^referral_history_"))

    # Practice handlers with access control
    app.add_handler(CallbackQueryHandler(start_practice, pattern="^practice$"))
    app.add_handler(CallbackQueryHandler(practice_by_course, pattern="^practice_course$"))
    app.add_handler(CallbackQueryHandler(practice_course_selected, pattern="^practice_course_"))
    app.add_handler(CallbackQueryHandler(practice_by_chapter, pattern="^practice_chapter$"))
    app.add_handler(CallbackQueryHandler(practice_course_for_chapter, pattern="^practice_course_"))
    app.add_handler(CallbackQueryHandler(practice_chapter_selected, pattern="^practice_chapter_"))

    # Exam handlers with access control
    app.add_handler(CallbackQueryHandler(start_exam, pattern="^exams$"))
    app.add_handler(CallbackQueryHandler(select_course, pattern="^exam_course_"))
    app.add_handler(CallbackQueryHandler(start_exam_selected, pattern="^start_exam_"))

    # Materials handlers
    app.add_handler(CallbackQueryHandler(materials_menu, pattern="^materials$"))
    app.add_handler(CallbackQueryHandler(course_materials, pattern="^course_materials_"))
    app.add_handler(CallbackQueryHandler(request_material, pattern="^request_material_"))

    # Help handler
    app.add_handler(CallbackQueryHandler(help_callback, pattern="^help$"))
    
    # Menu handler (main fallback) - NO ADMIN
    app.add_handler(CallbackQueryHandler(menu, pattern="^(exams|payment|materials|help|back_to_main|courses|practice|leaderboard|leaderboard_best|leaderboard_latest|leaderboard_average|profile)$"))
    app.add_handler(CallbackQueryHandler(menu))

    # Result command handler
    app.add_handler(MessageHandler(filters.Regex(r'^/result_\d+$'), show_detailed_result))

    # Poll answer handler for radio-style questions
    app.add_handler(PollAnswerHandler(handle_poll_answer))

    # Payment proof handler (text, photos, documents)
    app.add_handler(MessageHandler(
        (filters.TEXT | filters.PHOTO | filters.Document.ALL) & ~filters.COMMAND,
        receive_payment_proof
    ))

def start_bot_with_polling():
    """Start clean bot using polling mode with NO admin functionality"""
    global global_app
    
    max_retries = 7
    base_delay = 3
    max_delay = 60
    
    async def clean_startup():
        """Clean startup without admin handlers"""
        logger.info("🚀 Starting CLEAN bot startup (NO ADMIN)...")
        
        # Step 1: Ensure completely clean state
        await ensure_clean_state()
        
        # Step 2: Build application with enhanced settings
        logger.info("🔧 Building CLEAN bot application...")
        app = ApplicationBuilder().token(BOT_TOKEN).build()
        global_app = app
        
        # Setup signal handlers
        setup_signal_handlers()
        
        # Register ONLY clean handlers (NO ADMIN)
        register_clean_handlers(app)
        
        logger.info("✅ Clean bot application built (NO ADMIN handlers)")
        
        # Step 3: Start with enhanced polling options
        logger.info("📡 Starting CLEAN bot polling...")
        app.run_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True,
            timeout=30
        )
    
    # Main startup loop with enhanced error handling
    for attempt in range(max_retries):
        try:
            logger.info(f"🎯 Starting CLEAN bot (attempt {attempt + 1}/{max_retries})")
            
            # Run the clean startup
            asyncio.run(clean_startup())
            
            # If we get here, startup was successful
            logger.info("🎉 CLEAN bot started successfully!")
            break
            
        except Conflict as e:
            logger.error(f"💥 Conflict detected (attempt {attempt + 1}): {e}")
            
            # Enhanced conflict recovery
            if "getUpdates" in str(e) or "terminated by other" in str(e):
                logger.info("🔄 GetUpdates conflict detected, performing deep cleanup...")
                
                # Force webhook deletion with updates
                try:
                    asyncio.run(clear_webhook_completely())
                    logger.info("🧹 Force webhook deletion completed")
                except Exception as webhook_error:
                    logger.warning(f"⚠️  Webhook deletion failed: {webhook_error}")
                
                # Enhanced wait time with exponential backoff
                wait_time = min(base_delay * (2 ** attempt), max_delay)
                logger.info(f"⏳ Waiting {wait_time} seconds before retry...")
                
                # Clean up any remaining processes
                try:
                    cleanup_existing_bot()
                except Exception as cleanup_error:
                    logger.warning(f"⚠️  Cleanup error: {cleanup_error}")
                
                import time
                time.sleep(wait_time)
                
            else:
                # Other conflict types
                import time
                time.sleep(base_delay)
                
        except InvalidToken as e:
            logger.error(f"🔑 Invalid bot token: {e}")
            logger.error("❌ Cannot proceed without valid token")
            raise
            
        except KeyboardInterrupt:
            logger.info("🛑 Bot stopped by user")
            break
            
        except TelegramError as e:
            logger.error(f"📱 Telegram API error: {e}")
            if attempt < max_retries - 1:
                wait_time = min(base_delay * (2 ** attempt), max_delay)
                logger.info(f"⏳ Retrying in {wait_time} seconds...")
                import time
                time.sleep(wait_time)
            else:
                raise
                
        except Exception as e:
            logger.error(f"💥 Unexpected error (attempt {attempt + 1}): {e}")
            logger.error(f"Error type: {type(e).__name__}")
            
            if attempt < max_retries - 1:
                wait_time = min(base_delay * (2 ** attempt), max_delay)
                logger.info(f"⏳ Retrying in {wait_time} seconds...")
                import time
                time.sleep(wait_time)
            else:
                logger.error("💀 Max retries reached")
                raise
    
    logger.info("🎊 CLEAN bot startup completed successfully!")

def start_bot():
    """Main bot startup function - CLEAN VERSION (NO ADMIN)"""
    try:
        logger.info("🚀 Starting CLEAN BOT (NO ADMIN DUPLICATE MESSAGES)")
        start_bot_with_polling()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot failed to start: {e}")
        sys.exit(1)

if __name__ == "__main__":
    start_bot()
