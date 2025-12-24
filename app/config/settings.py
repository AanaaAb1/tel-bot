import os
from dotenv import load_dotenv

load_dotenv()

# Bot Configuration
BOT_TOKEN = os.getenv("BOT_TOKEN", "8184888715:AAEvw1RcRfltV8A-y2fAHqb6w-CNmskO5to")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/bot.db")

# Telegram API Configuration
TELEGRAM_API_BASE_URL = os.getenv("TELEGRAM_API_BASE_URL", "API")
TELEGRAM_API_PATH = os.getenv("TELEGRAM_API_PATH", "/")
TELEGRAM_API_URL = TELEGRAM_API_BASE_URL + TELEGRAM_API_PATH

# Process Management Configuration
ENABLE_PROCESS_CLEANUP = os.getenv("ENABLE_PROCESS_CLEANUP", "true").lower() == "true"
MAX_BOT_RETRIES = int(os.getenv("MAX_BOT_RETRIES", "3"))
BOT_RETRY_DELAY = int(os.getenv("BOT_RETRY_DELAY", "5"))
PID_FILE_PATH = os.getenv("PID_FILE_PATH", "bot.pid")

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", "bot.log")
LOG_MAX_SIZE = int(os.getenv("LOG_MAX_SIZE", str(10*1024*1024)))  # 10MB default
LOG_BACKUP_COUNT = int(os.getenv("LOG_BACKUP_COUNT", "5"))
ENABLE_FILE_LOGGING = os.getenv("ENABLE_FILE_LOGGING", "true").lower() == "true"

# Bot Behavior Configuration
DROP_PENDING_UPDATES = os.getenv("DROP_PENDING_UPDATES", "true").lower() == "true"
POLLING_TIMEOUT = int(os.getenv("POLLING_TIMEOUT", "10"))
ALLOWED_UPDATES = os.getenv("ALLOWED_UPDATES", "all")  # all, message, callback_query, etc.

# Webhook Configuration (Alternative to polling)
USE_WEBHOOK = os.getenv("USE_WEBHOOK", "false").lower() == "true"
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")
WEBHOOK_HOST = os.getenv("WEBHOOK_HOST", "0.0.0.0")
WEBHOOK_PORT = int(os.getenv("WEBHOOK_PORT", "8443"))
WEBHOOK_PATH = os.getenv("WEBHOOK_PATH", "/webhook")

# Admin Configuration
ADMIN_USER_IDS = os.getenv("ADMIN_USER_IDS", "").split(",") if os.getenv("ADMIN_USER_IDS") else []
ADMIN_ENABLED = len(ADMIN_USER_IDS) > 0

# Security Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ENABLE_AUDIT_LOG = os.getenv("ENABLE_AUDIT_LOG", "true").lower() == "true"

# Development Configuration
DEBUG_MODE = os.getenv("DEBUG_MODE", "false").lower() == "true"
