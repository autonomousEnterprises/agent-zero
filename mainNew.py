import threading, time, os, logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from agent import Agent, AgentConfig
from python.helpers.print_style import PrintStyle
import python.helpers.files as files
import models

# Configure logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Telegram bot token
TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"

# Initialize the Agent
def initialize_agent():
    chat_llm = models.get_openai_chat(temperature=0)
    utility_llm = models.get_openai_chat(temperature=0)
    embedding_llm = models.get_embedding_openai()

    config = AgentConfig(
        chat_model=chat_llm,
        utility_model=utility_llm,
        embeddings_model=embedding_llm,
        code_exec_docker_enabled=True,
        code_exec_ssh_enabled=True,
    )

    agent0 = Agent(number=0, config=config)
    return agent0

agent0 = initialize_agent()

# Start command handler
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Hi! I'm your AI agent. How can I assist you today?")

# Handle user messages
def handle_message(update: Update, context: CallbackContext) -> None:
    user_input = update.message.text.strip()
    user_id = update.message.from_user.id

    if user_input.lower() == 'e':
        update.message.reply_text("Goodbye!")
        return

    # Send the user's message to the agent
    assistant_response = agent0.message_loop(user_input)

    # Send the response back to the user
    update.message.reply_text(assistant_response)

# Error handler
def error(update: Update, context: CallbackContext) -> None:
    logger.warning(f"Update {update} caused error {context.error}")

# Main function to set up the bot
def main():
    # Set up the updater and dispatcher
    updater = Updater(TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # Set up command and message handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    dispatcher.add_error_handler(error)

    # Start the bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    print("Starting Telegram bot...")
    main()
