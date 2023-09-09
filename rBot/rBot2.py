import praw
from helpers2 import (
    contains_weekend_date,
    detect_and_convert_time,
    contains_relevant_keywords,
)

from config import CLIENT_ID, CLIENT_SECRET


reddit = praw.Reddit(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    user_agent="_LFSBot_1.0",
)
subreddit = reddit.subreddit("DestinySherpa")
print("=====================================")

for submission in subreddit.hot(limit=200):
    if "[lts]" in submission.title.lower() and "[gos]" not in submission.title.lower():
        if (
            contains_weekend_date(submission.title)
            or contains_weekend_date(submission.selftext)
            or contains_relevant_keywords(submission.title, submission.created_utc)
            or contains_relevant_keywords(submission.selftext, submission.created_utc)
        ):
            converted_times_title = detect_and_convert_time(submission.title)
            converted_times_selftext = detect_and_convert_time(submission.selftext)
            all_converted_times = converted_times_title + converted_times_selftext

            if all_converted_times:
                print(
                    f"{submission.title} (Time: {', '.join(all_converted_times)} CEST)"
                )
            else:
                print(submission.title)
