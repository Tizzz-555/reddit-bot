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
