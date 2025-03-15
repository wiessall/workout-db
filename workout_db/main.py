#%%
import os
import asyncio
import nest_asyncio
from dotenv import load_dotenv
from telegram.ext import Application, ContextTypes, CommandHandler, MessageHandler, filters
from workout_db.bot import listen, start, done, cancel
from workout_db.db import start_transaction, table_empty, load_initial_workouts




async def main():
    load_dotenv("/etc/workout-db.env")
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    CHAT_ID = os.getenv("CHAT_ID")
    DATA_SOURCE = os.getenv("WORKOUT_DATA")

    app = Application.builder().token(TELEGRAM_TOKEN).build()
    context = ContextTypes.DEFAULT_TYPE(application=app)
    await start_transaction(context)

    if table_empty(context):
        await load_initial_workouts(context, DATA_SOURCE)

    await start(context=context, update=None)

    app.add_handler(CommandHandler('start', start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, listen))
    app.add_handler(CommandHandler('done', done))
    app.add_handler(CommandHandler('cancel', cancel))

    print("Bot is running...")
    app.run_polling()

def run():
    nest_asyncio.apply()
    asyncio.run(main())

if __name__ == "__main__":
    run()