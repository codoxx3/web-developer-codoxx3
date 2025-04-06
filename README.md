# Image Styler Telegram Bot

A Telegram bot that can apply different artistic styles to images, including Ghibli, Contour, Vintage, and Watercolor styles.

## Setup

1. Clone this repository
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Create a Telegram bot using [BotFather](https://t.me/botfather) and get your bot token
4. Edit the `.env` file and replace `YOUR_TELEGRAM_BOT_TOKEN` with your actual token
5. Run the bot:
   ```
   python main.py
   ```

## Usage

1. Start a chat with your bot on Telegram
2. Send the bot a photo
3. Select one of the available styles:
   - Ghibli: Soft, dreamlike aesthetics inspired by Studio Ghibli animations
   - Contour: Outlined edges highlighting the image contours
   - Vintage: Sepia-toned old-time feel
   - Watercolor: Painterly watercolor effect
   - Random: Apply a randomly selected style

## Commands

- `/start` - Start the bot and get welcome message
- `/styles` - Show available style options
- `/help` - Get detailed help with using the bot
- `/quality` - Set your preferred image quality (Low, Medium, High)
- `/random` - Apply a random style to your last image
- `/feedback` - Send feedback or suggestions to improve the bot

## Features

1. **Multiple Style Options**: Choose from four different artistic styles for your images
2. **Quality Settings**: Balance between speed and image quality based on your preference
3. **Random Style Generator**: Let the bot surprise you with a randomly selected style
4. **Feedback System**: Share your thoughts and suggestions to help improve the bot 