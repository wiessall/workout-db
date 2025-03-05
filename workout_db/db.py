#%%
import os
import asyncpg
from datetime import date

from telegram.ext import ContextTypes

DATABASE_URL = os.getenv("DATABASE_URL")

async def get_workout(context: ContextTypes.DEFAULT_TYPE):
    conn = context.bot_data.get("db_conn")

    query = """
    SELECT machine, exercise, weight, reps, workout FROM workouts
    WHERE date = CURRENT_DATE - INTERVAL '7 days'
    """
    rows = await conn.fetch(query)
    return rows

async def insert_exercise(parsed_exercise: list[set]):
    conn = await asyncpg.connect(
        user='workout_user',
        password='workout',
        port=5432,
        host="/run/postgresql",
        database='workout_db',)
    query = """
    INSERT INTO workouts (machine, exercise, weight, reps, date, workout) VALUES ($1, $2, $3, $4, $5, $6)
    """

    for machine, exercise, weight, reps, workout in parsed_exercise:
        await conn.execute(query, machine, exercise, weight, reps, date.today(), workout)


async def start_transaction():
    conn = await asyncpg.connect(
        user='workout_user', 
        password='workout',
        port=5432, 
        host="/run/postgresql", 
        database='workout_db'
    )
    transaction = conn.transaction()
    await transaction.start()
    return conn, transaction    