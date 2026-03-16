import os
import threading
from flask import Flask
from telebot import TeleBot
from openai import OpenAI

# 1. Setup Environment Variables
# These will be pulled from Render's 'Environment Variables' settings
BOT_TOKEN = os.environ.get('BOT_TOKEN')
HF_TOKEN = os.environ.get('HF_TOKEN')

# 2. Initialize OpenAI Client (Hugging Face Router)
client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=HF_TOKEN,
)

bot = TeleBot(BOT_TOKEN)
app = Flask(__name__)

# Flask route to keep Render happy
@app.route('/')
def index():
    return "Bot is running!"

# 3. Telegram Bot Logic
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Hello! I am your AI Chatbot powered by Qwen via Hugging Face. How can I help you today?")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    try:
        # Send a "typing..." action so the user knows the bot is thinking
        bot.send_chat_action(message.chat.id, 'typing')

        # Call the Hugging Face API
        chat_completion = client.chat.completions.create(
            model="Qwen/Qwen2.5-72B-Instruct", # You can change this to the specific model string you prefer
            messages=[
                {"role": "user", "content": message.text}
            ],
            max_tokens=500
        )

        # Extract the response text
        response_text = chat_completion.choices[0].message.content
        bot.reply_to(message, response_text)

    except Exception as e:
        print(f"Error: {e}")
        bot.reply_to(message, "Sorry, I encountered an error processing that request.")

# 4. Run Flask and Bot together
def run_bot():
    bot.polling(none_stop=True)

if __name__ == "__main__":
    # Start the Telegram bot in a separate thread
    threading.Thread(target=run_bot).start()
    
    # Start the Flask server on the port provided by Render
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
