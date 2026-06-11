import os
import threading
from flask import Flask, redirect, request
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# 🤖 आपका नया बॉट टोकन यहाँ सेट है
BOT_TOKEN = "8947006366:AAGN5tgbkAnElu0oi-aB2pWveYcpYzRR6v0"

# 📢 आपके चैनल का यूजरनेम
CHANNEL_USERNAME = "@jorogamer"
CHANNEL_URL = "https://t.me/jorogamer"

# आपकी Render ऐप का नाम
YOUR_RENDER_APP_NAME = "file2linklite" 
BASE_URL = f"https://{YOUR_RENDER_APP_NAME}.onrender.com"

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# 🔒 यूजर ने चैनल जॉइन किया है या नहीं, यह चेक करने का फंक्शन
def check_must_join(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        if member.status in ['creator', 'administrator', 'member']:
            return True
        return False
    except Exception:
        # अगर कोई एरर आए (जैसे बॉट एडमिन न हो), तो बैकअप के लिए True कर देगा ताकि बॉट रुके नहीं
        return True

# 📢 जॉइन न करने पर दिखने वाला मैसेज और बटन
def send_join_request(chat_id):
    join_text = (
        "🚀 *To use this bot, you must join our channel!*\n\n"
        "Pehle neeche diye gaye button par click karke channel join karein, "
        "uske baad dubara `/start` dabayein."
    )
    markup = InlineKeyboardMarkup()
    markup.row(InlineKeyboardButton("📢 Join Channel", url=CHANNEL_URL))
    bot.send_message(chat_id, join_text, parse_mode="Markdown", reply_markup=markup)


# 🌐 Webhook Route
@app.route(f'/{BOT_TOKEN}', methods=['POST'])
def getMessage():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

# 🏠 होम रूट
@app.route('/')
def home():
    return "⚡ Premium File-to-Link Bot Is Running Alive ⚡", 200

# 🌐 CHROME DOWNLOAD REDIRECTOR
@app.route('/download/<path:file_path>')
def download_file(file_path):
    telegram_direct_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"
    return redirect(telegram_direct_url)


# --- TELEGRAM BOT LOGIC ---

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    # फ़ोर्स जॉइन चेक
    if not check_must_join(message.from_user.id):
        send_join_request(message.chat.id)
        return

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
        InlineKeyboardButton("📢 Channel", url=CHANNEL_URL),
        InlineKeyboardButton("👨‍💻 Developer", url="https://t.me/your_username") # यहाँ अपना यूजरनेम बदल सकते हैं
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown", reply_markup=markup)

@bot.message_handler(content_types=['document', 'video', 'audio', 'photo', 'voice'])
def handle_docs(message):
    # फ़ोर्स जॉइन चेक
    if not check_must_join(message.from_user.id):
        send_join_request(message.chat.id)
        return

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

        file_info = bot.get_file(file_id)
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

# 🛠️ AUTOMATIC WEBHOOK SETUP
def set_webhook():
    import time
    time.sleep(2)
    bot.remove_webhook()
    webhook_url = f"{BASE_URL}/{BOT_TOKEN}"
    bot.set_webhook(url=webhook_url)

if __name__ == '__main__':
    webhook_thread = threading.Thread(target=set_webhook)
    webhook_thread.daemon = True
    webhook_thread.start()
    
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
    
