import pytest
from unittest.mock import MagicMock

from workout_db.utils import parse_workout_message
#%%
@pytest.mark.parametrize("message, expected", [
   ("Squat 100kg 5 5 4 3",  [
        ("machine", "Squat", "100", 5, 999),
        ("machine", "Squat", "100", 5, 999),
        ("machine", "Squat", "100", 4, 999),
        ("machine", "Squat", "100", 3, 999),
    ]),
    ("Bench Press 200kg 3 2", [
            ("machine", "Bench Press", "200", 3, 999),
            ("machine", "Bench Press", "200", 2, 999),
    ]),
    ("bench press 80kg 5 85kg 4 90kg 3",  [
            ("machine", "Bench Press", "80", 5, 999),
            ("machine", "Bench Press", "85", 4, 999),
            ("machine", "Bench Press", "90", 3, 999),
    ]),
    ("Leg Press 45 50kg 5 60kg 3 12", [
            ("machine", "Leg Press 45", "50", 5, 999),
            ("machine", "Leg Press 45", "60", 3, 999),
            ("machine", "Leg Press 45", "60", 12, 999),
    ]),
    ("Dips bw 3 4 5", [
            ("machine", "Dips", "bw", 3, 999),
            ("machine", "Dips", "bw", 4, 999),
            ("machine", "Dips", "bw", 5, 999),
    ])
])
def test_parser(message, expected):
    mock_context = MagicMock()
    mock_context.bot_data.get.side_effect = lambda key, default: {
        "current_workout": 
"machine|Squat|100|4\nmachine|Bench Press|100|4\nmachine|Leg Press 45|60|12\nmachine|Dips|bw|3\n",
        "workout_number": 999
    }.get(key, default)
    assert parse_workout_message(message, mock_context) == expected, f"Expected: \n {expected} \n Output: \n {parse_workout_message(message, mock_context)}"


        
#%%
