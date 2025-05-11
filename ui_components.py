import logging
import time
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ConversationHandler
from telegram.error import BadRequest, TimedOut, NetworkError, TelegramError

from utils import transform_text, get_all_styles, get_stylish_char_by_index, generate_style_permutations
from styles import STYLISH_CHARS

# Set up logging
logger = logging.getLogger(__name__)

# Maximum retries for network operations
MAX_RETRIES = 3

async def retry_telegram_api_call(func, *args, **kwargs):
    """Retry Telegram API calls with exponential backoff"""
    retry_count = 0
    last_exception = None
    
    while retry_count < MAX_RETRIES:
        try:
            return await func(*args, **kwargs)
        except (TimedOut, NetworkError) as e:
            last_exception = e
            retry_count += 1
            wait_time = 1 * (2 ** retry_count)  # Exponential backoff
            logger.warning(f"API call failed, retrying in {wait_time}s: {str(e)}")
            time.sleep(wait_time)
        except TelegramError as e:
            logger.error(f"Telegram API error: {e}")
            raise
    
    # If we get here, all retries failed
    logger.error(f"All retries failed: {last_exception}")
    raise last_exception

async def send_or_edit_message(message, text, reply_markup, query=None):
    """Helper function to send a new message or edit existing message"""
    try:
        if query:
            try:
                return await retry_telegram_api_call(
                    query.edit_message_text,
                    text=text,
                    reply_markup=reply_markup
                )
            except BadRequest as e:
                # Message is not modified or can't be edited
                logger.warning(f"Could not edit message: {e}")
                return await retry_telegram_api_call(
                    query.message.reply_text,
                    text=text,
                    reply_markup=reply_markup
                )
        else:
            return await retry_telegram_api_call(
                message.reply_text,
                text=text,
                reply_markup=reply_markup
            )
    except Exception as e:
        logger.error(f"Error in send_or_edit_message: {e}")
        # Last resort: try to send a new message
        if message:
            return await message.reply_text(
                "There was an error displaying the interface. Please try again.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 Main Menu", callback_data="back_to_start")
                ]])
            )

async def show_char_grid(message, update=None, query=None):
    """Show a grid of stylish characters."""
    try:
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
        
        await send_or_edit_message(message, message_text, reply_markup, query)
        
        return ConversationHandler.END
    except Exception as e:
        logger.error(f"Error in show_char_grid: {e}")
        if message:
            await message.reply_text(
                "There was an error showing the character grid. Please try again.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 Main Menu", callback_data="back_to_start")
                ]])
            )
        return ConversationHandler.END

async def show_char_styles(update, context, char=None, query=None):
    """Show all styles for a specific character."""
    try:
        if not char and query and query.data.startswith("show_char_"):
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
                    row.append(InlineKeyboardButton(variant, callback_data=f"copy_char_{variant}"))
            keyboard.append(row)
        
        # Add navigation buttons
        keyboard.append([
            InlineKeyboardButton("🔙 Back to Characters", callback_data="show_all_chars")
        ])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        message_text = f"✨ All {len(variants)} stylish versions of '{char}':"
        
        if query:
            try:
                await retry_telegram_api_call(
                    query.edit_message_text,
                    text=message_text,
                    reply_markup=reply_markup
                )
            except Exception as e:
                logger.error(f"Error editing message: {e}")
                await query.message.reply_text(
                    text=message_text,
                    reply_markup=reply_markup
                )
        else:
            await update.message.reply_text(
                text=message_text,
                reply_markup=reply_markup
            )
    except Exception as e:
        logger.error(f"Error in show_char_styles: {e}")
        message = query.message if query else (update.message if update else None)
        if message:
            await message.reply_text(
                "There was an error showing the character styles. Please try again.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 Main Menu", callback_data="back_to_start")
                ]])
            )

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
    
    return ConversationHandler.END

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

async def show_all_character_styles(update, context):
    """Show all character styles in a grid format."""
    # Create keyboard for buttons
    keyboard = []
    
    # Get all letters
    letters = list('abcdefghijklmnopqrstuvwxyz')
    
    # Create a 5x5 grid of buttons
    chunk_size = 5  # 5 characters per row
    for i in range(0, len(letters), chunk_size):
        row = []
        for j in range(chunk_size):
            if i + j < len(letters):
                letter = letters[i + j]
                # Show the fancy version of each character in the button text
                fancy_letter = get_stylish_char_by_index(letter, 0)  # Get first style for display
                row.append(InlineKeyboardButton(f"{fancy_letter}", callback_data=f"show_char_{letter}"))
        keyboard.append(row)
    
    # Add navigation buttons
    keyboard.append([
        InlineKeyboardButton("🔙 Main Menu", callback_data="back_to_start")
    ])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message_text = "🔤 Choose a character to see all its stylish versions:"
    
    if update.message:
        await update.message.reply_text(text=message_text, reply_markup=reply_markup)
    else:
        await update.callback_query.edit_message_text(text=message_text, reply_markup=reply_markup) 