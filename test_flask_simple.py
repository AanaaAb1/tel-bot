#!/usr/bin/env python3
"""
Simple Flask test
"""

import sys
import os
from pathlib import Path

try:
    from flask import Flask
    print("✅ Flask import successful")
    
    app = Flask(__name__)
    
    @app.route('/')
    def hello():
        return "Flask is working!"
    
    @app.route('/test')
    def test():
        return "Test route works!"
    
    if __name__ == '__main__':
        print("🚀 Starting simple Flask test...")
        print("📱 Test URL: http://localhost:5001")
        print("🛑 Press Ctrl+C to stop")
        app.run(debug=True, host='0.0.0.0', port=5001)
        
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Flask may not be installed")
except Exception as e:
    print(f"❌ Error: {e}")
