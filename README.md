## Alertas de Movimiento de Criptomonedas

Este script de Python utiliza la API de Binance para escanear el mercado de futuros de criptomonedas y generar alertas de compra/venta basadas en la variación porcentual del precio y en indicadores técnicos como medias móviles (SMA), RSI y MACD.

**Características:**

* Escanea automáticamente el mercado de futuros de Binance en busca de oportunidades de trading.
* Genera alertas de compra (LONG) y venta (SHORT) basadas en la variación porcentual del precio en intervalos de tiempo específicos.
* Incorpora indicadores técnicos (SMA, RSI, MACD) para obtener señales de trading más sólidas.
* Calcula el punto de entrada sugerido para las señales de compra basado en el volumen de operaciones.
* Proporciona información adicional sobre el símbolo, la variación, el volumen y los precios máximo y mínimo.

**Instalación:**

1. Clona este repositorio:

   ```bash
   git clone https://github.com/iberi22/-Alertas-de-Movimiento-Binance-Futuros.git
   ```

2. Instala las dependencias:

   ```bash
   pip install python-binance pandas
   ```

3. Configura tus claves API de Binance:

   * Abre el archivo `main.py`.
   * Reemplaza las cadenas vacías (`''`) en la línea `client = Client('', '', tld='com')` con tus claves API y secret key de Binance.

**Uso:**

1. Ejecuta el script:

   ```bash
   python main.py
   ```

2. El script comenzará a escanear el mercado de futuros y generará alertas en la consola cuando se cumplan las condiciones definidas.

**Redes sociales:**

* Sígueme en Kick: [https://kick.com/donberi](https://kick.com/donberi)
* Sígueme en X (Twitter): [https://x.com/x_donberi](https://x.com/x_donberi)

**Advertencia:**

El trading de criptomonedas conlleva un alto riesgo. Este script es solo una herramienta de análisis y no debe considerarse como asesoramiento financiero. Realiza tu propia investigación y utiliza este script bajo tu propio riesgo.

**Contribuciones:**

¡Las contribuciones son bienvenidas! Si tienes alguna idea para mejorar este script o encuentras algún error, no dudes en abrir un issue o enviar un pull request.

**Licencia:**

Este proyecto está licenciado bajo la Licencia MIT. Consulta el archivo `LICENSE` para obtener más información.

**¡Happy trading!**
Codigo modificado con LLMs
**Codigo Original By El Gafastrading!**
https://github.com/ElGafasTrading/movement-alerts
script.py no modificado (Solo alertas por volumen)
