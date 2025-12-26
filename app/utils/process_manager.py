import os
import signal
import psutil
import logging
import asyncio
from pathlib import Path
from telegram import Bot
from app.config.settings import BOT_TOKEN

logger = logging.getLogger(__name__)

class ProcessManager:
    """Manages bot processes to prevent multiple instances"""
    
    def __init__(self, pid_file_path="bot.pid"):
        self.pid_file_path = pid_file_path
        self.pid_file = Path(pid_file_path)
    
    def get_bot_processes(self):
        """Find all running bot processes"""
        bot_processes = []
        try:
            current_process = psutil.Process()
            bot_keywords = ['python', 'run.py', 'telegram', 'bot']
            
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    # Skip current process
                    if proc.pid == current_process.pid:
                        continue
                    
                    proc_info = proc.info
                    cmdline_list = proc_info.get('cmdline', [])
                    if cmdline_list:
                        cmdline = ' '.join(cmdline_list)
                    else:
                        cmdline = ''
                    
                    # Check if this looks like a bot process
                    if any(keyword.lower() in cmdline.lower() for keyword in bot_keywords):
                        if 'run.py' in cmdline:
                            bot_processes.append(proc)
                            
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
                    
        except Exception as e:
            logger.error(f"Error finding bot processes: {e}")
            
        return bot_processes
    
    def kill_bot_processes(self):
        """Kill all existing bot processes"""
        bot_processes = self.get_bot_processes()
        
        if not bot_processes:
            logger.info("No existing bot processes found")
            return True
        
        logger.info(f"Found {len(bot_processes)} existing bot process(es)")
        
        killed_count = 0
        for proc in bot_processes:
            try:
                logger.info(f"Terminating process {proc.pid}: {' '.join(proc.cmdline())}")
                proc.terminate()
                
                # Wait for graceful termination
                try:
                    proc.wait(timeout=5)
                    killed_count += 1
                    logger.info(f"Process {proc.pid} terminated gracefully")
                except psutil.TimeoutExpired:
                    # Force kill if graceful termination fails
                    logger.warning(f"Force killing process {proc.pid}")
                    proc.kill()
                    killed_count += 1
                    
            except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                logger.warning(f"Could not kill process {proc.pid}: {e}")
        
        if killed_count > 0:
            # Give the system time to clean up
            import time
            time.sleep(2)
            
        return killed_count > 0
    
    def write_pid_file(self):
        """Write current process PID to file"""
        try:
            with open(self.pid_file, 'w') as f:
                f.write(str(os.getpid()))
            logger.info(f"PID file written: {self.pid_file}")
            return True
        except Exception as e:
            logger.error(f"Failed to write PID file: {e}")
            return False
    
    def read_pid_file(self):
        """Read PID from file"""
        try:
            if self.pid_file.exists():
                with open(self.pid_file, 'r') as f:
                    return int(f.read().strip())
        except Exception as e:
            logger.error(f"Failed to read PID file: {e}")
        return None
    
    def is_bot_running(self):
        """Check if another bot instance is running"""
        pid = self.read_pid_file()
        if not pid:
            return False
        
        try:
            process = psutil.Process(pid)
            cmdline = ' '.join(process.cmdline())
            if 'run.py' in cmdline:
                logger.warning(f"Bot already running with PID {pid}")
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            # Process doesn't exist, clean up stale PID file
            self.cleanup_pid_file()
        
        return False
    
    def cleanup_pid_file(self):
        """Remove stale PID file"""
        try:
            if self.pid_file.exists():
                self.pid_file.unlink()
                logger.info("Cleaned up stale PID file")
        except Exception as e:
            logger.error(f"Failed to cleanup PID file: {e}")
    
    async def clear_telegram_webhook(self):
        """Clear Telegram webhook and pending updates"""
        try:
            bot = Bot(token=BOT_TOKEN)
            
            # Get webhook info
            webhook_info = await bot.get_webhook_info()
            if webhook_info.url:
                logger.info(f"Current webhook: {webhook_info.url}")
                await bot.delete_webhook(drop_pending_updates=True)
                logger.info("✅ Webhook deleted with pending updates dropped")
            else:
                logger.info("ℹ️  No active webhook found")
            
            # Telegram webhook cleared successfully
            
            # Verify cleanup
            webhook_info = await bot.get_webhook_info()
            if not webhook_info.url:
                logger.info("✅ Webhook successfully cleared")
                return True
            else:
                logger.warning("⚠️  Webhook may still be active")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error clearing webhook: {e}")
            return False
    
    def kill_all_python_bot_processes(self):
        """Kill all Python processes that might be running our bot"""
        killed_count = 0
        try:
            current_process = psutil.Process()
            current_pid = current_process.pid
            
            for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'username']):
                try:
                    # Skip current process
                    if proc.pid == current_pid:
                        continue
                    
                    proc_info = proc.info
                    cmdline_list = proc_info.get('cmdline', [])
                    cmdline = ' '.join(cmdline_list) if cmdline_list else ''
                    
                    # Check if this looks like our bot
                    if ('python' in proc_info.get('name', '').lower() and 
                        ('run.py' in cmdline or 'telegram' in cmdline.lower())):
                        
                        logger.info(f"🔪 Terminating bot process {proc.pid}: {cmdline}")
                        proc.terminate()
                        
                        # Wait for graceful termination
                        try:
                            proc.wait(timeout=5)
                            killed_count += 1
                            logger.info(f"✅ Process {proc.pid} terminated gracefully")
                        except psutil.TimeoutExpired:
                            logger.warning(f"⚠️  Force killing process {proc.pid}")
                            proc.kill()
                            killed_count += 1
                            
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
                    
        except Exception as e:
            logger.error(f"❌ Error during process cleanup: {e}")
            
        if killed_count > 0:
            import time
            time.sleep(3)  # Wait for system cleanup
            
        return killed_count > 0
    
    def cleanup_all_pid_files(self):
        """Clean up all possible PID files"""
        pid_files = ['bot.pid', 'telegramexambot.pid', 'telegram_bot.pid']
        
        for pid_file_name in pid_files:
            pid_path = Path(pid_file_name)
            if pid_path.exists():
                try:
                    pid_path.unlink()
                    logger.info(f"🗑️  Removed PID file: {pid_file_name}")
                except Exception as e:
                    logger.warning(f"⚠️  Could not remove {pid_file_name}: {e}")
    
    def cleanup_existing_bot(self):
        """Enhanced cleanup of any existing bot instance with webhook clearing"""
        logger.info("🧹 Starting enhanced bot cleanup...")
        
        # Step 1: Kill all bot processes first (synchronous)
        logger.info("🗑️  Cleaning up bot processes...")
        processes_killed = self.kill_all_python_bot_processes()
        
        # Step 2: Clean up all PID files
        logger.info("🗑️  Cleaning up PID files...")
        self.cleanup_all_pid_files()
        
        # Step 3: Wait for system cleanup
        import time
        time.sleep(3)
        
        # Step 4: Verify cleanup
        if self.is_bot_running():
            logger.warning("⚠️  Bot still appears to be running after cleanup")
            # Force cleanup attempt
            self.kill_all_python_bot_processes()
            time.sleep(2)
        
        # Step 5: Write new PID file
        self.write_pid_file()
        
        logger.info("✅ Enhanced bot cleanup completed successfully")
        
        return True
    
    async def cleanup_existing_bot_async(self):
        """Async version of cleanup with webhook clearing"""
        logger.info("🧹 Starting enhanced bot cleanup (async)...")
        
        try:
            # Step 1: Clear Telegram webhook (async)
            await self.clear_telegram_webhook()
        except Exception as e:
            logger.warning(f"⚠️  Webhook cleanup failed: {e}")
        
        # Step 2: Run synchronous cleanup
        self.cleanup_existing_bot()
        
        return True

def cleanup_existing_bot():
    """Convenience function to cleanup existing bot instances"""
    manager = ProcessManager()
    manager.cleanup_existing_bot()

def is_bot_running():
    """Convenience function to check if bot is running"""
    manager = ProcessManager()
    return manager.is_bot_running()
