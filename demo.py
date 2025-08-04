from src.weather_collector import WeatherDataCollector

if __name__ == "__main__":
    # Initialize the weather data collector
    collector = WeatherDataCollector()
    
    # Specify cities for the demo (use a few to avoid rate limit issues)
    cities = ["New York", "London", "Tokyo"]
    
    print("\n🌦️ Weather Intelligence Demo\n===============================")
    for city in cities:
        print(f"\nFetching current weather for {city}...")
        current_weather = collector.get_current_weather(city)
        print(current_weather)
        
        print(f"\nFetching 5-day forecast for {city}...")
        forecast = collector.get_forecast(city, days=5)
        for day in forecast[:5]:
            print(day)
    
    print("\n✅ Demo completed successfully!")
