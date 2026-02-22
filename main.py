

    import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes

HF_API_KEY = os.getenv("HF_API_KEY")
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
HF_MODEL = "bigscience/bloomz-560m"

# Memoria de conversación por chat (últimos 10 intercambios)
chat_history = {}
MAX_HISTORY = 10

# Personalidad inicial
BOT_PERSONALITY = "Eres un asistente muy amigable, claro y motivador, siempre respondiendo de forma humana y cordial."

async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_message = update.message.text

    if chat_id not in chat_history:
        chat_history[chat_id] = []

    chat_history[chat_id].append(f"User: {user_message}")

    # Limitar memoria
    if len(chat_history[chat_id]) > MAX_HISTORY * 2:
        chat_history[chat_id] = chat_history[chat_id][-MAX_HISTORY*2:]

    # Prompt con personalidad
    prompt = BOT_PERSONALITY + "\n" + "\n".join(chat_history[chat_id]) + "\nAI:"

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

# Comandos especiales
async def rutina(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("💪 Aquí va tu rutina diaria: 3x15 flexiones, 3x10 sentadillas, 20 min cardio")

async def recordatorio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args:
        await update.message.reply_text("Escribí /recordatorio seguido del mensaje que querés guardar")
    else:
        await update.message.reply_text(f"Recordatorio guardado: {' '.join(args)}")

async def mpf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📚 Pregunta MPF: ¿Cuál es el artículo 222? Respuesta: ... (info de ejemplo)")

app = ApplicationBuilder().token(TOKEN).build()

# Handler de comandos
app.add_handler(CommandHandler("rutina", rutina))
app.add_handler(CommandHandler("recordatorio", recordatorio))
app.add_handler(CommandHandler("MPF", mpf))

# Handler de mensajes normales
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply))

app.run_polling()