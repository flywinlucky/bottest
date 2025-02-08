import os
import telebot
import requests
from flask import Flask, request
from dotenv import load_dotenv

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
    affiliate_id = message.text.strip()
    server_url = os.getenv("SERVER_URL", "http://127.0.0.1:5000")
    response = requests.get(f"{server_url}/referral/{affiliate_id}")
    
    if response.status_code == 200:
        referral_data = response.json()
        response_text = (
            f"Link Name - {referral_data['link_name']}\n"
            f"Referral Link - {referral_data['referral_link']}\n"
            f"Clicks - {referral_data['click_count']}\n"
            f"Revenue - {referral_data['income']}$\n"
            f"Revenue Share (%) - {referral_data['revenue_share']}%"
        )
    else:
        response_text = "Referral link not found."
    
    bot.reply_to(message, response_text)

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
