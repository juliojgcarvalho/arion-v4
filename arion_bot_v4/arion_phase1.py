# arion_phase1.py

from datetime import datetime
import requests
import pandas as pd
import numpy as np
from config_api import API_BASE, HEADERS

# === Funções de suporte ===

def fetch_ohlcv_data(symbol, timeframe):
    url = f"{API_BASE}/futures/um/v3/market/history/candles"
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
                candle[0] / 1000,        # timestamp (ms to s)
                float(candle[1]),        # open
                float(candle[2]),        # high
                float(candle[3]),        # low
                float(candle[4]),        # close
                float(candle[5])         # volume
            )
            for candle in raw_data
        ]
        return ohlcv

    except Exception as e:
        print(f"[ERRO] Falha ao buscar dados de {symbol}: {e}")
        return []

def calculate_rsi(close_prices, period=14):
    delta = close_prices.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def analyze_btc_trend():
    df = pd.DataFrame(fetch_ohlcv_data("BTC/USDT", "1h"), columns=["timestamp", "open", "high", "low", "close", "volume"])
    df["sma_8"] = df["close"].rolling(8).mean()
    df["sma_21"] = df["close"].rolling(21).mean()
    rsi = calculate_rsi(df["close"]).iloc[-1]

    if df["sma_8"].iloc[-1] > df["sma_21"].iloc[-1] and rsi > 55:
        return "bullish"
    elif df["sma_8"].iloc[-1] < df["sma_21"].iloc[-1] and rsi < 45:
        return "bearish"
    else:
        return "neutral"

def log_signal(symbol, indicadores, alocacao):
    print(f"[Arion] Sinal gerado para {symbol}")
    print(f"  Indicadores: {indicadores}")
    print(f"  Alocação: {alocacao}")

# === Execução principal ===

def run_phase1():
    print(f"[Arion] Início da análise - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    btc_trend = analyze_btc_trend()
    if btc_trend not in ["bullish", "bearish"]:
        print("[Arion] Tendência do BTC neutra. Sistema aguardando cenário mais claro.")
        return

    print(f"[Arion] Tendência do BTC: {btc_trend.upper()}")

    # Exemplos de ativos para analisar
    ativos = ["SOL/USDT", "ETH/USDT", "BNB/USDT"]

    for ativo in ativos:
        df = pd.DataFrame(fetch_ohlcv_data(ativo, "1h"), columns=["timestamp", "open", "high", "low", "close", "volume"])
        if df.empty:
            continue
        rsi = calculate_rsi(df["close"]).iloc[-1]

        if btc_trend == "bullish" and rsi < 35:
            log_signal(ativo, {"rsi": rsi}, {"allocation_usdt": 10.0})
        elif btc_trend == "bearish" and rsi > 65:
            log_signal(ativo, {"rsi": rsi}, {"allocation_usdt": 10.0})

if __name__ == "__main__":
    run_phase1()
