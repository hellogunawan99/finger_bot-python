import asyncio
import requests
from datetime import datetime, timedelta
from pytz import timezone as tz
from telegram import Bot

# Function to fetch the latest finger record for each employee in a specific department and event type from the API for the current day


def fetch_latest_finger_records(department_name, event_type, current_date, singapore_tz):
    url = f'http://localhost:3000/api/employees/department/{department_name}/finger-records'
    response = requests.get(url)
    print("API Response:", response.json())  # Print API response for debugging
    finger_records = response.json()

    # Filter records based on the event type and current date
    filtered_records = [record for record in finger_records if record['event_type'] ==
                        event_type and datetime.fromisoformat(record['event_time']).astimezone(singapore_tz).date() == current_date]

    # Sort the records by employee_id
    sorted_records = sorted(
        filtered_records, key=lambda x: x['employee_id'])

    # Get the latest record for each employee
    latest_records = {}
    for record in sorted_records:
        employee_name = record['employee_name']
        if employee_name not in latest_records:
            latest_records[employee_name] = record

    return list(latest_records.values())

# Function to send Telegram message


async def send_telegram_message(bot_token, chat_ids, department_name, records, event_type, singapore_tz):
    bot = Bot(token=bot_token)
    message = f'Latest Finger-{event_type} update for Section {department_name}:\n\n'
    for chat_id in chat_ids:
        for record in records:
            employee_name = record['employee_name']
            event_time = datetime.fromisoformat(
                record['event_time']).astimezone(singapore_tz)
            finger_time = event_time.strftime('%H:%M:%S')
            message += f"{employee_name}, Finger-{event_type}: {finger_time}\n"
        await bot.send_message(chat_id=chat_id, text=message)


async def run_bot(bot_token, bot_chat_data):
    singapore_tz = tz('Asia/Singapore')

    while True:
        # Get the current time in Singapore timezone
        now = datetime.now(singapore_tz)
        current_date = now.date()

        for data in bot_chat_data:
            department_name = data['department_name']
            chat_ids = data['chat_ids']

            # Calculate the next occurrence of 4:36 am Singapore time for "in" event type
            in_target_time = now.replace(
                hour=5, minute=13, second=0, microsecond=0)
            if now > in_target_time:
                in_target_time += timedelta(days=1)

            # Calculate the next occurrence of 4:51 am Singapore time for "out" event type
            out_target_time = now.replace(
                hour=5, minute=14, second=0, microsecond=0)
            if now > out_target_time:
                out_target_time += timedelta(days=1)

            # Calculate the delay until the next occurrence for "in" event type
            in_delay = (in_target_time - now).total_seconds()

            # Calculate the delay until the next occurrence for "out" event type
            out_delay = (out_target_time - now).total_seconds()

            # Schedule the "in" event type message after the delay
            await asyncio.sleep(in_delay)
            latest_records = fetch_latest_finger_records(
                department_name, 'in', current_date, singapore_tz)
            if latest_records:
                await send_telegram_message(bot_token, chat_ids, department_name, latest_records, 'in', singapore_tz)

            # Schedule the "out" event type message after the delay
            await asyncio.sleep(out_delay)
            latest_records = fetch_latest_finger_records(
                department_name, 'out', current_date, singapore_tz)
            if latest_records:
                await send_telegram_message(bot_token, chat_ids, department_name, latest_records, 'out', singapore_tz)

if __name__ == "__main__":
    # Define bot token and chat IDs for each department
    bot_token = 'YOUR_BOT_TOKEN'
    bot_chat_data = [
        {'department_name': 'mine dispatch development',
            'chat_ids': ['CHAT_ID_1', 'CHAT_ID_2']},
        {'department_name': 'another department',
            'chat_ids': ['CHAT_ID_3', 'CHAT_ID_4']},
        # Add more department data as needed
    ]

    asyncio.run(run_bot(bot_token, bot_chat_data))
