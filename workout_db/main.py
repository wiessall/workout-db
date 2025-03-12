#%%
import os
import asyncio
import nest_asyncio
from dotenv import load_dotenv
from telegram.ext import Application, ContextTypes, CommandHandler, MessageHandler, filters
from workout_db.bot import listen, start, done, cancel




async def main():
    load_dotenv()
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    CHAT_ID = os.getenv("CHAT_ID")

    app = Application.builder().token(TELEGRAM_TOKEN).build()
    context = ContextTypes.DEFAULT_TYPE(application=app)
    await start(context=context, update=None)

    app.add_handler(CommandHandler('start', start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, listen))
    app.add_handler(CommandHandler('done', done))
    app.add_handler(CommandHandler('cancel', cancel))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":

    nest_asyncio.apply()
    asyncio.run(main())