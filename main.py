import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes

# Variables de entorno
HF_API_KEY = os.getenv("HF_API_KEY")
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
HF_MODEL = "bigscience/bloomz-560m"

# Memoria de conversación por chat (últimos 10 intercambios)
chat_history = {}
MAX_HISTORY = 10

# Personalidad del bot
BOT_PERSONALITY = (
    "Eres un asistente muy amigable, claro y motivador, "
    "respondiendo de forma humana y cordial."
)

# Función principal de respuesta
async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_message = update.message.text

    if chat_id not in chat_history:
        chat_history[chat_id] = []