import logging
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from telegram.error import BadRequest, TimedOut, NetworkError, TelegramError

from config import WELCOME_MESSAGE, CHOOSING_STYLE, CUSTOMIZING_STYLE
from utils import transform_text, get_all_styles, format_styled_name
from ui_components import show_all_styled_names, show_style_combinations, show_char_styles

# Set up logging
logger = logging.getLogger(__name__)

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks."""
    # Safety check
    if not update or not update.callback_query:
        logger.warning("Received invalid callback update")
        return

    query = update.callback_query
    
    try:
        # Answer callback query to prevent "loading..." on the client side
        await query.answer()
        
        if query.data == "generate_name":
            # Prompt user to enter a name to style
            context.user_data['mode'] = 'generate_name'
            try:
                # Use retry pattern for UI operations
                retry_count = 0
                max_retries = 3
                while retry_count < max_retries:
                    try:
                        await query.edit_message_text("✏️ Enter your name or text to style it:")
                        logger.debug("Successfully prompted user for name input")
                        return CUSTOMIZING_STYLE
                    except (TimedOut, NetworkError) as e:
                        retry_count += 1
                        wait_time = 2 ** retry_count  # Exponential backoff
                        logger.warning(f"Network error when prompting for name (attempt {retry_count}): {e}. Waiting {wait_time}s before retry.")
                        time.sleep(wait_time)
                    except BadRequest as e:
                        logger.error(f"Failed to edit message: {e}")
                        # If edit fails, send a new message
                        await query.message.reply_text("✏️ Enter your name or text to style it:")
                        return CUSTOMIZING_STYLE
                
                # If we get here, we've exhausted retries
                logger.error("Failed to prompt for name after multiple retries")
                await query.message.reply_text("⚠️ Network issues detected. Please try again by clicking 'Generate Stylish Name' again.")
                return
            except Exception as e:
                logger.error(f"Unexpected error in generate_name handler: {e}")
                await query.message.reply_text("✏️ Enter your name or text to style it:")
                return CUSTOMIZING_STYLE
        
        elif query.data == "info_auto_style":
            # Show information about the auto-styling feature
            try:
                info_text = (
                    "✨ <b>Automatic Styling Feature</b> ✨\n\n"
                    "Just type any name or text directly in the chat, and I'll instantly create multiple stylish versions for you!\n\n"
                    "✅ Works with any name or text\n"
                    "✅ Creates beautiful designs with special characters\n"
                    "✅ No commands needed - just type and send!\n\n"
                    "Try it now - send me any name!"
                )
                
                keyboard = [[InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_start")]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await query.edit_message_text(
                    info_text,
                    parse_mode='HTML',
                    reply_markup=reply_markup
                )
            except Exception as e:
                logger.error(f"Error showing auto-style info: {e}")
                # Fallback to a new message if edit fails
                await query.message.reply_text("Just type any name or text to see it styled instantly!")
            return
        
        elif query.data == "generate_combos":
            # Prompt user to enter a name for combination styling
            context.user_data['mode'] = 'generate_combos'
            try:
                await query.edit_message_text("✏️ Enter your text to see style combinations:")
                return CUSTOMIZING_STYLE
            except BadRequest as e:
                logger.error(f"Failed to edit message: {e}")
                # If edit fails, send a new message
                await query.message.reply_text("✏️ Enter your text to see style combinations:")
                return CUSTOMIZING_STYLE
        
        elif query.data.startswith("copy_text_"):
            return await handle_copy_text(query, context)
        
        elif query.data.startswith("combo_page_"):
            return await handle_combo_page(query, context)
        
        elif query.data.startswith("regenerate_combos_"):
            return await handle_regenerate_combos(query, context)
        
        elif query.data.startswith("show_char_"):
            return await handle_show_char(update, context, query)
        
        elif query.data.startswith("copy_char_"):
            return await handle_copy_char(query)
        
        elif query.data.startswith("copy_style_"):
            return await handle_copy_style(query, context)
        
        elif query.data.startswith("back_to_styles_"):
            return await handle_back_to_styles(query, context)
        
        elif query.data.startswith("style_page_"):
            return await handle_style_page(query, context)
        
        elif query.data == "back_to_start":
            return await handle_back_to_start(query)
        
        else:
            # Unknown callback data
            logger.warning(f"Unknown callback data: {query.data}")
            return
            
    except TimedOut:
        logger.error("Request timed out")
        # Send a message to the user
        try:
            await query.message.reply_text(
                "⚠️ Connection timed out. Please try again."
            )
        except:
            pass
        return
        
    except NetworkError:
        logger.error("Network error occurred")
        # Send a message to the user
        try:
            await query.message.reply_text(
                "⚠️ Network error. Please try again later."
            )
        except:
            pass
        return
        
    except Exception as e:
        # Log any other exceptions
        logger.error(f"Error in handle_callback: {e}")
        try:
            await query.message.reply_text(
                "⚠️ Something went wrong. Please try again."
            )
        except:
            pass
        return

# Helper functions to keep the main handler clean
async def handle_copy_text(query, context):
    """Handle copying styled text for combinations"""
    try:
        styled_text = query.data.replace("copy_text_", "", 1)
        
        # Send the styled text as a separate message for easy copying
        copy_keyboard = [[InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_start")]]
        
        # Try to get the original text if available
        original_text = context.user_data.get('input_text', None)
        if original_text:
            # Limit original text length to avoid Button_data_invalid error
            truncated_text = original_text[:15] if len(original_text) > 15 else original_text
            copy_keyboard = [[InlineKeyboardButton("🔙 Back to Combinations", callback_data=f"regenerate_combos_{truncated_text}")]]
        
        reply_markup = InlineKeyboardMarkup(copy_keyboard)
        
        await query.message.reply_text(
            f"<b>Here's your styled text:</b>\n\n<code>{styled_text}</code>\n\n<i>👆 Tap and hold on the text above to copy it</i>",
            parse_mode='HTML',
            reply_markup=reply_markup
        )
    except Exception as e:
        logger.error(f"Error sending styled text: {e}")
        await query.answer("Could not send styled text", show_alert=True)
    return

async def handle_combo_page(query, context):
    """Handle pagination for combinations"""
    try:
        parts = query.data.split("_", 3)  # Split into at most 4 parts
        if len(parts) < 3:
            logger.error(f"Invalid combo_page data: {query.data}")
            await query.message.reply_text("Invalid pagination request. Please try again.")
            return
            
        try:
            page = int(parts[2])
        except ValueError:
            logger.error(f"Invalid page number in combo_page: {parts[2]}")
            page = 0
            
        # Get the input text, joining all remaining parts if there were splits in the text
        if len(parts) > 3:
            input_text = parts[3]
        else:
            # Fallback to stored text
            input_text = context.user_data.get('input_text', 'Sample')
        
        # Store the input text in context
        context.user_data['input_text'] = input_text
        
        logger.debug(f"Navigating to combinations page {page} for text: {input_text[:10]}...")
        
        # Use retry logic for API calls
        retry_count = 0
        max_retries = 3
        last_error = None
        
        while retry_count < max_retries:
            try:
                return await show_style_combinations(query.message, input_text, page=page, query=query)
            except (TimedOut, NetworkError) as e:
                retry_count += 1
                wait_time = 2 ** retry_count  # Exponential backoff
                last_error = e
                logger.warning(f"Network error in handle_combo_page (attempt {retry_count}): {e}. Waiting {wait_time}s.")
                time.sleep(wait_time)
        
        # If we get here, all retries failed
        logger.error(f"Failed to handle combo page after {max_retries} retries: {last_error}")
        await query.message.reply_text("Could not load combinations due to network issues. Please try again.")
    except Exception as e:
        logger.error(f"Error in handle_combo_page: {e}")
        await query.message.reply_text("Could not load combinations. Please try again.")
    return

async def handle_regenerate_combos(query, context):
    """Handle regenerating combinations"""
    try:
        # Get input text, handling potential underscore in the text
        input_parts = query.data.split("_", 2)  # Split at most twice
        if len(input_parts) < 3:
            logger.error(f"Invalid regenerate_combos data: {query.data}")
            await query.message.reply_text("Invalid regeneration request. Please try again.")
            return
            
        input_text = input_parts[2]
        
        # Store the input text in context
        context.user_data['input_text'] = input_text
        
        logger.debug(f"Regenerating combinations for text: {input_text[:10]}...")
        
        # Use retry logic for API calls
        retry_count = 0
        max_retries = 3
        last_error = None
        
        while retry_count < max_retries:
            try:
                # Show new combinations starting at page 0
                return await show_style_combinations(query.message, input_text, page=0, query=query)
            except (TimedOut, NetworkError) as e:
                retry_count += 1
                wait_time = 2 ** retry_count  # Exponential backoff
                last_error = e
                logger.warning(f"Network error in handle_regenerate_combos (attempt {retry_count}): {e}. Waiting {wait_time}s.")
                time.sleep(wait_time)
        
        # If we get here, all retries failed
        logger.error(f"Failed to regenerate combos after {max_retries} retries: {last_error}")
        await query.message.reply_text("Could not regenerate combinations due to network issues. Please try again.")
    except Exception as e:
        logger.error(f"Error in handle_regenerate_combos: {e}")
        await query.message.reply_text("Could not regenerate combinations. Please try again.")
    return

async def handle_show_char(update, context, query):
    """Handle showing character styles"""
    try:
        char = query.data.replace("show_char_", "")
        await show_char_styles(update, context, char, query)
    except Exception as e:
        logger.error(f"Error in handle_show_char: {e}")
        await query.message.reply_text("Could not load character styles. Please try again.")
    return

async def handle_copy_char(query):
    """Handle copying character styles"""
    try:
        styled_char = query.data.replace("copy_char_", "")
        # Send the styled character as a separate message for easy copying
        copy_keyboard = [[InlineKeyboardButton("🔙 Back", callback_data=f"show_char_{styled_char.lower()}")]]
        reply_markup = InlineKeyboardMarkup(copy_keyboard)
        
        await query.message.reply_text(
            f"<b>Here's your styled character:</b>\n\n<code>{styled_char}</code>\n\n<i>👆 Tap and hold on the text above to copy it</i>",
            parse_mode='HTML',
            reply_markup=reply_markup
        )
    except Exception as e:
        logger.error(f"Error in handle_copy_char: {e}")
        await query.message.reply_text("Could not copy character. Please try again.")
    return

async def handle_copy_style(query, context):
    """Handle copying a style"""
    try:
        parts = query.data.split("_", 3)
        if len(parts) > 3:
            style_index = int(parts[2])
            text = parts[3]
            styles = get_all_styles()
            
            # Use the format_styled_name function for template styling
            styled_text = format_styled_name(text, styles[style_index])
            
            # Send the styled text as a separate message for easy copying
            copy_keyboard = [[InlineKeyboardButton("🔙 Back to Styles", callback_data=f"back_to_styles_{text}")]]
            reply_markup = InlineKeyboardMarkup(copy_keyboard)
            
            await query.message.reply_text(
                f"<b>Here's your styled text:</b>\n\n<code>{styled_text}</code>\n\n<i>👆 Tap and hold on the text above to copy it</i>",
                parse_mode='HTML',
                reply_markup=reply_markup
            )
        else:
            await query.answer("Could not generate styled text", show_alert=True)
    except Exception as e:
        logger.error(f"Error in handle_copy_style: {e}")
        await query.message.reply_text("Could not copy style. Please try again.")
    return

async def handle_back_to_styles(query, context):
    """Handle going back to styles"""
    try:
        input_text = query.data.replace("back_to_styles_", "", 1)
        # Store the input text in context
        context.user_data['input_text'] = input_text
        return await show_all_styled_names(query.message, input_text, query=query)
    except Exception as e:
        logger.error(f"Error in handle_back_to_styles: {e}")
        await query.message.reply_text("Could not load styles. Please try again.")
    return

async def handle_style_page(query, context):
    """Handle pagination for name styles"""
    try:
        parts = query.data.split("_")
        input_text = parts[3]
        page = int(parts[2])
        # Store the input text in context
        context.user_data['input_text'] = input_text
        return await show_all_styled_names(query.message, input_text, name_page=page, char_page=0, query=query)
    except Exception as e:
        logger.error(f"Error in handle_style_page: {e}")
        await query.message.reply_text("Could not load style page. Please try again.")
    return

async def handle_back_to_start(query):
    """Handle going back to start screen"""
    try:
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
            await query.edit_message_text(
                text=f"{WELCOME_MESSAGE}",
                reply_markup=reply_markup
            )
        except Exception as e:
            logger.error(f"Failed to edit message: {e}")
            await query.message.reply_text(
                f"{WELCOME_MESSAGE}",
                reply_markup=reply_markup
            )
    except Exception as e:
        logger.error(f"Error in handle_back_to_start: {e}")
        # Try to send a new message as a last resort
        try:
            keyboard = [
                [
                    InlineKeyboardButton("✨ Generate Stylish Name ✨", callback_data="generate_name")
                ],
                [
                    InlineKeyboardButton("🎲 Generate Style Combinations", callback_data="generate_combos")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.message.reply_text("Welcome back to the Stylish Text Bot!", reply_markup=reply_markup)
        except:
            pass
    return 