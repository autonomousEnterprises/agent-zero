import asyncio
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from agent import Agent, AgentConfig
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
async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("Hi! I'm your AI agent. How can I assist you today?")

# Handle user messages
async def handle_message(update: Update, context: CallbackContext) -> None:
    user_input = update.message.text.strip()

    # Send the user's message to the agent
    assistant_response = agent0.message_loop(user_input)

    # Send the response back to the user
    await update.message.reply_text(assistant_response)

# Error handler
async def error(update: Update, context: CallbackContext) -> None:
    logger.warning(f"Update {update} caused error {context.error}")

# Main function to set up the bot
async def main():
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TOKEN).build()

    # Set up command and message handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Log all errors
    application.add_error_handler(error)

    # Start the bot
    await application.initialize()
    await application.start()
    await application.updater.start_polling()

    # Wait for shutdown signal
    await application.stop()
    await application.shutdown()

if __name__ == '__main__':
    print("Starting Telegram bot...")

    # Check if an event loop is already running
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        # If an event loop is already running, run the bot using `create_task`
        loop.create_task(main())
    else:
        # If no event loop is running, use `asyncio.run()`
        asyncio.run(main())
