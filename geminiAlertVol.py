import pandas as pd
from binance.client import Client

# Configura tu cliente de Binance
api_key = 'YOUR_API_KEY'
api_secret = 'YOUR_API_SECRET'
client = Client(api_key, api_secret)

# Función para cargar datos históricos
def load_data(symbol, timeframe):
    klines = client.futures_klines(symbol=symbol, interval=timeframe)
    df = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)
    df['close'] = df['close'].astype(float)
    return df

# Función para calcular el MACD
def calculate_macd(data, window_slow=26, window_fast=12, window_sign=9):
    ema_fast = data['close'].ewm(span=window_fast, adjust=False).mean()
    ema_slow = data['close'].ewm(span=window_slow, adjust=False).mean()
    macd = ema_fast - ema_slow
    macd_signal = macd.ewm(span=window_sign, adjust=False).mean()
    return macd, macd_signal

# Función para calcular RSI
def calculate_rsi(data, window=14):
    delta = data['close'].diff(1)
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(window=window).mean()
    avg_loss = loss.rolling(window=window).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    return rsi

# Función para generar señales de entrada con filtro RSI
def generate_signals(data):
    signals = pd.DataFrame(index=data.index)

    # Calcular MACD y su señal
    macd, macd_signal = calculate_macd(data)
    signals['macd'] = macd
    signals['signal'] = macd_signal

    # Calcular RSI
    signals['rsi'] = calculate_rsi(data)

    # Generar señal de compra (long) si RSI < 30 (sobreventa) y MACD cruza la señal hacia arriba
    signals.loc[(signals['macd'] > signals['signal']) & (data['close'] > data['close'].shift(1)) & (signals['rsi'] < 30), 'position'] = 'long'

    # Generar señal de venta (short) si RSI > 70 (sobrecompra) y MACD cruza la señal hacia abajo
    signals.loc[(signals['macd'] < signals['signal']) & (data['close'] < data['close'].shift(1)) & (signals['rsi'] > 70), 'position'] = 'short'

    return signals

# Función para enviar notificaciones
def send_notification(message):
    print(f"Notification: {message}")  # Aquí deberías implementar tu propio código para enviar notificaciones

# Función para buscar todas las monedas que terminan con "USDT"
def find_usdt_pairs(client):
    ticks = []
    lista_ticks = client.futures_symbol_ticker()  # Traer todas las monedas de futuros de Binance
    print('Numero de monedas encontradas #' + str(len(lista_ticks)))
    for tick in lista_ticks:
        if tick['symbol'][-4:] != 'USDT':  # Seleccionar todas las monedas en el par USDT
            continue
        ticks.append(tick['symbol'])
    print('Numero de monedas encontradas en el par USDT: #' + str(len(ticks)))
    return ticks

# Ejecutar el código
usdt_pairs = find_usdt_pairs(client)

for pair in usdt_pairs:
    try:
        data = load_data(pair, '5m')  # Carga datos históricos para cada par en intervalo de 5 minutos
        signals = generate_signals(data)

        # Verificar la última señal generada (actual)
        last_signal = signals.iloc[-1]  # Solo revisar la última fila (última vela)
        last_price = data['close'].iloc[-1]  # Último precio

        if last_signal['position'] == 'long':
            send_notification(f"Long signal on {pair}: Price = {last_price}, RSI = {last_signal['rsi']}")
        elif last_signal['position'] == 'short':
            send_notification(f"Short signal on {pair}: Price = {last_price}, RSI = {last_signal['rsi']}")
            print('Esperando 30 segundos...')
            print('')
            time.sleep(30)
    except Exception as e:
        print(f"Error processing pair {pair}: {e}")

