import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import os

API_URL = "http://localhost:8000"

st.set_page_config(page_title="Weather Trading Dashboard", page_icon="🌦️", layout="wide")

st.markdown("""
    <style>
    /* Premium Glassmorphism Look */
    .stApp {
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
    }
    .stMetric {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 15px;
        border: 1px solid rgba(255,255,255,0.1);
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    .stButton>button {
        background: linear-gradient(90deg, #00F0FF, #0077FF);
        border: none;
        color: white;
        border-radius: 8px;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0, 240, 255, 0.3);
    }
    hr {
        border-color: rgba(0, 240, 255, 0.3) !important;
    }
    </style>
""", unsafe_allow_html=True)


st.sidebar.title("🌦️ Control Panel")
st.sidebar.markdown("---")
st.sidebar.header("Agent Controls")
if st.sidebar.button("Run Agent Cycle"):
    try:
        response = requests.post(f"{API_URL}/start-agent")
        st.sidebar.success(response.json().get("status", "Started"))
    except Exception as e:
        st.sidebar.error(f"API Error: {e}")

st.sidebar.header("API Credentials")
import dotenv
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
current_openrouter = os.getenv("OPENROUTER_API_KEY", "")
current_apify = os.getenv("APIFY_API_TOKEN", "")

openrouter_input = st.sidebar.text_input("OpenRouter API Key", value=current_openrouter, type="password")
apify_input = st.sidebar.text_input("Apify API Token", value=current_apify, type="password")

if st.sidebar.button("Save Keys"):
    if openrouter_input:
        dotenv.set_key(env_path, "OPENROUTER_API_KEY", openrouter_input)
        os.environ["OPENROUTER_API_KEY"] = openrouter_input
    if apify_input:
        dotenv.set_key(env_path, "APIFY_API_TOKEN", apify_input)
        os.environ["APIFY_API_TOKEN"] = apify_input
    st.sidebar.success("Keys saved successfully! Run the cycle to apply.")

st.sidebar.markdown("---")
st.sidebar.header("Configuration")
cities = st.sidebar.multiselect("Selected Cities", ["Delhi", "London", "New York", "Tokyo", "Paris", "Miami", "Sydney"], default=["Delhi", "London", "New York", "Tokyo", "Paris"])
prediction_type = st.sidebar.selectbox("Prediction Type", ["Rain", "Snow", "Temperature", "Wind", "Humidity"])
starting_cap = st.sidebar.number_input("Starting Capital", value=1000.0)
max_risk = st.sidebar.slider("Maximum Risk %", 1, 100, 10)
kelly_fraction = st.sidebar.slider("Kelly Fraction", 0.0, 1.0, 0.25)
paper_trading = st.sidebar.toggle("Paper Trading", value=True)
model = st.sidebar.selectbox("OpenRouter Model", ["mistralai/mistral-7b-instruct:free", "google/gemma-7b-it:free"])

def fetch_data(endpoint):
    try:
        res = requests.get(f"{API_URL}/{endpoint}")
        if res.status_code == 200:
            return res.json()
    except:
        pass
    return []

st.title("Main Dashboard")
portfolio = fetch_data("portfolio")
analytics = fetch_data("analytics")

col1, col2, col3, col4 = st.columns(4)
p_cap = portfolio.get("total_capital", starting_cap) if portfolio else starting_cap
col1.metric("Portfolio Value", f"${p_cap:.2f}")
col2.metric("Daily Profit", f"${p_cap - starting_cap:.2f}")

open_trades = len([t for t in fetch_data("orders") if t.get("status") == "OPEN"])
col3.metric("Open Trades", open_trades)

win_rate = analytics.get("win_rate", 0.0) if analytics else 0.0
col4.metric("Win Rate", f"{win_rate:.1f}%")

st.markdown("---")
st.subheader("Today's Predictions")
preds = fetch_data("predictions")
if preds:
    st.dataframe(pd.DataFrame(preds).drop(columns=["id", "reasoning", "timestamp"], errors='ignore'), use_container_width=True)
else:
    st.info("No predictions yet.")

st.markdown("---")
st.subheader("Research Data")
data = fetch_data("weather")
if data:
    research_list = []
    import json
    for item in data:
        city = item.get("city_name")
        try:
            city_data = json.loads(item.get("data")) if isinstance(item.get("data"), str) else item.get("data")
            current = city_data.get("global_forecast", {}).get("current", {})
            temp = current.get("temperature_2m", "N/A")
            precip = current.get("precipitation", "N/A")
            local_news = city_data.get("local_forecast", "N/A")
            
            # Truncate news so the table doesn't get huge
            news_str = str(local_news)
            if len(news_str) > 60:
                news_str = news_str[:60] + "..."
                
            research_list.append({
                "City": city,
                "Temp (°C)": temp,
                "Precip (mm)": precip,
                "Local Forecast": news_str
            })
        except Exception:
            research_list.append({"City": city, "Temp (°C)": "Err", "Precip (mm)": "Err", "Local Forecast": "Parse Error"})
    
    st.dataframe(pd.DataFrame(research_list), use_container_width=True, hide_index=True)
else:
    st.info("No research data.")

st.markdown("---")
st.subheader("Polymarket Odds")
markets = fetch_data("markets")
if markets:
    st.dataframe(pd.DataFrame(markets), use_container_width=True)
else:
    st.info("No market data.")

st.markdown("---")
st.subheader("Trade History")
orders = fetch_data("orders")
if orders:
    df = pd.DataFrame(orders)
    st.dataframe(df, use_container_width=True)
else:
    st.info("No trades executed.")

st.markdown("---")
st.subheader("Risk Management & Exposure")
st.write(f"Using Kelly Criterion fraction: **{kelly_fraction}** | Max Risk per trade: **{max_risk}%**")
if orders:
    df = pd.DataFrame(orders)
    fig = px.bar(df, x="city_name", y="size", title="Exposure by City", color="side", color_discrete_sequence=["#00F0FF", "#0077FF"])
    fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="#F8FAFC")
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.subheader("Analytics & Performance")
if analytics:
    col_a1, col_a2, col_a3, col_a4 = st.columns(4)
    col_a1.metric("Sharpe Ratio", f"{analytics.get('sharpe_ratio', 0.0):.2f}")
    col_a2.metric("Win Rate", f"{analytics.get('win_rate', 0.0):.1f}%")
    col_a3.metric("ROI", f"{analytics.get('roi', 0.0):.2f}%")
    col_a4.metric("Max Drawdown", f"{analytics.get('drawdown', 0.0):.2f}%")
    st.caption(f"Last updated: {analytics.get('timestamp', 'N/A')}")
else:
    st.info("No analytics data yet.")
