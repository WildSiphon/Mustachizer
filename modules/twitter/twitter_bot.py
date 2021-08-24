import tweepy
import json
import requests
import os
import random
from io import BytesIO
from datetime import *
from urllib.request import urlopen
from modules.mustache.mustachizer import Mustachizer
from modules.mustache.errors import NoFaceFoundError
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
        self.__lastdate = datetime.now() - timedelta(hours=2)
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
        auth = tweepy.OAuthHandler(self.__token["API_KEY"], self.__token["API_SECRET_KEY"])
        auth.secure = True
        auth.set_access_token(self.__token["ACCESS_TOKEN"], self.__token["ACCESS_TOKEN_SECRET"])
        api = tweepy.API(auth, wait_on_rate_limit=True)
        
        if self.__debug:
            print(f"Connected to '{api.me().name}' @{api.me().screen_name}")
        return api

    def _mustachize_urls(self, urls):
        """Download pictures from urls and mustachize them.

        :param urls: urls of medias to mustachize
        :type urls: dict

        :return: mustachized medias
        :rtype: dict of io.BytesIO
        """
        if self.__debug:
            print(f"{len(urls)} pictures :")
       
        medias = []
        for url in urls:
            url_file = urlopen(url)
            image_buffer = url_file.read()
            try:
                output = self.__mustachizer.mustachize(BytesIO(image_buffer))
                medias.append(output)
                if self.__debug:
                    print(f"\t{url} -> Mustachized")
            except NoFaceFoundError:
                if self.__debug:
                    print(f"\t{url} -> No Faces found")
        
        return medias

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
        self.last_mentions = [
            tweet
            for tweet in last_mentions
            if self.__lastdate
            < datetime.strptime(tweet["created_at"], "%a %b %d %H:%M:%S +0000 %Y")
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
                self.__api.media_upload(file=media,filename="").media_id_string
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

        if self.__debug:
            print("Replied.")

    def reply_to_last_mentions(self):
        """Responds to all mentions that have appeared during the last period of time."""
        self._get_last_mentions()

        if self.__debug and len(self.last_mentions) != 0:
            print(
                f"{datetime.now()-timedelta(hours=2)} GMT +00:00 : {len(self.last_mentions)} new mention"
            )

        for tweet in self.last_mentions:
            self.tweet_with_medias = None
            
            # The mention is caused by a RT
            if "retweeted_status" in tweet:
                if self.__debug:
                    print(" Someone retweeted a mention. Ignoring.")

            # The mention is in a tweet with media
            elif "media" in tweet["entities"]:
                if self.__debug: print(' Type "media"', end=" ")
                self.tweet_with_medias = tweet

            # The mention is in a reply of a tweet
            elif tweet["in_reply_to_status_id_str"]:

                # The mention is caused by someone replying to the bot
                if tweet["in_reply_to_user_id_str"] == self.__api.me().id_str:
                    if self.__debug:
                        print(" Someone responded to a mustache. Ignoring.")
                
                # Everything seems fine
                else:
                    if self.__debug: print(' Type "reply"', end=" ")
                    replying_to = self.__api.statuses_lookup(
                        [tweet["in_reply_to_status_id_str"]]
                    )[0]._json

                    # The tweet to which the mention responds contains media
                    if "media" in replying_to["entities"]:
                        self.tweet_with_medias = replying_to
                    else:
                    #     self._reply_with_twitter_api(
                    #         status="Could not get any media from the tweet you're replying to :(",
                    #         in_reply_to_status_id=tweet["id_str"],
                    #     )
                        if self.__debug:
                            print(" No media found. Ignoring.")

            # The mention comes from something else (QRT...)
            else:
                print(" Not a response nor a RT and no media added to the tweet")
            
            # If good conditions where reunited
            if self.tweet_with_medias:
                urls = [
                    media["media_url_https"]
                    for media in self.tweet_with_medias["extended_entities"]["media"]
                ]

                # Mustachize
                medias = self._mustachize_urls(urls)
                
                # Reply
                self._reply_with_twitter_api(
                    medias, in_reply_to_status_id=tweet["id_str"]
                )

        # Update date with date of last mention
        if self.last_mentions:
            self.__lastdate = datetime.strptime(
                self.last_mentions[0]["created_at"], "%a %b %d %H:%M:%S +0000 %Y"
            )
