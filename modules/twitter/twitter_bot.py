import json
import logging
import tweepy

from datetime import datetime
from datetime import timezone

from dateutil import parser
from io import BytesIO
from moviepy.editor import VideoFileClip
from urllib.request import urlopen

from modules.mustache.errors import ImageIncorrectError
from modules.mustache.errors import NoFaceFoundError
from modules.mustache.mustachizer import Mustachizer
from modules.mustache.sentence_provider import SentenceProvider

# PATH="/home/pi/Bots/Stachebot/"
PATH = "./"


class BotTwitter:
    """Start the StacheBot on Twitter.

    :param debug: Whether it should print stuffs, defaults to False
    :type debug: bool, optional
    """

    def __init__(self, debug=False):
        """The constructor."""
        self.__debug = debug
        self.__lastdate = datetime.now(timezone.utc)
        self.__mustachizer = Mustachizer(debug=False)
        self.__sentence_provider = SentenceProvider()
        self.__token = self._get_credentials()
        self.__api = self._connect()

    def _get_credentials(self):
        """Get the credentials stored in `credentials.json`

        :return: connection token
        :rtype: dict
        """
        with open(f"{PATH}modules/twitter/credentials.json", "r") as f:
            token = json.load(f)
        return token

    def _connect(self):
        """Connect to the Twitter API."""
        auth = tweepy.OAuthHandler(
            self.__token["API_KEY"], self.__token["API_SECRET_KEY"]
        )
        auth.secure = True
        auth.set_access_token(
            self.__token["ACCESS_TOKEN"], self.__token["ACCESS_TOKEN_SECRET"]
        )
        api = tweepy.API(auth, wait_on_rate_limit=True)

        logging.info(f"Connected to '{api.me().name}' @{api.me().screen_name}")
        return api

    def _download_media_from_url(self, url, convert_to_gif=False):
        """Download media from its url.

        :param url: media's url
        :type url: str

        :param convert_to_gif: flag saying that media is not an image
        :type convert_to_gif: boolean

        :return: downloaded media
        :rtype: file
        """
        file = urlopen(url)
        if convert_to_gif:
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
        else:
            return file.read()

    def _mustachize_medias(self, medias):
        """Mustachize medias.

        :param medias: medias to mustachize
        :type medias: dict of dict

        :return: mustachized medias
        :rtype: list of io.BytesIO
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
                output = self.__mustachizer.mustachize(BytesIO(image_buffer))
                mustachized_medias.append(output)
                logging.info(f"\t{url} -> Mustachized")
            except NoFaceFoundError:
                logging.info(f"\t{url} -> No Faces found")
            except ImageIncorrectError as e:
                logging.error(e)

        return mustachized_medias

    def _get_last_mentions(self, max_tweets=1000):
        """Get a list of all mentions that have appeared during the last period of time.

        :param max_tweets: number max of tweets to scrap (default 1000)
        :return max_tweets: int
        """
        searched_tweets = [
            status._json
            for status in tweepy.Cursor(
                self.__api.search, q=f"@{self.__api.me().screen_name}"
            ).items(max_tweets)
        ]

        last_mentions = [
            tweet
            for tweet in searched_tweets
            if self.__api.me().screen_name
            in [t["screen_name"] for t in tweet["entities"]["user_mentions"]]
        ]

        return [
            tweet
            for tweet in last_mentions
            if self.__lastdate < parser.parse(tweet["created_at"])
        ]

    def _reply_with_twitter_api(self, medias=None, status="", in_reply_to_status_id=""):
        """Reply to a tweet with a media

        :param medias: list of medias to post
        :type medias: dict of io.BytesIO

        :param status: status to post
        :type status: str (default : "")

        :param in_reply_to_status_id: id of tweet to reply to
        :type in_reply_to_status_id: str (default : "")
        """

        if len(medias) != 0:
            status = self.__sentence_provider.provide()
            media_ids = [
                self.__api.media_upload(file=media, filename="").media_id_string
                for media in medias
            ]
            self.__api.update_status(
                status=status,
                media_ids=media_ids,
                in_reply_to_status_id=in_reply_to_status_id,
                auto_populate_reply_metadata=True,
            )

        # No medias
        else:
            if status == "":
                status = "No face found. Can't mustachize :("
            self.__api.update_status(
                status=status,
                in_reply_to_status_id=in_reply_to_status_id,
                auto_populate_reply_metadata=True,
            )

        logging.info("Replied.")

    def _reply_to_last_mentions(self):
        """
        Responds to all mentions that have appeared
        during the last period of time.
        """
        last_mentions = self._get_last_mentions()

        if len(last_mentions) != 0:
            logging.info(
                f"{datetime.now(timezone.utc)} UTC : {len(last_mentions)} new mention"
            )

        for tweet in last_mentions:
            tweet_with_medias = None

            # The mention is caused by a RT
            if "retweeted_status" in tweet:
                logging.info("Mention type : retweet")

            # The mention is in a tweet with media
            elif "media" in tweet["entities"]:
                logging.info("Mention type : media")
                tweet_with_medias = tweet

            # The mention is in a reply of a tweet
            elif tweet["in_reply_to_status_id_str"]:

                # The mention is caused by someone replying to the bot
                if tweet["in_reply_to_user_id_str"] == self.__api.me().id_str:
                    logging.info("Mention type : bot reply")

                # Everything seems fine
                else:
                    logging.info("Mention type : reply")
                    replying_to = self.__api.statuses_lookup(
                        [tweet["in_reply_to_status_id_str"]]
                    )[0]._json

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
                self._reply_with_twitter_api(
                    medias, in_reply_to_status_id=tweet["id_str"]
                )

        # Update date with date of last mention
        if last_mentions:
            self.__lastdate = parser.parse(last_mentions[0]["created_at"])

    def run(self):
        # while True:
        #     try:
        self._reply_to_last_mentions()

    # except tweepy.errors.TweepyException as e:
    #     logging.error(e)
