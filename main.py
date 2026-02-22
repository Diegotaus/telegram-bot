import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

HF_API_KEY = os.getenv("HF_API_KEY")
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
HF_MODEL = "bigscience/bloomz-560m"

# Memoria de conversación por chat (mantiene últimas 10 interacciones)
chat_history = {}

MAX_HISTORY = 10  # mantiene solo últimos 10 mensajes por chat

async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_message = update.message.text

    if chat_id not in chat_history:
        chat_history[chat_id] = []

    chat_history[chat_id].append(f"User: {user_message}")

    # Limitar la memoria
    if len(chat_history[chat_id]) > MAX_HISTORY * 2:
        chat_history[chat_id] = chat_history[chat_id][-MAX_HISTORY*2:]

    prompt = "\n".join(chat_history[chat_id]) + "\nAI:"

    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    payload = {"inputs": prompt}

    response = requests.post(
        f"https://api-inference.huggingface.co/models/{HF_MODEL}",
        headers=headers,
        json=payload
    )

    data = response.json()

    if "generated_text" in data[0]:
        text = data[0]["generated_text"].split("AI:")[-1].strip()
    else:
        text = "No entendí 😅"

    chat_history[chat_id].append(f"AI: {text}")

    await update.message.reply_text(text)

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply))
app.run_polling()
