import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler

from config import WELCOME_MESSAGE, HELP_MESSAGE, CHOOSING_STYLE, CUSTOMIZING_STYLE, SELECTING_CHAR
from utils import transform_text, get_all_styles, get_stylish_char_by_index
from ui_components import show_all_styled_names, show_style_combinations, show_name_styles_grid, show_char_grid

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
                InlineKeyboardButton("✨ Generate Stylish Name ✨", callback_data="generate_name")
            ],
            [
                InlineKeyboardButton("🎲 Generate Style Combinations", callback_data="generate_combos")
            ],
            [
                InlineKeyboardButton("👤 Our Channel", url="https://t.me/chamber_of_heart1")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        try:
            logger.debug("Attempting to send photo message")
            # Send image
            await update.message.reply_photo(
                photo=WELCOME_IMAGE_URL,
                caption=f"{WELCOME_MESSAGE}",
                reply_markup=reply_markup
            )
            logger.debug("Photo message sent successfully")
        except Exception as e:
            logger.error(f"Failed to send photo: {e}")
            # Fallback to text-only message
            logger.debug("Attempting to send text-only message")
            await update.message.reply_text(
                f"{WELCOME_MESSAGE}",
                reply_markup=reply_markup
            )
            logger.debug("Text-only message sent successfully")
    except Exception as e:
        logger.error(f"Error in start command: {e}")
        # Fallback to simple text message if everything else fails
        await update.message.reply_text(
            "Welcome to Stylish Text Bot! Tap Generate Stylish Name to get started."
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
    text = update.message.text
    context.user_data['input_text'] = text
    
    if context.user_data.get('mode') == 'generate_name':
        # Show a comprehensive grid with both name styles and character styles
        return await show_all_styled_names(update.message, text)
    elif context.user_data.get('mode') == 'generate_combos':
        # Show combinations of character styles
        return await show_style_combinations(update.message, text)
    else:
        # Fallback to standard name styling
        return await show_name_styles_grid(update.message, text) 