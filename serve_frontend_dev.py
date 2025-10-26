#!/usr/bin/env python
"""
Development server for OpenManus frontend
"""

import os
import subprocess
import sys
import time
import webbrowser
from pathlib import Path

def start_frontend_dev_server():
    """Start the Vite development server"""
    frontend_dir = Path("newweb/quantum-canvas-design")
    
    if not frontend_dir.exists():
        print("❌ Frontend directory not found")
        return None
    
    # Change to frontend directory
    original_dir = os.getcwd()
    try:
        os.chdir(frontend_dir)
        
        print("🚀 Starting Vite development server...")
        # Start the Vite development server
        process = subprocess.Popen([
            "npm", "run", "dev"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait a moment for server to start
        time.sleep(5)
        
        # Check if server started successfully
        if process.poll() is None:
            print("✅ Vite development server started successfully!")
            print("🌐 Frontend available at: http://localhost:8080")
            return process
        else:
            stdout, stderr = process.communicate()
            print("❌ Vite server failed to start:")
            print(stderr.decode())
            return None
            
    except Exception as e:
        print(f"❌ Error starting Vite server: {e}")
        return None
    finally:
        # Change back to original directory
        os.chdir(original_dir)

def start_backend_server():
    """Start the Flask backend server"""
    print("🚀 Starting OpenManus backend server...")
    try:
        # Start the Flask server on a different port
        process = subprocess.Popen([
            sys.executable, "web_ui.py", "--port", "5000"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait a moment for server to start
        time.sleep(3)
        
        # Check if server started successfully
        if process.poll() is None:
            print("✅ Backend server started successfully!")
            print("🌐 Backend API available at: http://localhost:5000")
            return process
        else:
            stdout, stderr = process.communicate()
            print("❌ Backend server failed to start:")
            print(stderr.decode())
            return None
    except Exception as e:
        print(f"❌ Error starting backend server: {e}")
        return None

def main():
    """Main function to start both frontend and backend servers"""
    print("🚀 Starting OpenManus Development Environment...")
    print("=" * 50)
    
    # Start backend server
    backend_process = start_backend_server()
    
    if not backend_process:
        print("❌ Failed to start backend server")
        return
    
    # Start frontend development server
    frontend_process = start_frontend_dev_server()
    
    if not frontend_process:
        print("❌ Failed to start frontend development server")
        # Terminate backend process
        backend_process.terminate()
        backend_process.wait()
        return
    
    print("\n🎯 OpenManus Development Environment is running!")
    print("   Backend API: http://localhost:5000")
    print("   Frontend UI: http://localhost:8080")
    print("   Press Ctrl+C to stop both servers")
    
    try:
        # Keep the script running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping servers...")
        frontend_process.terminate()
        backend_process.terminate()
        
        frontend_process.wait()
        backend_process.wait()
        
        print("✅ Both servers stopped")

if __name__ == "__main__":
    main()