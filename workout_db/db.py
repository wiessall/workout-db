# %%
import json
import os
import asyncpg
from datetime import datetime

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


async def insert_exercise(
    parsed_exercise: list[set], context: ContextTypes.DEFAULT_TYPE
):
    conn = context.bot_data.get("db_conn")

    query = """
    INSERT INTO workouts (machine, exercise, weight, reps, date, workout) VALUES ($1, $2, $3, $4, $5, $6)
    """

    for machine, exercise, weight, reps, workout in parsed_exercise:
        await conn.execute(
            query, machine, exercise, weight, reps, date.today(), workout
        )


async def start_transaction(context):
    db_host = os.getenv("DB_HOST", "/run/postgresql")
    db_port = int(os.getenv("DB_PORT", 5432))
    db_user = os.getenv("DB_USER", "workout_user")
    db_password = os.getenv("DB_PASSWORD", "workout")
    db_name = os.getenv("DB_NAME", "workout_db")

    conn = await asyncpg.connect(
        user=db_user,
        password=db_password,
        port=db_port,
        host=db_host,
        database=db_name,
    )
    transaction = conn.transaction()
    await transaction.start()

    context.bot_data["db_conn"] = conn
    context.bot_data["db_transaction"] = transaction


async def load_initial_workouts(context, data_source):
    conn = context.bot_data["db_conn"]
    if isinstance(data_source, str):
        try:
            workouts = json.loads(data_source)
        except Exception as e:
            print(f"String needs to be JSON-formatted:\n\n{e}")
    else:
        raise ValueError(f"data_source needs to be str but is {type(data_source)}")

    for workout in workouts:
        try:
            await conn.execute(
                """
               INSERT INTO workouts (Machine, Exercise, Weight, Reps, Date, Workout) 
               VALUES ($1, $2, $3, $4, $5, $6)
           """,
                *(
                    workout["Machine"],
                    workout["Exercise"],
                    workout["Weight"],
                    int(workout["Reps"]),
                    datetime.strptime(workout["Date"], '%Y-%m-%d'),
                    int(workout["Workout"]),
                ),
            )
        except Exception as e:
            print(f"Skipping invalid row {workout}:\n {e}")

    transaction = context.bot_data.get("db_transaction")
    if transaction:
        await transaction.commit()


async def table_empty(context) -> bool:
    conn = context.bot_data["db_conn"]
    query = """
        SELECT CASE
            WHEN EXISTS (SELECT * FROM workouts LIMIT 1)
            THEN 1
            ELSE 0
        END
    """
    exists = await conn.fetch(query)
    return ~bool(exists[0][0])
