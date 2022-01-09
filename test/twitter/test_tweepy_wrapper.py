import logging
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import Mock, patch

from tweepy import API
from tweepy.errors import Forbidden, TweepyException

from mustachizer.logging.configuration import ConfigureLogger
from mustachizer.twitter.errors import (
    TweetNotReachable,
    TwitterConnectionError,
    TwitterTokenError,
)
from mustachizer.twitter.tweepy_wrapper import TweepyWrapper
from mustachizer.utilities import JSONLoaderError

# Create logger at the correct level
ConfigureLogger(console_level="DEBUG")
logger = logging.getLogger("stachlog")

# Credentials
CREDENTIALS_OK_FILEPATH = Path("test", "resources", "twitter", "credentials_ok.json")
CREDENTIALS_KO_FILEPATH = Path("test", "resources", "twitter", "credentials_ko.json")

# Tweepy API bad response
TWEEPY_RESPONSE = Mock()
TWEEPY_RESPONSE.json.return_value = {}

# Mentions in timeline
MENTION_OK = Mock()
MENTION_OK._json = {
    "created_at": "Sat Dec 25 00:00:00 +0000 2100",
    "message": "This is ok mention",
}
MENTION_KO = Mock()
MENTION_KO._json = {
    "created_at": "Sat Dec 25 00:00:00 +0000 2000",
    "message": "This is ko mention",
}
MENTIONS_TIMELINE = [MENTION_OK, MENTION_KO]


class TestBotTwitter(unittest.TestCase):
    """
    Test `mustachizer.twitter.twitter_bot.TweepyWrapper`.
    """

    def setUp(self):
        # Tweepy wrapper
        with patch.object(
            TweepyWrapper, "CREDENTIALS_FILEPATH", CREDENTIALS_OK_FILEPATH
        ):
            self.tweepy_wrapper = TweepyWrapper()

    def test__init__(self):
        self.assertIsNone(self.tweepy_wrapper.info)
        self.assertEqual(
            self.tweepy_wrapper.token,
            {
                "API_SECRET_KEY": "API_SECRET_KEY",
                "ACCESS_TOKEN_SECRET": "ACCESS_TOKEN_SECRET",
                "API_KEY": "API_KEY",
                "ACCESS_TOKEN": "ACCESS_TOKEN",
            },
        )
        self.assertIsNone(self.tweepy_wrapper.api)

    def test_load_token(self):
        # load_token KO: JSONLoaderError
        with self.assertRaises(TwitterTokenError), patch(
            "mustachizer.twitter.tweepy_wrapper.LoadJSON"
        ) as patched_LoadJSON:
            patched_LoadJSON.side_effect = JSONLoaderError
            self.tweepy_wrapper.load_token()

        # load_token KO: Missing parameters
        with self.assertRaises(TwitterTokenError), patch.object(
            TweepyWrapper, "CREDENTIALS_FILEPATH", CREDENTIALS_KO_FILEPATH
        ):
            self.tweepy_wrapper.load_token()

    @patch("mustachizer.twitter.tweepy_wrapper.OAuthHandler")
    def test_connect(self, patched_OAuthHandler):
        # connect OK
        with patch("mustachizer.twitter.tweepy_wrapper.API"):
            self.tweepy_wrapper.connect()

        # connect KO: TweepyException
        with self.assertRaises(TwitterConnectionError), patch.object(
            API, "verify_credentials"
        ) as patched_API:
            patched_API.side_effect = TweepyException
            self.tweepy_wrapper.connect()

    def test_get_new_mentions(self):
        self.tweepy_wrapper.api = Mock()
        self.tweepy_wrapper.api.mentions_timeline.return_value = MENTIONS_TIMELINE

        new_mentions = self.tweepy_wrapper.get_new_mentions(
            posted_after=datetime.now(timezone.utc)
        )
        self.assertEqual(
            new_mentions,
            [
                {
                    "created_at": "Sat Dec 25 00:00:00 +0000 2100",
                    "message": "This is ok mention",
                }
            ],
        )

    def test_reply_to_status(self):
        self.tweepy_wrapper.api = Mock()

        # reply_to_status OK
        # self.tweepy_wrapper.reply_to_status(["media1", "media2"])

        # reply_to_status KO: Forbidden
        self.tweepy_wrapper.api.update_status.side_effect = Forbidden(TWEEPY_RESPONSE)
        with self.assertRaises(TweetNotReachable):
            self.tweepy_wrapper.reply_to_status()

    def test_properties(self):
        self.tweepy_wrapper.info = {
            "name": "tweepy_name",
            "screen_name": "tweepy_screen_name",
            "id_str": "tweepy_id_str",
        }
        self.assertEqual(
            self.tweepy_wrapper.name,
            "tweepy_name",
        )
        self.assertEqual(
            self.tweepy_wrapper.screen_name,
            "tweepy_screen_name",
        )
        self.assertEqual(
            self.tweepy_wrapper.id_str,
            "tweepy_id_str",
        )
