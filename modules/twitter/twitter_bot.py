import logging
from datetime import datetime, timezone
from io import BytesIO
from time import sleep
from urllib.request import urlopen

from dateutil import parser
from moviepy.editor import VideoFileClip

from modules.mustache.errors import ImageIncorrectError, NoFaceFoundError
from modules.mustache.mustachizer import Mustachizer
from modules.mustache.sentence_provider import SentenceProvider
from modules.twitter.tweepy_wrapper import TweepyWrapper


class BotTwitter:
    """
    The Twiter Bot.
    """

    def __init__(self, debug: bool = False):
        """
        Construct twitter's StacheBot.

        :param debug: Whether it should print stuffs, defaults to False
        """

        # Set up
        self.last_datetime = datetime.now(timezone.utc)
        self.mustachizer = Mustachizer(debug=debug)
        self.sentence_provider = SentenceProvider()

        # Tweepy configuration
        self.tweepy_wrapper = TweepyWrapper()

    def run(self) -> None:
        # TODO except error from connect
        self.tweepy_wrapper.connect()

        while True:
            mentions = []
            while not mentions:
                # TODO except error from get_last_mentions
                mentions = self.tweepy_wrapper.get_new_mentions(
                    posted_after_date=self.last_datetime
                )
                sleep(3)
            logging.info(
                f"{datetime.now(timezone.utc)} UTC : {len(mentions)} new mention"
            )

            for tweet in mentions:
                # TODO except error from reply_to_mentions
                self.reply_to_mentions(tweet=tweet)

    def reply_to_mentions(self, tweet: dict) -> None:
        """
        Responds to all mentions that have appeared
        during the last period of time.
        """
        tweet_with_medias = None

        # The mention is caused by a RT
        if "retweeted_status" in tweet:
            logging.info("Mention type : retweet")

        # The mention is in a tweet with media
        elif "media" in tweet["entities"]:
            tweet_with_medias = tweet
            logging.info("Mention type : media")

        # The mention is in a reply of a tweet
        elif tweet["in_reply_to_status_id_str"]:

            # The mention is caused by someone replying to the bot
            if tweet["in_reply_to_user_id_str"] == self.id_str:
                logging.info("Mention type : bot reply")

            # Everything seems fine
            else:
                logging.info("Mention type : reply")
                replying_to = self.get_tweet_object(tweet["in_reply_to_status_id_str"])

                # The tweet to which the mention responds contains media
                if "media" in replying_to["entities"]:
                    tweet_with_medias = replying_to
                else:
                    logging.info("No media found.")

        # The mention comes from something else (QRT...)
        else:
            logging.info("Mention type not supported !")

        # If good conditions were reunited
        if tweet_with_medias:
            medias = [
                media for media in tweet_with_medias["extended_entities"]["media"]
            ]

            # Mustachize
            medias = self._mustachize_medias(medias)

            # Reply
            msg = self.sentence_provider.provide()
            self.tweepy_wrapper.reply_to_status(
                medias=medias, msg=msg, status_id=tweet["id_str"]
            )

        # Update date with date of last mention
        self.last_datetime = max(self.last_datetime, parser.parse(tweet["created_at"]))

    def _download_media_from_url(
        self, url: str, convert_to_gif: bool = False
    ) -> BytesIO:
        """
        Download media from url.

        :param url: url's media
        :param convert_to_gif: media must be converted to gif

        :return: downloaded media
        """
        file = urlopen(url)
        if not convert_to_gif:
            return file.read()

        try:
            with open("/tmp/video_to_gif", "wb") as save_file:
                save_file.write(file.read())
            clip = VideoFileClip(
                filename="/tmp/video_to_gif",
                audio=False,
            )
            clip.write_gif(
                filename="/tmp/output.gif",
                fps=None,
                program="ffmpeg",
                logger=None,
            )
            return open("/tmp/output.gif", "rb").read()
        except OSError as e:
            logging.error(e)
            return BytesIO()

    def _mustachize_medias(self, medias: dict) -> list:
        """
        Mustachize medias.

        :param medias: medias to mustachize

        :return: mustachized medias
        """
        logging.info(f"{len(medias)} medias :")

        mustachized_medias = []
        for media in medias:
            if media["type"] == "photo":
                url = media["media_url_https"]
                convert_to_gif = False
            elif media["type"] == "animated_gif":
                url = media["video_info"]["variants"][0]["url"]
                convert_to_gif = True

            image_buffer = self._download_media_from_url(
                url=url,
                convert_to_gif=convert_to_gif,
            )
            try:
                output = self.mustachizer.mustachize(BytesIO(image_buffer))
                mustachized_medias.append(output)
                logging.info(f"\t{url} -> Mustachized")
            except NoFaceFoundError:
                logging.info(f"\t{url} -> No Faces found")
            except ImageIncorrectError as e:
                logging.error(e)

        return mustachized_medias

    def get_tweet_object(self, id: str) -> dict:
        return self.tweepy_wrapper.api.lookup_statuses(id=[id])[0]._json

    @property
    def id_str(self):
        return self.tweepy_wrapper.id_str
