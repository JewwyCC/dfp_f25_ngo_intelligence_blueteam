import praw
from .config import RedditAuth


def get_reddit_client() -> praw.Reddit:
    auth = RedditAuth()
    reddit = praw.Reddit(
        client_id=auth.client_id,
        client_secret=auth.client_secret,
        user_agent=auth.user_agent,
    )
    return reddit





