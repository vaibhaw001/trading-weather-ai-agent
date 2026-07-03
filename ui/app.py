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
        trades = pd.read_sql_query("SELECT city_name as City, timestamp as Date, side as Side, size as Shares, price as 'Avg Price', status as Status, pnl as PnL FROM trades ORDER BY timestamp DESC", conn)
        history = pd.read_sql_query("SELECT timestamp as Date, city_name as City, event_predicted as Prediction, probability as Probability, confidence as Confidence FROM predictions ORDER BY timestamp DESC", conn)
        conn.close()
        return trades, history
    except Exception as e:
        return pd.DataFrame(), pd.DataFrame()

trades_df, history_df = load_db_data()

if not trades_df.empty:
    open_positions_df = trades_df[trades_df['Status'] == 'OPEN'].copy()
    closed_positions_df = trades_df[trades_df['Status'] != 'OPEN'].copy()
else:
    open_positions_df = pd.DataFrame(columns=["City", "Date", "Side", "Shares", "Avg Price", "Status", "PnL"])
    closed_positions_df = pd.DataFrame(columns=["City", "Date", "Side", "Shares", "Avg Price", "Status", "PnL"])

if not closed_positions_df.empty:
    total_closed = len(closed_positions_df)
    winning_trades = len(closed_positions_df[closed_positions_df['Status'] == 'CLOSED_WIN'])
    win_rate = (winning_trades / total_closed) * 100
    total_pnl = closed_positions_df['PnL'].sum()
    roi = (total_pnl / settings.STARTING_BANKROLL) * 100
    
    win_rate_str = f"{win_rate:.1f}%"
    roi_str = f"{roi:.2f}%"
    roi_delta = f"+${total_pnl:.2f}" if total_pnl >= 0 else f"-${abs(total_pnl):.2f}"
    win_rate_delta = f"{total_closed} Settled"
else:
    win_rate_str = "N/A"
    roi_str = "N/A"
    roi_delta = "Pending Resolution"
    win_rate_delta = "Pending Resolution"

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Current Bankroll", f"${settings.STARTING_BANKROLL + (total_pnl if not closed_positions_df.empty else 0):.2f}", "+$0.00")
with col2:
    st.metric("Active Risk (Exposure)", f"${len(open_positions_df) * 10 if not open_positions_df.empty else 0}", f"{len(open_positions_df)} Open Trades", delta_color="inverse")
with col3:
    st.metric("Historical Win Rate", win_rate_str, win_rate_delta)
with col4:
    st.metric("Total ROI", roi_str, roi_delta)

st.markdown("---")

# --- OPEN POSITIONS ---
st.subheader("Active Positions (Paper Trading)")

if open_positions_df.empty:
    st.info("No active positions found in database. Run the daemon to execute trades.")
else:
    # Hide the extra columns for active display to keep it clean
    display_df = open_positions_df.drop(columns=["Status", "PnL"])
    st.dataframe(display_df, use_container_width=True, hide_index=True)

# --- MANUAL HEDGING ---
st.subheader("Manual Interventions & Hedging")
st.write("Use this panel to manually hedge or close positions if the AI's risk parameters fail or market conditions change drastically.")

hedge_col1, hedge_col2 = st.columns([3, 1])
with hedge_col1:
    hedge_city = st.selectbox("Select Position to Hedge / Close", open_positions_df["City"].tolist() if not open_positions_df.empty else ["No Positions"])
with hedge_col2:
    st.write("")
    st.write("")
    if st.button("Execute Reverse Hedge", type="primary"):
        if hedge_city != "No Positions":
            try:
                db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), settings.DATABASE_PATH.replace("sqlite:///", ""))
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM trades WHERE city_name = ?", (hedge_city,))
                conn.commit()
                conn.close()
                st.success(f"Manual Hedge executed for {hedge_city}. Position has been closed.")
                st.rerun()
            except Exception as e:
                st.error(f"Failed to close position: {e}")
        else:
            st.warning("No position selected to hedge.")

st.markdown("---")

# --- SETTLED TRADES ---
st.subheader("Settled Trades (History)")

if closed_positions_df.empty:
    st.info("No trades have been resolved yet.")
else:
    def color_status(val):
        color = 'green' if 'WIN' in val else 'red'
        return f'color: {color}'

    styled_closed = closed_positions_df.style.map(color_status, subset=['Status'])
    st.dataframe(styled_closed, use_container_width=True, hide_index=True)

st.markdown("---")

# --- PREDICTION HISTORY ---
st.subheader("AI Prediction History (Model Evaluation)")

if history_df.empty:
    st.info("No predictions found in database. Run the daemon to generate predictions.")
else:
    st.dataframe(history_df, use_container_width=True, hide_index=True)
