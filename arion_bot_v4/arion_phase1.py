import requests
from datetime import datetime
import pandas as pd
import numpy as np

url = "https://fapi.binance.com/fapi/v1/klines"
API_BASE_HEADERS = {"User-Agent": "ArionBot/1.0"}

def fetch_ohlcv_data(symbol, interval):
    params = {
        "symbol": symbol,
        "interval": interval,
        "limit": 100
    }

    try:
        response = requests.get(url, params=params, timeout=10, headers=API_BASE_HEADERS)
        response.raise_for_status()
        raw_data = response.json()
        ohlcv = [
            (
                candle[0] // 1000,     # timestamp (ms to s)
                float(candle[1]),      # open
                float(candle[2]),      # high
                float(candle[3]),      # low
                float(candle[4]),      # close
                float(candle[5])       # volume
            )
            for candle in raw_data
        ]
        return ohlcv
    except Exception as e:
        print(f"[ERRO] Falha ao buscar dados de {symbol}: {e}")
        return []

def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    return rsi

def log_signal(symbol, indicators, context):
    print(f"[Arion LOG] Sinal detectado para {symbol}")
    print(f"Indicadores: {indicators}")
    print(f"Contexto: {context}")
