# bot.py
import asyncio
import signal
import nest_asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)
from database import init_db, add_user, get_all_users

import os
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# ----------------------------
# Handlers
# ----------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    chat_id = update.effective_chat.id

    added = await add_user(chat_id, user_name)
    if added:
        await update.message.reply_text(f"👋 Hi {user_name}! You’ve been added to the database.")
    else:
        await update.message.reply_text(f"👋 Hi {user_name}! You are already registered.")

async def users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    all_users = await get_all_users()
    if not all_users:
        await update.message.reply_text("No users found yet.")
    else:
        user_list = "\n".join([f"• {name}" for name in all_users])
        await update.message.reply_text(f"📋 Registered users:\n{user_list}")

async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("Say Hi 👋", callback_data="hi"),
            InlineKeyboardButton("Say Bye 👋", callback_data="bye")
        ]
    ]
    await update.message.reply_text("Choose an option:", reply_markup=InlineKeyboardMarkup(keyboard))

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "hi":
        await query.edit_message_text("You pressed 👋 Hi!")
    elif query.data == "bye":
        await query.edit_message_text("You pressed 👋 Bye!")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"You said: {update.message.text}")

# ----------------------------
# Main function
# ----------------------------
def main():
    nest_asyncio.apply()  # Prevent "event loop already running" issues on Windows
    loop = asyncio.get_event_loop()

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Register handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("users", users))
    app.add_handler(CommandHandler("buttons", buttons))
    app.add_handler(CallbackQueryHandler(button_click))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Graceful shutdown on Ctrl+C
    def stop_signal_handler(signum, frame):
        print("\n🛑 Stopping bot...")
        loop.create_task(app.stop())  # Stops polling gracefully

    signal.signal(signal.SIGINT, stop_signal_handler)
    signal.signal(signal.SIGTERM, stop_signal_handler)

    print("🤖 Bot initializing...")
    loop.run_until_complete(init_db())
    print("✅ Bot polling started... Waiting for messages.")

    try:
        app.run_polling()
    except RuntimeError as e:
        print(f"⚠️ Runtime error: {e}")
    finally:
        print("✅ Bot stopped cleanly.")

# ----------------------------
if __name__ == "__main__":
    main()

