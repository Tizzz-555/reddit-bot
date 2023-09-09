import praw
import time
import logging

from helpers import (
    contains_weekend_date,
    detect_and_convert_time,
    contains_relevant_keywords,
    is_within_schedule,
)


from datetime import datetime


from config import CLIENT_ID, CLIENT_SECRET, USER_AGENT, USERNAME, PASSWORD


def main():
    # Setting up logging
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    reddit = praw.Reddit(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        user_agent=USER_AGENT,
        username=USERNAME,
        password=PASSWORD,
    )
    subreddit = reddit.subreddit("DestinySherpa")
    logging.info("Bot started")

    print("=====================================")
    current_datetime = datetime.now()

    while True:
        try:
            for submission in subreddit.hot(limit=20):
                if (
                    "[lts]" in submission.title.lower()
                    and "[gos]" not in submission.title.lower()
                ):
                    if (
                        contains_weekend_date(submission.title)
                        or contains_weekend_date(submission.selftext)
                        or contains_relevant_keywords(
                            submission.title, submission.created_utc
                        )
                        or contains_relevant_keywords(
                            submission.selftext, submission.created_utc
                        )
                    ):
                        # Use the enhanced function to extract day and time
                        converted_times_title = detect_and_convert_time(
                            submission.title, submission.created_utc
                        )
                        converted_times_selftext = detect_and_convert_time(
                            submission.selftext, submission.created_utc
                        )

                        # Filter out past times
                        future_times_title = [
                            (day, t)
                            for day, t in converted_times_title
                            if datetime.strptime(
                                f"{current_datetime.year}/{day} {t}", "%Y/%A %H:%M"
                            )
                            > current_datetime
                        ]
                        future_times_selftext = [
                            (day, t)
                            for day, t in converted_times_selftext
                            if datetime.strptime(
                                f"{current_datetime.year}/{day} {t}", "%Y/%A %H:%M"
                            )
                            > current_datetime
                        ]

                        # Check if the detected times fall within the specified schedule and are in the future
                        if any(
                            is_within_schedule(
                                day.capitalize(), datetime.strptime(t, "%H:%M").time()
                            )
                            for day, t in future_times_title + future_times_selftext
                        ):
                            print(submission.title)
                            submission.reply(
                                "Hello, I would love to be joining this! I am a Warlock. Discord: tix555#1664 Bungie id: tix555#7313"
                            )
                            logging.info(f"Replied to post: {submission.id}")
                            return

            # Monitor the rate limits
            used = int(reddit.auth.limits["used"])
            remaining = int(reddit.auth.limits["remaining"])
            reset_time = int(reddit.auth.limits["reset_timestamp"] - time.time())

            logging.info(
                f"API Used: {used}, Remaining: {remaining}, Resets in: {reset_time}s"
            )

            if (
                remaining <= 10
            ):  # If we're close to the limit, wait until the reset time
                logging.warning("Close to API limit. Pausing until reset.")
                time.sleep(reset_time + 10)  # Extra 10 seconds for safety
            else:
                time.sleep(30)  # Wait for 30 seconds before the next iteration

        except Exception as e:
            logging.error(f"Error encountered: {e}")
            time.sleep(60)  # If there's an error, wait a bit before trying again


if __name__ == "__main__":
    main()
