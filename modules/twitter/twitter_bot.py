import tweepy
import json
import requests
import os
import random
from urllib.request import urlopen
from io import BytesIO
from datetime import *
from modules.mustache.mustachizer import Mustachizer
from modules.mustache.errors import NoFaceFoundError
from modules.mustache.sentence_provider import SentenceProvider

#PATH="/home/pi/Bots/Stachebot/"
PATH = "./"


class BotTwitter:
    """Start the StacheBot on Twitter.

    :param debug: Whether it should print stuffs, defaults to False
    :type debug: bool, optional
    """

    def __init__(self, debug=False):
        """The constructor."""
        self.debug = debug
        self.lastdate = datetime.now() - timedelta(hours=2)
        self.mustachizer = Mustachizer(debug=False)
        self.sentence_provider = SentenceProvider()
        self._connect()
        self.name = self.api.me().name
        self.screen_name = self.api.me().screen_name
        self.id = self.api.me().id_str
        if self.debug:
            print(f"Connected to '{self.name}' @{self.screen_name}")

    def _get_credentials(self):
        """Getting the credentials in `credentials.json`"""
        with open(f"{PATH}modules/twitter/credentials.json", "r") as f:
            token = json.load(f)
        self.consumer_key = token["API_KEY"]
        self.consumer_secret = token["API_SECRET_KEY"]
        self.access_token = token["ACCESS_TOKEN"]
        self.access_token_secret = token["ACCESS_TOKEN_SECRET"]

    def _connect(self):
        """Connect to the Twitter API."""
        self._get_credentials()
        auth = tweepy.OAuthHandler(self.consumer_key, self.consumer_secret)
        auth.secure = True
        auth.set_access_token(self.access_token, self.access_token_secret)
        self.api = tweepy.API(auth, wait_on_rate_limit=True)

    def _mustachize_urls(self, urls):
        """Download pictures from urls and mustachize them."""
        if self.debug:
            print(f"{len(urls)} pictures :")
        medias = []
        for url in urls:
            url_file = urlopen(url)
            image_buffer = url_file.read()
            try:
                output = self.mustachizer.mustachize(BytesIO(image_buffer))
                medias.append(output)
                if self.debug:
                    print(f"\t{url} -> Mustachized")
            except NoFaceFoundError:
                if self.debug:
                    print(f"\t{url} -> No Faces found")
        return medias

    def _get_last_mentions(self, max_tweets=1000):
        """Get a list of all mentions that have appeared during the last period of time."""
        searched_tweets = [
            status._json
            for status in tweepy.Cursor(
                self.api.search, q=f"@{self.screen_name}"
            ).items(max_tweets)
        ]
        last_mentions = [
            tweet
            for tweet in searched_tweets
            if self.screen_name
            in [t["screen_name"] for t in tweet["entities"]["user_mentions"]]
        ]
        self.last_mentions = [
            tweet
            for tweet in last_mentions
            if self.lastdate
            < datetime.strptime(tweet["created_at"], "%a %b %d %H:%M:%S +0000 %Y")
        ]

    def _reply_with_twitter_api(self, medias=None, status="", in_reply_to_status_id=None):
        """Reply to a tweet with a media"""
        if len(medias) != 0:
            status = self.sentence_provider.provide()
            media_ids = [
                self.api.media_upload(file=media,filename="").media_id_string
                for media in medias
            ]
            self.api.update_status(
                status=status,
                media_ids=media_ids,
                in_reply_to_status_id=in_reply_to_status_id,
                auto_populate_reply_metadata=True,
            )
        else:
            if status == "":
                status = "No face found. Can't mustachize :("
            self.api.update_status(
                status=status,
                in_reply_to_status_id=in_reply_to_status_id,
                auto_populate_reply_metadata=True,
            )
        if self.debug:
            print("Replied.")

    def reply_to_last_mentions(self):
        """Responds to all mentions that have appeared during the last period of time."""
        self._get_last_mentions()
        if self.debug and len(self.last_mentions) != 0:
            print(
                f"{datetime.now()-timedelta(hours=2)} GMT +00:00 : {len(self.last_mentions)} new mention"
            )
        for tweet in self.last_mentions:
            print(tweet)
            self.tweet_with_medias = None
            if "retweeted_status" in tweet:
                if self.debug:
                    print(" Someone retweeted a mention. Ignoring.")
            elif "media" in tweet["entities"]:
                if self.debug:
                    print(' Type "media"', end=" ")
                self.tweet_with_medias = tweet
            elif tweet["in_reply_to_status_id_str"]:
                if tweet["in_reply_to_user_id_str"] == self.id:
                    if self.debug:
                        print(" Someone responded to a mustache. Ignoring.")
                else:
                    if self.debug:
                        print(' Type "reply"', end=" ")
                    replying_to = self.api.statuses_lookup(
                        [tweet["in_reply_to_status_id_str"]]
                    )[0]._json
                    print(replying_to)
                    if "media" in replying_to["entities"]:
                        self.tweet_with_medias = replying_to
                    else:
                    #     self._reply_with_twitter_api(
                    #         status="Could not get any media from the tweet you're replying to :(",
                    #         in_reply_to_status_id=tweet["id_str"],
                    #     )
                        if self.debug:
                            print(" No media found. Ignoring.")
            else:
                print(" Not a response nor a RT and no media added to the tweet")
            if self.tweet_with_medias:
                urls = [
                    media["media_url_https"]
                    for media in self.tweet_with_medias["extended_entities"]["media"]
                ]
                medias = self._mustachize_urls(urls)
                self._reply_with_twitter_api(
                    medias, in_reply_to_status_id=tweet["id_str"]
                )
        if self.last_mentions:
            self.lastdate = datetime.strptime(
                self.last_mentions[0]["created_at"], "%a %b %d %H:%M:%S +0000 %Y"
            )