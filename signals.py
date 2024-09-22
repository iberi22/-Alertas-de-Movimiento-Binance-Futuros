from calculations import calculate_sma, calculate_rsi, calculate_macd

def generate_signals(tick, klines):
    """
    Generates trading signals based on technical indicators, only if there is a confluence of buy or sell signals in RSI, SMA, and MACD.
    Also calculates the entry point based on volume.
    """

    # Calculate technical indicators
    sma_short = calculate_sma(klines, 50)
    sma_long = calculate_sma(klines, 200)
    rsi = calculate_rsi(klines)
    macd_line, signal_line, _ = calculate_macd(klines)

    signals = []
    entry_point = None

    # Check if there are enough elements in the SMA lists
    if len(sma_short) >= 2 and len(sma_long) >= 2:
        # Logic for buy signals
        buy_sma = sma_short[-1] > sma_long[-1] and sma_short[-2] <= sma_long[-2]
        buy_rsi = rsi[-1] < 30
        buy_macd = macd_line[-1] > signal_line[-1] and macd_line[-2] <= signal_line[-2]

        if buy_sma and buy_rsi and buy_macd:
            # Calculate the entry point based on volume
            volumes = [float(kline[5]) for kline in klines[-60:]]
            avg_volume = sum(volumes) / len(volumes)
            entry_point = float(klines[-1][4]) + (3 * avg_volume)

            signals.append(('CONFLUENCIA', 'Compra', tick, entry_point))

        # Logic for sell signals
        sell_sma = sma_short[-1] < sma_long[-1] and sma_short[-2] >= sma_long[-2]
        sell_rsi = rsi[-1] > 70
        sell_macd = macd_line[-1] < signal_line[-1] and macd_line[-2] >= signal_line[-2]

        if sell_sma and sell_rsi and sell_macd:
            signals.append(('CONFLUENCIA', 'Venta', tick, None))

    return signals