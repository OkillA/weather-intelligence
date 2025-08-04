#!/usr/bin/env python3
"""
Quick Deployment Helper for Weather Intelligence Dashboard
"""

import os
import subprocess
import sys

def main():
    print("🚀 Weather Intelligence Dashboard - Deployment Helper")
    print("=" * 60)
    
    print("""
🌐 DEPLOYMENT OPTIONS:

1. 🏆 Streamlit Cloud (Recommended - Free & Easy)
   - Professional hosting
   - Automatic updates from GitHub
   - Custom domain available
   - Perfect for portfolio

2. 🏠 Local Network (Quick Demo)
   - Share immediately on your network
   - Good for local presentations
   - Temporary access

3. 🔧 Manual Setup Guide
   - Step-by-step instructions
   - GitHub repository setup
    """)
    
    choice = input("Choose deployment option (1/2/3): ").strip()
    
    if choice == "1":
        print("\n🏆 STREAMLIT CLOUD DEPLOYMENT")
        print("-" * 40)
        print("""
📋 Steps to deploy on Streamlit Cloud:

1. Create GitHub Repository:
   - Go to: https://github.com/new
   - Repository name: weather-intelligence
   - Make it public
   - Don't initialize with README (we have files)

2. Push Your Code:
   Run these commands in your terminal:
   
   git init
   git add .
   git commit -m "Weather Intelligence Dashboard"
   git branch -M main
   git remote add origin https://github.com/[YOUR_USERNAME]/weather-intelligence.git
   git push -u origin main

3. Deploy on Streamlit:
   - Go to: https://share.streamlit.io
   - Sign in with GitHub
   - Click "New app"
   - Repository: [YOUR_USERNAME]/weather-intelligence
   - Branch: main
   - Main file path: app.py
   - Click "Deploy!"

4. Your app will be live at:
   https://[YOUR_USERNAME]-weather-intelligence-app-[RANDOM].streamlit.app

🔑 Optional: Add API key in Streamlit Cloud settings for live data
   (Without API key, app uses impressive mock data)
        """)
        
    elif choice == "2":
        print("\n🏠 LOCAL NETWORK DEPLOYMENT")
        print("-" * 40)
        
        try:
            # Get local IP
            import socket
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            
            print(f"🌐 Starting server on your network...")
            print(f"📍 Your IP: {local_ip}")
            print(f"🔗 Share this URL: http://{local_ip}:8501")
            print("\n⚠️  Make sure others are on the same WiFi network!")
            print("🛑 Press Ctrl+C to stop the server")
            
            # Start Streamlit server
            subprocess.run([
                sys.executable, "-m", "streamlit", "run", "app.py",
                "--server.address", "0.0.0.0",
                "--server.port", "8501"
            ])
            
        except Exception as e:
            print(f"❌ Error: {e}")
            print("💡 Try running manually: streamlit run app.py --server.address 0.0.0.0")
    
    elif choice == "3":
        print("\n🔧 MANUAL SETUP GUIDE")
        print("-" * 40)
        print("📖 Check DEPLOYMENT.md for detailed instructions")
        print("📂 All files are ready in this directory")
        print("🌟 Your app is portfolio-ready!")
    
    else:
        print("❌ Invalid choice. Please run again and select 1, 2, or 3.")
    
    print("\n✨ Weather Intelligence Dashboard is ready to impress!")
    print("🎯 Perfect for showcasing your ML and web development skills!")

if __name__ == "__main__":
    main()
