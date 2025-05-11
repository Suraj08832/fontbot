import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Bot token - Using the provided token directly
BOT_TOKEN = os.environ.get("BOT_TOKEN") or os.getenv("BOT_TOKEN", "7877213016:AAGt4O2V1NLaeaK5r1VVPSdMomywo-KCt-4")

# Conversation states
CHOOSING_STYLE, CUSTOMIZING_STYLE = range(2)

# Welcome message
WELCOME_MESSAGE = """
✨✨✨ STYLISH TEXT BOT ✨✨✨

🌟 Transform your plain text into beautiful, eye-catching styles! 🌟

💫 Perfect for:
   • Instagram & TikTok Bio
   • Telegram Username
   • WhatsApp Status
   • Social Media Posts
   • Standing out from the crowd!

👇 Get started with the buttons below 👇
"""

# Help message
HELP_MESSAGE = """
📖 How to use the Stylish Text Bot:

1️⃣ Use "Choose Style" button to select from our pre-made styles
2️⃣ Use "Custom Style" button for unique character replacements
3️⃣ Simply type your text and see it transformed instantly!

✅ Available Commands:
• /start - Restart the bot
• /help - Show this help message
• /style - Choose a style directly 
• /custom - Create custom text directly

💡 Pro Tips:
• Try different styles for the same text
• Combine with emojis for extra flair
• Share your styled text everywhere!

🔔 Questions or feedback? Contact @fontbot_support
""" 