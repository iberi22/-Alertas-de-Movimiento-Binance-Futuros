from binance.client import Client
import time
import logging

# Configuración de la API de Binance
api_key = 'TU_API_KEY'  # Reemplaza con tu clave API real
api_secret = 'TU_API_SECRET'  # Reemplaza con tu clave secreta real
client = Client(api_key, api_secret)

# Parámetros de variación
variacion = 5  # Variacion en los ultimos 30 minutos en porcentaje
variacion_100 = 7  # Variacion en los ultimos 30 minutos si tiene menos de 100k de volumen
variacionfast = 2  # Variacion en los ultimos 2 minutos en porcentaje

# Configuración de logging
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

# Función para buscar los símbolos de pares USDT
def buscarticks():
    ticks = []
    lista_ticks = client.futures_symbol_ticker()  # Traer todas las monedas de futuros
    print(f'Numero de monedas encontradas #{len(lista_ticks)}')
    for tick in lista_ticks:
        if tick['symbol'][-4:] == 'USDT':  # Selecciona las monedas en el par USDT
            ticks.append(tick['symbol'])
    print(f'Numero de monedas encontradas en el par USDT: #{len(ticks)}')
    return ticks

# Función para obtener datos históricos (klines)
def get_klines(tick):
    try:
        klines = client.futures_klines(symbol=tick, interval=Client.KLINE_INTERVAL_1MINUTE, limit=30)
        return klines
    except Exception as e:
        logging.error(f"Error al obtener datos históricos para {tick}: {e}")
        return []

# Función para obtener información del ticker
def infoticks(tick):
    try:
        info = client.futures_ticker(symbol=tick)
        return info
    except Exception as e:
        logging.error(f"Error al obtener información del ticker para {tick}: {e}")
        return {}

# Función para formatear los volúmenes a un formato más legible
def human_format(volumen):
    magnitude = 0
    while abs(volumen) >= 1000:
        magnitude += 1
        volumen /= 1000.0
    return '%.2f%s' % (volumen, ['', 'K', 'M', 'G', 'T', 'P'][magnitude])

# Función para verificar las variaciones en las klines
def porcentaje_klines(tick, klines, knumber):
    inicial = float(klines[0][4])  # Precio inicial de la primera vela
    final = float(klines[knumber][4])  # Precio final de la última vela

    # Condición LONG
    if inicial > final:
        result = round(((inicial - final) / inicial) * 100, 2)
        if result >= variacion:
            info = infoticks(tick)
            if not info:
                return  # Si no hay info del ticker, salta

            volumen = float(info['quoteVolume'])
            if volumen > 100000000 or result >= variacion_100:
                print('LONG: ' + tick)
                print('Variacion: ' + str(result) + '%')
                print('Volumen: ' + human_format(volumen))
                print('Precio max: ' + info['highPrice'])
                print('Precio min: ' + info['lowPrice'])
                print('')

    # Condición SHORT
    if final > inicial:
        result = round(((final - inicial) / inicial) * 100, 2)
        if result >= variacion:
            info = infoticks(tick)
            if not info:
                return  # Si no hay info del ticker, salta

            volumen = float(info['quoteVolume'])
            if volumen > 100000000 or result >= variacion_100:
                print('SHORT: ' + tick)
                print('Variacion: ' + str(result) + '%')
                print('Volumen: ' + human_format(volumen))
                print('Precio max: ' + info['highPrice'])
                print('Precio min: ' + info['lowPrice'])
                print('')

    # Condición FAST (en los últimos 2 minutos)
    if knumber >= 3:
        inicial = float(klines[knumber-2][4])
        final = float(klines[knumber][4])
        if inicial < final:
            result = round(((final - inicial) / inicial) * 100, 2)
            if result >= variacionfast:
                info = infoticks(tick)
                if not info:
                    return  # Si no hay info del ticker, salta

                volumen = float(info['quoteVolume'])
                print('FAST SHORT!: ' + tick)
                print('Variacion: ' + str(result) + '%')
                print('Volumen: ' + human_format(volumen))
                print('Precio max: ' + info['highPrice'])
                print('Precio min: ' + info['lowPrice'])
                print('')

# Bucle principal para escanear todas las monedas
while True:
    ticks = buscarticks()
    print('Escaneando monedas...')
    print('')

    for tick in ticks:
        klines = get_klines(tick)
        knumber = len(klines)
        if knumber > 0:
            knumber = knumber - 1
            porcentaje_klines(tick, klines, knumber)

    print('Esperando 30 segundos...')
    print('')
    time.sleep(30)
