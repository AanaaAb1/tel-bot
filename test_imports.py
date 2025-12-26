#!/usr/bin/env python3
"""
Simple import test for the bot components
"""

print("🚀 Starting import test...")

try:
    print("1. Testing settings import...")
    from app.config.settings import BOT_TOKEN
    print(f"✅ Settings loaded - Token: {BOT_TOKEN[:20]}...")
except Exception as e:
    print(f"❌ Settings import failed: {e}")
    exit(1)

try:
    print("2. Testing profile handler import...")
    from app.handlers.profile_handler_fixed import register_profile_handlers
    print("✅ Profile handler import successful")
except Exception as e:
    print(f"❌ Profile handler import failed: {e}")
    exit(1)

try:
    print("3. Testing dispatcher import...")
    from app.bot.dispatcher_fixed import register_handlers
    print("✅ Dispatcher import successful")
except Exception as e:
    print(f"❌ Dispatcher import failed: {e}")
    exit(1)

try:
    print("4. Testing bot creation...")
    from telegram import Application
    app = Application.builder().token(BOT_TOKEN).build()
    print("✅ Bot application created successfully")
except Exception as e:
    print(f"❌ Bot creation failed: {e}")
    exit(1)

print("\n🎉 All imports successful! Bot is ready to start.")
