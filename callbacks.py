import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler

from config import WELCOME_MESSAGE, CHOOSING_STYLE, CUSTOMIZING_STYLE
from utils import transform_text, get_all_styles
from ui_components import show_all_styled_names, show_style_combinations, show_char_styles

# Set up logging
logger = logging.getLogger(__name__)

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks."""
    query = update.callback_query
    await query.answer()
    
    if query.data == "generate_name":
        # Prompt user to enter a name to style
        context.user_data['mode'] = 'generate_name'
        await query.edit_message_text("✏️ Enter your name or text to style it:")
        return CUSTOMIZING_STYLE
    
    elif query.data == "generate_combos":
        # Prompt user to enter a name for combination styling
        context.user_data['mode'] = 'generate_combos'
        await query.edit_message_text("✏️ Enter your text to see style combinations:")
        return CUSTOMIZING_STYLE
    
    elif query.data.startswith("copy_text_"):
        # Handle copying styled text for combinations
        styled_text = query.data.replace("copy_text_", "", 1)
        
        # Send the styled text as a separate message for easy copying
        copy_keyboard = [[InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_start")]]
        
        # Try to get the original text if available
        original_text = context.user_data.get('input_text', None)
        if original_text:
            copy_keyboard = [[InlineKeyboardButton("🔙 Back to Combinations", callback_data=f"regenerate_combos_{original_text}")]]
        
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
    
    elif query.data.startswith("regenerate_combos_"):
        # User wants to regenerate combinations with the same text
        input_text = query.data.replace("regenerate_combos_", "", 1)
        # Store the input text in context
        context.user_data['input_text'] = input_text
        # Show new combinations starting at page 0
        return await show_style_combinations(query.message, input_text, page=0, query=query)
    
    elif query.data.startswith("show_char_"):
        # Show all styles for a specific character
        char = query.data.replace("show_char_", "")
        await show_char_styles(update, context, char, query)
        return
    
    elif query.data.startswith("copy_char_"):
        # Copy a specific character style
        styled_char = query.data.replace("copy_char_", "")
        # Send the styled character as a separate message for easy copying
        copy_keyboard = [[InlineKeyboardButton("🔙 Back", callback_data=f"show_char_{styled_char.lower()}")]]
        reply_markup = InlineKeyboardMarkup(copy_keyboard)
        
        await query.message.reply_text(
            f"<b>Here's your styled character:</b>\n\n<code>{styled_char}</code>\n\n<i>👆 Tap and hold on the text above to copy it</i>",
            parse_mode='HTML',
            reply_markup=reply_markup
        )
        return
    
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
        return 