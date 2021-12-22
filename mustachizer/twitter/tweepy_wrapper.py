import logging
from datetime import datetime
from time import sleep

import tweepy
from dateutil import parser
from tweepy import API, OAuthHandler
from tweepy.errors import TweepyException

from mustachizer import PATH
from mustachizer.twitter.errors import (
    TweetNotReachable,
    TwitterConnectionError,
    TwitterTokenError,
)
from mustachizer.utilities import JSONLoaderError, LoadJSON

logger = logging.getLogger("stachlog")


class TweepyWrapper:
    """
    Homemade wrapper for Tweepy.
    """

    TOKEN_REQUIREMENT = {
        "API_KEY",
        "API_SECRET_KEY",
        "ACCESS_TOKEN",
        "ACCESS_TOKEN_SECRET",
    }

    def __init__(self):
        """
        Construct the Tweepy wrapper.
        """
        # Info
        self.info = None

        # Token
        self.token = None
        self.load_token()

        # API
        self.api = None

    def load_token(self) -> None:
        """
        Load and check connection token from JSON file.

        :raises TwitterTokenError: can't load token or token missing parameters
        """
        # Load
        credentials_filepath = PATH / "mustachizer" / "twitter" / "credentials.json"
        try:
            self.token = LoadJSON(filepath=credentials_filepath)
        except JSONLoaderError as error:
            raise TwitterTokenError(error) from error

        # Check
        if not self.TOKEN_REQUIREMENT.issubset(self.token):
            missing_parameters = self.TOKEN_REQUIREMENT - self.token.keys()
            error_message = (
                f"Missing parameter(s) {missing_parameters} "
                f"in '{credentials_filepath}'."
            )
            raise TwitterTokenError(error_message)

    def connect(self) -> None:
        """
        Connect to the Twitter API.
        """
        auth = OAuthHandler(
            self.token["API_KEY"],
            self.token["API_SECRET_KEY"],
        )
        auth.secure = True
        auth.set_access_token(
            self.token["ACCESS_TOKEN"],
            self.token["ACCESS_TOKEN_SECRET"],
        )
        self.api = API(auth, wait_on_rate_limit=True)
        try:
            self.info = self.api.verify_credentials()._json
        except TweepyException as error:
            error_message = "Failed to establish a new connection to 'api.twitter.com'."
            raise TwitterConnectionError(error_message) from error

    # TODO raise Exeption if fail
    def get_new_mentions(self, posted_after: datetime) -> list:
        """
        Get a list of all mentions that have appeared during the last period of time.

        :param posted_after_date: get mentions after this datetime
        """
        logger.info("+++ WAITING")

        new_mentions = []
        while not new_mentions:
            mentions_timeline = self.api.mentions_timeline()
            logger.debug(f"| {len(mentions_timeline)} status found...")

            for status in mentions_timeline:
                status = status._json
                # Status must neither be a retweet or an old tweet
                if (
                    parser.parse(status["created_at"]) > posted_after
                    and "retweeted_status" not in status
                ):
                    new_mentions.append(status)

            sleep(12)

        logger.info(f"+ {len(new_mentions)} new mention(s).")
        logger.info("+++ STOP WAITING\n")
        return new_mentions

    def reply_to_status(
        self, medias: dict = [], msg: str = "", status_id: str = ""
    ) -> None:
        """
        Reply to a tweet.

        :param medias: list of medias to post
        :param msg: text to post
        :param status_id: tweet's id to reply to
        """
        if medias:
            media_ids = [
                self.api.media_upload(file=media, filename="").media_id_string
                for media in medias
            ]
        else:
            media_ids = None

        try:
            self.api.update_status(
                status=msg,
                media_ids=media_ids,
                in_reply_to_status_id=status_id,
                auto_populate_reply_metadata=True,
            )
        # TODO handle this and post big medias
        except tweepy.errors.BadRequest as error:
            error_message = "Media too big, file size must be under 5242880 bytes."
            raise NotImplementedError(error_message) from error
        except tweepy.errors.Forbidden as error:
            error_message = "Tweet deleted or no more visible to you."
            raise TweetNotReachable(error_message) from error

    @property
    def name(self):
        return self.info["name"]

    @property
    def screen_name(self):
        return self.info["screen_name"]

    @property
    def id_str(self):
        return self.info["id_str"]
