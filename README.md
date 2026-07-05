# 🌦️ Polymarket Weather Trading AI Agent

An autonomous multi-agent quantitative trading system that predicts global weather events and executes simulated paper trades on Polymarket.

## 🌟 Overview

The Polymarket Weather Trading AI Agent is a sophisticated algorithmic trading bot designed to analyze meteorological data and trade weather-related contracts on Polymarket. It utilizes a multi-agent architecture where specialized AI agents handle different stages of the trading pipeline, from data acquisition and analysis to risk management and trade execution.

## 🏗️ Architecture & Working

The system is fully decoupled into a **FastAPI Backend** and a **Streamlit Dashboard**, powered by a robust multi-agent pipeline and a local SQLite database (SQLAlchemy). 

The core working mechanism is a sequential pipeline of specialized agents:

1. **Data Ingestion (`agents/research_agent.py`)**: 
   - **Functionality**: Connects to external APIs like Apify and Open-Meteo.
   - **Working**: Scrapes global and localized weather data concurrently. It gathers historical data, current conditions, and forecasts relevant to active Polymarket weather markets.

2. **Reasoning Engine (`agents/prediction_agent.py`)**: 
   - **Functionality**: Acts as the quantitative forecaster.
   - **Working**: Passes the structured weather data into an OpenRouter LLM (optimized for `meta-llama/llama-3.2-3b-instruct:free`). The LLM analyzes the data against market conditions to output precise win probabilities, confidence scores, and detailed, logical reasoning for its predictions.

3. **Risk Management (`agents/risk_agent.py`)**: 
   - **Functionality**: Determines optimal capital allocation.
   - **Working**: Implements the mathematical **Kelly Criterion** against current Polymarket odds. It calculates the exact fraction of the portfolio to risk on a given trade to maximize long-term growth while capping maximum exposure to prevent ruin.

4. **Execution & Alerts (`agents/trading_agent.py`)**: 
   - **Functionality**: Handles order execution and notifications.
   - **Working**: Executes simulated paper trades based on the Risk Agent's sizing. It logs the trades in the database and pushes live, HTML-formatted Telegram notifications to your mobile device instantly.

5. **Data Persistence (`database/models.py`)**: 
   - **Functionality**: Robust local storage.
   - **Working**: A local SQLite database (`weather_agent.db`) persists all predictions, market odds, executed orders, and portfolio history across cycles, allowing for performance tracking over time.

6. **Frontend UI (`ui/streamlit_app.py`)**: 
   - **Functionality**: Interactive analytics and control panel.
   - **Working**: Provides a glassmorphism-themed dark mode dashboard to monitor active risk, view the AI's reasoning, track portfolio PnL (Profit and Loss), and manually execute agent cycles.

## ⚙️ Key Functionalities

- **Autonomous Agent Cycles**: Trigger a full end-to-end cycle (Research -> Predict -> Risk -> Trade) with a single click.
- **Real-time Cycle Monitoring**: Background task progress is tracked in real-time with an active UI loading state, automatically refreshing the dashboard upon completion.
- **Paper Trading Portfolio**: Completely simulated trading environment to test the AI's efficacy without risking real capital.
- **Database Reset**: Easily wipe your paper trading portfolio and prediction history to start fresh via the `🔄 Reset Data` button on the dashboard.
- **Latest Results Spotlight**: The most recent prediction and its detailed logical reasoning are pinned to the top of the dashboard for quick visibility.
- **Robust LLM Integration**: Uses `meta-llama/llama-3.2-3b-instruct:free` via OpenRouter to ensure stable JSON generation and reliable API uptime.

## 🚀 Getting Started

### 1. Installation

Clone the repository and install the required dependencies:

```bash
git clone https://github.com/vaibhaw001/trading-weather-ai-agent.git
cd trading-weather-ai-agent
pip install -r requirements.txt
```

### 2. Configuration & API Keys

You can enter your API keys directly into the **Control Panel** in the Streamlit UI, which will securely save them to your local `.env` file. You will need:
- **OpenRouter API Key**: For free LLM inference.
- **Apify API Token**: For web scraping Polymarket and weather sources.
- **Telegram Bot Token & Chat ID**: (Optional) For receiving real-time mobile trade alerts.

### 3. Usage & Running the Application

The system requires running the Backend API and the Frontend UI concurrently in two separate terminal windows.

**Terminal 1: Start the Core FastAPI Backend**
```bash
python api/main.py
```
*This starts the backend server that manages the database and coordinates the AI agents.*

**Terminal 2: Launch the Analytics Dashboard**
```bash
streamlit run ui/streamlit_app.py
```
*This launches the interactive web interface.*

### 4. Interacting with the UI

1. Open `http://localhost:8501` in your browser.
2. **Setup**: If it's your first time, input your API keys in the sidebar Control Panel.
3. **Execution**: Click **"Run Agent Cycle"** from the sidebar to trigger a full pipeline execution. 
4. **Monitoring**: The UI will pause and display a loading state while the AI completes its research, prediction, and trading logic. Once finished, the dashboard will refresh to show you the new PnL, the latest prediction, and the agent's rationale.
5. **Resetting**: To clear your trading history and start over, use the **"🔄 Reset Data"** button at the top right of the Main Dashboard.
