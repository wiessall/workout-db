import pytest
from datetime import date
from unittest.mock import AsyncMock, patch, MagicMock, Mock
from workout_db.db import get_workout, insert_exercise, start_transaction

@pytest.mark.asyncio
async def test_get_workout():
    mock_conn = AsyncMock()
    mock_conn.fetch = AsyncMock(return_value=[("E10", "Squat", "30", 12, 2)])

    # Mock `context.bot_data["db_conn"]`
    mock_context = AsyncMock()
    mock_context.bot_data = {"db_conn": mock_conn}

    result = await get_workout(mock_context)

    # fetch() was called with correct SQL?
    query = """
    SELECT machine, exercise, weight, reps, workout FROM workouts
    WHERE date = CURRENT_DATE - INTERVAL '7 days'
    """
    mock_conn.fetch.assert_called_once_with(query)

    # return value is correctly passed?
    assert result == [("E10", "Squat", "30", 12, 2)]

@pytest.mark.asyncio
async def test_insert_exercise():
    mock_conn = AsyncMock()
    mock_conn.execute = AsyncMock()

    example_exercise = [("E10", "Squat", "30", 12, 2)]
    example_with_date = ("E10", "Squat", "30", 12, date.today(), 2)

    query = """
    INSERT INTO workouts (machine, exercise, weight, reps, date, workout) VALUES ($1, $2, $3, $4, $5, $6)
    """

    with patch("workout_db.db.asyncpg.connect", return_value=mock_conn):
        await insert_exercise(example_exercise)

        mock_conn.execute.assert_called_once_with(query, *example_with_date)

@pytest.mark.asyncio
async def test_start_transaction():
    mock_conn = Mock()
    mock_transaction = Mock()
    mock_transaction.start = AsyncMock()
    mock_conn.transaction.return_value = mock_transaction

    
    with patch("workout_db.db.asyncpg.connect", return_value=mock_conn):
        conn, transaction = await start_transaction()

    # Starts transaction?
    mock_transaction.start.assert_awaited_once()

    # Connects to DB?
    assert conn == mock_conn
    assert transaction == mock_transaction
