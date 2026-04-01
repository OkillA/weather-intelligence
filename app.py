import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime
import time
import logging
from src.weather_collector import WeatherDataCollector

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ── Page configuration (must be first Streamlit call) ────────────────────────
st.set_page_config(
    page_title="Weather Intelligence",
    page_icon="⛅",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={"About": "**Weather Intelligence** — Real-time global weather analytics"},
)

# ── Session state ─────────────────────────────────────────────────────────────
if "weather_collector" not in st.session_state:
    st.session_state.weather_collector = WeatherDataCollector()
if "unit" not in st.session_state:
    st.session_state.unit = "C"

collector: WeatherDataCollector = st.session_state.weather_collector

# ── Temperature helpers ───────────────────────────────────────────────────────
def to_f(celsius: float) -> float:
    return celsius * 9 / 5 + 32

def display_temp(celsius: float) -> float:
    return to_f(celsius) if st.session_state.unit == "F" else celsius

def fmt_temp(celsius: float) -> str:
    if st.session_state.unit == "F":
        return f"{to_f(celsius):.1f}°F"
    return f"{celsius:.1f}°C"

def temp_unit() -> str:
    return "°F" if st.session_state.unit == "F" else "°C"

# ── Weather condition metadata ─────────────────────────────────────────────────
_CONDITION_META: dict = {
    "Clear":        {"icon": "☀️",  "color": "#f7971e",
                     "gradient": "linear-gradient(135deg,#f9a826 0%,#f7971e 55%,#e55d25 100%)"},
    "Clouds":       {"icon": "⛅",  "color": "#7f8fa6",
                     "gradient": "linear-gradient(135deg,#2c3e50 0%,#3b4d63 55%,#7f8fa6 100%)"},
    "Rain":         {"icon": "🌧️", "color": "#4facfe",
                     "gradient": "linear-gradient(135deg,#1a2a6c 0%,#1e5799 55%,#4facfe 100%)"},
    "Drizzle":      {"icon": "🌦️", "color": "#74b9ff",
                     "gradient": "linear-gradient(135deg,#1e3c72 0%,#2a5298 55%,#74b9ff 100%)"},
    "Thunderstorm": {"icon": "⛈️", "color": "#9b59b6",
                     "gradient": "linear-gradient(135deg,#1a0533 0%,#4a1272 55%,#9b59b6 100%)"},
    "Snow":         {"icon": "❄️",  "color": "#cce4f0",
                     "gradient": "linear-gradient(135deg,#1e3a5f 0%,#2980b9 55%,#cce4f0 100%)"},
    "Mist":         {"icon": "🌫️", "color": "#adb5bd",
                     "gradient": "linear-gradient(135deg,#3d4852 0%,#636e72 55%,#adb5bd 100%)"},
    "Fog":          {"icon": "🌁",  "color": "#adb5bd",
                     "gradient": "linear-gradient(135deg,#3d4852 0%,#636e72 55%,#adb5bd 100%)"},
    "Haze":         {"icon": "🌤️", "color": "#fdcb6e",
                     "gradient": "linear-gradient(135deg,#7d4f00 0%,#c98a00 55%,#fdcb6e 100%)"},
}
_DEFAULT_META = {
    "icon": "🌡️", "color": "#4facfe",
    "gradient": "linear-gradient(135deg,#0d1117 0%,#1a3a6c 55%,#4facfe 100%)",
}

def get_meta(condition: str) -> dict:
    return _CONDITION_META.get(condition, _DEFAULT_META)

def wind_dir_label(deg: float) -> str:
    dirs = ["N","NNE","NE","ENE","E","ESE","SE","SSE",
            "S","SSW","SW","WSW","W","WNW","NW","NNW"]
    return dirs[round(deg / 22.5) % 16]

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* === BASE === */
html, body, [class*="css"] { font-family: 'Inter','Segoe UI',system-ui,sans-serif; }
.main .block-container { padding-top: 1rem; padding-bottom: 2rem; max-width: 1280px; }
#MainMenu, footer { visibility: hidden; }

/* === SIDEBAR === */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg,#0d1117 0%,#12192b 100%) !important;
    border-right: 1px solid rgba(255,255,255,0.06);
}
[data-testid="stSidebar"] > div:first-child { padding: 1.25rem 1rem 2rem; }

