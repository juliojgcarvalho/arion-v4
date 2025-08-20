# arion_phase1.py
# Módulo de funções auxiliares para o monitoramento Arion

import requests
import pandas as pd
from datetime import datetime

# API da Binance para candles futuros
API_BASE = "https://fapi.binance.com"

def fetch_ohlcv_data(symbol, interval):
    """
    Busca dados OHLCV da Binance Futures.
    """
    url = f"{API_BASE}/fapi/v1/klines"
    params = {
        "symbol": symbol,
        "interval": interval,
        "limit": 100
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        raw_data = response.json()
        ohlcv = [
            (
                candle[0] // 1000,    # timestamp (ms to s)
                float(candle[1]),     # open
                float(candle[2]),     # high
                float(candle[3]),     # low
                float(candle[4]),     # close
                float(candle[5])      # volume
            )
            for candle in raw_data
        ]
        return ohlcv
    except Exception as e:
        print(f"[ERRO] Falha ao buscar dados de {symbol}: {e}")
        return []

def calculate_rsi(series, period=14):
    """
    Calcula o RSI (Índice de Força Relativa) para uma série de preços.
    """
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def log_signal(symbol, indicators, allocation):
    """
    Registra o sinal da operação detectada.
    """
    print(f"[Arion] Sinal detectado em {symbol} | Indicadores: {indicators} | Alocação: {allocation}")
