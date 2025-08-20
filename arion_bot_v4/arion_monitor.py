# arion_monitor.py
# Monitoramento e execução da Técnica 3x no Arion

from datetime import datetime, timedelta
import numpy as np
import pandas as pd

# Dados simulados para backtest
from arion_phase1 import fetch_ohlcv_data, calculate_rsi, log_signal

MAX_LIQUIDATION_RISK = 0.07  # 7%

# Simulação da posição aberta
portfolio = {
    "SOLUSDT": {
        "entry_price": 110.0,
        "quantity": 0.5,
        "leverage": 20,
        "status": "open",
        "direction": "buy",
        "3x_used": False
    }
}

banca_total = 100.0  # USD fictício
lucros_vencedores = {
    "ETHUSDT": 6.0,
    "BNBUSDT": 4.0
}

# Detecção de estabilização (gráfico 4H)
def detect_stabilization(symbol):
    df = pd.DataFrame(fetch_ohlcv_data(symbol, "4h"), columns=["timestamp", "open", "high", "low", "close", "volume"])
    df["body"] = abs(df["close"] - df["open"])
    avg_body = df["body"].tail(15).mean()
    stable_candles = df["body"].tail(15) < avg_body * 0.6
    return stable_candles.sum() >= 8

# Trigger de reversão (gráfico 5m)
def trigger_strength(symbol):
    df = pd.DataFrame(fetch_ohlcv_data(symbol, "5m"), columns=["timestamp", "open", "high", "low", "close", "volume"])
    last = df.iloc[-1]
    prev = df.iloc[-2]
    avg_volume = df["volume"].tail(5).mean()
    condition_1 = last["volume"] > avg_volume * 2
    condition_2 = last["close"] > prev["high"]
    return condition_1 and condition_2

# Execução do 3x
def execute_3x(symbol):
    pos = portfolio[symbol]
    if pos["3x_used"]:
        return
    pos["quantity"] *= 4  # posição total = 1x original + 3x nova entrada
    pos["3x_used"] = True
    print(f"[Arion] Técnica 3x aplicada em {symbol}. Quantidade agora: {pos['quantity']:.2f}")

# Checagem de lucro e saída parcial
def manage_partial_exit(symbol, current_price):
    pos = portfolio[symbol]
    if pos["3x_used"] and current_price >= pos["entry_price"]:
        print(f"[Arion] Operação revertida em {symbol}. Saída de 80% com lucro.")
        pos["quantity"] *= 0.2
        pos["entry_price"] = current_price
        log_signal(symbol, {"rsi": calculate_rsi(pd.Series([current_price]), 14).iloc[-1]}, {"allocation_usdt": 8.0})

# Verifica se ainda faz sentido manter a posição
def exit_if_trend_reverses(symbol):
    df = pd.DataFrame(fetch_ohlcv_data(symbol, "1h"), columns=["timestamp", "open", "high", "low", "close", "volume"])
    df["sma_8"] = df["close"].rolling(8).mean()
    df["sma_21"] = df["close"].rolling(21).mean()
    rsi = calculate_rsi(df["close"], 14).iloc[-1]
    if df["sma_8"].iloc[-1] < df["sma_21"].iloc[-1] and rsi < 50:
        print(f"[Arion] Tendência perdeu força. Encerrando {symbol}.")
        portfolio[symbol]["status"] = "closed"

# Alívio de risco de liquidação
def manage_liquidation_risk():
    risk = np.random.uniform(0.05, 0.1)  # Simula risco atual
    if risk > MAX_LIQUIDATION_RISK:
        total_reduzido = 0.0
        for k, lucro in sorted(lucros_vencedores.items(), key=lambda x: x[1], reverse=True):
            print(f"[Arion] Reduzindo lucro de {k} para aliviar risco.")
            total_reduzido += lucro
            if total_reduzido / banca_total > (risk - MAX_LIQUIDATION_RISK):
                break
        print(f"[Arion] Risco ajustado com redução de {total_reduzido:.2f} USD em lucros.")

# Loop de monitoramento
def monitor():
    for symbol, pos in portfolio.items():
        if pos["status"] != "open":
            continue

        current_price = fetch_ohlcv_data(symbol, "1h")[-1][4]  # preço de fechamento atual

        if not pos["3x_used"] and detect_stabilization(symbol):
            if trigger_strength(symbol):
                execute_3x(symbol)

        if pos["3x_used"]:
            manage_partial_exit(symbol, current_price)
            exit_if_trend_reverses(symbol)

    manage_liquidation_risk()

import time

if __name__ == "__main__":
    print(f"[Arion Monitor] Início do monitoramento - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    while True:
        monitor()
        time.sleep(300)  # Espera 5 minutos entre cada execução
