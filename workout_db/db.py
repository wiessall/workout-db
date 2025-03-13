#%%
import os
import asyncpg
from datetime import date

from telegram.ext import ContextTypes

DATABASE_URL = os.getenv("DATABASE_URL")

async def get_workout(context: ContextTypes.DEFAULT_TYPE):
    conn = context.bot_data.get("db_conn")

    query = """
    WITH latest_workout AS (
        SELECT workout, MAX(date) AS latest_date 
        FROM workouts
        GROUP BY workout 
        ORDER BY latest_date ASC 
        LIMIT 1
    ) SELECT machine, exercise, weight, reps, workout 
    FROM workouts
    WHERE (workout, date) IN (SELECT workout, latest_date FROM latest_workout);
    """
    rows = await conn.fetch(query)
    print(f"rows\n {rows}")
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