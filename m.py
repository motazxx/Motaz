import asyncio
import logging
import json
import os
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# Configuration
BOT_TOKEN = '7841899027:AAGQML02gethSeEoEm4Y9YpDpxi9_QfZELo'
CHAT_ID = '7613045174'
DATA_FILE = 'bot_data.json'

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AdvancedTelegramBot:
    def __init__(self, token):
        self.token = token
        self.application = Application.builder().token(token).build()
        self.user_data = self.load_data()
        self.setup_handlers()
    
    def load_data(self):
        """Load user data from file"""
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_data(self):
        """Save user data to file"""
        try:
            with open(DATA_FILE, 'w') as f:
                json.dump(self.user_data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving data: {e}")
    
    def setup_handlers(self):
        """Setup all handlers"""
        # Command handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("menu", self.menu_command))
        self.application.add_handler(CommandHandler("stats", self.stats_command))
        self.application.add_handler(CommandHandler("broadcast", self.broadcast_command))
        
        # Callback query handler for inline keyboards
        self.application.add_handler(CallbackQueryHandler(self.button_callback))
        
        # Message handlers
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        self.application.add_handler(MessageHandler(filters.PHOTO, self.handle_photo))
        
        # Error handler
        self.application.add_error_handler(self.error_handler)
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user = update.effective_user
        user_id = str(user.id)
        
        # Save user data
        if user_id not in self.user_data:
            self.user_data[user_id] = {
                'first_name': user.first_name,
                'username': user.username,
                'join_date': datetime.now().isoformat(),
                'message_count': 0
            }
            self.save_data()
        
        welcome_text = f"""
🎉 Welcome {user.first_name}!

I'm an advanced Telegram bot with many features:

🔹 Interactive menus
🔹 User statistics
🔹 Message broadcasting
🔹 Photo handling
🔹 Data persistence

Use /menu to see all options or /help for detailed information.
        """
        
        keyboard = [
            [InlineKeyboardButton("📋 Menu", callback_data="menu")],
            [InlineKeyboardButton("📊 Stats", callback_data="stats")],
            [InlineKeyboardButton("❓ Help", callback_data="help")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(welcome_text, reply_markup=reply_markup)
    
    async def menu_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show interactive menu"""
        keyboard = [
            [InlineKeyboardButton("📊 My Stats", callback_data="stats")],
            [InlineKeyboardButton("🔔 Test Notification", callback_data="notify")],
            [InlineKeyboardButton("📝 Send Feedback", callback_data="feedback")],
            [InlineKeyboardButton("❓ Help", callback_data="help")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text("🎛️ Bot Menu - Choose an option:", reply_markup=reply_markup)
    
    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show user statistics"""
        user_id = str(update.effective_user.id)
        
        if user_id in self.user_data:
            data = self.user_data[user_id]
            join_date = datetime.fromisoformat(data['join_date']).strftime('%Y-%m-%d %H:%M')
            
            stats_text = f"""
📊 Your Statistics:

👤 Name: {data['first_name']}
📅 Joined: {join_date}
💬 Messages sent: {data['message_count']}
🆔 User ID: {user_id}

Total bot users: {len(self.user_data)}
            """
        else:
            stats_text = "No statistics available. Send /start to initialize your data."
        
        await update.message.reply_text(stats_text)
    
    async def broadcast_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Broadcast message to all users (admin only)"""
        user_id = str(update.effective_user.id)
        
        # Check if user is admin (you can modify this condition)
        if user_id != CHAT_ID:
            await update.message.reply_text("❌ You don't have permission to use this command.")
            return
        
        if not context.args:
            await update.message.reply_text("Usage: /broadcast <message>")
            return
        
        message = ' '.join(context.args)
        sent_count = 0
        
        for uid in self.user_data:
            try:
                await context.bot.send_message(chat_id=int(uid), text=f"📢 Broadcast:\n\n{message}")
                sent_count += 1
            except Exception as e:
                logger.error(f"Failed to send broadcast to {uid}: {e}")
        
        await update.message.reply_text(f"✅ Broadcast sent to {sent_count} users.")
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle inline keyboard callbacks"""
        query = update.callback_query
        await query.answer()
        
        if query.data == "menu":
            await self.menu_command(update, context)
        elif query.data == "stats":
            await self.stats_command(update, context)
        elif query.data == "help":
            await self.help_command(update, context)
        elif query.data == "notify":
            await query.edit_message_text("🔔 Test notification sent!")
        elif query.data == "feedback":
            await query.edit_message_text("📝 Please send your feedback as a regular message.")
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show help information"""
        help_text = """
🆘 Help & Commands:

📋 Commands:
• /start - Initialize bot
• /menu - Show interactive menu
• /stats - View your statistics
• /help - Show this help
• /broadcast - Send message to all users (admin)

✨ Features:
• Interactive inline keyboards
• User statistics tracking
• Photo handling
• Data persistence
• Error logging
• Broadcast messaging

💡 Tips:
• Send any text message for auto-response
• Send photos to get file information
• Use inline buttons for quick actions

Need support? Contact the administrator.
        """
        
        if hasattr(update, 'callback_query') and update.callback_query:
            await update.callback_query.edit_message_text(help_text)
        else:
            await update.message.reply_text(help_text)
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages"""
        user_id = str(update.effective_user.id)
        message_text = update.message.text.lower()
        
        # Update message count
        if user_id in self.user_data:
            self.user_data[user_id]['message_count'] += 1
            self.save_data()
        
        # Smart responses
        if any(word in message_text for word in ['hello', 'hi', 'hey']):
            response = f"Hello {update.effective_user.first_name}! 👋"
        elif 'how are you' in message_text:
            response = "I'm doing great! Thanks for asking. 😊"
        elif any(word in message_text for word in ['thanks', 'thank you']):
            response = "You're very welcome! 😊"
        elif 'time' in message_text:
            current_time = datetime.now().strftime('%H:%M:%S')
            response = f"🕐 Current time: {current_time}"
        elif 'date' in message_text:
            current_date = datetime.now().strftime('%Y-%m-%d')
            response = f"📅 Today's date: {current_date}"
        else:
            responses = [
                "That's interesting! Tell me more. 🤔",
                "I understand! Thanks for sharing. 😊",
                "Got it! Anything else I can help with?",
                f"You said: '{update.message.text}'\n\nTry /menu for more options!"
            ]
            import random
            response = random.choice(responses)
        
        await update.message.reply_text(response)
    
    async def handle_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle photo messages"""
        photo = update.message.photo[-1]  # Get highest resolution
        file_info = await context.bot.get_file(photo.file_id)
        
        response = f"""
📸 Photo received!

File ID: {photo.file_id}
File size: {photo.file_size} bytes
Dimensions: {photo.width}x{photo.height}

Thanks for sharing! 😊
        """
        
        await update.message.reply_text(response)
    
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle errors"""
        logger.error(f"Update {update} caused error {context.error}")
    
    def run(self):
        """Start the bot"""
        logger.info("Starting advanced bot...")
        print("🚀 Advanced Bot is starting...")
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    try:
        bot = AdvancedTelegramBot(BOT_TOKEN)
        bot.run()
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        logger.error(f"Bot error: {e}")
