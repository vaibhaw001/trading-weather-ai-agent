# 🌦️ Polymarket Weather Trading AI Agent

An autonomous multi-agent quantitative trading system that predicts global weather events and executes simulated paper trades on Polymarket.

## 🏗️ Architecture

The backend is built around a service-oriented, multi-agent architecture designed for robustness and modularity:

1. **Weather Ingestion (`services/weather_service.py`)**: Connects to the Apify API to scrape global and localized weather data.
2. **Reasoning Engine (`agents/prediction_agent.py`)**: Passes normalized weather structures into an OpenRouter LLM (Llama 3) configured with strict prompt engineering. It acts as a quant forecaster and outputs precise win probabilities and confidence scores.
3. **Risk Management (`agents/risk_agent.py`)**: Implements the mathematical **Kelly Criterion** against simulated Polymarket odds to determine the optimal capital allocation per trade, maximizing growth while preventing ruin through a configured maximum exposure cap.
4. **Execution & UI (`ui/app.py` & `services/notification_service.py`)**: Executes paper trades, pushes live Telegram notifications, and updates a local Streamlit dashboard to monitor active risk, manual hedges, and historical PnL.

## 🚀 Getting Started

### 1. Installation
Clone the repository and install the dependencies:
```bash
git clone https://github.com/vaibhaw001/trading-weather-ai-agent.git
cd trading-weather-ai-agent
pip install -r requirements.txt
```

### 2. Configuration
Rename the `.env.example` file to `.env` and fill in your keys:
- **OpenRouter API Key** (Free LLM inference)
- **Apify API Token** (Web scraping)
- **Telegram Bot Token** (Optional, for mobile trade alerts)

### 3. Usage

**Run the Core Trading Daemon**
To execute a single cycle of data ingestion, AI probability prediction, and trade execution:
```bash
python main.py
```

**Launch the Analytics Dashboard**
To view the live PnL, track open positions, and execute manual hedges:
```bash
streamlit run ui/app.py
```
