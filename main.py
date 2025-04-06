from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes, ConversationHandler
from PIL import Image, ImageFilter, ImageEnhance, ImageOps
import io
import os
import random
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get the token from environment variables
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Dictionary to store user's last image
user_images = {}
# Dictionary to store user preferences
user_preferences = {}

# Conversation states
FEEDBACK = 1

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome to the Image Styler Bot!\n\n"
        "Send me any image, and I'll help you transform it into different styles.\n"
        "Available commands:\n"
        "/styles - Show available style options\n"
        "/help - Get help with using this bot\n"
        "/quality - Set image quality preference\n"
        "/random - Apply a random style to your last image"
    )

async def show_styles(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Available styles:\n"
        "- Ghibli (soft, dreamlike aesthetic)\n"
        "- Contour (outlined edges)\n"
        "- Vintage (old-time feel)\n"
        "- Watercolor (painterly effect)\n\n"
        "Send me an image first, then select a style!"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "🖼 *Image Styler Bot Help* 🖼\n\n"
        "*How to use this bot:*\n"
        "1. Simply send me any photo\n"
        "2. Choose a style from the buttons\n"
        "3. Wait for your styled image\n\n"
        
        "*Available Commands:*\n"
        "/start - Restart the bot\n"
        "/styles - See all available styles\n"
        "/help - Show this help message\n"
        "/quality - Set your preferred image quality\n"
        "/random - Apply a random style to your image\n"
        "/feedback - Send feedback to improve the bot\n\n"
        
        "*Tips:*\n"
        "• For best results, send clear images\n"
        "• Images are processed almost instantly\n"
        "• Your last image is remembered for quick styling\n"
        "• Use /quality to balance quality and processing speed"
    )
    
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def set_quality(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    keyboard = [
        [
            InlineKeyboardButton("Low (Faster)", callback_data="quality_low"),
            InlineKeyboardButton("Medium", callback_data="quality_medium")
        ],
        [
            InlineKeyboardButton("High (Better Quality)", callback_data="quality_high")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "Select your preferred image quality:\n"
        "This affects the resolution of processed images.",
        reply_markup=reply_markup
    )

async def handle_quality_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    quality = query.data.split("_")[1]
    
    # Set quality preference
    if quality == "low":
        user_preferences[user_id] = {"quality": 0.5, "quality_name": "Low"}
    elif quality == "medium":
        user_preferences[user_id] = {"quality": 0.75, "quality_name": "Medium"}
    elif quality == "high":
        user_preferences[user_id] = {"quality": 1.0, "quality_name": "High"}
    
    await query.edit_message_text(
        f"Quality preference set to {user_preferences[user_id]['quality_name']}."
    )

async def feedback_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Please type your feedback or suggestions. Your input helps improve this bot!"
    )
    return FEEDBACK

async def receive_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    feedback = update.message.text
    user = update.effective_user
    
    # Here you would typically store or send the feedback somewhere
    print(f"Feedback received from {user.full_name} (ID: {user.id}): {feedback}")
    
    await update.message.reply_text(
        "Thank you for your feedback! It will help improve the bot."
    )
    return ConversationHandler.END

async def cancel_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Feedback canceled.")
    return ConversationHandler.END

async def random_style(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id not in user_images:
        await update.message.reply_text("Please send an image first!")
        return
    
    styles = ["ghibli", "contour", "vintage", "watercolor"]
    selected_style = random.choice(styles)
    
    image = user_images[user_id]
    
    # Apply the selected style
    if selected_style == "ghibli":
        styled_image = apply_ghibli_style(image)
        style_name = "Ghibli"
    elif selected_style == "contour":
        styled_image = image.filter(ImageFilter.CONTOUR)
        style_name = "Contour"
    elif selected_style == "vintage":
        styled_image = apply_vintage_style(image)
        style_name = "Vintage"
    elif selected_style == "watercolor":
        styled_image = apply_watercolor_style(image)
        style_name = "Watercolor"
    
    # Apply quality settings if available
    if user_id in user_preferences and "quality" in user_preferences[user_id]:
        quality_factor = user_preferences[user_id]["quality"]
        if quality_factor < 1.0:
            # Resize image based on quality preference
            width, height = styled_image.size
            new_width = int(width * quality_factor)
            new_height = int(height * quality_factor)
            styled_image = styled_image.resize((new_width, new_height), Image.LANCZOS)
    
    # Save the styled image to bytes
    bio = io.BytesIO()
    bio.name = f'{selected_style}_image.png'
    styled_image.save(bio, 'PNG')
    bio.seek(0)
    
    await update.message.reply_photo(
        photo=bio,
        caption=f"Here's your image with a randomly selected {style_name} style!"
    )

async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # Get the largest available photo
    photo_file = await update.message.photo[-1].get_file()
    photo_bytes = await photo_file.download_as_bytearray()
    
    # Open the image and store it for this user
    image = Image.open(io.BytesIO(photo_bytes))
    user_images[user_id] = image
    
    # Create keyboard with style options
    keyboard = [
        [
            InlineKeyboardButton("Ghibli", callback_data="style_ghibli"),
            InlineKeyboardButton("Contour", callback_data="style_contour")
        ],
        [
            InlineKeyboardButton("Vintage", callback_data="style_vintage"),
            InlineKeyboardButton("Watercolor", callback_data="style_watercolor")
        ],
        [
            InlineKeyboardButton("Random Style", callback_data="style_random")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text("Choose a style for your image:", reply_markup=reply_markup)

async def apply_style(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    if user_id not in user_images:
        await query.edit_message_text("Please send an image first!")
        return
    
    style = query.data.split("_")[1]
    image = user_images[user_id]
    
    # Apply the selected style
    if style == "random":
        styles = ["ghibli", "contour", "vintage", "watercolor"]
        style = random.choice(styles)
    
    if style == "ghibli":
        styled_image = apply_ghibli_style(image)
        style_name = "Ghibli"
    elif style == "contour":
        styled_image = image.filter(ImageFilter.CONTOUR)
        style_name = "Contour"
    elif style == "vintage":
        styled_image = apply_vintage_style(image)
        style_name = "Vintage"
    elif style == "watercolor":
        styled_image = apply_watercolor_style(image)
        style_name = "Watercolor"
    else:
        await query.edit_message_text("Unknown style selected!")
        return
    
    # Apply quality settings if available
    if user_id in user_preferences and "quality" in user_preferences[user_id]:
        quality_factor = user_preferences[user_id]["quality"]
        if quality_factor < 1.0:
            # Resize image based on quality preference
            width, height = styled_image.size
            new_width = int(width * quality_factor)
            new_height = int(height * quality_factor)
            styled_image = styled_image.resize((new_width, new_height), Image.LANCZOS)
    
    # Save the styled image to bytes
    bio = io.BytesIO()
    bio.name = f'{style}_image.png'
    styled_image.save(bio, 'PNG')
    bio.seek(0)
    
    await context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo=bio,
        caption=f"Here's your image with {style_name} style!"
    )
    await query.edit_message_text("Want to try another style? Send a new image!")

def apply_ghibli_style(image):
    # Ghibli style typically has soft colors, increased saturation, and dreamlike quality
    image = image.copy()
    
    # Increase saturation slightly
    enhancer = ImageEnhance.Color(image)
    image = enhancer.enhance(1.3)
    
    # Soften the image
    image = image.filter(ImageFilter.GaussianBlur(radius=0.5))
    
    # Increase brightness slightly
    enhancer = ImageEnhance.Brightness(image)
    image = enhancer.enhance(1.1)
    
    # Increase contrast
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(1.1)
    
    return image

def apply_vintage_style(image):
    # Create a sepia-like effect
    image = image.copy()
    
    # Convert to sepia tone
    image = ImageOps.colorize(
        image.convert('L'), 
        "#704214",  # dark brown
        "#C0A080"   # light tan
    )
    
    # Reduce brightness
    enhancer = ImageEnhance.Brightness(image)
    image = enhancer.enhance(0.85)
    
    return image

def apply_watercolor_style(image):
    image = image.copy()
    
    # Apply watercolor effect through multiple steps
    # Step 1: Simplify the image with slight blur
    image = image.filter(ImageFilter.GaussianBlur(radius=1))
    
    # Step 2: Enhance edges to simulate paint edges
    image = image.filter(ImageFilter.EDGE_ENHANCE)
    
    # Step 3: Increase saturation
    enhancer = ImageEnhance.Color(image)
    image = enhancer.enhance(1.4)
    
    return image

def main():
    if not TOKEN:
        print("Error: TELEGRAM_BOT_TOKEN environment variable not set!")
        return
        
    app = ApplicationBuilder().token(TOKEN).build()

    # Command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("styles", show_styles))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("quality", set_quality))
    app.add_handler(CommandHandler("random", random_style))
    
    # Feedback conversation handler
    feedback_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("feedback", feedback_command)],
        states={
            FEEDBACK: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_feedback)],
        },
        fallbacks=[CommandHandler("cancel", cancel_feedback)],
    )
    app.add_handler(feedback_conv_handler)
    
    # Message and callback handlers
    app.add_handler(MessageHandler(filters.PHOTO, handle_image))
    app.add_handler(CallbackQueryHandler(handle_quality_selection, pattern="^quality_"))
    app.add_handler(CallbackQueryHandler(apply_style, pattern="^style_"))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
