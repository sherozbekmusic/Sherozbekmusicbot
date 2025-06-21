import os, logging, yt_dlp, asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# Tokenni tizim o‘zgaruvchisidan oladi
TOKEN = os.getenv("BOT_TOKEN")
logging.basicConfig(level=logging.INFO)

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎵 Qaysi qo‘shiqni qidiramiz? Menga nomini yozing!")

async def get_music(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.message.text
    msg = await update.message.reply_text("🔍 Qidirilmoqda...")

    ydl_opts = {
        "format": "bestaudio/best",
        "noplaylist": True,
        "outtmpl": "track.%(ext)s",
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192"
        }],
        "quiet": True,
    }

    try:
        loop = asyncio.get_event_loop()

        def download():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                return ydl.extract_info(f"ytsearch:{query}", download=True)["entries"][0]

        info = await loop.run_in_executor(None, download)

        await ctx.bot.send_audio(
            chat_id=update.effective_chat.id,
            audio=open("track.mp3", "rb"),
            title=info["title"][:60],
            performer=info.get("uploader", "")
        )

    except Exception as e:
        logging.error(e)
        await msg.edit_text("❌ Qo‘shiq topilmadi yoki yuklab bo‘lmadi.")
    finally:
        if os.path.exists("track.mp3"):
            os.remove("track.mp3")

# Botni ishga tushirish
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, get_music))

if __name__ == "__main__":
    app.run_polling()