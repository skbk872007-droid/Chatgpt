import os
import logging
import requests
from urllib.parse import quote
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# ── Configuration ─────────────────────────────────────────────────────────────
BOT_TOKEN = os.environ.get("BOT_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN")
CHATGPT_API = "https://gpt-3-5.apis-bj-devs.workers.dev/"

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


# ── Helpers ───────────────────────────────────────────────────────────────────
def ask_chatgpt(prompt: str) -> str:
    """Send a prompt to the ChatGPT API and return the text response."""
    try:
        url = f"{CHATGPT_API}?prompt={quote(prompt)}"
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()
        if data.get("status") and data.get("reply"):
            return data["reply"].strip()
        return "⚠️ Empty response from ChatGPT."
    except requests.exceptions.Timeout:
        return "⏳ Request timed out. Please try again."
    except requests.exceptions.RequestException as e:
        logger.error("ChatGPT API error: %s", e)
        return "❌ Failed to reach the ChatGPT API. Try again later."


# ── Handlers ──────────────────────────────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "👋 Hello! I'm an AI assistant powered by *ChatGPT (GPT-3.5)*.\n\n"
        "Just send me any message and I'll respond!\n\n"
        "Commands:\n"
        "/start — Show this message\n"
        "/help  — How to use the bot\n"
        "/clear — Clear your chat context",
        parse_mode="Markdown",
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "🤖 *How to use this bot:*\n\n"
        "Simply type any question or message and I'll reply using Gemini AI.\n\n"
        "Examples:\n"
        "• _What is machine learning?_\n"
        "• _Write a poem about the sea_\n"
        "• _Translate 'hello' to Spanish_",
        parse_mode="Markdown",
    )


async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data.clear()
    await update.message.reply_text("🗑️ Context cleared! Starting fresh.")


async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_message = update.message.text
    user_name = update.effective_user.first_name
    logger.info("Message from %s: %s", user_name, user_message)

    waiting_msg = await update.message.reply_text("⏳ Please wait, I'm thinking...")

    reply = ask_chatgpt(user_message)

    await waiting_msg.delete()

    await update.message.reply_text(reply)

# ── Main ──────────────────────────────────────────────────────────────────────
def main() -> None:
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("clear", clear))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

    logger.info("Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
    
