# IndiaQuant MCP – AI Stock Assistant

IndiaQuant MCP is an AI-powered stock market analysis assistant that provides live market data, technical indicators, options analysis, and portfolio risk monitoring.

## Live Deployment
https://indiaquant-mcp-v5pa.onrender.com/

## Features

### 1. Market Data Engine
- Fetch live stock prices using yfinance
- Support NSE stocks
- Historical OHLC data retrieval

### 2. AI Trade Signal Generator
- RSI indicator
- Technical analysis signal generation
- BUY / SELL / HOLD signals

### 3. Options Chain Analyzer
- Options chain retrieval
- Black-Scholes Greeks calculation
- Unusual options activity detection

### 4. Portfolio Risk Manager
- Virtual portfolio tracking
- Real-time P&L calculation
- Position monitoring

### 5. MCP Tools Layer
The system exposes trading tools through an MCP-compatible tool interface.

Tools implemented:

- get_live_price
- generate_signal
- get_options_chain
- analyze_sentiment
- place_virtual_trade
- get_portfolio_pnl
- calculate_greeks
- detect_unusual_activity
- scan_market
- get_sector_heatmap

## Architecture

Frontend:
- HTML
- JavaScript
- Fetch API

Backend:
- FastAPI
- Python

Data Sources:
- yfinance
- News APIs

Deployment:
- Render cloud platform

## Setup (Local)

Install dependencies:
pip install -r requirements.txt


Run server:
uvicorn server:app --reload


Open browser:
http://127.0.0.1:8000


## Deployment

The application is deployed on Render free tier.  
The server may sleep after inactivity and automatically wake when accessed.

## Author
Sai Gagan Sirigeri
