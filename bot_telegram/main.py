import os
import asyncio
from dotenv import load_dotenv
from gradio_client import Client
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
)

load_dotenv()

ALPHA_BOT_TOKEN = os.getenv("ALPHA_BOT_TOKEN", "")
HF_TOKEN = os.getenv("HF_TOKEN", None)
ALPHA_SPACE_ID = os.getenv("ALPHA_SPACE_ID", "magistrigusti/allod-alpha")

hf_client = None


def get_hf_client():
    global hf_client
    if hf_client is None:
        hf_client = Client(ALPHA_SPACE_ID, hf_token=HF_TOKEN)
    return hf_client


def ask_alpha(question):
    try:
        client = get_hf_client()
        result = client.predict(question, api_name="/ask")
        if isinstance(result, str) and result.strip():
            return result.strip()
        return "Нет ответа."
    except Exception as e:
        print(f"[Alpha HF] {e}")
        return "Альфа временно недоступна. Повтори через 30 секунд."


async def start_command(update: Update, context):
    await update.message.reply_text(
        "Приветствую, Лорд!\n"
        "Я Альфа — советник Аллода Зион.\n\n"
        "Просто напиши вопрос."
    )


async def handle_message(update: Update, context):
    text = update.message.text
    if not text or not text.strip():
        return

    await update.message.chat.send_action(ChatAction.TYPING)

    loop = asyncio.get_event_loop()
    answer = await loop.run_in_executor(None, ask_alpha, text.strip())

    await update.message.reply_text(answer)


def main():
    if not ALPHA_BOT_TOKEN:
        print("[Alpha Bot] ALPHA_BOT_TOKEN is not set!")
        return

    app = Application.builder().token(ALPHA_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("[Alpha Bot] Started!")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()