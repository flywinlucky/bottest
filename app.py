import os
import telebot
from flask import Flask, request
from dotenv import load_dotenv

# Încarcă variabilele din fișierul .env
load_dotenv()

# Token-ul botului
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Inițializează bot-ul cu threaded=False
bot = telebot.TeleBot(TOKEN, threaded=False)

# Inițializează aplicația Flask
app = Flask(__name__)

# Comanda /start
@bot.message_handler(commands=['start', 'Start'])
def send_welcome(message):
    bot.reply_to(message, "Salut! Sunt un bot simplu și sunt aici să te ajut.")

# Endpoint pentru webhook
@app.route('/' + TOKEN, methods=['POST'])
def webhook():
    json_str = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "OK", 200

# Setează webhook-ul
@app.route('/', methods=['GET', 'POST'])
def index():
    bot.remove_webhook()
    bot.set_webhook(url=f"https://{os.getenv('RENDER_APP_DOMAIN')}/{TOKEN}")
    return "Bot is running!", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
