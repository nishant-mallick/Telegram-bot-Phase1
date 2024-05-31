import telegram
from telegram.ext import Application, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup

TOKEN = '7240022324:AAGciK3XjufQJvL4VqP4aIgJKcUGNNeNiTY'  # Replace with your actual Telegram bot token
BOT_USERNAME = '@protopulpitbot'
SUPPORT_GROUP_CHAT_ID = -1002162203436  # Replace with the actual chat ID of the support group

# Define the knowledge base for FAQs
FAQS = {
    "How do I book a ride?": "To book a ride, open the [app](https://play.google.com/store/apps/details?id=com.pulpit.travel_driver_pulpit) and click on 'Book a Ride'. Enter your pickup and drop-off locations, and choose your preferred ride type.",
    "What are the payment options?": "Our [app](https://play.google.com/store/apps/details?id=com.pulpit.travel_driver_pulpit) accept multiple payment options including credit cards, debit cards, and digital wallets.",
    "How can I cancel my ride?": "To cancel your ride, go to 'Your Rides', select the ride you want to cancel, and click on 'Cancel Ride'. For more queries visit our [app](https://play.google.com/store/apps/details?id=com.pulpit.travel_driver_pulpit)",
    "Is there a customer support number?": "Yes,  For more queries visit our [app](https://play.google.com/store/apps/details?id=com.pulpit.travel_driver_pulpit)",
    "What safety measures are in place?": "Our drivers follow all safety protocols including wearing masks, sanitizing the vehicle, and maintaining social distance. For more queries visit our [app](https://play.google.com/store/apps/details?id=com.pulpit.travel_driver_pulpit)"
}

# A dictionary to map support group message IDs to user IDs
message_id_to_user_id = {}

# Function to notify agents
async def notify_agents(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.callback_query.from_user
    context.user_data['user_id'] = user.id
    context.user_data['username'] = user.username
    context.user_data['in_chat'] = True

    await context.bot.send_message(
        chat_id=SUPPORT_GROUP_CHAT_ID,
        text=f"User {user.username} ({user.id}) needs assistance. Please respond to them directly."
    )
    end_chat_button = InlineKeyboardMarkup([[InlineKeyboardButton("End Chat", callback_data=f"end_chat_{user.id}")]])
    await context.bot.send_message(
        chat_id=SUPPORT_GROUP_CHAT_ID,
        text="Press the button below when you want to end the chat.",
        reply_markup=end_chat_button
    )

    end_chat_button_user = InlineKeyboardMarkup([[InlineKeyboardButton("End Chat", callback_data=f"end_chat_{user.id}")]])
    await update.callback_query.message.reply_text("You are now connected to an agent. Press 'End Chat' to finish.", reply_markup=end_chat_button_user)

async def send_options(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('in_chat', False):
        return  # Do not send options if in chat with agent

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

    context.user_data['awaiting_ride_details'] = True

async def capture_ride_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('awaiting_ride_details'):
        ride_details = update.message.text  # Capture user-provided details
        context.user_data['awaiting_ride_details'] = False  # Reset the flag

        # Simulate successful ride posting (replace with actual logic)
        await update.message.reply_text("Your ride has been successfully posted!\nDetails:\n" + ride_details)

        # Offer further assistance
        await send_options(update, context)
    elif context.user_data.get('in_chat'):
        # Forward the user's message to the support group
        user_id = context.user_data['user_id']
        username = context.user_data['username']
        message = update.message.text
        sent_message = await context.bot.send_message(
            chat_id=SUPPORT_GROUP_CHAT_ID,
            text=f"Message from {username} ({user_id}): {message}"
        )
        # Map the sent message ID to the user ID
        message_id_to_user_id[sent_message.message_id] = user_id
    else:
        await send_options(update, context)

async def handle_agent_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat_id == SUPPORT_GROUP_CHAT_ID:
        # Check if the message is a reply to a forwarded user message
        if update.message.reply_to_message:
            original_message_id = update.message.reply_to_message.message_id
            user_id = message_id_to_user_id.get(original_message_id)
            if user_id:
                # Forward the message from the agent to the user
                message = update.message.text
                await context.bot.send_message(chat_id=user_id, text=message)

async def handle_queries(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()  # Acknowledge the callback query

    # Create a keyboard with the FAQs and "Talk with Agent" option
    faq_buttons = [[InlineKeyboardButton(question, callback_data=question)] for question in FAQS.keys()]
    faq_buttons.append([InlineKeyboardButton("Talk with Agent", callback_data="talk_with_agent")])
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

async def handle_talk_with_agent(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()  # Acknowledge the callback query

    # Inform the user that they will be connected to an agent
    await query.message.reply_text("Connecting you to an agent...")

    # Mark the user as in chat
    context.user_data['in_chat'] = True

    # Notify the support team
    await notify_agents(update, context)

async def handle_end_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()  # Acknowledge

    user_id = query.data.split("_")[-1]
    
    if 'in_chat' in context.user_data and context.user_data.get('in_chat'):
        # Mark the user as no longer in chat
        context.user_data['in_chat'] = False

        # Notify both user and support team
        await context.bot.send_message(chat_id=user_id, text="The chat has been ended by the agent. How can I assist you further?")
        await context.bot.send_message(chat_id=SUPPORT_GROUP_CHAT_ID, text=f"Chat with user {user_id} has ended.")
    
        # Offer main menu options again
        await send_options(update, context)
    else:
        await query.message.reply_text("No active chat found to end.")

async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    if query.data == "post_ride":
        await handle_post_ride(update, context)
    elif query.data == "queries":
        await handle_queries(update, context)
    elif query.data == "talk_with_agent":
        await handle_talk_with_agent(update, context)
    elif query.data.startswith("end_chat"):
        await handle_end_chat(update, context)
    else:
        await handle_faq_response(update, context)

if __name__ == '__main__':
    app = Application.builder().token(TOKEN).build()

    # Handle all text messages from users
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & ~filters.Chat(SUPPORT_GROUP_CHAT_ID), capture_ride_details))

    # Handle all text messages from support agents
    app.add_handler(MessageHandler(filters.TEXT & filters.Chat(SUPPORT_GROUP_CHAT_ID), handle_agent_message))

    # Handle callback queries
    app.add_handler(CallbackQueryHandler(handle_callback_query))

    print(f'Bot @{BOT_USERNAME} is polling...')
    app.run_polling()
