import logging
import time
import signal
import sys
import threading
import datetime
import os
import atexit
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from telegram.error import TimedOut, NetworkError, TelegramError, Conflict

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
# Flag for auto-restart
auto_restart_flag = False
# Path to PID file
PID_FILE = "fontbot.pid"

def check_running_instance():
    """Check if another instance of the bot is already running"""
    if os.path.exists(PID_FILE):
        try:
            with open(PID_FILE, 'r') as f:
                old_pid = int(f.read().strip())
            
            # Check if the process with this PID exists
            try:
                # This will raise an exception if the process doesn't exist
                os.kill(old_pid, 0)
                logger.warning(f"Another instance is already running with PID {old_pid}")
                return True
            except OSError:
                # Process with this PID doesn't exist
                logger.info(f"Removing stale PID file for process {old_pid}")
                os.remove(PID_FILE)
        except Exception as e:
            logger.error(f"Error checking existing instance: {e}")
            os.remove(PID_FILE)
    
    # Create PID file
    try:
        with open(PID_FILE, 'w') as f:
            f.write(str(os.getpid()))
    except Exception as e:
        logger.error(f"Error creating PID file: {e}")
    
    return False

def cleanup_pid_file():
    """Remove the PID file when the bot exits"""
    try:
        if os.path.exists(PID_FILE):
            os.remove(PID_FILE)
            logger.info("PID file removed")
    except Exception as e:
        logger.error(f"Error removing PID file: {e}")

def signal_handler(sig, frame):
    """Handle signals to gracefully stop the bot"""
    print('Received signal, stopping bot...')
    global auto_restart_flag
    auto_restart_flag = False
    cleanup_pid_file()
    if app:
        app.stop()
    sys.exit(0)

# Setup signal handlers
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)
# Register cleanup on exit
atexit.register(cleanup_pid_file)

class WatchdogError(Exception):
    """Exception raised when the watchdog detects no activity"""
    pass

def auto_restart_timer():
    """Timer function to auto-restart the bot every 10 minutes"""
    global app, auto_restart_flag
    
    if not auto_restart_flag:
        return
    
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{current_time}] Auto-restart timer triggered. Restarting bot...")
    
    try:
        if app:
            app.stop()
    except Exception as e:
        print(f"Error stopping app during auto-restart: {e}")
    
    # Schedule the next restart if the flag is still set
    if auto_restart_flag:
        threading.Timer(600, auto_restart_timer).start()  # 600 seconds = 10 minutes

def error_handler(update, context):
    """Log Errors caused by Updates."""
    if update:
        logger.warning('Update "%s" caused error "%s"', update, context.error)
    else:
        logger.warning('An error occurred: %s', context.error)
    
    if isinstance(context.error, NetworkError):
        logger.error("Network error occurred: %s", context.error)
        # Wait a bit before retrying
        time.sleep(1)
    elif isinstance(context.error, TimedOut):
        logger.error("Request timed out: %s", context.error)
        # Wait a bit before retrying
        time.sleep(5)
    elif isinstance(context.error, Conflict):
        logger.error("Conflict error: %s", context.error)
        # For conflict errors, we need to completely restart the bot
        global auto_restart_flag
        auto_restart_flag = False
        if app:
            app.stop()
    elif isinstance(context.error, TelegramError):
        logger.error("Telegram API error: %s", context.error)

def main():
    """Start the bot."""
    global app
    
    # Check if another instance is running
    if check_running_instance():
        logger.error("Another instance of the bot is already running. Exiting.")
        return False
    
    try:
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
        
        # Add additional command handlers for better user experience
        app.add_handler(CommandHandler("name", lambda update, context: custom_command(update, context)))
        app.add_handler(CommandHandler("font", lambda update, context: custom_command(update, context)))
        app.add_handler(CommandHandler("text", lambda update, context: custom_command(update, context)))
        app.add_handler(CommandHandler("generate", lambda update, context: custom_command(update, context)))
        
        # Add handlers for common text inputs (not commands)
        # These filters match if the message contains these phrases
        text_filter_patterns = [
            filters.Regex(r'(?i)generate.*name'),    # "generate name" in any case
            filters.Regex(r'(?i)stylish.*name'),     # "stylish name" in any case
            filters.Regex(r'(?i)font.*style'),       # "font style" in any case
            filters.Regex(r'(?i)style.*text'),       # "style text" in any case
            filters.Regex(r'(?i)style.*combination') # "style combination" in any case
        ]
        
        # Combine all text filters with OR
        combined_text_filter = text_filter_patterns[0]
        for pattern in text_filter_patterns[1:]:
            combined_text_filter = combined_text_filter | pattern
        
        # Add a handler for these common text inputs (not commands)
        app.add_handler(MessageHandler(combined_text_filter & ~filters.COMMAND, start))
        
        # Regular text handler (must be last)
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
        
        # Add callback query handler
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
        
        return True
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
        cleanup_pid_file()
        return False

if __name__ == '__main__':
    retry_count = 0
    max_retries = 5
    
    # Set auto-restart flag
    auto_restart_flag = True
    
    # Start the auto-restart timer
    if auto_restart_flag:
        # Set up timer for first auto-restart (10 minutes from now)
        threading.Timer(600, auto_restart_timer).start()
        print("Auto-restart timer set for every 10 minutes")
    
    while True:  # Infinite loop for continuous operation
        try:
            # Start the main function
            print(f"Starting bot (attempt {retry_count + 1})...")
            success = main()
            
            # If we couldn't start because another instance is running, exit
            if not success:
                print("Could not start bot. Exiting.")
                break
        except KeyboardInterrupt:
            print("Bot stopped by user")
            auto_restart_flag = False
            cleanup_pid_file()
            break
        except (NetworkError, TimedOut) as e:
            retry_count += 1
            wait_time = min(30, 5 * retry_count)  # Increase wait time with each retry, max 30 seconds
            print(f"Network error: {e}. Restarting in {wait_time} seconds... (attempt {retry_count}/{max_retries})")
            time.sleep(wait_time)
        except Conflict as e:
            print(f"Conflict with another bot instance: {e}")
            print("Waiting 30 seconds before trying again...")
            time.sleep(30)
            cleanup_pid_file()  # Remove the PID file since we're likely defunct
        except Exception as e:
            retry_count += 1
            wait_time = min(60, 10 * retry_count)  # Longer wait for more serious errors
            print(f"Critical error: {e}")
            print(f"Restarting bot in {wait_time} seconds... (attempt {retry_count}/{max_retries})")
            time.sleep(wait_time)
        finally:
            if app:
                try:
                    app.stop()
                except:
                    pass
            # Make sure we clean up the PID file if the bot is exiting
            cleanup_pid_file()
        
        # Reset retry count if we've reached the max retries
        if retry_count >= max_retries:
            print("Max retry attempts reached. Resetting retry counter.")
            retry_count = 0
            # Wait a bit longer before the next round of retries
            time.sleep(120)  # 2 minutes
        
        # If auto-restart flag is False, exit the loop
        if not auto_restart_flag:
            break
    
    print("Bot stopped") 