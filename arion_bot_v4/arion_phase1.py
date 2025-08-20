from datetime import datetime
import requests
import numpy as np
import pandas as pd
from config_api import API_BASE, HEADERS

def fetch_ohlcv_data(symbol, timeframe):
    url = f"{API_BASE}/fapi/v1/klines"
    params = {
        "symbol": symbol,
        "interval": timeframe,
        "limit": 100
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        raw_data = response.json()
        ohlcv = [
            (
                candle[0] // 1000,  # timestamp (ms to s)
                float(candle[1]),  # open
                float(candle[2]),  # high
                float(candle[3]),  # low
                float(candle[4]),  # close
                float(candle[5])   # volume
            )
            for candle in raw_data
        ]
        return ohlcv

    except Exception as e:
        print(f"[ERRO] Falha ao buscar dados de {symbol}: {e}")
        return []

def calculate_rsi(prices, period=14):
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def log_signal(symbol, indicators, context):
    print(f"[ARION - SINAL] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {symbol} - Indicadores: {indicators} - Contexto: {context}")

# Execução principal
def run_phase1():
    print(f"[Arion] Início da análise - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    btc_trend = analyze_btc_trend()

    if btc_trend not in ["bullish", "bearish"]:
        print("[Arion] Tendência do BTC neutra. Sistema aguardando cenário mais claro.")
        return

    print(f"[Arion] Tendência do BTC: {btc_trend.upper()}")

    # Lista de ativos a analisar
    symbols = ["SOLUSDT", "ETHUSDT", "BNBUSDT"]

    for symbol in symbols:
        ohlcv = fetch_ohlcv_data(symbol, "1h")
        if not ohlcv or len(ohlcv) < 21:
            print(f"[Arion] Dados insuficientes para {symbol}")
            continue

        df = pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])
        df["rsi"] = calculate_rsi(df["close"])

        last_rsi = df["rsi"].iloc[-1]
        print(f"[Arion] {symbol} - RSI atual: {last_rsi:.2f}")

        if btc_trend == "bullish" and last_rsi < 30:
            log_signal(symbol, {"rsi": last_rsi}, {"tendência": btc_trend})
        elif btc_trend == "bearish" and last_rsi > 70:
            log_signal(symbol, {"rsi": last_rsi}, {"tendência": btc_trend})

def analyze_btc_trend():
    data = fetch_ohlcv_data("BTCUSDT", "4h")
    if not data or len(data) < 21:
        return "neutral"

    df = pd.DataFrame(data, columns=["timestamp", "open", "high", "low", "close", "volume"])
    df["sma_8"] = df["close"].rolling(window=8).mean()
    df["sma_21"] = df["close"].rolling(window=21).mean()

    if df["sma_8"].iloc[-1] > df["sma_21"].iloc[-1]:
        return "bullish"
    elif df["sma_8"].iloc[-1] < df["sma_21"].iloc[-1]:
        return "bearish"
    else:
        return "neutral"

if __name__ == "__main__":
    run_phase1()
