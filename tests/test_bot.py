#%%
import os
import pytest
import asyncpg
import numpy as np
from unittest.mock import MagicMock, patch, AsyncMock

from workout_db.bot import start, cancel, done, listen, send_workout
#%%
@pytest.mark.asyncio
async def test_start_sets_vars():
    mock_context = MagicMock()
    mock_context.bot_data = {}

    await start(None, mock_context)

    assert "db_conn" in mock_context.bot_data
    assert "db_transaction" in mock_context.bot_data
    assert "workout_buffer" in mock_context.bot_data
    assert "current_workout" in mock_context.bot_data
    assert "workout_number" in mock_context.bot_data

    assert isinstance(mock_context.bot_data["db_conn"], asyncpg.connection.Connection)
    assert isinstance(mock_context.bot_data["db_transaction"], asyncpg.transaction.Transaction)
    assert isinstance(mock_context.bot_data["workout_buffer"], list)
    assert isinstance(mock_context.bot_data["current_workout"], str)
    assert isinstance(mock_context.bot_data["workout_number"], np.integer)

@pytest.mark.asyncio
@patch("workout_db.bot.start_transaction", new_callable=AsyncMock)
@patch("workout_db.bot.send_workout", autospec=True)
@patch("workout_db.bot.get_workout", new_callable=AsyncMock)
async def test_start_sends_workout(mock_get_workout, mock_send_workout, mock_start_transaction):
    mock_start_transaction.return_value = (MagicMock(), MagicMock())

    mock_get_workout.return_value = [(0, 1, 2, 4), ("E10", "Squat", "30", 12, 2),
                                     ("E10", "Squat", "30", 12, 2),
                                     ("E10", "Squat", "30", 12, 2),
    ]

    mock_context = MagicMock()
    mock_context.bot_data = {}

    await start(None, mock_context)

    mock_get_workout.assert_called_once_with(mock_context)
    expected_message = '0|1|2|4\nE10|Squat|30|12\nE10|Squat|30|12\nE10|Squat|30|12\n'
    mock_send_workout.assert_called_once_with(expected_message)

@pytest.mark.asyncio
async def test_cancel():
    mock_context = AsyncMock()
    mock_update = AsyncMock()
    mock_context.bot_data = {
        "db_conn" : AsyncMock(),
        "db_transaction" : AsyncMock(),
    }
    mock_db_conn = mock_context.bot_data["db_conn"]
    mock_db_transaction = mock_context.bot_data["db_transaction"]

    await cancel(mock_update, mock_context)

    mock_db_conn.close.assert_awaited_once()
    mock_db_transaction.rollback.assert_awaited_once()

    assert len(mock_context.bot_data["workout_buffer"])==0
    assert mock_context.bot_data["db_conn"] is None
    assert mock_context.bot_data["db_transaction"] is None

@pytest.mark.asyncio
# @patch("workout_db.bot.insert_exercise", new_callable=AsyncMock)
async def test_done():
    mock_context = AsyncMock()
    mock_update = AsyncMock()
    mock_context.bot_data = {
        "db_conn" : AsyncMock(),
        "db_transaction" : AsyncMock(),
        "workout_buffer": [("E10", "Squat", "30", 12, "2025-03-05", 2),]
    }
    mock_db_conn = mock_context.bot_data["db_conn"]
    mock_db_transaction = mock_context.bot_data["db_transaction"]

    # await done(mock_update, mock_context)
    with patch("workout_db.bot.insert_exercise", new_callable=AsyncMock) as mock_insert_exercise:
        await done(mock_update, mock_context)  # Call function

    mock_db_conn.close.assert_awaited_once()
    mock_db_transaction.commit.assert_awaited_once()
    mock_context.application.shutdown.assert_awaited_once()

    assert len(mock_context.bot_data["workout_buffer"])==0
    assert mock_context.bot_data["db_conn"] is None
    assert mock_context.bot_data["db_transaction"] is None


@pytest.mark.asyncio
async def test_listen_updates_context():
    mock_context = AsyncMock()
    mock_context.bot_data = {
        "workout_buffer": [],
    }
    mock_update = AsyncMock()
    mock_update.message.text = "Squat 30kg 12 12 12"

    with patch("workout_db.bot.parse_workout_message", return_value=("Squat", "30", 12, 12, 12)):
        await listen(mock_update, mock_context)

    assert mock_context.bot_data["workout_buffer"] == [("Squat",  "30", 12, 12, 12)]

@pytest.mark.asyncio
async def test_listen_sends_warning():
    mock_update = AsyncMock()
    mock_context = AsyncMock()
    mock_context.bot_data = {

        "current_workout":
            "machine|Squat|100|4\nmachine|Bench Press|100|4\nmachine|Leg Press 45|60|12\nmachine|Dips|bw|3\n",
        "workout_number": 1,
    }

    mock_update.message.text = "Erroneous message"
    await listen(mock_update, mock_context)
    mock_update.message.reply_text.assert_awaited_once_with("Invalid format!")


@pytest.mark.asyncio
async def test_send_workout_missing_env_vars():
    with patch.dict(os.environ, {"TELEGRAM_TOKEN": "", "CHAT_ID": ""}):
        with pytest.raises(Exception):  # Expect an error when trying to send a message
            await send_workout("Test workout")


@pytest.mark.asyncio
async def test_done_no_active_session():
    mock_update = AsyncMock()
    mock_context = AsyncMock()
    mock_context.bot_data = {"workout_buffer": [], "db_conn": None}

    await done(mock_update, mock_context)

    mock_update.message.reply_text.assert_called_once_with("No active session. Start workout typing /start")

@pytest.mark.asyncio
async def test_cancel_no_active_transaction():
    mock_update = AsyncMock()
    mock_context = AsyncMock()
    mock_context.bot_data = {"db_transaction": None}

    await cancel(mock_update, mock_context)

    mock_update.message.reply_text.assert_called_once_with("No active transaction. Start workout typing /start")

@pytest.mark.asyncio
async def test_cancel_no_db_connection():
    mock_update = AsyncMock()
    mock_context = AsyncMock()
    mock_context.bot_data = {"db_conn": None}

    await cancel(mock_update, mock_context)

    mock_update.message.reply_text.assert_called_once_with("No active transaction. Start workout typing /start")

# %%
