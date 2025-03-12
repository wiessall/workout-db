#%%
import asyncio
import os
from telegram import Bot, Update
from telegram.ext import ContextTypes
from dotenv import load_dotenv

from workout_db.utils import parse_workout_message, format_response
from workout_db.db import insert_exercise, start_transaction, get_workout


async def send_workout(message):
    load_dotenv()
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    CHAT_ID = os.getenv("CHAT_ID")

    bot = Bot(token=TELEGRAM_TOKEN)
    message = f"Here is today's workout: \n {message}"
    await bot.send_message(text=message, chat_id=CHAT_ID)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE,  ):
    
    # if update:
    #     chat_id = update.effective_chat.id
    # else:
    #     chat_id = CHAT_ID

    conn, transaction = start_transaction()
    
    context.bot_data["db_conn"] = conn
    context.bot_data["db_transaction"] = transaction
    context.bot_data["workout_buffer"] = []

    current_workout = await get_workout(context)
    current_workout, n = format_response(current_workout)
    await send_workout(current_workout)

    context.bot_data["current_workout"] = current_workout
    context.bot_data["workout_number"] = n




async def listen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message.text
    parsed_exercise = parse_workout_message(message, context)

    if parsed_exercise:
        context.bot_data["workout_buffer"].append(parsed_exercise)
        await update.message.reply_text("Exercise added! 💪")
    else:
        await update.message.reply_text("Invalid format!")



async def done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    workout_buffer = context.bot_data.get("workout_buffer", [])
    conn = context.bot_data.get("db_conn")

    if not workout_buffer or not conn:
        await update.message.reply_text("No active session. Start workout typing /start")
        return

    for exercise in workout_buffer:
        await insert_exercise(exercise)
    
    transaction = context.bot_data.get("db_transaction")
    if transaction:
        await transaction.commit()

    await conn.close()
    context.bot_data["workout_buffer"] = []
    context.bot_data["db_conn"] = None
    context.bot_data["db_transaction"] = None

    await update.message.reply_text("Workout saved! 💪")
    await context.application.shutdown()
    asyncio.get_event_loop().stop()


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conn = context.bot_data.get("db_conn")
    transaction = context.bot_data.get("db_transaction")

    if transaction:
        await transaction.rollback()
        await conn.close()
    else:
        await update.message.reply_text("No active transaction. Start workout typing /start")
        return
        
    context.bot_data["workout_buffer"] = []
    context.bot_data["db_conn"] = None
    context.bot_data["db_transaction"] = None
    
    await update.message.reply_text("Workout canceled. Start new workout typing /start. Close the service for today by typing /done")
    