/* === HERO CARD === */
.weather-hero {
    border-radius: 24px;
    padding: 2rem 2.5rem 1.75rem;
    margin-bottom: 1.25rem;
    position: relative;
    overflow: hidden;
    box-shadow: 0 24px 80px rgba(0,0,0,0.55);
}
.weather-hero::after {
    content: '';
    position: absolute;
    inset: 0;
    background: rgba(0,0,0,0.12);
    border-radius: inherit;
    pointer-events: none;
}
.hero-content {
    position: relative; z-index: 1;
    display: flex; align-items: flex-start;
    justify-content: space-between; flex-wrap: wrap; gap: 1rem;
}
.hero-left .hero-city {
    font-size: 1rem; font-weight: 600;
    text-transform: uppercase; letter-spacing: 0.12em;
    color: rgba(255,255,255,0.78); margin: 0 0 0.2rem;
}
.hero-left h1 {
    font-size: 4.6rem; font-weight: 800;
    line-height: 1; margin: 0; color: #fff; letter-spacing: -2px;
}
.hero-left .hero-desc {
    font-size: 1.05rem; color: rgba(255,255,255,0.82);
    text-transform: capitalize; margin-top: 0.3rem;
}
.hero-right { text-align: right; }
.hero-icon {
    font-size: 7rem; line-height: 1;
    filter: drop-shadow(0 6px 20px rgba(0,0,0,0.45));
    display: block;
}
.hero-country {
    font-size: 0.78rem; font-weight: 600;
    color: rgba(255,255,255,0.6);
    text-transform: uppercase; letter-spacing: 0.1em;
    margin-top: 0.5rem;
}
.stat-pills { display: flex; flex-wrap: wrap; gap: 0.55rem; margin-top: 1.4rem; }
.stat-pill {
    background: rgba(255,255,255,0.16);
    backdrop-filter: blur(10px);
    border-radius: 50px;
    padding: 0.38rem 0.9rem;
    font-size: 0.82rem; font-weight: 500;
    color: rgba(255,255,255,0.95);
    white-space: nowrap;
    display: inline-flex; align-items: center; gap: 0.3rem;
    border: 1px solid rgba(255,255,255,0.12);
}

/* === SECTION HEADING === */
.section-heading {
    font-size: 0.68rem; font-weight: 700;
    text-transform: uppercase; letter-spacing: 0.12em;
    color: #8b949e; margin: 0 0 0.7rem;
}

