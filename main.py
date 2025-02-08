import streamlit as st
from binance.client import Client
import time
from datetime import datetime
from signals import generate_signals  # Asumo que tienes un archivo signals.py
import requests
from bs4 import BeautifulSoup
import nltk
from textblob import TextBlob

# --- Configuración ---
variacion = 5  # Variación en los últimos 30 minutos en porcentaje
variacion_100 = 7  # Variación si volumen < 100k
variacionfast = 2  # Variación en los últimos 2 minutos en porcentaje
API_KEY = ""  # **¡REEMPLAZA CON TU API KEY REAL! O usa Streamlit Secrets**
API_SECRET = "" # **¡REEMPLAZA CON TU API SECRET REAL! O usa Streamlit Secrets**
client = Client(API_KEY, API_SECRET, tld='com') # Inicializar cliente Binance

# --- Funciones de tu script adaptadas para Streamlit ---
class bcolors: # Mantener las clases de color para la salida en Streamlit (se mostrarán como texto plano)
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    OKCYAN = '\033[96m'
    ENDC = '\033[0m'
    OKBLUE = '\033[94m'

def buscarticks():
    """Busca todos los símbolos de futuros en Binance"""
    ticks = []
    lista_ticks = client.futures_symbol_ticker()
    for tick in lista_ticks:
        if tick['symbol'][-4:] != 'USDT':  # Seleccione solo monedas en par USDT
            continue
        ticks.append(tick['symbol'])
    return ticks

def get_klines(tick):
    """Obtiene los datos de velas para un símbolo específico"""
    klines = client.futures_klines(symbol=tick, interval=Client.KLINE_INTERVAL_1MINUTE, limit=30, timeout=30)
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

def analizar_klines_streamlit(tick, klines, knumber):
    """Analiza los datos de velas y genera alertas para Streamlit"""
    alerts = [] # Lista para guardar las alertas y mostrarlas en Streamlit

    # Obtener la hora actual
    now = datetime.now()
    current_time = now.strftime("%Y-%m-%d %H:%M:%S")

    inicial = float(klines[0][4])
    final = float(klines[knumber][4])

    # LONG
    if inicial > final:
        result = round(((inicial - final) / inicial) * 100, 2)
        if result >= variacion:
            info = infoticks(tick)
            volumen = float(info['quoteVolume'])
            if volumen > 100000000 or result >= variacion_100:
                alert_message = f"""
                {bcolors.WARNING}--------------------------------------------------{bcolors.ENDC}
                {bcolors.FAIL}{current_time} - **LONG**: {tick}{bcolors.ENDC}
                [Binance Futures](https://www.binance.com/es/futures/{tick}/) - [Bitget Futures](https://www.bitget.com/futures/usdt/{tick}/)
                {bcolors.OKCYAN}Variación: {result}%{bcolors.ENDC} - {bcolors.OKCYAN}Volumen: {human_format(volumen)}{bcolors.ENDC}
                {bcolors.OKCYAN}Precio max: {info["highPrice"]}{bcolors.ENDC} - {bcolors.OKCYAN}Precio min: {info["lowPrice"]}{bcolors.ENDC}
                {bcolors.WARNING}--------------------------------------------------{bcolors.ENDC}
                """
                alerts.append(alert_message)

    # SHORT
    if final > inicial:
        result = round(((final - inicial) / inicial) * 100, 2)
        if result >= variacion:
            info = infoticks(tick)
            volumen = float(info['quoteVolume'])
            if volumen > 100000000 or result >= variacion_100:
                alert_message = f"""
                {bcolors.WARNING}--------------------------------------------------{bcolors.ENDC}
                {bcolors.FAIL}{current_time} - **SHORT**: {tick}{bcolors.ENDC}
                [Binance Futures](https://www.binance.com/es/futures/{tick}/) - [Bitget Futures](https://www.bitget.com/futures/usdt/{tick}/)
                {bcolors.OKCYAN}Variación: {result}%{bcolors.ENDC} - {bcolors.OKCYAN}Volumen: {human_format(volumen)}{bcolors.ENDC}
                {bcolors.OKCYAN}Precio max: {info["highPrice"]}{bcolors.ENDC} - {bcolors.OKCYAN}Precio min: {info["lowPrice"]}{bcolors.ENDC}
                {bcolors.WARNING}--------------------------------------------------{bcolors.ENDC}
                """
                alerts.append(alert_message)

    # FAST SHORT
    if knumber >= 3:
        inicial = float(klines[knumber - 2][4])
        final = float(klines[knumber][4])
        if inicial < final:
            result = round(((final - inicial) / inicial) * 100, 2)
            if result >= variacionfast:
                info = infoticks(tick)
                volumen = float(info['quoteVolume'])
                alert_message = f"""
                {bcolors.WARNING}--------------------------------------------------{bcolors.ENDC}
                {bcolors.FAIL}{current_time} - **FAST SHORT!**: {tick}{bcolors.ENDC}
                [Binance Futures](https://www.binance.com/es/futures/{tick}/) - [Bitget Futures](https://www.bitget.com/futures/usdt/{tick}/)
                {bcolors.OKCYAN}Variación: {result}%{bcolors.ENDC} - {bcolors.OKCYAN}Volumen: {human_format(volumen)}{bcolors.ENDC}
                {bcolors.OKCYAN}Precio max: {info["highPrice"]}{bcolors.ENDC} - {bcolors.OKCYAN}Precio min: {info["lowPrice"]}{bcolors.ENDC}
                {bcolors.WARNING}--------------------------------------------------{bcolors.ENDC}
                """
                alerts.append(alert_message)

    # Generar señales técnicas (si es necesario mostrar algo de generate_signals en la UI, adaptarlo aquí)
    technical_signals = generate_signals(tick, klines) # Asumo que generate_signals existe y funciona

    return alerts # Retornar la lista de alertas

# --- Interfaz de Streamlit ---
st.title("Alertas de Criptomonedas Binance Futures")
st.write("Monitoreando variaciones de precios en Binance Futures en tiempo real.")

alertas_totales = [] # Lista para acumular todas las alertas de todos los ticks

with st.spinner('Buscando ticks y analizando...'): # Mostrar un spinner mientras se procesa
    ticks = buscarticks()
    st.write(f"Número de monedas encontradas en par USDT: {len(ticks)}") # Mostrar info en Streamlit

    for tick in ticks:
        klines = get_klines(tick)
        if klines: # Verificar si se obtuvieron klines correctamente
            alertas_tick = analizar_klines_streamlit(tick, klines, 29) # Analizar con la última vela (índice 29 en lista de 30)
            if alertas_tick: # Si hay alertas para este tick
                alertas_totales.extend(alertas_tick) # Añadir alertas a la lista total
        else:
            st.error(f"No se pudieron obtener klines para {tick}. Skipping...") # Mostrar error si no hay klines

if alertas_totales: # Si hay alertas en total
    st.header("Alertas Encontradas:")
    for alerta in alertas_totales:
        st.markdown(alerta, unsafe_allow_html=True) # Mostrar cada alerta con formato Markdown y HTML (para colores)
else:
    st.info("No se encontraron alertas en este momento.") # Mensaje si no hay alertas

st.caption("Información obtenida de Binance Futures en tiempo real (aproximado).")
