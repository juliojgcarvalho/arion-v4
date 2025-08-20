def fetch_ohlcv_data(symbol, timeframe):
    import requests
    from config_api import API_BASE, HEADERS

    symbol = symbol.replace("/", "")  # Corrige o formato para a Binance (ex: SOL/USDT -> SOLUSDT)

    url = f"{API_BASE}/fapi/v1/klines"
    params = {
        "symbol": symbol,
        "interval": timeframe,
        "limit": 100
    }

    try:
        response = requests.get(url, params=params, timeout=10, headers=HEADERS)
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
