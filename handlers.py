import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
import time

from config import WELCOME_MESSAGE, HELP_MESSAGE, CHOOSING_STYLE, CUSTOMIZING_STYLE, SELECTING_CHAR
from utils import transform_text, get_all_styles, get_stylish_char_by_index
from ui_components import show_all_styled_names, show_style_combinations, show_name_styles_grid, show_char_grid
from telegram.error import TimedOut, NetworkError

# Set up logging
logger = logging.getLogger(__name__)

# Welcome image URL
WELCOME_IMAGE_URL = "https://telegra.ph/httpsyoutubeZrpEIw8IWwksiQlfLq0IxVxjEYpQq-05-11"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send welcome message with image and buttons when the command /start is issued."""
    try:
        logger.debug("Start command received")
        # Create a simpler menu with generate options
        keyboard = [
            [
                InlineKeyboardButton("🔥 Just type any name to style it! 🔥", callback_data="info_auto_style")
            ],
            [
                InlineKeyboardButton("✨ Example Styles Gallery ✨", callback_data="generate_name")
            ],
            [
                InlineKeyboardButton("👤 Our Channel", url="https://t.me/chamber_of_heart1")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        welcome_text = f"{WELCOME_MESSAGE}\n\n✅ Simply type any name or text and I'll instantly style it for you!"
        
        try:
            logger.debug("Attempting to send photo message")
            # Send image
            await update.message.reply_photo(
                photo=WELCOME_IMAGE_URL,
                caption=welcome_text,
                reply_markup=reply_markup
            )
            logger.debug("Photo message sent successfully")
        except Exception as e:
            logger.error(f"Failed to send photo: {e}")
            # Fallback to text-only message
            logger.debug("Attempting to send text-only message")
            await update.message.reply_text(
                welcome_text,
                reply_markup=reply_markup
            )
            logger.debug("Text-only message sent successfully")
    except Exception as e:
        logger.error(f"Error in start command: {e}")
        # Fallback to simple text message if everything else fails
        await update.message.reply_text(
            "Welcome to Stylish Text Bot! Just type any name and I'll style it for you instantly."
        )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send help message when the command /help is issued."""
    try:
        await update.message.reply_text(HELP_MESSAGE)
    except Exception as e:
        logger.error(f"Error in help command: {e}")
        await update.message.reply_text("For help, use the menu buttons or type /style to style text.")

async def style_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start the style selection process."""
    keyboard = []
    styles = get_all_styles()
    
    # Create keyboard with style options
    for i in range(0, len(styles), 2):
        row = []
        row.append(InlineKeyboardButton(f"Style {i+1}", callback_data=f"style_{i}"))
        if i + 1 < len(styles):
            row.append(InlineKeyboardButton(f"Style {i+2}", callback_data=f"style_{i+1}"))
        keyboard.append(row)
    
    # Add a back button
    keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="back_to_start")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("✨ Please choose a style:", reply_markup=reply_markup)
    return CHOOSING_STYLE

async def custom_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start the custom style creation process."""
    await update.message.reply_text("✏️ Please enter the text you want to style:")
    return CUSTOMIZING_STYLE

async def char_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show stylish characters grid."""
    return await show_char_grid(update.message, update=update)

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text input from users."""
    try:
        text = update.message.text
        context.user_data['input_text'] = text
        
        # Always process input as a name to style regardless of mode
        logger.debug(f"Processing text for styling: {text[:10]}...")
        
        # Show a comprehensive grid with both name styles and character styles
        try:
            return await show_all_styled_names(update.message, text)
        except (TimedOut, NetworkError) as e:
            logger.error(f"Network error when generating styled names: {e}")
            # Retry after a short delay
            await update.message.reply_text("⚠️ Network issue detected. Retrying...")
            time.sleep(2)
            try:
                return await show_all_styled_names(update.message, text)
            except Exception as retry_e:
                logger.error(f"Failed to generate styled names after retry: {retry_e}")
                await update.message.reply_text("⚠️ Sorry, I couldn't process your request. Please try again later.")
                return
        except Exception as e:
            logger.error(f"Error generating styled names: {e}")
            await update.message.reply_text("⚠️ Sorry, I couldn't generate styled names. Please try again with different text.")
            return
    except Exception as e:
        logger.error(f"Unexpected error in handle_text: {e}")
        try:
            await update.message.reply_text("⚠️ Something went wrong. Please try again.")
        except:
            pass
        return 