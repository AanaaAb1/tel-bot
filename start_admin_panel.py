#!/usr/bin/env python3
"""
Admin Panel Startup Script
Simple script to start the admin panel
"""

import sys
import os
import subprocess
from pathlib import Path

def main():
    print("🚀 Starting Admin Panel...")
    print("=" * 50)
    
    # Change to project directory
    project_dir = Path(__file__).parent
    os.chdir(project_dir)
    print(f"📁 Working directory: {project_dir}")
    
    # Check if admin_panel.py exists
    admin_panel_path = project_dir / "admin_panel.py"
    if not admin_panel_path.exists():
        print("❌ admin_panel.py not found!")
        return 1
    
    print("✅ admin_panel.py found")
    print("🌐 Starting Flask server...")
    print("🔗 URL: http://localhost:5000")
    print("🛑 Press Ctrl+C to stop")
    print("=" * 50)
    
    try:
        # Start the admin panel
        subprocess.run([sys.executable, "admin_panel.py"])
    except KeyboardInterrupt:
        print("\n👋 Admin panel stopped")
        return 0
    except Exception as e:
        print(f"❌ Error starting admin panel: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
