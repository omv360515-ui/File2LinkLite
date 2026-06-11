import os
import threading
from flask import Flask, redirect
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# टेलीग्राम बॉट टोकन
BOT_TOKEN = "8723304184:AAH0j1kr7xq9TGA2X4cAvhNJgjnb7ANeeoQ"

# आपकी रेंडर ऐप का नाम (Render पर सर्विस बनाते समय जो नाम रखेंगे)
YOUR_RENDER_APP_NAME = "file2linklite" 

# रेंडर का फाइनल URL जो सीधे क्रोम को ट्रिगर करेगा
BASE_URL = f"https://{YOUR_RENDER_APP_NAME}.onrender.com"

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# Render.com के लिए होम रूट (Health Check)
@app.route('/')
def home():
    return "⚡ Premium File-to-Link Bot Is Running Alive ⚡", 200

# 🌐 CHROME DOWNLOAD REDIRECTOR (FIXED)
@app.route('/download/<path:file_path>')
def download_file(file_path):
    telegram_direct_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"
    return redirect(telegram_direct_url)


# --- TELEGRAM BOT LOGIC ---

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    user_name = message.from_user.first_name
    welcome_text = (
        f"👋 *Welcome, {user_name}!*\n\n"
        "✨ *PREMIUM FILE TO LINK CONVERTER*\n"
        "▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n"
        "⚡ *Features:*\n"
        "├ 📂 Instant File to Link Conversion\n"
        "├ 🚀 High-Speed Chrome Download Link\n"
        "└ 🛡️ 100% Safe & Secure Encryption\n\n"
        "📥 *Kaise Use Karein?*\n"
        "Aap koi bhi File, Document, APK, Video, ya Audio is chat me send karein. Bot turant usko Chrome download link me badal dega!"
    )
    
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("📢 Channel", url="https://t.me/your_channel"),
        InlineKeyboardButton("👨‍💻 Developer", url="https://t.me/your_username")
    )
    
    bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown", reply_markup=markup)

@bot.message_handler(content_types=['document', 'video', 'audio', 'photo', 'voice'])
def handle_docs(message):
    processing_msg = bot.send_message(
        message.chat.id, 
        "⏳ *Processing your file...*\n`[▒▒▒▒▒▒▒▒▒▒] 0%` \n⚡ Please wait a moment...", 
        parse_mode="Markdown"
    )
    
    try:
        if message.content_type == 'photo':
            file_id = message.photo[-1].file_id
            file_name = f"photo_{file_id[:6]}.jpg"
        elif message.content_type == 'video':
            file_id = message.video.file_id
            file_name = message.video.file_name or "video.mp4"
        elif message.content_type == 'audio':
            file_id = message.audio.file_id
            file_name = message.audio.file_name or "audio.mp3"
        elif message.content_type == 'voice':
            file_id = message.voice.file_id
            file_name = "voice_message.ogg"
        else:
            file_id = message.document.file_id
            file_name = message.document.file_name or "file"

        # टेलीग्राम सर्वर से फाइल पाथ निकालना
        file_info = bot.get_file(file_id)
        
        # ?tgOpenInApp=0 से टेलीग्राम इन-ऐप ब्राउज़र बाईपास होगा और क्रोम खुलेगा
        chrome_download_link = f"{BASE_URL}/download/{file_info.file_path}?tgOpenInApp=0"
        
        bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=processing_msg.message_id,
            text="⏳ *Uploading to Server...*\n`[████████▒▒] 80%`",
            parse_mode="Markdown"
        )
        
        success_text = (
            "✅ *File Successfully Converted!*\n"
            "▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n"
            f"📄 *File Name:* `{file_name}`\n"
            "🌐 *Platform:* Google Chrome Supported\n"
            "🌟 *Status:* Premium Link Generated\n"
            "▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n"
            "👇 *Neeche diye button par click karke download karein:* "
        )
        
        download_markup = InlineKeyboardMarkup()
        download_markup.row(
            InlineKeyboardButton("🌐 Open in Chrome & Download", url=chrome_download_link)
        )
        
        bot.delete_message(message.chat.id, processing_msg.message_id)
        bot.send_message(message.chat.id, success_text, parse_mode="Markdown", reply_markup=download_markup)

    except Exception as e:
        bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=processing_msg.message_id,
            text=f"❌ *Error:* Link generate karne me dikkat aayi. Kripya dobara koshish karein.\n`Error: {str(e)}`",
            parse_mode="Markdown"
        )

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

def run_bot():
    print("🤖 Bot is polling...")
    bot.infinity_polling(skip_meaningful=True)

if __name__ == '__main__':
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    
    run_bot()
    
