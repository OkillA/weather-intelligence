import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import json
import os
from typing import Dict, List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class WeatherDataCollector:
    """
    Collects real-time weather data from OpenWeatherMap API
    Features: rate limiting, caching, error handling, multiple cities
    """
    
    def __init__(self, api_key: Optional[str] = None):
        # Try to get API key from environment or parameter
        self.api_key = api_key or os.getenv('OPENWEATHER_API_KEY')
        self.base_url = "https://api.openweathermap.org/data/2.5"
        
        # Session for connection pooling
        self.session = requests.Session()
        
        # Rate limiting (60 calls per minute for free tier)
        self.last_request_time = 0
        self.min_request_interval = 1  # 1 second between requests
        
        # Simple caching
        self.cache = {}
        self.cache_duration = 600  # 10 minutes cache
        
        # Major cities for weather tracking
        self.cities = {
            'New York': {'lat': 40.7128, 'lon': -74.0060, 'country': 'US'},
            'London': {'lat': 51.5074, 'lon': -0.1278, 'country': 'GB'},
            'Tokyo': {'lat': 35.6762, 'lon': 139.6503, 'country': 'JP'},
            'Paris': {'lat': 48.8566, 'lon': 2.3522, 'country': 'FR'},
            'Sydney': {'lat': -33.8688, 'lon': 151.2093, 'country': 'AU'},
            'Mumbai': {'lat': 19.0760, 'lon': 72.8777, 'country': 'IN'},
            'São Paulo': {'lat': -23.5505, 'lon': -46.6333, 'country': 'BR'},
            'Cairo': {'lat': 30.0444, 'lon': 31.2357, 'country': 'EG'},
            'Berlin': {'lat': 52.5200, 'lon': 13.4050, 'country': 'DE'},
            'Toronto': {'lat': 43.6532, 'lon': -79.3832, 'country': 'CA'},
            'Seoul': {'lat': 37.5665, 'lon': 126.9780, 'country': 'KR'},
            'Moscow': {'lat': 55.7558, 'lon': 37.6173, 'country': 'RU'},
            'Los Angeles': {'lat': 34.0522, 'lon': -118.2437, 'country': 'US'},
            'Singapore': {'lat': 1.3521, 'lon': 103.8198, 'country': 'SG'},
            'Dubai': {'lat': 25.2048, 'lon': 55.2708, 'country': 'AE'}
        }
    
    def _rate_limit(self):
        """Ensure we don't exceed API rate limits"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last
            time.sleep(sleep_time)
        self.last_request_time = time.time()
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached data is still valid"""
        if cache_key not in self.cache:
            return False
        
        cached_time = self.cache[cache_key].get('timestamp', 0)
        return (time.time() - cached_time) < self.cache_duration
    
    def _get_from_cache(self, cache_key: str):
        """Get data from cache if valid"""
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]['data']
        return None
    
    def _save_to_cache(self, cache_key: str, data):
        """Save data to cache with timestamp"""
        self.cache[cache_key] = {
            'data': data,
            'timestamp': time.time()
        }
    
    def get_current_weather(self, city: str) -> Dict:
        """Get current weather for a specific city"""
        try:
            cache_key = f"current_{city}"
            cached_data = self._get_from_cache(cache_key)
            if cached_data:
                print(f"📋 Using cached data for {city}")
                return cached_data
            
            if not self.api_key:
                print("⚠️ No API key found, using mock data")
                return self._get_mock_weather(city)
            
            city_info = self.cities.get(city)
            if not city_info:
                print(f"❌ City {city} not found")
                return self._get_mock_weather(city)
            
            print(f"🌍 Fetching live weather for {city}...")
            self._rate_limit()
            
            url = f"{self.base_url}/weather"
            params = {
                'lat': city_info['lat'],
                'lon': city_info['lon'],
                'appid': self.api_key,
                'units': 'metric'  # Celsius
            }
            
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                weather_data = self._parse_current_weather(data, city)
                self._save_to_cache(cache_key, weather_data)
                print(f"✅ Successfully fetched weather for {city}")
                return weather_data
            else:
                print(f"⚠️ API error ({response.status_code}), using mock data for {city}")
                return self._get_mock_weather(city)
                
        except Exception as e:
            print(f"❌ Error fetching weather for {city}: {e}")
            return self._get_mock_weather(city)
    
    def _parse_current_weather(self, data: Dict, city: str) -> Dict:
        """Parse OpenWeatherMap API response"""
        return {
            'city': city,
            'temperature': data['main']['temp'],
            'feels_like': data['main']['feels_like'],
            'humidity': data['main']['humidity'],
            'pressure': data['main']['pressure'],
            'wind_speed': data.get('wind', {}).get('speed', 0),
            'wind_direction': data.get('wind', {}).get('deg', 0),
            'visibility': data.get('visibility', 10000) / 1000,  # Convert to km
            'weather_main': data['weather'][0]['main'],
            'weather_description': data['weather'][0]['description'],
            'cloudiness': data['clouds']['all'],
            'sunrise': datetime.fromtimestamp(data['sys']['sunrise']),
            'sunset': datetime.fromtimestamp(data['sys']['sunset']),
            'country': data['sys']['country'],
            'timezone': data['timezone'],
            'timestamp': datetime.now()
        }
    
    def get_forecast(self, city: str, days: int = 5) -> List[Dict]:
        """Get weather forecast for a city"""
        try:
            cache_key = f"forecast_{city}_{days}"
            cached_data = self._get_from_cache(cache_key)
            if cached_data:
                print(f"📋 Using cached forecast for {city}")
                return cached_data
            
            if not self.api_key:
                print("⚠️ No API key found, using mock forecast")
                return self._get_mock_forecast(city, days)
            
            city_info = self.cities.get(city)
            if not city_info:
                return self._get_mock_forecast(city, days)
            
            print(f"🔮 Fetching {days}-day forecast for {city}...")
            self._rate_limit()
            
            url = f"{self.base_url}/forecast"
            params = {
                'lat': city_info['lat'],
                'lon': city_info['lon'],
                'appid': self.api_key,
                'units': 'metric',
                'cnt': days * 8  # 8 forecasts per day (3-hour intervals)
            }
            
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                forecast_data = self._parse_forecast(data, city)
                self._save_to_cache(cache_key, forecast_data)
                print(f"✅ Successfully fetched forecast for {city}")
                return forecast_data
            else:
                print(f"⚠️ Forecast API error ({response.status_code}), using mock data")
                return self._get_mock_forecast(city, days)
                
        except Exception as e:
            print(f"❌ Error fetching forecast for {city}: {e}")
            return self._get_mock_forecast(city, days)
    
    def _parse_forecast(self, data: Dict, city: str) -> List[Dict]:
        """Parse forecast API response"""
        forecasts = []
        for item in data['list']:
            forecasts.append({
                'city': city,
                'datetime': datetime.fromtimestamp(item['dt']),
                'temperature': item['main']['temp'],
                'feels_like': item['main']['feels_like'],
                'humidity': item['main']['humidity'],
                'pressure': item['main']['pressure'],
                'weather_main': item['weather'][0]['main'],
                'weather_description': item['weather'][0]['description'],
                'wind_speed': item.get('wind', {}).get('speed', 0),
                'cloudiness': item['clouds']['all'],
                'precipitation_prob': item.get('pop', 0) * 100  # Convert to percentage
            })
        return forecasts
    
    def get_multiple_cities_weather(self, city_list: List[str] = None) -> Dict:
        """Get current weather for multiple cities"""
        if city_list is None:
            city_list = list(self.cities.keys())[:8]  # Limit to 8 cities to avoid rate limits
        
        weather_data = {}
        for city in city_list:
            weather_data[city] = self.get_current_weather(city)
            time.sleep(0.5)  # Small delay between requests
        
        return weather_data
    
    def _get_mock_weather(self, city: str) -> Dict:
        """Generate realistic mock weather data"""
        # Base temperatures by region (rough approximation)
        base_temps = {
            'New York': 15, 'London': 12, 'Tokyo': 18, 'Paris': 14,
            'Sydney': 22, 'Mumbai': 28, 'São Paulo': 25, 'Cairo': 26,
            'Berlin': 10, 'Toronto': 8, 'Seoul': 16, 'Moscow': 5,
            'Los Angeles': 24, 'Singapore': 30, 'Dubai': 32
        }
        
        base_temp = base_temps.get(city, 20)
        temp_variation = np.random.normal(0, 5)
        temperature = base_temp + temp_variation
        
        return {
            'city': city,
            'temperature': round(temperature, 1),
            'feels_like': round(temperature + np.random.normal(0, 2), 1),
            'humidity': np.random.randint(30, 90),
            'pressure': np.random.randint(1000, 1025),
            'wind_speed': round(np.random.uniform(0, 15), 1),
            'wind_direction': np.random.randint(0, 360),
            'visibility': round(np.random.uniform(5, 15), 1),
            'weather_main': np.random.choice(['Clear', 'Clouds', 'Rain', 'Snow', 'Mist']),
            'weather_description': np.random.choice(['clear sky', 'few clouds', 'light rain', 'overcast']),
            'cloudiness': np.random.randint(0, 100),
            'sunrise': datetime.now().replace(hour=6, minute=30),
            'sunset': datetime.now().replace(hour=18, minute=45),
            'country': self.cities.get(city, {}).get('country', 'XX'),
            'timezone': 0,
            'timestamp': datetime.now()
        }
    
    def _get_mock_forecast(self, city: str, days: int = 5) -> List[Dict]:
        """Generate mock forecast data"""
        forecasts = []
        base_weather = self._get_mock_weather(city)
        
        for day in range(days):
            for hour in range(0, 24, 3):  # Every 3 hours
                forecast_time = datetime.now() + timedelta(days=day, hours=hour)
                temp_variation = np.random.normal(0, 3)
                
                forecasts.append({
                    'city': city,
                    'datetime': forecast_time,
                    'temperature': round(base_weather['temperature'] + temp_variation, 1),
                    'feels_like': round(base_weather['temperature'] + temp_variation + np.random.normal(0, 1), 1),
                    'humidity': np.random.randint(40, 85),
                    'pressure': base_weather['pressure'] + np.random.randint(-5, 5),
                    'weather_main': np.random.choice(['Clear', 'Clouds', 'Rain']),
                    'weather_description': np.random.choice(['clear sky', 'partly cloudy', 'light rain']),
                    'wind_speed': round(np.random.uniform(2, 12), 1),
                    'cloudiness': np.random.randint(10, 80),
                    'precipitation_prob': np.random.randint(0, 60)
                })
        
        return forecasts[:days * 8]  # Limit to requested days
    
    def get_cities_list(self) -> List[str]:
        """Get list of supported cities"""
        return list(self.cities.keys())
    
    def get_city_coordinates(self, city: str) -> Dict:
        """Get coordinates for a city"""
        return self.cities.get(city, {'lat': 0, 'lon': 0, 'country': 'XX'})
