import re
import pandas as pd

from telegram.ext import ContextTypes

def parse_workout_message(incoming_message: str, context: ContextTypes.DEFAULT_TYPE) -> list[set]:
    message = incoming_message.strip().split()

    current_workout = context.bot_data.get("current_workout", "No workout available today.")
    workout_number = context.bot_data.get("workout_number", "No workout available today.")
    current_workout = current_workout.split('|')
    machine = current_workout[0]
    workout = workout_number

    parsed_exercise: list[set] = []
    i = 0
    weight = None
    exercise = ""
    while i < len(message):
        bit = message[i]
        if weight is None and not ("kg" in bit.lower() or bit.lower() == "bw"):
            exercise += f" {bit}"
        elif not bit.isdigit() and ("kg" in bit.lower() or bit.lower() == "bw"):
            weight = re.search(r'\d+|bw', bit).group()
        elif bit.isdigit():
            reps = int(bit)
            parsed_exercise.append((machine, exercise.strip().title(), weight, reps, workout))
        i += 1

    return parsed_exercise

def format_response(response: list[str]):
    df = pd.DataFrame(response)
    print(df.head())
    workout = df.pop(4).unique()[0]
    return df.to_csv(sep='|', header=False, index=False), workout