import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import time
from src.weather_collector import WeatherDataCollector

# Page configuration
st.set_page_config(
    page_title="Weather Intelligence Dashboard",
    page_icon="🌦️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'weather_collector' not in st.session_state:
    st.session_state.weather_collector = WeatherDataCollector()

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 5px solid #1f77b4;
    }
    .weather-description {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin: 1rem 0;
    }
    /* Fix spacing and prevent overlaps in right column */
    .stContainer {
        margin-bottom: 1rem;
    }
    .stMetric {
        margin-bottom: 0.5rem;
    }
    [data-testid="stVerticalBlock"] > [style*="flex-direction: column"] > div {
        margin-bottom: 1rem;
    }
    /* Ensure proper spacing around plotly charts */
    .js-plotly-plot {
        margin-bottom: 2rem !important;
    }
    /* Style for section headers to ensure proper spacing */
    h3 {
        margin-top: 2rem !important;
        margin-bottom: 1rem !important;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Header
    st.markdown('<h1 class="main-header">🌦️ Weather Intelligence Dashboard</h1>', unsafe_allow_html=True)
    st.markdown('<p class="weather-description">AI-Powered Weather Analytics & Forecasting Platform</p>', unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.title("🌍 Weather Controls")
    
    # Get available cities
    cities = st.session_state.weather_collector.get_cities_list()
    
    # City selection
    selected_city = st.sidebar.selectbox(
        "Select a City",
        cities,
        index=0,
        help="Choose a city to view detailed weather information"
    )
    
    # Refresh button
    if st.sidebar.button("🔄 Refresh Data", help="Fetch latest weather data"):
        # Clear cache to force refresh
        if hasattr(st.session_state.weather_collector, 'cache'):
            st.session_state.weather_collector.cache.clear()
        st.rerun()
    
    # Auto-refresh toggle
    auto_refresh = st.sidebar.checkbox("🔄 Auto-refresh (30s)", value=False)
    
    # Info about API
    with st.sidebar.expander("ℹ️ About Data Source"):
        st.markdown("""
        **Data Source**: OpenWeatherMap API
        
        **Features**:
        - Real-time weather data
        - 5-day forecasts
        - Global city coverage
        - Professional weather metrics
        
        **Note**: If no API key is configured, the app uses realistic mock data for demonstration.
        """)
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Current weather section
        st.subheader(f"🌡️ Current Weather in {selected_city}")
        
        # Get current weather data
        with st.spinner(f"Fetching weather data for {selected_city}..."):
            current_weather = st.session_state.weather_collector.get_current_weather(selected_city)
        
        if current_weather:
            # Weather metrics in columns
            metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
            
            with metric_col1:
                st.metric(
                    label="🌡️ Temperature",
                    value=f"{current_weather['temperature']:.1f}°C",
                    delta=f"Feels like {current_weather['feels_like']:.1f}°C"
                )
            
            with metric_col2:
                st.metric(
                    label="💧 Humidity",
                    value=f"{current_weather['humidity']}%"
                )
            
            with metric_col3:
                st.metric(
                    label="🌬️ Wind Speed",
                    value=f"{current_weather['wind_speed']:.1f} m/s"
                )
            
            with metric_col4:
                st.metric(
                    label="🔍 Visibility",
                    value=f"{current_weather['visibility']:.1f} km"
                )
            
            # Weather description
            st.markdown(f"""
            <div style="text-align: center; margin: 1rem 0;">
                <h3>{current_weather['weather_description'].title()}</h3>
                <p>Pressure: {current_weather['pressure']} hPa | Cloudiness: {current_weather['cloudiness']}%</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Additional details in expandable section
            with st.expander("📊 Detailed Weather Information"):
                detail_col1, detail_col2 = st.columns(2)
                
                with detail_col1:
                    st.write(f"**Weather Type**: {current_weather['weather_main']}")
                    st.write(f"**Pressure**: {current_weather['pressure']} hPa")
                    st.write(f"**Wind Direction**: {current_weather['wind_direction']}°")
                    st.write(f"**Country**: {current_weather['country']}")
                
                with detail_col2:
                    st.write(f"**Sunrise**: {current_weather['sunrise'].strftime('%H:%M')}")
                    st.write(f"**Sunset**: {current_weather['sunset'].strftime('%H:%M')}")
                    st.write(f"**Last Updated**: {current_weather['timestamp'].strftime('%H:%M:%S')}")
        
        # Forecast section
        st.subheader(f"📅 5-Day Forecast for {selected_city}")
        
        with st.spinner("Loading forecast data..."):
            forecast_data = st.session_state.weather_collector.get_forecast(selected_city, days=5)
        
        if forecast_data:
            # Convert forecast to DataFrame for easier plotting
            df_forecast = pd.DataFrame(forecast_data)
            df_forecast['date'] = pd.to_datetime(df_forecast['datetime'])
            
            # Create temperature trend chart
            fig_temp = px.line(
                df_forecast,
                x='date',
                y='temperature',
                title=f'Temperature Trend - {selected_city}',
                labels={'temperature': 'Temperature (°C)', 'date': 'Date & Time'},
                line_shape='spline'
            )
            fig_temp.update_layout(height=400)
            st.plotly_chart(fig_temp, use_container_width=True)
            
            # Daily summary
            st.subheader("📋 Daily Summary")
            
            # Group by day for daily summary
            df_forecast['day'] = df_forecast['date'].dt.date
            daily_summary = df_forecast.groupby('day').agg({
                'temperature': ['min', 'max', 'mean'],
                'humidity': 'mean',
                'precipitation_prob': 'max',
                'weather_main': lambda x: x.mode()[0] if not x.empty else 'Unknown'
            }).round(1)
            
            # Flatten column names
            daily_summary.columns = ['Min Temp (°C)', 'Max Temp (°C)', 'Avg Temp (°C)', 
                                   'Avg Humidity (%)', 'Max Rain Chance (%)', 'Weather']
            
            st.dataframe(daily_summary, use_container_width=True)
    
    with col2:
        # Weather map section
        st.subheader("🗺️ Global Weather Map")
        
        # Get weather for all supported cities
        all_cities = st.session_state.weather_collector.get_cities_list()
        
        with st.spinner("Loading global weather data..."):
            global_weather = {}
            for city in all_cities:
                weather_data = st.session_state.weather_collector.get_current_weather(city)
                if weather_data:
                    coords = st.session_state.weather_collector.get_city_coordinates(city)
                    global_weather[city] = {
                        **weather_data,
                        **coords
                    }
        
        if global_weather:
            # Create map data
            map_data = []
            for city, data in global_weather.items():
                map_data.append({
                    'city': city,
                    'lat': data['lat'],
                    'lon': data['lon'],
                    'temperature': data['temperature'],
                    'humidity': data['humidity'],
                    'weather': data['weather_main']
                })
            
            df_map = pd.DataFrame(map_data)
            
            # Create map, center on selected city
            selected_coords = st.session_state.weather_collector.get_city_coordinates(selected_city)
            fig_map = px.scatter_map(
                df_map,
                lat='lat',
                lon='lon',
                size='temperature',
                color='temperature',
                hover_name='city',
                hover_data={'temperature': True, 'humidity': True, 'weather': True},
                color_continuous_scale='RdYlBu_r',
                size_max=15,
                zoom=2,
                title=f"Global Temperature Map - Centered on {selected_city}",
                center={'lat': selected_coords['lat'], 'lon': selected_coords['lon']}
            )
            
            fig_map.update_layout(
                map_style="open-street-map",
                height=500,
                margin={"r":0,"t":30,"l":0,"b":0}
            )
            
            st.plotly_chart(fig_map, use_container_width=True)
        
        # Add spacing to prevent overlap with map attribution
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Weather statistics
        st.subheader("📊 Weather Statistics")
        
        if global_weather:
            temps = [data['temperature'] for data in global_weather.values()]
            humidities = [data['humidity'] for data in global_weather.values()]
            
            # Create metrics in a container to avoid overlap
            with st.container():
                st.metric("🌡️ Global Avg Temp", f"{np.mean(temps):.1f}°C")
                st.metric("💧 Global Avg Humidity", f"{np.mean(humidities):.0f}%")
                st.metric("🏙️ Cities Monitored", len(global_weather))
                
                # Add some spacing
                st.write("")
        
        # Weather alerts section
        st.subheader("⚠️ Weather Alerts")
        
        if current_weather:
            alerts = []
            
            # Temperature alerts
            if current_weather['temperature'] > 35:
                alerts.append("🔥 **Heat Warning**: Very high temperature detected!")
            elif current_weather['temperature'] < 0:
                alerts.append("❄️ **Freeze Warning**: Temperature below freezing!")
            
            # Wind alerts
            if current_weather['wind_speed'] > 10:
                alerts.append("💨 **Wind Advisory**: Strong winds detected!")
            
            # Humidity alerts
            if current_weather['humidity'] > 85:
                alerts.append("💧 **High Humidity**: Very humid conditions!")
            
            # Visibility alerts
            if current_weather['visibility'] < 5:
                alerts.append("🌫️ **Low Visibility**: Poor visibility conditions!")
            
            if alerts:
                for alert in alerts:
                    st.warning(alert)
            else:
                st.success("✅ No weather alerts for this location")
    
    # Auto-refresh functionality
    if auto_refresh:
        time.sleep(30)
        st.rerun()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 1rem 0;">
        🌦️ Weather Intelligence Dashboard | Built with Streamlit & OpenWeatherMap API<br>
        <small>Part of AI/ML Portfolio demonstrating real-time data integration and visualization</small>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
