# arion_phase1.py
# Fase 1: Análise BTC + Scanner de Altcoins

from datetime import datetime
import pandas as pd
import numpy as np

# Módulos internos simulados (versão didática)
def analyze_btc_trend(symbol="BTC/USDT", timeframe="1d"):
    data = fetch_ohlcv_data(symbol, timeframe)
    df = pd.DataFrame(data, columns=["timestamp", "open", "high", "low", "close", "volume"])
    df["sma_8"] = df["close"].rolling(8).mean()
    df["sma_21"] = df["close"].rolling(21).mean()
    if df["sma_8"].iloc[-1] > df["sma_21"].iloc[-1]:
        return "bullish"
    elif df["sma_8"].iloc[-1] < df["sma_21"].iloc[-1]:
        return "bearish"
    else:
        return "neutral"

def scan_altcoins(timeframe="4h"):
    return ["ETH/USDT", "BNB/USDT", "SOL/USDT"]

def validate_entry(ohlcv, trend):
    df = pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])
    df["sma_8"] = df["close"].rolling(8).mean()
    df["sma_21"] = df["close"].rolling(21).mean()
    last_rsi = calculate_rsi(df["close"], 14).iloc[-1]
    if df["sma_8"].iloc[-1] > df["sma_21"].iloc[-1] and last_rsi > 50:
        return {"valid": True, "rsi": last_rsi, "sma_condition": True}
    return {"valid": False}

def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def get_risk_allocation(pair):
    return {"pair": pair, "allocation_usdt": 10.0, "leverage": 20}

import requests
import time

def fetch_ohlcv_data(symbol, timeframe):
    """
    Busca dados reais da Binance Futures em formato OHLCV.
    Ex: symbol = "BTC/USDT", timeframe = "4h"
    """
    symbol = symbol.replace("/", "").upper()

    # Mapear os timeframes do Arion para os da Binance
    interval_map = {
        "1m": "1m", "5m": "5m", "15m": "15m",
        "1h": "1h", "4h": "4h", "1d": "1d"
    }
    interval = interval_map.get(timeframe, "1h")

    url = f"https://fapi.binance.com/fapi/v1/klines"
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
                candle[0] / 1000,      # timestamp (ms to s)
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
        print(f"[ERRO] Falha ao buscar dados de {symbol}: {e}"
        return []


# Execução principal
def run_phase1():
    print(f"[Arion] Início da análise - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    btc_trend = analyze_btc_trend()
    if btc_trend not in ["bullish", "bearish"]:
        print("[Arion] Tendência do BTC neutra. Sistema aguardando cenário mais claro.")
        return

    print(f"[Arion] Tendência do BTC: {btc_trend.upper()}")
    candidate_pairs = scan_altcoins()
    print(f"[Arion] Pares candidatos encontrados: {len(candidate_pairs)}")

    for pair in candidate_pairs:
        try:
            ohlcv = fetch_ohlcv_data(pair, timeframe="4h")
            signal = validate_entry(ohlcv, trend=btc_trend)
            if signal['valid']:
                allocation = get_risk_allocation(pair)
                log_signal(pair, signal, allocation)
                print(f"[Arion] Sinal confirmado para {pair}: entrada técnica válida.")
        except Exception as e:
            print(f"[Arion] Erro ao validar {pair}: {str(e)}")

if __name__ == "__main__":
    run_phase1()
