import logging
import os
import requests
import random
import itertools
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto, InputFile
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, ConversationHandler, filters
from config import BOT_TOKEN, WELCOME_MESSAGE, HELP_MESSAGE, CHOOSING_STYLE, CUSTOMIZING_STYLE
from utils import transform_text, create_custom_style, get_all_styles, get_stylish_char_by_index, get_styled_text, get_character_style, get_style_combinations
from styles import STYLISH_CHARS, NAME_STYLES, name_styles, character_styles

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Welcome image URL - using a more reliable image source
WELCOME_IMAGE_URL = "https://telegra.ph/httpsyoutubeZrpEIw8IWwksiQlfLq0IxVxjEYpQq-05-11"  # Telegraph image URL

# Add a new state for stylish character selection
CHOOSING_STYLE, CUSTOMIZING_STYLE, SELECTING_CHAR = range(3)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send welcome message with image and buttons when the command /start is issued."""
    try:
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
            # Send image
            await update.message.reply_photo(
                photo=WELCOME_IMAGE_URL,
                caption=f"{WELCOME_MESSAGE}",
                reply_markup=reply_markup
            )
        except Exception as e:
            logger.error(f"Failed to send photo: {e}")
            # Fallback to text-only message
            await update.message.reply_text(
                f"{WELCOME_MESSAGE}",
                reply_markup=reply_markup
            )
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

async def show_char_grid(message, update=None, query=None):
    """Show a grid of stylish characters."""
    # Use all 26 letters in a grid
    letters = list('abcdefghijklmnopqrstuvwxyz')
    
    # Create a 5x5 grid of buttons (plus an extra row for z)
    keyboard = []
    chunk_size = 5  # 5 characters per row
    for i in range(0, len(letters), chunk_size):
        row = []
        for j in range(chunk_size):
            if i + j < len(letters):
                letter = letters[i + j]
                # Show the fancy version of each character in the button text
                fancy_letter = get_stylish_char_by_index(letter, 0)  # Get first style for display
                row.append(InlineKeyboardButton(f"{fancy_letter}", callback_data=f"char_{letter}"))
        keyboard.append(row)
    
    # Add Generate Name button
    keyboard.append([
        InlineKeyboardButton("✨ Generate Stylish Name", callback_data="gen_name_with_chars")
    ])
    
    # Add a back button
    keyboard.append([InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_start")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message_text = "🔤 Choose a character to see all stylish versions or generate a name:"
    
    if query:
        try:
            # Try to edit the message if it's a text message
            await query.edit_message_text(text=message_text, reply_markup=reply_markup)
        except Exception as e:
            try:
                # Try to edit the caption if it's a photo message
                await query.edit_message_caption(caption=message_text, reply_markup=reply_markup)
            except Exception as e:
                logger.error(f"Error editing message: {e}")
                # If all else fails, send a new message
                await query.message.reply_text(text=message_text, reply_markup=reply_markup)
    else:
        await message.reply_text(text=message_text, reply_markup=reply_markup)
    
    return SELECTING_CHAR

async def show_char_styles(update: Update, context: ContextTypes.DEFAULT_TYPE, char=None, query=None):
    """Show all styles for a specific character."""
    if not char and query and query.data.startswith("char_"):
        char = query.data.split("_")[1]
    
    if not char:
        return
    
    # Get all stylish variations of the character
    variants = STYLISH_CHARS.get(char, [char])
    
    # Create a keyboard with all styles in 5x5 grid format
    keyboard = []
    
    # Show all variants in rows of 5
    chunk_size = 5  # 5 variants per row
    for i in range(0, len(variants), chunk_size):
        row = []
        for j in range(chunk_size):
            if i + j < len(variants):
                variant = variants[i + j]
                row.append(InlineKeyboardButton(variant, callback_data=f"copy_{variant}"))
        keyboard.append(row)
    
    # Add name generation with this character style
    keyboard.append([
        InlineKeyboardButton(f"✨ Generate Name with {char.upper()} Styles", callback_data=f"gen_name_with_char_{char}")
    ])
    
    # Add navigation buttons
    keyboard.append([InlineKeyboardButton("🔙 Back to Characters", callback_data="show_chars")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message_text = f"✨ All {len(variants)} stylish versions of '{char}':"
    
    if query:
        try:
            # Try to edit the message if it's a text message
            await query.edit_message_text(text=message_text, reply_markup=reply_markup)
        except Exception as e:
            try:
                # Try to edit the caption if it's a photo message
                await query.edit_message_caption(caption=message_text, reply_markup=reply_markup)
            except Exception as e:
                logger.error(f"Error in show_char_styles: {e}")
                # If all else fails, send a new message
                await query.message.reply_text(text=message_text, reply_markup=reply_markup)
    else:
        await update.message.reply_text(text=message_text, reply_markup=reply_markup)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks."""
    query = update.callback_query
    await query.answer()
    
    if query.data == "generate_name":
        # Prompt user to enter a name to style
        context.user_data['mode'] = 'generate_name'
        try:
            await query.edit_message_text("✏️ Enter your name or text to see all stylish versions (tap any to send for copying):")
        except Exception as e:
            try:
                await query.edit_message_caption(caption="✏️ Enter your name or text to see all stylish versions (tap any to send for copying):")
            except Exception as e:
                logger.error(f"Error in generate_name: {e}")
                await query.message.reply_text("✏️ Enter your name or text to see all stylish versions (tap any to send for copying):")
        return CUSTOMIZING_STYLE
    
    elif query.data == "generate_combos":
        # Prompt user to enter a name for combination styling
        context.user_data['mode'] = 'generate_combos'
        try:
            await query.edit_message_text("✏️ Enter your name or text to see different style combinations (tap any to send for copying):")
        except Exception as e:
            try:
                await query.edit_message_caption(caption="✏️ Enter your name or text to see different style combinations (tap any to send for copying):")
            except Exception as e:
                logger.error(f"Error in generate_combos: {e}")
                await query.message.reply_text("✏️ Enter your name or text to see different style combinations (tap any to send for copying):")
        return CUSTOMIZING_STYLE
    
    elif query.data.startswith("regenerate_combos_"):
        # User wants to regenerate combinations with the same text
        input_text = query.data.replace("regenerate_combos_", "", 1)
        # Store the input text in context
        context.user_data['input_text'] = input_text
        # Show new combinations starting at page 0
        return await show_style_combinations(query.message, input_text, page=0, query=query)
    
    elif query.data.startswith("copy_style_"):
        # User wants to copy a styled name directly from the button
        parts = query.data.split("_", 3)
        if len(parts) > 3:
            style_index = int(parts[2])
            text = parts[3]
            styled_text = transform_text(text, get_all_styles()[style_index])
            
            # Send the styled text as a separate message for easy copying
            copy_keyboard = [[InlineKeyboardButton("🔙 Back to Styles", callback_data=f"back_to_styles_{text}")]]
            reply_markup = InlineKeyboardMarkup(copy_keyboard)
            
            await query.message.reply_text(
                f"<b>Here's your styled text:</b>\n\n<code>{styled_text}</code>\n\n<i>👆 Tap and hold on the text above to copy it</i>",
                parse_mode='HTML',
                reply_markup=reply_markup
            )
            
            await query.answer("Tap and hold to copy the text!")
        else:
            await query.answer("Could not generate styled text", show_alert=True)
        return
    
    elif query.data.startswith("copy_text_"):
        # User wants to copy a styled text directly from the button
        styled_text = query.data.replace("copy_text_", "", 1)
        
        # Send the styled text as a separate message for easy copying
        copy_keyboard = [[InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_start")]]
        
        # Try to get the original text if available
        original_text = context.user_data.get('input_text', None)
        if original_text:
            copy_keyboard = [[InlineKeyboardButton("🔙 Back to Styles", callback_data=f"back_to_styles_{original_text}")]]
        
        reply_markup = InlineKeyboardMarkup(copy_keyboard)
        
        try:
            await query.message.reply_text(
                f"<b>Here's your styled text:</b>\n\n<code>{styled_text}</code>\n\n<i>👆 Tap and hold on the text above to copy it</i>",
                parse_mode='HTML',
                reply_markup=reply_markup
            )
            
            await query.answer("Tap and hold to copy the text!")
        except Exception as e:
            logger.error(f"Error sending styled text: {e}")
            await query.answer("Could not send styled text", show_alert=True)
        return
    
    elif query.data.startswith("combo_page_"):
        # Handle pagination for combinations
        parts = query.data.split("_")
        page = int(parts[2])
        input_text = parts[3]
        # Store the input text in context
        context.user_data['input_text'] = input_text
        return await show_style_combinations(query.message, input_text, page=page, query=query)
    
    elif query.data.startswith("back_to_styles_"):
        # Return to the styles grid
        input_text = query.data.replace("back_to_styles_", "", 1)
        # Store the input text in context
        context.user_data['input_text'] = input_text
        return await show_all_styled_names(query.message, input_text, query=query)
    
    elif query.data.startswith("style_page_"):
        # Handle pagination for name styles
        parts = query.data.split("_")
        input_text = parts[3]
        page = int(parts[2])
        # Store the input text in context
        context.user_data['input_text'] = input_text
        return await show_all_styled_names(query.message, input_text, name_page=page, char_page=0, query=query)
    
    elif query.data.startswith("char_page_"):
        # Handle pagination for character styles
        parts = query.data.split("_")
        input_text = parts[3]
        page = int(parts[2])
        name_page = int(parts[4]) if len(parts) > 4 else 0
        # Store the input text in context
        context.user_data['input_text'] = input_text
        return await show_all_styled_names(query.message, input_text, name_page=name_page, char_page=page, query=query)
    
    elif query.data == "back_to_start":
        # Back to start screen
        keyboard = [
            [
                InlineKeyboardButton("✨ Generate Stylish Name ✨", callback_data="generate_name")
            ],
            [
                InlineKeyboardButton("🎲 Generate Style Combinations", callback_data="generate_combos")
            ],
            [
                InlineKeyboardButton("👤 Our Channel", url="https://t.me/fontbot_updates")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        try:
            # Try to send a new photo message
            await query.message.reply_photo(
                photo=WELCOME_IMAGE_URL,
                caption=f"{WELCOME_MESSAGE}",
                reply_markup=reply_markup
            )
            # Try to delete the old message
            await query.message.delete()
        except Exception as e:
            logger.error(f"Failed to send new photo: {e}")
            try:
                # Try to edit the message if it's a text message
                await query.edit_message_text(
                    text=f"{WELCOME_MESSAGE}",
                    reply_markup=reply_markup
                )
            except Exception as e:
                logger.error(f"Failed to edit message text: {e}")
                try:
                    # Try to edit with photo if possible
                    await query.edit_message_media(
                        media=InputMediaPhoto(
                            media=WELCOME_IMAGE_URL,
                            caption=f"{WELCOME_MESSAGE}"
                        ),
                        reply_markup=reply_markup
                    )
                except Exception as e:
                    logger.error(f"Failed to edit message media: {e}")
                    try:
                        # Try to edit the caption if it's a photo message
                        await query.edit_message_caption(
                            caption=f"{WELCOME_MESSAGE}",
                            reply_markup=reply_markup
                        )
                    except Exception as e:
                        logger.error(f"Failed to edit message caption: {e}")
                        # If all else fails, send a new message
                        await query.message.reply_text(
                            f"{WELCOME_MESSAGE}",
                            reply_markup=reply_markup
                        )
    
    elif query.data == "do_nothing":
        # Just a placeholder for buttons that shouldn't do anything when clicked
        await query.answer()
        return

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

async def show_name_styles_grid(message, input_text, query=None):
    """Show a grid of styled versions of the input text."""
    styles = get_all_styles()
    
    # Show all styles at once in 5x5 grids
    keyboard = []
    
    # Create multiple 5x5 grids showing styled names
    chunk_size = 5  # 5 styles per row
    for i in range(0, len(styles), chunk_size):
        row = []
        for j in range(chunk_size):
            if i + j < len(styles):
                style_idx = i + j
                # Apply the style to the input text
                styled_text = transform_text(input_text, styles[style_idx])
                # Truncate if too long - show a better preview
                styled_preview = (styled_text[:6] + "...") if len(styled_text) > 9 else styled_text
                row.append(InlineKeyboardButton(f"{styled_preview}", callback_data=f"select_style_{style_idx}"))
        if row:  # Only add non-empty rows
            keyboard.append(row)
    
    # Add options for more actions
    keyboard.append([
        InlineKeyboardButton("🔄 New Text", callback_data="try_new"),
        InlineKeyboardButton("🔠 Char Styles", callback_data="show_chars")
    ])
    
    # Add a back button
    keyboard.append([InlineKeyboardButton("🔙 Main Menu", callback_data="back_to_start")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message_text = f"✨ All styles for '{input_text}':"
    
    if query:
        try:
            # Try to edit the message if it's a text message
            await query.edit_message_text(message_text, reply_markup=reply_markup)
        except Exception as e:
            try:
                # Try to edit the caption if it's a photo message
                await query.edit_message_caption(caption=message_text, reply_markup=reply_markup)
            except Exception as e:
                logger.error(f"Error editing message: {e}")
                # If all else fails, send a new message
                await query.message.reply_text(text=message_text, reply_markup=reply_markup)
    else:
        await message.reply_text(text=message_text, reply_markup=reply_markup)
    
    # Store the input text for later use
    if hasattr(message, 'bot_data'):
        if not hasattr(message, 'context'):
            message.context = {}
        message.context.user_data = {'input_text': input_text}
    
    return CHOOSING_STYLE

async def show_all_styled_names(message, input_text, name_page=0, char_page=0, query=None):
    """Show name styles for the input text with pagination."""
    # Create keyboard for buttons
    keyboard = []
    
    # Calculate pages
    name_styles = get_all_styles()
    styles_per_page = 10  # Show 10 name styles per page (2 rows of 5)
    total_name_pages = (len(name_styles) + styles_per_page - 1) // styles_per_page
    
    # Get current page of name styles
    start_idx = name_page * styles_per_page
    end_idx = min(start_idx + styles_per_page, len(name_styles))
    current_page_styles = name_styles[start_idx:end_idx]
    
    # Add title for name styles section
    keyboard.append([
        InlineKeyboardButton(f"✨ Name Styles (Page {name_page+1}/{total_name_pages}) ✨", callback_data="do_nothing")
    ])
    
    # Add name styles (current page)
    for i in range(0, len(current_page_styles), 5):
        row = []
        for j in range(5):
            if i + j < len(current_page_styles):
                style_idx = start_idx + i + j
                # Apply the style to the input text
                styled_text = transform_text(input_text, name_styles[style_idx])
                # Truncate if too long
                styled_preview = (styled_text[:6] + "...") if len(styled_text) > 9 else styled_text
                row.append(InlineKeyboardButton(f"{styled_preview}", callback_data=f"copy_style_{style_idx}_{input_text}"))
        if row:
            keyboard.append(row)
    
    # Add name styles pagination
    nav_row = []
    if name_page > 0:
        nav_row.append(InlineKeyboardButton("⬅️ Prev Styles", callback_data=f"style_page_{name_page-1}_{input_text}"))
    if name_page < total_name_pages - 1:
        nav_row.append(InlineKeyboardButton("Next Styles ➡️", callback_data=f"style_page_{name_page+1}_{input_text}"))
    
    if nav_row:
        keyboard.append(nav_row)
    
    # Add navigation buttons
    keyboard.append([
        InlineKeyboardButton("🔄 Try New Name", callback_data="generate_name"),
        InlineKeyboardButton("🔙 Main Menu", callback_data="back_to_start")
    ])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message_text = f"✨ Tap any style to get copyable text - '{input_text}' (browse all with next/prev):"
    
    if query:
        try:
            # Try to edit the message if it's a text message
            await query.edit_message_text(text=message_text, reply_markup=reply_markup)
        except Exception as e:
            try:
                # Try to edit the caption if it's a photo message
                await query.edit_message_caption(caption=message_text, reply_markup=reply_markup)
            except Exception as e:
                logger.error(f"Error editing message: {e}")
                # If all else fails, send a new message
                await query.message.reply_text(text=message_text, reply_markup=reply_markup)
    else:
        await message.reply_text(text=message_text, reply_markup=reply_markup)
    
    return ConversationHandler.END

def generate_style_permutations(text, max_combos=25):
    """Generate combinations of styled characters for a given text."""
    styled_variations = []
    
    # For each character in the text, get all possible styled variants
    char_options = []
    for char in text:
        if char.lower().isalpha() and char.lower() in STYLISH_CHARS:
            # Get styles for this character
            if char.isupper():
                # For uppercase, get lowercase variants and convert to uppercase
                variants = [v.upper() if v.isalpha() else v for v in STYLISH_CHARS[char.lower()]]
                # Add the original uppercase char at the beginning
                variants.insert(0, char)
                char_options.append(variants[:3])  # Limit to 3 variants to manage combinations
            else:
                # For lowercase, use lowercase variants
                variants = STYLISH_CHARS[char]
                # Add the original char at the beginning
                variants.insert(0, char)
                char_options.append(variants[:3])  # Limit to 3 variants to manage combinations
        else:
            # For non-alphabet characters, only one option - the character itself
            char_options.append([char])
    
    # Generate systematic combinations for short texts
    if len(char_options) <= 4:  # For short words, try more combinations
        for combo in itertools.product(*char_options):
            styled_text = ''.join(combo)
            styled_variations.append(styled_text)
            if len(styled_variations) >= max_combos:
                break
    else:
        # For longer texts, use randomized approach to avoid too many combinations
        # First add the original text
        styled_variations.append(text)
        
        # Then add some varied styles where each character might be styled
        attempt_count = 0
        max_attempts = max_combos * 3  # Limit attempts to avoid infinite loops
        
        while len(styled_variations) < max_combos and attempt_count < max_attempts:
            attempt_count += 1
            
            # Create a random styled variation
            styled_chars = []
            for i, variants in enumerate(char_options):
                # Randomly decide whether to style this character
                if random.random() > 0.5 or len(variants) <= 1:
                    # Keep original character
                    styled_chars.append(text[i])
                else:
                    # Choose a random variant different from the original
                    non_original = [v for v in variants if v != text[i]]
                    if non_original:
                        styled_chars.append(random.choice(non_original))
                    else:
                        styled_chars.append(text[i])
            
            styled_text = ''.join(styled_chars)
            
            # Only add if this is a new variation and differs from original
            if styled_text != text and styled_text not in styled_variations:
                styled_variations.append(styled_text)
    
    # If we still don't have enough variations, add some fully random ones
    while len(styled_variations) < max_combos and len(styled_variations) < 2**len(text):
        styled_chars = []
        for i, variants in enumerate(char_options):
            styled_chars.append(random.choice(variants))
            
        styled_text = ''.join(styled_chars)
        if styled_text not in styled_variations:
            styled_variations.append(styled_text)
    
    return styled_variations[:max_combos]

async def show_style_combinations(message, input_text, page=0, query=None):
    """Show combinations of character styles for the input text."""
    # Create keyboard for buttons
    keyboard = []
    
    # Generate style combinations
    all_combinations = generate_style_permutations(input_text)
    
    # Calculate pagination
    combos_per_page = 10  # 10 combinations per page (2 rows of 5)
    total_pages = (len(all_combinations) + combos_per_page - 1) // combos_per_page
    
    # Get current page of combinations
    start_idx = page * combos_per_page
    end_idx = min(start_idx + combos_per_page, len(all_combinations))
    current_page_combos = all_combinations[start_idx:end_idx]
    
    # Add title
    keyboard.append([
        InlineKeyboardButton(f"🎲 Style Combinations (Page {page+1}/{total_pages}) 🎲", callback_data="do_nothing")
    ])
    
    # Add style combinations (current page)
    for i in range(0, len(current_page_combos), 5):  # Five combinations per row (5x5 grid)
        row = []
        for j in range(5):
            if i + j < len(current_page_combos):
                styled_text = current_page_combos[i + j]
                # Truncate if too long
                styled_preview = (styled_text[:6] + "...") if len(styled_text) > 9 else styled_text
                row.append(InlineKeyboardButton(f"{styled_preview}", callback_data=f"copy_text_{styled_text}"))
        if row:
            keyboard.append(row)
    
    # Add pagination navigation
    nav_row = []
    if page > 0:
        nav_row.append(InlineKeyboardButton("⬅️ Prev Combos", callback_data=f"combo_page_{page-1}_{input_text}"))
    if page < total_pages - 1:
        nav_row.append(InlineKeyboardButton("Next Combos ➡️", callback_data=f"combo_page_{page+1}_{input_text}"))
    
    if nav_row:
        keyboard.append(nav_row)
    
    # Add regenerate option
    keyboard.append([
        InlineKeyboardButton("🔄 Generate New Combinations", callback_data=f"regenerate_combos_{input_text}")
    ])
    
    # Add navigation buttons
    keyboard.append([
        InlineKeyboardButton("🔄 Try New Text", callback_data="generate_combos"),
        InlineKeyboardButton("🔙 Main Menu", callback_data="back_to_start")
    ])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message_text = f"✨ Tap any combination to copy - '{input_text}' (browse with next/prev):"
    
    if query:
        try:
            # Try to edit the message if it's a text message
            await query.edit_message_text(text=message_text, reply_markup=reply_markup)
        except Exception as e:
            try:
                # Try to edit the caption if it's a photo message
                await query.edit_message_caption(caption=message_text, reply_markup=reply_markup)
            except Exception as e:
                logger.error(f"Error editing message: {e}")
                # If all else fails, send a new message
                await query.message.reply_text(text=message_text, reply_markup=reply_markup)
    else:
        await message.reply_text(text=message_text, reply_markup=reply_markup)
    
    return ConversationHandler.END

async def main():
    """Start the bot."""
    # Create the Application
    application = Application.builder().token(BOT_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("styles", show_all_styled_names))
    application.add_handler(CommandHandler("characters", show_all_character_styles))
    application.add_handler(CommandHandler("combine", show_style_combinations))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    application.add_handler(CallbackQueryHandler(handle_callback))

    # Start the Bot
    await application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    import asyncio
    asyncio.run(main()) 