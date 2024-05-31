import telegram
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
import nltk
from nltk.chat.util import Chat, reflections

# Ensure NLTK resources are downloaded
nltk.download('punkt')

# Define a set of pairs (input, response) and reflections
pairs = [
    [
        r'hi|hello|hey',
        ['Hello!', 'Hi there!', 'Hey!']
    ],
    [
        r'I need your assistance regarding my order',
        ['Please, provide me with your order id']
    ],
    [
        r'I have a complaint',
        ['Please elaborate on your concern']
    ],
    [
        r'how long it will take to receive an order?',
        ['An order takes 3-5 Business days to get delivered.']
    ],
    [
        r'okay thanks|thank you',
        ['No problem! Have a good day!']
    ],
    [
        r'bye|goodbye',
        ['Bye!', 'Goodbye!']
    ]
]

# Create a Chat object
chatbot = Chat(pairs, reflections)

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

    await query.message.reply_text("Please ask your query:")

    # Use another message handler to capture the query details
    context.user_data['awaiting_query'] = True


async def capture_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('awaiting_query'):
        user_query = update.message.text  # Capture user-provided query
        context.user_data['awaiting_query'] = False  # Reset the flag

        # Process the query using the chatbot
        response = chatbot.respond(user_query)
        if response:
            await update.message.reply_text(response)
        else:
            await update.message.reply_text("I'm sorry, I don't understand that.")

        # Offer further assistance
        await send_options(update, context)
    else:
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
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, capture_ride_details))

    # Handle query text messages
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, capture_query))

    # Handle callback queries
    app.add_handler(CallbackQueryHandler(handle_callback_query))

    print(f'Bot @{BOT_USERNAME} is polling...')
    app.run_polling()
