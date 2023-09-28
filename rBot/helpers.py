import re
from datetime import datetime, timedelta, time

# Define the schedules
schedules = {
    "Friday": [time(20, 0), time(22, 0)],
    "Saturday": [time(9, 0), time(22, 0)],
    "Sunday": [time(9, 0), time(17, 0)],
}


def extract_information(title):
    # Extracting date (may appear in different formats)
    date_match = re.search(r"(\d{1,2}/\d{1,2})", title)
    date_str = date_match.group(1) if date_match else None

    # Extracting time (assumes it appears in a format like '12PM' or '2pm')
    time_match = re.search(r"(\d{1,2}\s?(?:AM|PM|am|pm))", title, re.IGNORECASE)
    time_str = time_match.group(1) if time_match else None

    # Extracting timezone (we'll look for common timezones for simplicity)
    timezone_patterns = [
        (r"CEST", "CEST"),
        (r"(EST|ET)", "EST"),
        (r"GMT", "GMT"),
        (r"PST", "PST"),
        (r"BST", "BST"),
    ]
    timezone_str = None
    for pattern, tz in timezone_patterns:
        if re.search(pattern, title, re.IGNORECASE):
            timezone_str = tz
            break

    return date_str, time_str, timezone_str


def convert_date(date_str):
    # Splitting the date string into two components
    first, second = map(int, date_str.split("/"))

    # Determine if the first value is the day or month based on its size
    day, month = (first, second) if first > 12 else (second, first)

    # Assuming current year
    current_year = datetime.now().year

    # Creating a datetime object
    return datetime(year=current_year, month=month, day=day)


def convert_time(time_str, timezone):
    # Normalize the time string (remove spaces) and convert it into a datetime object
    normalized_time_str = time_str.replace(" ", "").upper()
    time_obj = datetime.strptime(normalized_time_str, "%I%p")

    # Timezone conversions to CEST
    timezone_offsets = {
        "CEST": timedelta(hours=0),
        "EST": timedelta(hours=6),
        "ET": timedelta(hours=6),
        "GMT": timedelta(hours=2),
        "PST": timedelta(hours=9),
        "BST": timedelta(hours=1),
    }

    # Apply the timezone offset
    converted_time = time_obj + timezone_offsets[timezone]

    return converted_time.time()


def is_within_schedule(date, time_obj):
    # Get the day of the week for the date
    day_of_week = date.strftime("%A")

    # Check if the day of week is in the schedule
    if day_of_week not in schedules:
        return False

    # Get the start and end time for the given day
    start_time, end_time = schedules[day_of_week]

    # Construct a datetime object from the date and time_obj
    extracted_datetime = datetime.combine(date, time_obj)

    # Check if the extracted datetime is in the past
    if extracted_datetime < datetime.now():
        return False

    # Check if the time is within the schedule for the given day
    return start_time <= time_obj <= end_time
