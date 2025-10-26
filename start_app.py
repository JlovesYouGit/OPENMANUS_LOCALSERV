#!/usr/bin/env python
"""
Startup script for OpenManus with integrated frontend
"""

import os
import subprocess
import sys
import time
import webbrowser
from pathlib import Path

def check_frontend_build():
    """Check if frontend is built, build if needed"""
    frontend_dist = Path("newweb/quantum-canvas-design/dist")
    if not frontend_dist.exists():
        print("Frontend build not found. Building frontend...")
        try:
            # Try to build the frontend
            result = subprocess.run([
                sys.executable, "build_frontend.py"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Frontend built successfully!")
                return True
            else:
                print("❌ Frontend build failed:")
                print(result.stderr)
                return False
        except Exception as e:
            print(f"❌ Error building frontend: {e}")
            return False
    else:
        print("✅ Frontend build found")
        return True

def start_server():
    """Start the Flask server"""
    print("Starting OpenManus server...")
    try:
        # Start the Flask server
        process = subprocess.Popen([
            sys.executable, "web_ui.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait a moment for server to start
        time.sleep(3)
        
        # Check if server started successfully
        if process.poll() is None:
            print("✅ Server started successfully!")
            print("Opening browser...")
            webbrowser.open("http://localhost:5000")
            return process
        else:
            stdout, stderr = process.communicate()
            print("❌ Server failed to start:")
            print(stderr.decode())
            return None
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        return None

def main():
    """Main startup function"""
    print("🚀 Starting OpenManus with integrated frontend...")
    print("=" * 50)
    
    # Check and build frontend if needed
    if not check_frontend_build():
        print("⚠️  Frontend build failed. Starting server with fallback UI...")
    
    # Start the server
    server_process = start_server()
    
    if server_process:
        print("\n🎯 OpenManus is now running!")
        print("   URL: http://localhost:5000")
        print("   Press Ctrl+C to stop the server")
        
        try:
            # Keep the script running
            server_process.wait()
        except KeyboardInterrupt:
            print("\n🛑 Stopping server...")
            server_process.terminate()
            server_process.wait()
            print("✅ Server stopped")
    else:
        print("❌ Failed to start OpenManus")
        sys.exit(1)

if __name__ == "__main__":
    main()