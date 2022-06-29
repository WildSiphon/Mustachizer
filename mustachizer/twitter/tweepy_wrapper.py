import logging
from datetime import datetime
from time import sleep

from dateutil import parser
from tweepy import API, OAuthHandler
from tweepy.errors import Forbidden, TweepyException

from mustachizer import PATH
from mustachizer.twitter.errors import (
    MediaTypeError,
    MixedMediasError,
    MultipleUploadError,
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

    CREDENTIALS_FILEPATH = PATH / "mustachizer" / "twitter" / "credentials.json"

    TOKEN_REQUIREMENT = {
        "API_KEY",
        "API_SECRET_KEY",
        "ACCESS_TOKEN",
        "ACCESS_TOKEN_SECRET",
    }

    TWITTER_MEDIA_TYPES = {"photo", "animated_gif", "video"}

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
        try:
            self.token = LoadJSON(filepath=TweepyWrapper.CREDENTIALS_FILEPATH)
        except JSONLoaderError as error:
            raise TwitterTokenError(error) from error

        # Check
        if not TweepyWrapper.TOKEN_REQUIREMENT.issubset(self.token):
            missing_parameters = TweepyWrapper.TOKEN_REQUIREMENT - self.token.keys()
            error_message = (
                f"Missing parameter(s) {missing_parameters} "
                f"in '{TweepyWrapper.CREDENTIALS_FILEPATH}'."
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

        logger.info("Waiting for new mention(s)")
        logger.debug(f"Total of {len(self.api.mentions_timeline())} status found")

        new_mentions = []
        while True:
            for status in self.api.mentions_timeline():
                status = status._json
                # Status must neither be a retweet or an old tweet
                if (
                    parser.parse(status["created_at"]) > posted_after
                    and "retweeted_status" not in status
                ):
                    new_mentions.append(status)

            if new_mentions:
                break
            sleep(12)

        logger.info(f"{len(new_mentions)} new mention(s) found")
        return new_mentions

    def reply_to_status(
        self, medias: list = [], msg: str = "", status_id: str = ""
    ) -> None:
        """
        Reply to a tweet.

        :param medias: list of dict containing media buffer and twitter media type
        :param msg: text to post
        :param status_id: tweet's id to reply to
        """
        medias_types = {media["type"] for media in medias}

        # Check medias types
        bad_type = medias_types.difference(TweepyWrapper.TWITTER_MEDIA_TYPES)
        if bad_type:
            error_message = (
                f"Invalid media type given: '{', '.join(bad_type)}'. "
                f"Must be in {list(TweepyWrapper.TWITTER_MEDIA_TYPES)}."
            )
            raise MediaTypeError(error_message)

        media_ids = []

        # All medias are photos
        if all(type_ == "photo" for type_ in medias_types):
            for media in medias:
                media_ids.append(
                    self.api.media_upload(
                        filename="",
                        file=media["buffer"],
                    ).media_id_string
                )

        # All medias are GIF
        elif all(type_ == "animated_gif" for type_ in medias_types):

            if len(medias) != 1:
                error_message = "Can't upload multiple gif in a single tweet."
                raise MultipleUploadError(error_message)

            for media in medias:
                media_ids.append(
                    self.api.chunked_upload(
                        filename="",
                        file=media["buffer"],
                        file_type="image/gif",
                        media_category="tweet_gif",
                        wait_for_async_finalize=True,
                    ).media_id_string
                )

        # All medias are videos
        elif all(type_ == "video" for type_ in medias_types):
            error_message = "Mustachization of video is not yet implemented."
            raise NotImplementedError(error_message)

        else:
            error_message = "Can't upload different type of media at the same time."
            raise MixedMediasError(error_message)

        # TODO use create_media_metadata() to add alt text to medias

        try:
            self.api.update_status(
                status=msg,
                media_ids=media_ids,
                in_reply_to_status_id=status_id,
                auto_populate_reply_metadata=True,
            )
        except Forbidden as error:
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
