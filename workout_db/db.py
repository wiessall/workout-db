import asyncpg
import os

DATABASE_URL = os.getenv("DATABASE_URL")

async def get_workout():
    conn = await asyncpg.connect(database_url)
    query = """
    SELECT exercise, weight, reps FROM workout
    WHERE date = CURRENT_DATE - INTERVAL '7 days'
    """
    rows = await conn.fetch(query)
    await conn.close()
    return rows