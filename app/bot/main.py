import logging
import signal
import sys
import time
import asyncio
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram.error import Conflict, InvalidToken, TelegramError
from app.config.settings import BOT_TOKEN, WEBHOOK_URL
from app.bot.dispatcher_fixed import register_handlers
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

async def start_bot_with_webhook():
    """Start bot using webhook mode"""
    global global_app
    
    try:
        logger.info("Starting bot with webhook mode...")
        
        app = ApplicationBuilder().token(BOT_TOKEN).build()
        global_app = app
        
        # Setup signal handlers
        setup_signal_handlers()
        
        # register handlers
        register_handlers(app)
        
        # Set webhook
        webhook_url = f"{WEBHOOK_URL}/webhook"
        await app.bot.set_webhook(url=webhook_url)
        
        logger.info(f"Webhook set to: {webhook_url}")
        logger.info("Bot initialized successfully with webhook")
        
        # Start the application
        await app.initialize()
        await app.start()
        
        # Keep running
        await asyncio.Event().wait()
        
    except Exception as e:
        logger.error(f"Webhook startup failed: {e}")
        raise

def start_bot_with_polling():
    """Start bot using polling mode with enhanced conflict handling"""
    global global_app
    
    max_retries = 7  # Increased from 5
    base_delay = 3   # Increased from 2
    max_delay = 60   # Maximum delay cap
    
    async def enhanced_startup():
        """Enhanced startup with comprehensive cleanup"""
        logger.info("🚀 Starting enhanced bot startup sequence...")
        
        # Step 1: Ensure completely clean state
        await ensure_clean_state()
        
        # Step 2: Build application with enhanced settings
        logger.info("🔧 Building bot application...")
        app = ApplicationBuilder().token(BOT_TOKEN).build()
        global_app = app
        
        # Setup signal handlers
        setup_signal_handlers()
        
        # Register handlers
        register_handlers(app)
        
        logger.info("✅ Bot application built and handlers registered")
        
        # Step 3: Start with enhanced polling options
        logger.info("📡 Starting bot polling with enhanced settings...")
        app.run_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True,
            timeout=30
        )
    
    # Main startup loop with enhanced error handling
    for attempt in range(max_retries):
        try:
            logger.info(f"🎯 Starting bot (attempt {attempt + 1}/{max_retries})")
            
            # Run the enhanced startup
            asyncio.run(enhanced_startup())
            
            # If we get here, startup was successful
            logger.info("🎉 Bot started successfully!")
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
                logger.error("💀 Max retries reached, attempting webhook fallback...")
                # Try webhook mode as last resort
                try:
                    asyncio.run(start_bot_with_webhook())
                    return
                except Exception as webhook_error:
                    logger.error(f"💥 Webhook fallback also failed: {webhook_error}")
                    raise
    
    logger.info("🎊 Bot startup completed successfully!")

def start_bot():
    """Main bot startup function with mode selection"""
    try:
        # Try polling mode first (more common for development)
        start_bot_with_polling()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot failed to start: {e}")
        sys.exit(1)
