# arion_phase1.py
# Fase 1: Coleta e Análise de Dados

import requests
import pandas as pd
import numpy as np
from datetime import datetime

# Coleta de dados OHLCV da Binance Futures
def fetch_ohlcv_data(symbol, interval):
    url = "https://fapi.binance.com/fapi/v1/klines"
    params = {
        "symbol": symbol.replace("/", ""),  # Ex: SOL/USDT -> SOLUSDT
        "interval": interval,
        "limit": 100
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        raw_data = response.json()
        ohlcv = [
            (
                candle[0],     # timestamp
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

# Cálculo do RSI (Índice de Força Relativa)
def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

# Registro de sinais
def log_signal(symbol, indicators, context=None):
    print(f"[LOG] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | {symbol} | RSI: {indicators['rsi']:.2f}")
    if context:
        print(f"[LOG CONTEXTO] {context}")
