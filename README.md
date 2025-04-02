# Stylish Name Bot 🤖

A Telegram bot that generates stylish fonts for names.

## Railway Deployment Instructions

1. **Prerequisites**
   - A Railway account (sign up at railway.app)
   - Your Telegram Bot Token
   - Git installed on your computer

2. **Deployment Steps**
   1. Go to [Railway Dashboard](https://railway.app/dashboard)
   2. Click "New Project"
   3. Select "Deploy from GitHub repo"
   4. Choose this repository (https://github.com/Suraj08832/fontbot)
   5. Add the following environment variable:
      - `TELEGRAM_BOT_TOKEN`: Your Telegram bot token from @BotFather

3. **Environment Variables**
   ```
   TELEGRAM_BOT_TOKEN=your_bot_token_here
   ```

4. **Features**
   - Generates stylish fonts for names
   - Handles edited messages in group chats
   - Multiple font styles available
   - Easy to use commands

5. **Commands**
   - `/start` - Start the bot
   - `/style <name>` - Generate stylish fonts for your name

## Local Development

1. Clone the repository:
   ```bash
   git clone https://github.com/Suraj08832/fontbot.git
   cd fontbot
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file with your bot token:
   ```
   TELEGRAM_BOT_TOKEN=your_bot_token_here
   ```
4. Run the bot:
   ```bash
   python stylish_name_bot.py
   ```

## Features ✨

- Convert regular names into stylish versions using special characters
- Support for multiple languages and special characters
- Easy to use commands
- Random style generation for variety

## Example 💡

```
/style John
```
Might generate something like:
```
✨ Your stylish name:
j̶o̶h̶n̶
```

## Contributing 🤝

Feel free to submit issues and enhancement requests! 