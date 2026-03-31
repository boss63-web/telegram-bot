from telegram import (
    Update,
    ReplyKeyboardMarkup,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

TOKEN = "8660116841:AAHYRppOiooGqZoLVT-ElgATAwwrfXZSCCg"
ADMIN_ID = 1353810188

users = {}
pending_deposits = {}

# -------- MENU --------
def menu():
    return ReplyKeyboardMarkup(
        [
            ["💰 Deposit"],
            ["🎮 Play"]
        ],
        resize_keyboard=True
    )

# -------- START --------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    users[user_id] = {"step": None}

    await update.message.reply_text(
        "Welcome 👋",
        reply_markup=menu()
    )

# -------- HANDLE TEXT --------
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    # -------- DEPOSIT --------
    if text == "💰 Deposit":
        users[user_id]["step"] = "enter_amount"
        await update.message.reply_text("💰 Enter deposit amount:")

    elif users.get(user_id, {}).get("step") == "enter_amount":
        if text.isdigit():
            amount = int(text)

            pending_deposits[user_id] = {
                "amount": amount,
                "photo": None
            }

            users[user_id]["step"] = "waiting_photo"
            await update.message.reply_text("📸 Send payment screenshot")
        else:
            await update.message.reply_text("❌ Enter valid amount")

    # -------- PLAY BUTTON --------
    elif text == "🎮 Play":
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔥 Play Now", url="https://ahmedsgame.netlify.app/")]
        ])

        await update.message.reply_text(
            "🎮 Click below to start:",
            reply_markup=keyboard
        )

# -------- HANDLE PHOTO --------
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if users.get(user_id, {}).get("step") == "waiting_photo":
        photo = update.message.photo[-1].file_id
        pending_deposits[user_id]["photo"] = photo

        amount = pending_deposits[user_id]["amount"]

        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ Approve", callback_data=f"approve_{user_id}"),
                InlineKeyboardButton("❌ Reject", callback_data=f"reject_{user_id}")
            ]
        ])

        await context.bot.send_photo(
            chat_id=ADMIN_ID,
            photo=photo,
            caption=f"Deposit Request\nUser: {user_id}\nAmount: {amount}",
            reply_markup=keyboard
        )

        users[user_id]["step"] = None

        await update.message.reply_text(
            "⏳ Wait until admin approves your payment"
        )

# -------- ADMIN BUTTONS --------
async def handle_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if update.effective_user.id != ADMIN_ID:
        return

    data = query.data

    # APPROVE
    if data.startswith("approve_"):
        user_id = int(data.split("_")[1])

        if user_id in pending_deposits:
            pending_deposits.pop(user_id)

            await context.bot.send_message(
                user_id,
                "✅ Deposited successfully"
            )

            await query.edit_message_caption("✅ Approved")

    # REJECT
    elif data.startswith("reject_"):
        user_id = int(data.split("_")[1])

        if user_id in pending_deposits:
            pending_deposits.pop(user_id)

            await context.bot.send_message(
                user_id,
                "❌ Please first make a payment"
            )

            await query.edit_message_caption("❌ Rejected")

# -------- MAIN --------
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(CallbackQueryHandler(handle_admin))

    print("Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()