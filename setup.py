#!/usr/bin/env python3
"""
Weather Intelligence Dashboard Setup Script
Helps users configure the OpenWeatherMap API key for live data
"""

import os
import sys
from pathlib import Path

def main():
    print("🌦️ Weather Intelligence Dashboard - Setup")
    print("=" * 50)
    
    print("""
🔑 To get LIVE weather data, you need a free OpenWeatherMap API key:

1. Visit: https://openweathermap.org/api
2. Click "Sign Up" (it's free!)
3. Create an account
4. Go to "API keys" section
5. Copy your API key

📋 Features with API key:
   ✅ Real-time weather data for 15+ global cities
   ✅ Accurate 5-day forecasts
   ✅ Live temperature maps
   ✅ Professional weather metrics
   
🎯 Features without API key:
   ✅ Realistic mock data for demonstration
   ✅ All dashboard functionality works
   ✅ Perfect for portfolio showcase
    """)
    
    choice = input("\nDo you have an OpenWeatherMap API key? (y/n): ").lower().strip()
    
    if choice == 'y':
        api_key = input("\nEnter your OpenWeatherMap API key: ").strip()
        
        if api_key:
            # Create .env file
            env_path = Path('.env')
            env_content = f"OPENWEATHER_API_KEY={api_key}\n"
            
            try:
                with open(env_path, 'w') as f:
                    f.write(env_content)
                
                print("✅ API key saved successfully!")
                print("🚀 You can now run the app with live data:")
                print("   python demo.py")
                print("   streamlit run app.py")
                
            except Exception as e:
                print(f"❌ Error saving API key: {e}")
                print("💡 You can manually create a .env file with:")
                print(f"   OPENWEATHER_API_KEY={api_key}")
        else:
            print("⚠️ No API key entered. App will use mock data.")
    
    else:
        print("✅ No problem! The app works great with mock data.")
        print("🎯 Perfect for demonstrating all features in your portfolio.")
    
    print("\n🌟 Ready to run Weather Intelligence Dashboard!")
    print("📊 Demo: python demo.py")
    print("🌐 Web App: streamlit run app.py")
    print("\n💼 This project showcases:")
    print("   • Real-time API integration")
    print("   • Interactive data visualization")
    print("   • Modern web dashboard development")
    print("   • Professional data science skills")

if __name__ == "__main__":
    main()
