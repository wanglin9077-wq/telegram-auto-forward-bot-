import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters
)

# ────────────────
# Load config
# ────────────────
with open("config.json", "r", encoding="utf-8") as f:
    CONFIG = json.load(f)

BOT_TOKEN = CONFIG["BOT_TOKEN"]
SOURCE_GROUP_ID = CONFIG["SOURCE_GROUP_ID"]

# ────────────────
# User data handling
# ────────────────
def load_users():
    try:
        with open("users.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def save_users(data):
    with open("users.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# ────────────────
# /start command
# ────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🇰🇭 ភាសាខ្មែរ", callback_data="lang_kh")],
        [InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")]
    ]
    await update.message.reply_text(
        "សូមជ្រើសរើសភាសា / Please choose your language:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ────────────────
# Language selection
# ────────────────
async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = str(query.from_user.id)
    users = load_users()
    lang = "kh" if query.data == "lang_kh" else "en"
    users[user_id] = {"language": lang}
    save_users(users)

    if lang == "kh":
        await query.edit_message_text("✅ អរគុណ! បតនឹងប្រើភាសាខ្មែរ។")
    else:
        await query.edit_message_text("✅ Thanks! The bot will use English.")

# ────────────────
# Forward messages from the group
# ────────────────
async def forward_from_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != SOURCE_GROUP_ID:
        return  # Only forward from configured group

    users = load_users()
    for user_id in users.keys():
        try:
            await update.message.copy(chat_id=int(user_id))
        except Exception as e:
            print(f"⚠️ Could not forward to {user_id}: {e}")

# ────────────────
# Run bot
# ────────────────
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(set_language))
    app.add_handler(MessageHandler(filters.ALL, forward_from_group))

    print("🚀 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
