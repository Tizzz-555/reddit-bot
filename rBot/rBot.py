import praw
import time
import logging
from datetime import datetime
from config import CLIENT_ID, CLIENT_SECRET, USER_AGENT, USERNAME, PASSWORD
from helpers import (
    extract_information,
    convert_date,
    convert_time,
    is_within_schedule,
)


def main():
    # Setting up logging
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )
    # Initialize Reddit client
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
                if "[lts]" in submission.title.lower():
                    # Extract information from the title
                    date_str, time_str, timezone_str = extract_information(
                        submission.title
                    )

                    # If any information is missing, skip this submission
                    if not (date_str and time_str and timezone_str):
                        continue

                    # Convert date and time to CEST
                    date_obj = convert_date(date_str)
                    time_obj = convert_time(time_str, timezone_str)

                    # Check if the date and time fit into the provided schedule
                    if is_within_schedule(date_obj, time_obj):
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
