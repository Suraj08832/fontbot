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
    """Send a message when the command /start is issued."""
    keyboard = [
        [
            InlineKeyboardButton("🎨 Font Bot", url="https://t.me/Fonts_designer_bot"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    welcome_text = (
        "👋 Welcome to the Font Styling Bot!\n\n"
        "If you want to convert your normal name to a stylish font, use this bot.\n"
        "After that, send me your stylish name, and I will generate it into a fancy name."
    )
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)

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