/* === ALERT ITEMS === */
.alert-box {
    border-radius: 12px; padding: 0.55rem 0.9rem;
    margin-bottom: 0.45rem;
    display: flex; align-items: center; gap: 0.45rem;
    font-size: 0.83rem; font-weight: 500;
}
.alert-critical { background: rgba(255,82,82,0.15);  border-left: 3px solid #ff5252; color: #ff8a80; }
.alert-warning  { background: rgba(255,171,0,0.13);  border-left: 3px solid #ffab00; color: #ffe082; }
.alert-info     { background: rgba(79,172,254,0.12); border-left: 3px solid #4facfe; color: #82cfff; }
.alert-ok       { background: rgba(0,230,118,0.10);  border-left: 3px solid #00e676; color: #69f0ae; }

/* === MINI STATS (sidebar) === */
.mini-stats { display: flex; flex-direction: column; gap: 0.45rem; }
.mini-stat {
    display: flex; justify-content: space-between; align-items: center;
    padding: 0.45rem 0.7rem;
    background: rgba(255,255,255,0.05); border-radius: 10px;
}
.mini-stat .ms-label { font-size: 0.76rem; color: #8b949e; }
.mini-stat .ms-value { font-size: 0.88rem; font-weight: 600; color: #e6edf3; }

/* === CITY RANKINGS === */
.rank-item {
    display: flex; justify-content: space-between; align-items: center;
    padding: 0.42rem 0;
    border-bottom: 1px solid rgba(255,255,255,0.05);
}
.rank-item:last-child { border-bottom: none; }
.rank-item .ri-city { font-size: 0.83rem; color: #c9d1d9; }
.rank-item .ri-val  { font-size: 0.86rem; font-weight: 600; }

/* === STREAMLIT OVERRIDES === */
[data-testid="stMetric"] {
    background: rgba(255,255,255,0.04) !important;
    border-radius: 14px !important;
    padding: 0.85rem 1rem !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
}
.stTabs [data-baseweb="tab-list"] {
    background: rgba(255,255,255,0.04);
    border-radius: 12px; padding: 3px; gap: 2px; border-bottom: none;
}
.stTabs [data-baseweb="tab"] {
    background: transparent; border-radius: 9px;
    color: #8b949e; font-size: 0.83rem; font-weight: 500;
    padding: 5px 14px; border: none;
}
.stTabs [aria-selected="true"] {
    background: #4facfe !important;
    color: #0d1117 !important; font-weight: 700 !important;
}
.stButton > button {
    background: linear-gradient(135deg,#4facfe,#00f2fe);
    color: #0d1117; border: none; border-radius: 10px;
    font-weight: 600; font-size: 0.85rem; width: 100%;
    transition: opacity .2s, transform .1s;
}
.stButton > button:hover { opacity: .88; transform: translateY(-1px); }
div[data-testid="stDataFrame"] { border-radius: 12px; overflow: hidden; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⛅ Weather Intelligence")
    st.markdown(
        '<p style="color:#8b949e;font-size:0.79rem;margin-top:-0.6rem;margin-bottom:1rem;">'
        "Real-time global analytics</p>",
        unsafe_allow_html=True,
    )

    cities = collector.get_cities_list()
    selected_city = st.selectbox("🏙️ City", cities, index=0)

    unit_choice = st.radio("🌡️ Units", ["°C", "°F"], horizontal=True)
    st.session_state.unit = "F" if unit_choice == "°F" else "C"

    st.markdown("---")

    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("🔄 Refresh"):
            collector.cache.clear()
            st.rerun()
    with col_b:
        auto_refresh = st.checkbox("Auto 30s", value=False)

    st.markdown("---")

    # Placeholders — filled after we fetch data
    alerts_placeholder = st.empty()

    st.markdown("---")
    stats_placeholder = st.empty()

    st.markdown("---")
    with st.expander("ℹ️ About", expanded=False):
        st.markdown(
            "**Data**: OpenWeatherMap API  \n"
            "**Cache**: 10-minute refresh  \n"
            "**Coverage**: 15 global cities  \n\n"
            "*No API key? Realistic mock data is used automatically.*"
        )


# ─────────────────────────────────────────────────────────────────────────────
# FETCH DATA
# ─────────────────────────────────────────────────────────────────────────────
with st.spinner(f"Loading weather for {selected_city}…"):
    current_weather = collector.get_current_weather(selected_city)

with st.spinner("Loading forecast…"):
    forecast_data = collector.get_forecast(selected_city, days=5)

with st.spinner("Loading global data…"):
    global_weather: dict = {}
    for city in collector.get_cities_list():
        data = collector.get_current_weather(city)
        if data:
            coords = collector.get_city_coordinates(city)
            global_weather[city] = {**data, **coords}


# ─────────────────────────────────────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(
    f'<p style="color:#484f58;font-size:0.78rem;text-align:right;margin-bottom:0.5rem;">'
    f'Updated {datetime.now().strftime("%B %d, %Y · %H:%M")}</p>',
    unsafe_allow_html=True,
)


# ─────────────────────────────────────────────────────────────────────────────
# HERO CARD
# ─────────────────────────────────────────────────────────────────────────────
if current_weather:
    meta = get_meta(current_weather["weather_main"])
    wdir = wind_dir_label(current_weather.get("wind_direction", 0))
    st.markdown(
        f"""
        <div class="weather-hero" style="background:{meta['gradient']};">
          <div class="hero-content">
            <div class="hero-left">
              <p class="hero-city">📍 {selected_city}</p>
              <h1>{fmt_temp(current_weather["temperature"])}</h1>
              <p class="hero-desc">{current_weather["weather_description"].title()}</p>
              <div class="stat-pills">
                <span class="stat-pill">🤔 Feels {fmt_temp(current_weather["feels_like"])}</span>
                <span class="stat-pill">💧 {current_weather["humidity"]}% humidity</span>
                <span class="stat-pill">💨 {current_weather["wind_speed"]:.1f} m/s {wdir}</span>
                <span class="stat-pill">👁️ {current_weather["visibility"]:.0f} km vis.</span>
                <span class="stat-pill">🔵 {current_weather["pressure"]} hPa</span>
                <span class="stat-pill">☁️ {current_weather["cloudiness"]}% cloud</span>
              </div>
            </div>
            <div class="hero-right">
              <span class="hero-icon">{meta['icon']}</span>
              <p class="hero-country">🌍 {current_weather.get("country", "")}</p>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.expander("🔍 More details"):
        dc1, dc2, dc3 = st.columns(3)
        with dc1:
            st.metric("🌅 Sunrise", current_weather["sunrise"].strftime("%H:%M"))
        with dc2:
            st.metric("🌇 Sunset", current_weather["sunset"].strftime("%H:%M"))
        with dc3:
            st.metric(
                "🧭 Wind Dir",
                f"{wdir} ({current_weather.get('wind_direction', 0):.0f}°)",
            )
else:
    st.error("⚠️ Could not load weather data. Please refresh or check your connection.")


# ─────────────────────────────────────────────────────────────────────────────
# FORECAST
# ─────────────────────────────────────────────────────────────────────────────
if forecast_data:
    st.markdown('<p class="section-heading">📅 5-Day Forecast</p>', unsafe_allow_html=True)

    df = pd.DataFrame(forecast_data)
    df["date"] = pd.to_datetime(df["datetime"])
    df["temp_d"] = df["temperature"].apply(display_temp)
    df["feels_d"] = df["feels_like"].apply(display_temp)

    _chart_layout = dict(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20, r=20, t=30, b=20),
        legend=dict(
            bgcolor="rgba(0,0,0,0.3)",
            bordercolor="rgba(255,255,255,0.1)",
            borderwidth=1,
        ),
        xaxis=dict(gridcolor="rgba(255,255,255,0.05)", showgrid=True),
        yaxis=dict(gridcolor="rgba(255,255,255,0.05)", showgrid=True),
    )

    tab_temp, tab_precip, tab_wind = st.tabs(
        ["🌡️ Temperature", "💧 Humidity & Rain", "💨 Wind Speed"]
    )

    with tab_temp:
        fig_t = go.Figure()
        fig_t.add_trace(go.Scatter(
            x=df["date"], y=df["temp_d"],
            mode="lines", name=f"Temperature ({temp_unit()})",
            line=dict(color="#4facfe", width=2.5, shape="spline"),
            fill="tozeroy", fillcolor="rgba(79,172,254,0.10)",
        ))
        fig_t.add_trace(go.Scatter(
            x=df["date"], y=df["feels_d"],
            mode="lines", name=f"Feels Like ({temp_unit()})",
            line=dict(color="#f093fb", width=1.8, dash="dot", shape="spline"),
        ))
        fig_t.update_layout(
            height=320,
            yaxis_title=f"Temperature ({temp_unit()})",
            **_chart_layout,
        )
        st.plotly_chart(fig_t, use_container_width=True)

    with tab_precip:
        fig_p = go.Figure()
        fig_p.add_trace(go.Bar(
            x=df["date"], y=df["precipitation_prob"],
            name="Rain Chance (%)",
            marker_color="rgba(79,172,254,0.65)",
            marker_line_color="#4facfe", marker_line_width=1,
        ))
        fig_p.add_trace(go.Scatter(
            x=df["date"], y=df["humidity"],
            mode="lines", name="Humidity (%)",
            line=dict(color="#00f2fe", width=2, shape="spline"),
            yaxis="y2",
        ))
        fig_p.update_layout(
            height=320,
            yaxis=dict(
                title="Precipitation Probability (%)", range=[0, 100],
                gridcolor="rgba(255,255,255,0.05)",
            ),
            yaxis2=dict(
                title="Humidity (%)", overlaying="y", side="right",
                range=[0, 100], gridcolor="rgba(0,0,0,0)",
            ),
            **{k: v for k, v in _chart_layout.items() if k != "yaxis"},
        )
        st.plotly_chart(fig_p, use_container_width=True)

    with tab_wind:
        fig_w = go.Figure()
        fig_w.add_trace(go.Scatter(
            x=df["date"], y=df["wind_speed"],
            mode="lines", name="Wind Speed (m/s)",
            line=dict(color="#43e97b", width=2.5, shape="spline"),
            fill="tozeroy", fillcolor="rgba(67,233,123,0.10)",
        ))
        fig_w.update_layout(
            height=320,
            yaxis_title="Wind Speed (m/s)",
            **_chart_layout,
        )
        st.plotly_chart(fig_w, use_container_width=True)

    with st.expander("📋 Daily Summary Table"):
        df["day"] = df["date"].dt.date
        daily = df.groupby("day").agg(
            min_temp=("temp_d", "min"),
            max_temp=("temp_d", "max"),
            avg_humidity=("humidity", "mean"),
            max_rain=("precipitation_prob", "max"),
            avg_wind=("wind_speed", "mean"),
            condition=("weather_main",
                       lambda x: x.value_counts().index[0] if not x.value_counts().empty else "Unknown"),
        ).round(1)
        daily.index = [f"{d.strftime('%A, %b')} {d.day}" for d in daily.index]
        daily.columns = [
            f"Min ({temp_unit()})", f"Max ({temp_unit()})",
            "Humidity (%)", "Rain Chance (%)", "Wind (m/s)", "Condition",
        ]
        st.dataframe(daily, use_container_width=True)


# ─────────────────────────────────────────────────────────────────────────────
# GLOBAL MAP
# ─────────────────────────────────────────────────────────────────────────────
if global_weather:
    st.markdown(
        '<p class="section-heading" style="margin-top:1.5rem;">🗺️ Global Temperature Map</p>',
        unsafe_allow_html=True,
    )

    map_rows = [
        {
            "city": city,
            "lat": d["lat"],
            "lon": d["lon"],
            "temp_display": round(display_temp(d["temperature"]), 1),
            "humidity": d["humidity"],
            "condition": d["weather_main"],
            "marker_size": 14,
        }
        for city, d in global_weather.items()
    ]
    df_map = pd.DataFrame(map_rows)
    selected_coords = collector.get_city_coordinates(selected_city)

    fig_map = px.scatter_map(
        df_map,
        lat="lat", lon="lon",
        color="temp_display",
        size="marker_size", size_max=14,
        hover_name="city",
        hover_data={
            "temp_display": True, "humidity": True, "condition": True,
            "lat": False, "lon": False, "marker_size": False,
        },
        color_continuous_scale="Turbo",
        zoom=1.5,
        center={"lat": selected_coords["lat"], "lon": selected_coords["lon"]},
        labels={"temp_display": f"Temp ({temp_unit()})"},
    )
    fig_map.update_layout(
        map_style="carto-darkmatter",
        height=440,
        paper_bgcolor="rgba(0,0,0,0)",
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        coloraxis_colorbar=dict(
            bgcolor="rgba(22,27,43,0.85)",
            bordercolor="rgba(255,255,255,0.1)",
            tickfont=dict(color="#e6edf3"),
            title=dict(text=f"Temp ({temp_unit()})", font=dict(color="#8b949e")),
        ),
    )
    st.plotly_chart(fig_map, use_container_width=True)


# ─────────────────────────────────────────────────────────────────────────────
# CITY RANKINGS
# ─────────────────────────────────────────────────────────────────────────────
if global_weather:
    st.markdown(
        '<p class="section-heading" style="margin-top:1.5rem;">🏆 City Rankings</p>',
        unsafe_allow_html=True,
    )

    by_temp = sorted(global_weather.items(), key=lambda x: x[1]["temperature"])
    by_hum = sorted(global_weather.items(), key=lambda x: x[1]["humidity"], reverse=True)

    def _rank_html(items: list, value_fn, color: str) -> str:
        html = ""
        for city, data in items:
            val = value_fn(data)
            html += (
                f'<div class="rank-item">'
                f'<span class="ri-city">{city}</span>'
                f'<span class="ri-val" style="color:{color}">{val}</span>'
                f'</div>'
            )
        return html

    rc1, rc2, rc3 = st.columns(3)
    with rc1:
        st.markdown('<p class="section-heading">🔥 Hottest</p>', unsafe_allow_html=True)
        st.markdown(
            _rank_html(by_temp[-5:][::-1], lambda d: fmt_temp(d["temperature"]), "#ff6b6b"),
            unsafe_allow_html=True,
        )
    with rc2:
        st.markdown('<p class="section-heading">❄️ Coldest</p>', unsafe_allow_html=True)
        st.markdown(
            _rank_html(by_temp[:5], lambda d: fmt_temp(d["temperature"]), "#74b9ff"),
            unsafe_allow_html=True,
        )
    with rc3:
        st.markdown('<p class="section-heading">💧 Most Humid</p>', unsafe_allow_html=True)
        st.markdown(
            _rank_html(by_hum[:5], lambda d: f"{d['humidity']}%", "#00cec9"),
            unsafe_allow_html=True,
        )


# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR: ALERTS
# ─────────────────────────────────────────────────────────────────────────────
with alerts_placeholder.container():
    st.markdown('<p class="section-heading">⚠️ Alerts</p>', unsafe_allow_html=True)
    if current_weather:
        temp  = current_weather["temperature"]
        wind  = current_weather["wind_speed"]
        hum   = current_weather["humidity"]
        vis   = current_weather["visibility"]

        alerts_html = ""
        if temp > 38:
            alerts_html += '<div class="alert-box alert-critical">🔥 Extreme heat!</div>'
        elif temp > 33:
            alerts_html += '<div class="alert-box alert-warning">☀️ Heat advisory</div>'
        if temp < -10:
            alerts_html += '<div class="alert-box alert-critical">❄️ Extreme cold!</div>'
        elif temp < 0:
            alerts_html += '<div class="alert-box alert-warning">🌨️ Freeze warning</div>'
        if wind > 15:
            alerts_html += '<div class="alert-box alert-critical">💨 Dangerous winds!</div>'
        elif wind > 10:
            alerts_html += '<div class="alert-box alert-warning">💨 Wind advisory</div>'
        if hum > 90:
            alerts_html += '<div class="alert-box alert-info">💧 Very high humidity</div>'
        if vis < 2:
            alerts_html += '<div class="alert-box alert-warning">🌫️ Very low visibility</div>'
        elif vis < 5:
            alerts_html += '<div class="alert-box alert-info">🌫️ Reduced visibility</div>'

        if not alerts_html:
            alerts_html = '<div class="alert-box alert-ok">✅ All clear</div>'
        st.markdown(alerts_html, unsafe_allow_html=True)
    else:
        st.markdown(
            '<div class="alert-box alert-info">⚡ No data</div>',
            unsafe_allow_html=True,
        )


# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR: GLOBAL STATS
# ─────────────────────────────────────────────────────────────────────────────
with stats_placeholder.container():
    st.markdown('<p class="section-heading">📊 Global Stats</p>', unsafe_allow_html=True)
    if global_weather:
        all_temps  = [d["temperature"] for d in global_weather.values()]
        all_hums   = [d["humidity"]    for d in global_weather.values()]
        all_winds  = [d["wind_speed"]  for d in global_weather.values()]
        st.markdown(
            f"""
            <div class="mini-stats">
              <div class="mini-stat">
                <span class="ms-label">🌡️ Avg temp</span>
                <span class="ms-value">{fmt_temp(float(np.mean(all_temps)))}</span>
              </div>
              <div class="mini-stat">
                <span class="ms-label">💧 Avg humidity</span>
                <span class="ms-value">{np.mean(all_hums):.0f}%</span>
              </div>
              <div class="mini-stat">
                <span class="ms-label">💨 Avg wind</span>
                <span class="ms-value">{np.mean(all_winds):.1f} m/s</span>
              </div>
              <div class="mini-stat">
                <span class="ms-label">🏙️ Cities</span>
                <span class="ms-value">{len(global_weather)}</span>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ─────────────────────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    '<div style="text-align:center;color:#484f58;font-size:0.77rem;padding:0.4rem 0;">'
    '⛅ <strong style="color:#6e7681;">Weather Intelligence</strong> &nbsp;·&nbsp; '
    "Built with Streamlit &amp; OpenWeatherMap &nbsp;·&nbsp; "
    "15 global cities monitored in real-time"
    "</div>",
    unsafe_allow_html=True,
)


# ─────────────────────────────────────────────────────────────────────────────
# AUTO-REFRESH
# ─────────────────────────────────────────────────────────────────────────────
if auto_refresh:
    time.sleep(30)
    st.rerun()
