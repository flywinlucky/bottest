import os
import telebot
from flask import Flask, request
from dotenv import load_dotenv
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Încarcă variabilele din fișierul .env
load_dotenv()

# Verifică dacă rulează pe server (dacă RENDER_APP_DOMAIN este setat)
RUNNING_ON_SERVER = bool(os.getenv("RENDER_APP_DOMAIN"))

if RUNNING_ON_SERVER:
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")  # Token-ul din variabilele de mediu
else:
    # Citește token-ul din fișier doar pe localhost
    with open("secretbottoken.txt", "r") as file:
        TOKEN = file.read().strip()

# Inițializează bot-ul
bot = telebot.TeleBot(TOKEN, threaded=False)

# Dacă suntem pe server, inițializăm Flask
if RUNNING_ON_SERVER:
    app = Flask(__name__)

# Comanda /start
@bot.message_handler(commands=['start', 'DA'])
def send_welcome(message):
    bot.reply_to(message, "Salut! Te rog să trimiți ID-ul tău de afiliat.")

# Handler pentru orice mesaj text
@bot.message_handler(func=lambda message: True)
def handle_affiliate_token(message):
    response_text = (
        "Link Name - temkatut.com\n"
        "Referral Link - https://www.temkatut.com/\n"
        "Clicks - 7653\n"
        "Revenue - 550$\n"
        "Revenue Share (%) - 50%"
    )
    bot.reply_to(message, response_text)

# Handler pentru callback-urile inline keyboard
@bot.callback_query_handler(func=lambda call: call.data == "show_links")
def show_links(call):
    response_text = (
        "Link Name - temkatut.com\n"
        "Referral Link - https://www.temkatut.com/\n"
        "Clicks - 7653\n"
        "Revenue - 550$\n"
        "Revenue Share (%) - 50%"
    )
    bot.send_message(call.message.chat.id, response_text)

# Endpoint pentru webhook (doar pe server)
if RUNNING_ON_SERVER:
    @app.route('/' + TOKEN, methods=['POST'])
    def webhook():
        json_str = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_str)
        bot.process_new_updates([update])
        return "OK", 200

    @app.route('/', methods=['GET', 'POST'])
    def index():
        bot.remove_webhook()
        bot.set_webhook(url=f"https://{os.getenv('RENDER_APP_DOMAIN')}/{TOKEN}")
        return "Webhook set!", 200

# Pornirea corectă a botului
if __name__ == "__main__":
    if RUNNING_ON_SERVER:
        # Rulează Flask pe server
        app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
    else:
        # Rulează local cu polling
        bot.remove_webhook()
        print("Bot running in polling mode (local)...")
        bot.polling(none_stop=True)
