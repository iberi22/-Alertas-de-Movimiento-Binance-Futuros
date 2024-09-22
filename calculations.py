import pandas as pd
import numpy as np

def create_klines_df(klines):
    """Crea un DataFrame a partir de los datos de klines."""
    return pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])

def calculate_sma(klines, period):
    """Calcula la media móvil simple (SMA) para un período dado."""
    df = create_klines_df(klines)
    df['close'] = pd.to_numeric(df['close'])
    sma = df['close'].rolling(window=period).mean()
    return {'SMA': sma.tolist()}

def calculate_rsi(klines, period=14):
    """Calcula el índice de fuerza relativa (RSI) para un período dado."""
    df = create_klines_df(klines)
    df['close'] = pd.to_numeric(df['close'])
    delta = df['close'].diff()
    gain = delta.mask(delta < 0, 0)
    loss = -delta.mask(delta > 0, 0)
    avg_gain = gain.ewm(com=(period - 1), min_periods=period).mean()
    avg_loss = loss.ewm(com=(period - 1), min_periods=period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return {'RSI': rsi.tolist()}

def calculate_macd(klines, slow_period=26, fast_period=12, signal_period=9):
    """Calcula la convergencia/divergencia de la media móvil (MACD)."""
    df = create_klines_df(klines)
    df['close'] = pd.to_numeric(df['close'])
    exp1 = df['close'].ewm(span=fast_period, adjust=False).mean()
    exp2 = df['close'].ewm(span=slow_period, adjust=False).mean()
    macd_line = exp1 - exp2
    signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()
    histogram = macd_line - signal_line
    return {'MACD': macd_line.tolist(), 'Signal': signal_line.tolist(), 'Histogram': histogram.tolist()}