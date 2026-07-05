# 🌦️ Polymarket Weather Trading AI Agent

An autonomous multi-agent quantitative trading system that predicts global weather events and executes simulated paper trades on Polymarket.

## 🏗️ Architecture

The system has been fully re-architected into a decoupled **FastAPI Backend** and **Streamlit Dashboard**, powered by a robust multi-agent pipeline and SQLAlchemy SQLite database.

1. **Weather Ingestion (`agents/research_agent.py`)**: Connects to Apify & Open-Meteo to scrape global and localized weather data concurrently.
2. **Reasoning Engine (`agents/prediction_agent.py`)**: Passes normalized weather structures into an OpenRouter LLM (currently optimized for `meta-llama/llama-3.2-3b-instruct:free`). It acts as a quant forecaster and outputs precise win probabilities, confidence scores, and detailed logical reasoning.
3. **Risk Management (`agents/risk_agent.py`)**: Implements the mathematical **Kelly Criterion** against Polymarket odds to determine optimal capital allocation, maximizing growth while capping max exposure.
4. **Execution & Alerts (`agents/trading_agent.py`)**: Executes paper trades and pushes live HTML-formatted Telegram notifications to your mobile device instantly.
5. **Data Persistence (`database/models.py`)**: A local SQLite database robustly persists predictions, market odds, orders, and portfolio history across cycles.
6. **Frontend UI (`ui/streamlit_app.py`)**: An interactive, glassmorphism-themed dark mode dashboard to monitor active risk, view reasoning, and execute agent cycles manually.

## ✨ Recent Updates

* **Real-time Cycle Monitoring:** The "Run Agent Cycle" button now tracks background task progress in real-time with an active UI loading state, automatically refreshing the dashboard upon completion.
* **Database Reset:** Easily wipe your paper trading portfolio and prediction history to start fresh via the new `🔄 Reset Data` button at the top right of the dashboard.
* **Latest Results Spotlight:** The most recent prediction and its logical reasoning are now pinned to the top of the dashboard for quick visibility.
* **Model Overhaul:** The default backend LLM is migrated to `meta-llama/llama-3.2-3b-instruct:free` to ensure stable JSON generation and API uptime.

## 🚀 Getting Started

### 1. Installation
Clone the repository and install the dependencies:
```bash
git clone https://github.com/vaibhaw001/trading-weather-ai-agent.git
cd trading-weather-ai-agent
pip install -r requirements.txt
```

### 2. Configuration
You can enter your API keys directly into the **Control Panel** in the Streamlit UI, which will securely save them to your local `.env` file. You will need:
- **OpenRouter API Key** (Free LLM inference)
- **Apify API Token** (Web scraping)
- **Telegram Bot Token & Chat ID** (Optional, for mobile trade alerts)

### 3. Usage

You must run the Backend and the UI concurrently in two separate terminal windows.

**Terminal 1: Start the Core FastAPI Backend**
```bash
python api/main.py
```

**Terminal 2: Launch the Analytics Dashboard**
```bash
streamlit run ui/streamlit_app.py
```

Open `http://localhost:8501` in your browser. From the sidebar Control Panel, you can click **"Run Agent Cycle"** to trigger a full pipeline execution. The UI will pause and wait for the AI to complete its trading logic before showing you the new PnL, predictions, and rationale. 

To clear your history, use the **"🔄 Reset Data"** button at the top right of the Main Dashboard.
