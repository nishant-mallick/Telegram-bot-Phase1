
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

# Define a function to handle the conversation
def chatbot_conversation():
    print("Welcome to the Bot Service! Let me know how can I help you?")
    name = input("Enter your name: ")
    print(f"Hello {name}, how can I assist you today?")
    while True:
        user_input = input(f"{name}: ")
        if user_input.lower() in ['bye', 'goodbye']:
            print("Bot: Bye!")
            break
        else:
            response = chatbot.respond(user_input)
            if response:
                print(f"Bot: {response}")
            else:
                print("Bot: I'm sorry, I don't understand that.")

# Start the conversation
chatbot_conversation()