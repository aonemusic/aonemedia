import os
import asyncio
import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# നിങ്ങളുടെ ബോട്ട് ടോക്കൺ ഇവിടെ നൽകുക
TOKEN = 'YOUR_BOT_TOKEN_HERE'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 ഹലോ! ഞാൻ ഒരു വീഡിയോ/ഓഡിയോ ഡൗൺലോഡർ ബോട്ട് ആണ്.\n\n"
        "ഏതെങ്കിലും സോഷ്യൽ മീഡിയ ലിങ്ക് അയച്ചു തരൂ."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    if "http" not in url:
        await update.message.reply_text("സാധുവായ ഒരു ലിങ്ക് അയക്കൂ 🔗")
        return

    keyboard = [
        [InlineKeyboardButton("🎥 Video", callback_data=f"vid|{url}")],
        [InlineKeyboardButton("🎵 Audio (MP3)", callback_data=f"aud|{url}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("നിങ്ങൾക്ക് എന്താണ് വേണ്ടത്?", reply_markup=reply_markup)

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    choice, url = query.data.split('|')
    chat_id = query.message.chat_id
    sent_msg = await context.bot.send_message(chat_id=chat_id, text="ഡൗൺലോഡ് തുടങ്ങുന്നു... ⏳")

    # ഡൗൺലോഡ് സെറ്റിംഗ്‌സ്
    if choice == "vid":
        ydl_opts = {
            'format': 'best',
            'outtmpl': 'downloads/%(title)s.%(ext)s',
        }
    else:
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': 'downloads/%(title)s.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            if choice == "aud":
                filename = os.path.splitext(filename)[0] + ".mp3"

        await sent_msg.edit_text("ഫയൽ അയക്കുന്നു... 📤")
        
        if choice == "vid":
            await context.bot.send_video(chat_id=chat_id, video=open(filename, 'rb'))
        else:
            await context.bot.send_audio(chat_id=chat_id, audio=open(filename, 'rb'))
        
        # അയച്ച ശേഷം ഫയൽ ഡിലീറ്റ് ചെയ്യുന്നു
        os.remove(filename)
        await sent_msg.delete()

    except Exception as e:
        await sent_msg.edit_text(f"ക്ഷമിക്കണം, ഒരു പിശക് സംഭവിച്ചു: {str(e)}")

def main():
    # 'downloads' എന്ന ഫോൾഡർ ഉണ്ടെന്ന് ഉറപ്പാക്കുന്നു
    if not os.path.exists('downloads'):
        os.makedirs('downloads')
        
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(button_click))
    
    print("ബോട്ട് പ്രവർത്തിക്കുന്നു...")
    app.run_polling()

if __name__ == '__main__':
    main()
