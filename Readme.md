# IndiaQuant MCP – AI Stock Market Assistant

## Overview

IndiaQuant MCP is a real-time AI-powered stock market assistant built using **FastAPI**.
It exposes Indian stock market intelligence as **MCP-compatible tools** that can be used by AI agents such as Claude.

The system provides real-time market data, technical analysis, options analytics, portfolio simulation, and market scanning using **100% free APIs**.

---

## Architecture

The system consists of five main modules:

### 1. Market Data Engine

Fetches live stock prices and historical OHLC data using **yfinance**.

### 2. AI Trade Signal Generator

Generates trading signals using:

* RSI
* MACD
* Bollinger Bands
* News sentiment analysis

Outputs: **BUY / SELL / HOLD with confidence score**

### 3. Options Chain Analyzer

Analyzes options market including:

* Options chain data
* Black-Scholes Greeks calculation
* Unusual options activity detection

### 4. Portfolio Risk Manager

Maintains a virtual portfolio using SQLite.

Features:

* Virtual trading
* Real-time P&L
* Live price updates

### 5. MCP Tools Layer

Exposes 10 MCP-compatible tools that AI agents can call via JSON-RPC.

---

## Tools Implemented

1. get_live_price
2. get_options_chain
3. analyze_sentiment
4. generate_signal
5. get_portfolio_pnl
6. place_virtual_trade
7. calculate_greeks
8. detect_unusual_activity
9. scan_market
10. get_sector_heatmap

---

## APIs Used

All APIs used are **free and legal**.

* yfinance (live stock data)
* NewsAPI (news sentiment)
* pandas-ta (technical indicators)

No scraping.
No paid APIs.

---

## Installation

Clone the repository:

git clone https://github.com/SaiGagan13/indiaquant-mcp.git

Install dependencies:

pip install -r requirements.txt

Run the server:

python -m uvicorn server:app --reload

---

## Usage

Open the dashboard:

http://127.0.0.1:8000

API documentation:

http://127.0.0.1:8000/docs

---

## MCP JSON-RPC Example

POST /rpc

{
"jsonrpc":"2.0",
"method":"get_live_price",
"params":{"symbol":"RELIANCE"},
"id":1
}

---

## Technologies Used

* Python
* FastAPI
* SQLite
* pandas
* numpy
* pandas-ta
* yfinance

---

## Future Improvements

* Full MCP protocol compliance
* Portfolio risk scoring
* Advanced chart visualization
* Deployment to cloud infrastructure
