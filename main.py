import telegram
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup

TOKEN = '7240022324:AAGciK3XjufQJvL4VqP4aIgJKcUGNNeNiTY'  # Replace with your actual Telegram bot token
BOT_USERNAME = '@protopulpitbot'


async def send_options(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = "Hello from Pulpit, how can I assist you?"

    markup = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Post Ride", callback_data="post_ride"),
            InlineKeyboardButton("Queries", callback_data="queries")
        ]
    ])
    await update.message.reply_text(msg, reply_markup=markup)


async def handle_post_ride(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()  # Acknowledge the callback query

    await query.message.reply_text("Please provide your ride details (origin, destination, date, time, etc.):")

    # Use another message handler to capture ride details
    @context.dispatcher.message_handler(filters.TEXT)
    async def capture_ride_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
        ride_details = update.message.text  # Capture user-provided details
        # Simulate successful ride posting (replace with actual logic)
        await update.message.reply_text("Your ride has been successfully posted!\nDetails:\n" + ride_details)

        # Offer further assistance
        await send_options(update, context)

    # Remove the message handler after capturing details (optional)
    context.dispatcher.remove_handler(capture_ride_details)


async def handle_queries(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()  # Acknowledge the callback query

    # Implement your knowledge base logic here (replace with placeholder)
    answer = "Sorry, I'm still under development for handling queries. Stay tuned!"

    await query.message.reply_text(answer)

    # Offer further assistance
    await send_options(update, context)


async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    if query.data == "post_ride":
        await handle_post_ride(update, context)
    elif query.data == "queries":
        await handle_queries(update, context)


if __name__ == '__main__':
    app = Application.builder().token(TOKEN).build()

    # Handle all text messages
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, send_options))

    # Handle callback queries
    app.add_handler(CallbackQueryHandler(handle_callback_query))

    print(f'Bot @{BOT_USERNAME} is polling...')
    app.run_polling()
