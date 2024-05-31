import telegram
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup

TOKEN = '7240022324:AAGciK3XjufQJvL4VqP4aIgJKcUGNNeNiTY'  # Replace with your actual Telegram bot token
BOT_USERNAME = '@protopulpitbot'

# Define the knowledge base for FAQs
FAQS = {
    "How do I book a ride?": "To book a ride, open the [app](https://play.google.com/store/apps/details?id=com.pulpit.travel_driver_pulpit) and click on 'Book a Ride'. Enter your pickup and drop-off locations, and choose your preferred ride type.",
    "What are the payment options?": "Our [app](https://play.google.com/store/apps/details?id=com.pulpit.travel_driver_pulpit) accept multiple payment options including credit cards, debit cards, and digital wallets.",
    "How can I cancel my ride?": "To cancel your ride, go to 'Your Rides', select the ride you want to cancel, and click on 'Cancel Ride'. For more queries visit our [app](https://play.google.com/store/apps/details?id=com.pulpit.travel_driver_pulpit)",
    "Is there a customer support number?": "Yes,  For more queries visit our [app](https://play.google.com/store/apps/details?id=com.pulpit.travel_driver_pulpit)",
    "What safety measures are in place?": "Our drivers follow all safety protocols including wearing masks, sanitizing the vehicle, and maintaining social distance. For more queries visit our [app](https://play.google.com/store/apps/details?id=com.pulpit.travel_driver_pulpit)"
}

async def send_options(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = "Hello from Pulpit, how can I assist you?"

    markup = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Post Ride", callback_data="post_ride"),
            InlineKeyboardButton("Queries", callback_data="queries")
        ]
    ])

    if update.message:
        await update.message.reply_text(msg, reply_markup=markup)
    elif update.callback_query:
        await update.callback_query.message.reply_text(msg, reply_markup=markup)

async def handle_post_ride(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()  # Acknowledge the callback query

    await query.message.reply_text("Please provide your ride details (origin, destination, date, time, etc.):")

    # Use another message handler to capture ride details
    context.user_data['awaiting_ride_details'] = True

async def capture_ride_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('awaiting_ride_details'):
        ride_details = update.message.text  # Capture user-provided details
        context.user_data['awaiting_ride_details'] = False  # Reset the flag

        # Simulate successful ride posting (replace with actual logic)
        await update.message.reply_text("Your ride has been successfully posted!\nDetails:\n" + ride_details)

        # Offer further assistance
        await send_options(update, context)
    else:
        await send_options(update, context)

async def handle_queries(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()  # Acknowledge the callback query

    # Create a keyboard with the FAQs
    faq_buttons = [[InlineKeyboardButton(question, callback_data=question)] for question in FAQS.keys()]
    markup = InlineKeyboardMarkup(faq_buttons)

    await query.message.reply_text("Here are some frequently asked questions:", reply_markup=markup)

async def handle_faq_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()  # Acknowledge the callback query

    # Retrieve the answer from the FAQS dictionary
    question = query.data
    answer = FAQS.get(question, "Sorry, I don't have an answer for that question.")

    await query.message.reply_text(answer)

    # Offer further assistance
    await send_options(update, context)

async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    if query.data == "post_ride":
        await handle_post_ride(update, context)
    elif query.data == "queries":
        await handle_queries(update, context)
    else:
        await handle_faq_response(update, context)

if __name__ == '__main__':
    app = Application.builder().token(TOKEN).build()

    # Handle all text messages
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, capture_ride_details))

    # Handle callback queries
    app.add_handler(CallbackQueryHandler(handle_callback_query))

    print(f'Bot @{BOT_USERNAME} is polling...')
    app.run_polling()
