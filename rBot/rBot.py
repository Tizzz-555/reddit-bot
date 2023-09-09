import praw

# from helpers import (
#     contains_weekend_date,
#     detect_and_convert_time,
#     contains_relevant_keywords,
#     is_within_schedule,
# )
import re
from datetime import datetime


def is_weekend(date_string):
    current_year = datetime.now().year
    try:
        date_obj = datetime.strptime(f"{current_year}/{date_string}", "%Y/%m/%d")
    except ValueError:
        return False
    return date_obj.weekday() in [4, 5, 6]


def contains_weekend_date(text):
    date_pattern = r"\b\d{1,2}/\d{1,2}\b"
    dates = re.findall(date_pattern, text)
    for date in dates:
        if is_weekend(date):
            return True
    return False


def is_relevant_tonight(created_utc):
    created_date = datetime.utcfromtimestamp(created_utc)
    return created_date.weekday() in [3, 4, 5]


def is_relevant_tomorrow(created_utc):
    created_date = datetime.utcfromtimestamp(created_utc)
    return created_date.weekday() in [3, 4]


def final_convert_to_CEST(time_str, timezone_str):
    timezone_offsets = {
        "EST": -4,  # Considering Eastern Daylight Time (EDT)
        "PACIFIC": -7,  # Considering Pacific Daylight Time (PDT)
        "PST": -7,  # Considering Pacific Daylight Time (PDT)
        "CENTRAL": -5,  # Considering Central Daylight Time (CDT)
        "CST": -5,  # Considering Central Daylight Time (CDT)
        "MST": -6,  # Considering Mountain Daylight Time (MDT)
        "EASTERN": -4,  # Considering Eastern Daylight Time (EDT)
    }
    match = re.match(r"(\d+)(?::(\d+))?", time_str)
    hours = int(match.group(1))
    minutes = int(match.group(2) or 0)
    if "pm" in time_str.lower() and hours != 12:
        hours += 12
    utc_hours = (hours - timezone_offsets[timezone_str.upper()]) % 24
    cest_hours = (utc_hours + 2) % 24
    return f"{cest_hours:02}:{minutes:02}"


def detect_and_convert_time(text):
    text = text.lower()
    time_pattern = r"(\d{1,2}(?::\d{1,2})?\s*[apm]{0,2})\s*(est|pst|cst|mst|pacific|central|eastern)"
    matches = re.findall(time_pattern, text)
    converted_times = []
    for time_str, timezone_str in matches:
        converted_times.append(final_convert_to_CEST(time_str, timezone_str))
    return converted_times


def contains_relevant_keywords(text, created_utc):
    keyword_validators = {
        "this weekend": lambda _: True,
        "this saturday": lambda _: True,
        "tonight": is_relevant_tonight,
        "this afternoon": is_relevant_tonight,
        "tomorrow": is_relevant_tomorrow,
    }
    for keyword, validator in keyword_validators.items():
        if keyword in text.lower() and validator(created_utc):
            return True
    return False


from datetime import time


def is_within_schedule(day, given_time):
    """Checks if the given time on a specified day is within the provided schedule.

    :param day: Day of the week (e.g., "Friday", "Saturday", "Sunday")
    :param given_time: Time to check
    :return: True if within schedule, False otherwise
    """
    schedules = {
        "Friday": [time(20, 30), time(23, 0)],
        "Saturday": [time(9, 0), time(23, 0)],
        "Sunday": [time(9, 0), time(21, 0)],
    }

    if day not in schedules:
        return False

    start_time, end_time = schedules[day]
    return start_time <= given_time < end_time


def enhanced_detect_and_convert_time(text, created_utc):
    text = text.lower()
    time_pattern = r"(\d{1,2}(?::\d{1,2})?\s*[apm]{0,2})\s*(est|pst|cst|mst|pacific|central|eastern)"
    weekday_pattern = r"(monday|tuesday|wednesday|thursday|friday|saturday|sunday)"

    matches = re.findall(time_pattern, text)
    weekdays = re.findall(weekday_pattern, text)

    # If no specific day is mentioned, infer the day from the created_utc
    if not weekdays:
        weekdays = [datetime.utcfromtimestamp(created_utc).strftime("%A").lower()]

    converted_times = []
    for time_str, timezone_str in matches:
        for weekday in weekdays:
            converted_times.append(
                (weekday, final_convert_to_CEST(time_str, timezone_str))
            )
    return converted_times


from config import CLIENT_ID, CLIENT_SECRET, USERNAME, PASSWORD


reddit = praw.Reddit(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    user_agent="_LFSBot_1.0",
    username=USERNAME,
    password=PASSWORD,
)
subreddit = reddit.subreddit("DestinySherpa")
print("=====================================")

for submission in subreddit.hot(limit=50):
    if "[lts]" in submission.title.lower() and "[gos]" not in submission.title.lower():
        if (
            contains_weekend_date(submission.title)
            or contains_weekend_date(submission.selftext)
            or contains_relevant_keywords(submission.title, submission.created_utc)
            or contains_relevant_keywords(submission.selftext, submission.created_utc)
        ):
            # Use the enhanced function to extract day and time
            converted_times_title = enhanced_detect_and_convert_time(
                submission.title, submission.created_utc
            )
            converted_times_selftext = enhanced_detect_and_convert_time(
                submission.selftext, submission.created_utc
            )

            all_converted_times = [
                time for _, time in converted_times_title + converted_times_selftext
            ]

            if all_converted_times:
                print(
                    f"{submission.title} (Time: {', '.join(all_converted_times)} CEST)"
                )
            else:
                print(submission.title)

            # Check if the detected times fall within the specified schedule
            # if any(
            #     is_within_schedule(
            #         day.capitalize(), datetime.strptime(t, "%H:%M").time()
            #     )
            #     for day, t in converted_times_title + converted_times_selftext
            # ):
            #     submission.reply(
            #         "Hello, I would love to be joining this! I am a Warlock. Discord: tix555#1664 Bungie id: tix555#7313"
            #     )
