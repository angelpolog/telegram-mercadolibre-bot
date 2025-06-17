import os
import telegram
from flask import Flask, request
import logging

# Configuración básica de logging para ver qué está pasando
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# --- Configuración desde Variables de Entorno (Secrets) ---
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID') # ID del chat a donde enviarás las notificaciones

# --- Inicialización de la App ---
app = Flask(__name__)

# Inicializa el bot de Telegram solo si el token está presente
if TELEGRAM_BOT_TOKEN:
    bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)
    logging.info("Bot de Telegram inicializado.")
else:
    logging.warning("TELEGRAM_BOT_TOKEN no encontrado. El bot no funcionará.")
    bot = None

@app.route('/')
def index():
    return "El bot está vivo!", 200

@app.route('/mercadolibre/notifications', methods=['POST'])
def mercadolibre_notifications():
    notification_data = request.json
    logging.info(f"Notificación recibida de Mercado Libre: {notification_data}")

    if not bot:
        logging.error("El bot de Telegram no está inicializado. No se puede enviar el mensaje.")
        return {"status": "error", "message": "Bot no configurado"}, 500

    # Procesa la notificación de Mercado Libre
    if notification_data and notification_data.get('topic') == 'items':
        resource_url = notification_data.get('resource')
        if resource_url:
            item_id = resource_url.split('/')[-1]

            # Prepara y envía el mensaje
            message = f"🔔 ¡Alerta Mercado Libre! Hubo una actualización en el producto con ID: {item_id}"

            if TELEGRAM_CHAT_ID:
                try:
                    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
                    logging.info(f"Notificación enviada a Telegram al chat ID: {TELEGRAM_CHAT_ID}")
                except Exception as e:
                    logging.error(f"Error al enviar el mensaje a Telegram: {e}")
            else:
                logging.warning("TELEGRAM_CHAT_ID no está configurado. No se envió la notificación.")

    return {"status": "ok"}, 200

if __name__ == '__main__':
    # Fly.io usa la variable de entorno PORT
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)