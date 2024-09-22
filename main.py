from binance.client import Client
import time
from signals import generate_signals

# Parámetros de variación
variacion = 5  # Variación en los últimos 30 minutos en porcentaje
variacion_100 = 7  # Variación en los últimos 30 minutos en porcentaje si tiene menos de 100k de volumen
variacionfast = 2  # Variación en los últimos 2 minutos en porcentaje

# Cliente Binance
client = Client('', '', tld='com')

def buscarticks():
    """Busca todos los símbolos de futuros en Binance"""
    ticks = []
    lista_ticks = client.futures_symbol_ticker()
    print(f'Número de monedas encontradas: {len(lista_ticks)}')

    for tick in lista_ticks:
        if tick['symbol'][-4:] != 'USDT':  # Seleccione solo monedas en par USDT
            continue
        ticks.append(tick['symbol'])

    print(f'Número de monedas encontradas en par USDT: {len(ticks)}')
    return ticks

def get_klines(tick):
    """Obtiene los datos de velas para un símbolo específico"""
    klines = client.futures_klines(symbol=tick, interval=Client.KLINE_INTERVAL_1MINUTE, limit=30)
    return klines

def infoticks(tick):
    """Obtiene información adicional para un símbolo específico"""
    info = client.futures_ticker(symbol=tick)
    return info

def human_format(volumen):
    """Formatea el volumen en una representación humana"""
    magnitude = 0
    while abs(volumen) >= 1000:
        magnitude += 1
        volumen /= 1000.0
    return '%.2f%s' % (volumen, ['', 'K', 'M', 'G', 'T', 'P'][magnitude])

def analizar_klines(tick, klines, knumber):
    """Analiza los datos de velas y genera señales de trading"""
    inicial = float(klines[0][4])
    final = float(klines[knumber][4])

    # LONG
    if inicial > final:
        result = round(((inicial - final) / inicial) * 100, 2)
        if result >= variacion:
            info = infoticks(tick)
            volumen = float(info['quoteVolume'])
            if volumen > 100000000 or result >= variacion_100:
                print(f'LONG: {tick}')
                print(f'Variación: {result}%')
                print(f'Volumen: {human_format(volumen)}')
                print(f'Precio max: {info["highPrice"]}')
                print(f'Precio min: {info["lowPrice"]}')
                print('')

    # SHORT
    if final > inicial:
        result = round(((final - inicial) / inicial) * 100, 2)
        if result >= variacion:
            info = infoticks(tick)
            volumen = float(info['quoteVolume'])
            if volumen > 100000000 or result >= variacion_100:
                print(f'SHORT: {tick}')
                print(f'Variación: {result}%')
                print(f'Volumen: {human_format(volumen)}')
                print(f'Precio max: {info["highPrice"]}')
                print(f'Precio min: {info["lowPrice"]}')
                print('')

    # FAST
    if knumber >= 3:
        inicial = float(klines[knumber-2][4])
        final = float(klines[knumber][4])
        if inicial < final:
            result = round(((final - inicial) / inicial) * 100, 2)
            if result >= variacionfast:
                info = infoticks(tick)
                volumen = float(info['quoteVolume'])
                print(f'FAST SHORT!: {tick}')
                print(f'Variación: {result}%')
                print(f'Volumen: {human_format(volumen)}')
                print(f'Precio max: {info["highPrice"]}')
                print(f'Precio min: {info["lowPrice"]}')
                print('')

      # Generar señales basadas en indicadores técnicos
    technical_signals = generate_signals(tick, klines)

    # Imprimir todas las señales
    for signal in technical_signals:
        print(f'Señal {signal[0]}: {signal[1]} {signal[2]}')

while True:
    ticks = buscarticks()
    print('Escaneando monedas...')
    print('')
    for tick in ticks:
        klines = get_klines(tick)
        knumber = len(klines)
        if knumber > 0:
            knumber = knumber - 1
            analizar_klines(tick, klines, knumber)
    print('Esperando 30 segundos...')
    print('')
    time.sleep(30)
