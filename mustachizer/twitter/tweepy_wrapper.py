import logging
from datetime import datetime

from dateutil import parser
from tweepy import API, OAuthHandler

from mustachizer import PATH
from mustachizer.twitter.errors import TweepyWrapperError
from mustachizer.utilities import JSONFilepathError, LoadJSON

logger = logging.getLogger("stachlog")


class TweepyWrapper:
    """
    Homemade wrapper for Tweepy.
    """

    def __init__(self):
        """
        Construct the Tweepy wrapper.
        """

        # Token
        credentials_filepath = PATH / "mustachizer" / "twitter" / "credentials.json"
        try:
            self.token = LoadJSON(filepath=credentials_filepath)
        except JSONFilepathError as error:
            raise TweepyWrapperError(error) from error

        # API
        self.api = None

    # TODO raise Exeption if fail
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

        logger.info(f"Connected to '{self.name}' @{self.screen_name}")

    # TODO raise Exeption if fail
    def get_new_mentions(self, posted_after_date: datetime) -> list:
        """
        Get a list of all mentions that have appeared during the last period of time.

        :param posted_after_date: get mentions after this datetime
        """
        return [
            status._json
            for status in self.api.mentions_timeline()
            if parser.parse(status._json["created_at"]) > posted_after_date
        ]

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
            self.api.update_status(
                status=msg,
                media_ids=media_ids,
                in_reply_to_status_id=status_id,
                auto_populate_reply_metadata=True,
            )
            logger.info("Replied.")
            return

        # No medias
        if msg == "":
            status = "No face found. Can't mustachize :("

        self.api.update_status(
            status=status,
            in_reply_to_status_id=status_id,
            auto_populate_reply_metadata=True,
        )
        logger.info("Replied.")

    @property
    def info(self):
        return self.api.verify_credentials()._json

    @property
    def name(self):
        return self.info["name"]

    @property
    def screen_name(self):
        return self.info["screen_name"]

    @property
    def id_str(self):
        return self.info["id_str"]
