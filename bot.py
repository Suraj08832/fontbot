import logging
import time
import signal
import sys
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from telegram.error import TimedOut, NetworkError, TelegramError

from config import BOT_TOKEN
from handlers import start, help_command, style_command, custom_command, char_command, handle_text
from callbacks import handle_callback

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)
logger = logging.getLogger(__name__)

# Global variable to track the application for the watchdog
app = None

def signal_handler(sig, frame):
    """Handle signals to gracefully stop the bot"""
    print('Received signal, stopping bot...')
    if app:
        app.stop()
    sys.exit(0)

# Setup signal handlers
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

class WatchdogError(Exception):
    """Exception raised when the watchdog detects no activity"""
    pass

def error_handler(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)
    
    if isinstance(context.error, NetworkError):
        logger.error("Network error occurred: %s", context.error)
        # Wait a bit before retrying
        time.sleep(1)
    elif isinstance(context.error, TimedOut):
        logger.error("Request timed out: %s", context.error)
        # Wait a bit before retrying
        time.sleep(5)
    elif isinstance(context.error, TelegramError):
        logger.error("Telegram API error: %s", context.error)

def main():
    """Start the bot."""
    global app
    
    # Create the Application with optimized connection parameters
    builder = Application.builder().token(BOT_TOKEN)
    
    # Set connection pool parameters
    builder.connection_pool_size(8)  # Default is 1
    builder.connect_timeout(15.0)     # Default is 5.0
    builder.read_timeout(10.0)        # Default is None
    builder.write_timeout(10.0)       # Default is None
    
    # Build application
    app = builder.build()
    
    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("style", style_command))
    app.add_handler(CommandHandler("custom", custom_command))
    app.add_handler(CommandHandler("char", char_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(CallbackQueryHandler(handle_callback))
    
    # Add error handler
    app.add_error_handler(error_handler)
    
    # Start the Bot
    print("Starting bot...")
    
    # Start the Bot with optimization
    app.run_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True,  # Don't process updates that happened while the bot was offline
        pool_timeout=30,           # How long to wait for the next update
        timeout=15,                # Timeout for long polling
        read_timeout=15            # Read timeout for getting updates
    )

if __name__ == '__main__':
    try:
        # Start the main function
        main()
    except KeyboardInterrupt:
        print("Bot stopped by user")
    except Exception as e:
        print(f"Error: {e}")
        # If the bot crashes, restart it after a short delay
        time.sleep(5)
        print("Restarting bot...")
        main()
    finally:
        print("Bot stopped") 