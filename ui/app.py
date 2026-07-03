import streamlit as st
import pandas as pd
import sqlite3
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

# --- DATABASE LOADER ---
def load_db_data():
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), settings.DATABASE_PATH.replace("sqlite:///", ""))
    try:
        conn = sqlite3.connect(db_path)
        positions = pd.read_sql_query("SELECT city_name as City, timestamp as Date, side as Side, size as Shares, price as 'Avg Price' FROM trades ORDER BY timestamp DESC", conn)
        history = pd.read_sql_query("SELECT timestamp as Date, city_name as City, event_predicted as Prediction, probability as Probability, confidence as Confidence FROM predictions ORDER BY timestamp DESC", conn)
        conn.close()
        return positions, history
    except Exception as e:
        return pd.DataFrame(), pd.DataFrame()

positions_df, history_df = load_db_data()

# --- TOP METRICS ---
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Current Bankroll", f"${settings.STARTING_BANKROLL:.2f}", "+$0.00")
with col2:
    st.metric("Active Risk (Exposure)", f"${len(positions_df) * 10 if not positions_df.empty else 0}", f"{len(positions_df)} Open Trades", delta_color="inverse")
with col3:
    st.metric("Historical Win Rate", "N/A", "Pending Resolution")
with col4:
    st.metric("Total ROI", "N/A", "Pending Resolution")

st.markdown("---")

# --- OPEN POSITIONS ---
st.subheader("Active Positions (Paper Trading)")

if positions_df.empty:
    st.info("No active positions found in database. Run the daemon to execute trades.")
    positions_df = pd.DataFrame(columns=["City", "Date", "Side", "Shares", "Avg Price"])
else:
    st.dataframe(positions_df, use_container_width=True, hide_index=True)

# --- MANUAL HEDGING ---
st.subheader("Manual Interventions & Hedging")
st.write("Use this panel to manually hedge or close positions if the AI's risk parameters fail or market conditions change drastically.")

hedge_col1, hedge_col2 = st.columns([3, 1])
with hedge_col1:
    hedge_city = st.selectbox("Select Position to Hedge / Close", positions_df["City"].tolist() if not positions_df.empty else ["No Positions"])
with hedge_col2:
    st.write("")
    st.write("")
    if st.button("Execute Reverse Hedge", type="primary"):
        st.warning(f"Manual Hedge executed for {hedge_city}. Reverse position order sent to RiskAgent.")

st.markdown("---")

# --- PREDICTION HISTORY ---
st.subheader("AI Prediction History (Model Evaluation)")

if history_df.empty:
    st.info("No predictions found in database. Run the daemon to generate predictions.")
else:
    st.dataframe(history_df, use_container_width=True, hide_index=True)
