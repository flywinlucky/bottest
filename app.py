import os
import telebot
from flask import Flask, request
from dotenv import load_dotenv

# Încarcă variabilele din fișierul .env
load_dotenv()

# Verifică dacă este pe server (dacă RENDER_APP_DOMAIN este setat)
if os.getenv("RENDER_APP_DOMAIN"):
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")  # Token-ul din variabilele de mediu
else:
    # Citeste token-ul din fisierul secretbottoken.txt
    with open("secretbottoken.txt", "r") as file:
        TOKEN = file.read().strip()

# Inițializează bot-ul cu threaded=False
bot = telebot.TeleBot(TOKEN, threaded=False)

# Inițializează aplicația Flask
app = Flask(__name__)

# Comanda /start
@bot.message_handler(commands=['start', 'DA'])
def send_welcome(message):
    bot.reply_to(message, "Salut!")

# Endpoint pentru webhook
@app.route('/' + TOKEN, methods=['POST'])
def webhook():
    json_str = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "OK", 200

# Setează webhook-ul sau rulează local
@app.route('/', methods=['GET', 'POST'])
def index():
    if os.getenv("RENDER_APP_DOMAIN"):
        bot.remove_webhook()
        bot.set_webhook(url=f"https://{os.getenv('RENDER_APP_DOMAIN')}/{TOKEN}")
        return "Webhook set!", 200
    else:
        return "Bot is running in local mode! Webhook not set.", 200

if __name__ == "__main__":
    bot.polling(none_stop=True)
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))

