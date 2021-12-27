import logging
import sys
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path
from urllib.request import urlopen

from dateutil import parser
from moviepy.editor import VideoFileClip

from mustachizer.errors import ImageIncorrectError, NoFaceFoundError
from mustachizer.mustache_applicator import MustacheApplicator
from mustachizer.twitter.errors import (
    TweetNotReachable,
    TwitterConnectionError,
    TwitterTokenError,
)
from mustachizer.twitter.tweepy_wrapper import TweepyWrapper
from mustachizer.utilities.sentence_provider import SentenceProvider

logger = logging.getLogger("stachlog")


class BotTwitter:
    """
    The Twiter Bot.
    """

    def __init__(self):
        """
        Construct twitter's StacheBot.
        """
        # Set up
        self.last_datetime = datetime.now(timezone.utc)
        self.mustachizer = MustacheApplicator(debug=False)
        self.sentence_provider = SentenceProvider()

        # Tweepy configuration
        try:
            self.tweepy_wrapper = TweepyWrapper()
        except TwitterTokenError as error:
            logger.error(error)
            sys.exit(1)

    def run(self) -> None:
        """
        Brings bot to life.
        """
        try:
            self.tweepy_wrapper.connect()
            logger.info(f"Connected to '{self.name}' @{self.screen_name}\n")
        except TwitterConnectionError as error:
            logger.error(error)
            sys.exit(1)

        while True:
            # TODO except error from get_new_mentions
            mentions = self.tweepy_wrapper.get_new_mentions(
                posted_after=self.last_datetime
            )
            self.process_mentions(mentions)

    def process_mentions(self, mentions: list):
        for tweet in mentions:
            logger.info("+~~~~ NEW MENTION")
            # TODO except error from get_tweet_containing_medias
            tweet_with_medias = self.get_tweet_containing_medias(tweet=tweet)

            # Update datetime with datetime of last mention
            self.last_datetime = max(
                self.last_datetime,
                parser.parse(tweet["created_at"]),
            )

            # Bad case :(
            if not tweet_with_medias:
                logger.info("+ Tweet ignored.")
                continue
            # Mustachize
            try:
                medias = self.mustachize_medias(
                    medias=tweet_with_medias["extended_entities"]["media"]
                )
                if medias:
                    message = self.sentence_provider.provide()
                else:
                    message = "No face found. Can't mustachize :("
            except NotImplementedError as error:
                medias = []
                message = error

            # Reply
            try:
                self.tweepy_wrapper.reply_to_status(
                    medias=medias, msg=message, status_id=tweet["id_str"]
                )
            except (TweetNotReachable, NotImplementedError) as error:
                logger.error(f"X {error}")
        else:
            logger.info("+~~~~ ALL DONE\n")

    def get_tweet_containing_medias(self, tweet: dict) -> dict:
        """
        Identify and return tweet to respond to.

        :param tweet: Tweet mentioning the bot.
        """
        # The mention is in a tweet with media
        if "media" in tweet["entities"]:
            logger.info("+ Mentioned in a tweet containing media(s).")
            return tweet

        # The mention is in a reply of a tweet
        if tweet["in_reply_to_status_id_str"]:

            # The mention is caused by someone replying to the bot
            if tweet["in_reply_to_user_id_str"] == self.id_str:
                logger.info("+ Caused by a reply to the bot.")
                return {}

            # Everything seems fine
            logger.info("+ Mentioned in a reply.")
            replying_to = self.get_tweet_object(tweet["in_reply_to_status_id_str"])

            # The tweet to which the mention responds contains media
            if "media" in replying_to["entities"]:
                logger.info("+ Reply contains medias.")
                return replying_to

            logger.info("+ No media found in reply.")
            return {}

        # The mention comes from something else (QRT...)
        logger.info("+ Mention type not supported.")
        return {}

    def download_media_from_url(
        self, url: str, convert_to_gif: bool = False, tmp_folder: Path = Path("/tmp")
    ) -> BytesIO:
        """
        Download media from url.

        :param url: url's media.
        :param convert_to_gif: media must be converted to gif.
        :tmp_folder: where to save temporary video files when converting to gif.

        :return: downloaded media
        """
        file = urlopen(url)
        if not convert_to_gif:
            return file.read()

        # TODO tmp must be in mustachizer folder
        try:
            tmp_filepath = Path(tmp_folder)
            with open(tmp_filepath / "video_to_gif", "wb") as save_file:
                save_file.write(file.read())
            clip = VideoFileClip(
                filename=f"{tmp_filepath}/video_to_gif",
                audio=False,
            )
            clip.write_gif(
                filename=tmp_filepath / "output.gif",
                fps=None,
                program="ffmpeg",
                logger=None,
            )
            return open(tmp_filepath / "output.gif", "rb").read()
        # TODO do not return BytesIO() object but raise exception instead
        except OSError as error:
            logger.error(f"X {error}")
            return BytesIO()

    def mustachize_medias(self, medias: list) -> list:
        """
        Put mustachs on medias.

        :param medias: list of medias to mustachize
        """
        logger.debug(f"| {len(medias)} medias found:")

        mustachized_medias = []
        for media in medias:
            media_type = media["type"]

            if media_type == "photo":
                url = media["media_url_https"]
                convert_to_gif = False

            if media_type == "animated_gif":
                url = media["video_info"]["variants"][0]["url"]
                convert_to_gif = True

            if media_type == "video":
                error_message = "Media is a video and videos are not yet supported."
                logger.error(f"X {error_message}")
                raise NotImplementedError(error_message)

            logger.info(f"+-- Processing: {media_type.replace('_',' ')} ({url})")

            # TODO raise exception in download_media_from_url()
            image_buffer = self.download_media_from_url(
                url=url,
                convert_to_gif=convert_to_gif,
            )
            try:
                mustachized_media = self.mustachizer.mustachize(BytesIO(image_buffer))
                mustachized_medias.append(mustachized_media)
            except (NoFaceFoundError, ImageIncorrectError) as error:
                logger.warning(f"X {error}")

        return mustachized_medias

    def get_tweet_object(self, id: str) -> dict:
        return self.tweepy_wrapper.api.lookup_statuses(id=[id])[0]._json

    @property
    def id_str(self):
        return self.tweepy_wrapper.id_str

    @property
    def name(self):
        return self.tweepy_wrapper.name

    @property
    def screen_name(self):
        return self.tweepy_wrapper.screen_name
