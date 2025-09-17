#!/usr/bin/env python3
"""
Start the PharmaTrust Flask server
"""

import webbrowser
import time
import threading
from app import app

def open_browser():
    """Open browser after a short delay"""
    time.sleep(2)
    webbrowser.open('http://localhost:5000')

if __name__ == '__main__':
    print("🚀 Starting PharmaTrust Server...")
    print("📱 Opening browser in 2 seconds...")
    
    # Start browser in a separate thread
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    print("🌐 Server will be available at:")
    print("   - http://localhost:5000")
    print("   - http://127.0.0.1:5000")
    print("\n📋 Available endpoints:")
    print("   - / (Main Dashboard)")
    print("   - /verify (Product Verification)")
    print("   - /api/medicines (API)")
    print("   - /api/balance (API)")
    print("\n⏹️  Press Ctrl+C to stop the server")
    print("-" * 50)
    
    # Start Flask server
    app.run(debug=True, host='0.0.0.0', port=5000)
