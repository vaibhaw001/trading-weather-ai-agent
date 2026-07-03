import streamlit as st
import pandas as pd
import sys
import os

# Ensure the root project directory is in the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import settings

# Page configuration
st.set_page_config(page_title="Weather Agent Dashboard", page_icon="🌦️", layout="wide")

st.title("🌦️ Polymarket Weather Trading AI")
st.markdown("Real-time monitoring dashboard for the autonomous quantitative trading agent.")

# --- SIDEBAR ---
st.sidebar.header("Risk Parameters")
st.sidebar.write(f"**Starting Bankroll:** ${settings.STARTING_BANKROLL:.2f}")
st.sidebar.write(f"**Max Loss (Daily):** ${settings.MAX_DAILY_LOSS:.2f}")
st.sidebar.write(f"**Max Exposure Limit:** {settings.MAX_EXPOSURE_PER_TRADE * 100}%")

if st.sidebar.button("Force Agent Cycle"):
    st.sidebar.success("Daemon cycle triggered! (Check terminal for logs)")

# --- TOP METRICS ---
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Current Bankroll", f"${settings.STARTING_BANKROLL:.2f}", "+$0.00")
with col2:
    st.metric("Active Risk (Exposure)", "$150.00", "2 Open Trades", delta_color="inverse")
with col3:
    st.metric("Historical Win Rate", "68.5%", "+2.1%")
with col4:
    st.metric("Total ROI", "15.2%", "+1.0%")

st.markdown("---")

# --- OPEN POSITIONS ---
st.subheader("Active Positions (Paper Trading)")

# In a production setting, this would be fetched from SQLite via the database/ module
mock_positions = pd.DataFrame([
    {"Date": "2023-11-01 08:30", "City": "London", "Side": "BUY_YES", "Shares": 250, "Avg Price": "$0.40", "Total Stake": "$100.00", "Current Odds": "$0.45", "Unrealized PnL": "+$12.50"},
    {"Date": "2023-11-01 09:15", "City": "New York", "Side": "BUY_NO", "Shares": 500, "Avg Price": "$0.10", "Total Stake": "$50.00", "Current Odds": "$0.08", "Unrealized PnL": "-$10.00"}
])

st.dataframe(mock_positions, use_container_width=True, hide_index=True)

# --- MANUAL HEDGING ---
st.subheader("Manual Interventions & Hedging")
st.write("Use this panel to manually hedge or close positions if the AI's risk parameters fail or market conditions change drastically.")

hedge_col1, hedge_col2 = st.columns([3, 1])
with hedge_col1:
    hedge_city = st.selectbox("Select Position to Hedge / Close", mock_positions["City"].tolist())
with hedge_col2:
    st.write("")
    st.write("")
    if st.button("Execute Reverse Hedge", type="primary"):
        st.warning(f"Manual Hedge executed for {hedge_city}. Reverse position order sent to RiskAgent.")

st.markdown("---")

# --- PREDICTION HISTORY ---
st.subheader("AI Prediction History (Model Evaluation)")
mock_history = pd.DataFrame([
    {"Date": "2023-10-25", "City": "Tokyo", "Prediction": "Rain", "Probability": "85%", "Confidence": "90%", "Actual": "Rain", "Result": "✅ WIN"},
    {"Date": "2023-10-26", "City": "Sydney", "Prediction": "No Rain", "Probability": "65%", "Confidence": "75%", "Actual": "Rain", "Result": "❌ LOSS"},
    {"Date": "2023-10-28", "City": "Miami", "Prediction": "Rain", "Probability": "55%", "Confidence": "40%", "Actual": "Rain", "Result": "✅ WIN"},
])

def color_result(val):
    color = 'green' if 'WIN' in val else 'red'
    return f'color: {color}'

styled_history = mock_history.style.map(color_result, subset=['Result'])
st.dataframe(styled_history, use_container_width=True, hide_index=True)
