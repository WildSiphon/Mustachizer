import datetime
import logging
import unittest
from unittest.mock import Mock, patch

from mustachizer.logging.configuration import ConfigureLogger
from mustachizer.mustache_applicator import MustacheApplicator
from mustachizer.twitter.errors import (  # TweetNotReachable,
    TwitterConnectionError,
    TwitterTokenError,
)
from mustachizer.twitter.tweepy_wrapper import TweepyWrapper
from mustachizer.twitter.twitter_bot import BotTwitter
from mustachizer.utilities.sentence_provider import SentenceProvider

# Create logger at the correct level
ConfigureLogger(console_level="ERROR")
logger = logging.getLogger("stachlog")

TWEET_TEMPLATE = {
    "entities": None,
    "in_reply_to_status_id_str": None,
}


class TestBotTwitter(unittest.TestCase):
    """
    Test `mustachizer.twitter.twitter_bot.BotTwitter`.
    """

    def setUp(self):
        # BotTwitter
        patched_TweepyWrapper = Mock()
        patched_TweepyWrapper.id_str = "bot_id_str"
        patched_TweepyWrapper.name = "bot_name"
        patched_TweepyWrapper.screen_name = "bot_screen_name"
        with patch(
            "mustachizer.twitter.twitter_bot.TweepyWrapper",
            return_value=patched_TweepyWrapper,
        ):
            self.twitter_bot = BotTwitter()

        # Tweet template
        self.tweet_template = {
            "in_reply_to_user_id_str": "user_id_str",
            "in_reply_to_status_id_str": "status_id_str",
            "entities": {},
        }

    def test__init__(self):
        """
        Test initialization.
        """
        # Initialization KO
        self.assertIsInstance(self.twitter_bot.last_datetime, datetime.datetime)
        self.assertIsInstance(self.twitter_bot.mustachizer, MustacheApplicator)
        self.assertIsInstance(self.twitter_bot.sentence_provider, SentenceProvider)
        self.assertIsNotNone(self.twitter_bot.tweepy_wrapper)

        # Initialization KO
        patched_TweepyWrapper = Mock(side_effect=TwitterTokenError())
        with patch.object(
            TweepyWrapper, "__init__", patched_TweepyWrapper
        ), self.assertRaises(SystemExit):
            BotTwitter()

    def test_run(self):
        """
        Test run method.
        """
        # Run OK: raise Exception to stop while loop
        patched_process_mentions = Mock(side_effect=Exception())
        with patch.object(
            BotTwitter, "process_mentions", patched_process_mentions
        ), self.assertRaises(Exception):
            self.twitter_bot.run()
            self.twitter_bot.tweepy_wrapper.get_new_mentions.assert_called()
            self.twitter_bot.process_mentions.assert_called()

        # Run KO
        with self.assertRaises(SystemExit):
            self.twitter_bot.tweepy_wrapper.connect = Mock(
                side_effect=TwitterConnectionError
            )
            self.twitter_bot.run()

    def test_process_mentions(self):
        pass

    def test_get_tweet_containing_medias(self):
        # Tweet is a reply to a status
        with patch.object(BotTwitter, "get_tweet_object") as returned_tweet_object:
            # Status does not contain medias
            returned_tweet_object.return_value = {"entities": {}}
            return_tweet = self.twitter_bot.get_tweet_containing_medias(
                tweet=self.tweet_template
            )
            self.assertEqual(return_tweet, {})

            # Status contains medias
            returned_tweet_object.return_value = {"entities": {"media": {}}}
            return_tweet = self.twitter_bot.get_tweet_containing_medias(
                tweet=self.tweet_template
            )
            self.assertEqual(return_tweet, {"entities": {"media": {}}})

        # Tweet is a reply to the bot
        self.tweet_template["in_reply_to_user_id_str"] = "bot_id_str"
        return_tweet = self.twitter_bot.get_tweet_containing_medias(
            tweet=self.tweet_template
        )
        self.assertEqual(return_tweet, {})

        # Mention type not supported
        self.tweet_template["in_reply_to_status_id_str"] = None
        return_tweet = self.twitter_bot.get_tweet_containing_medias(
            tweet=self.tweet_template
        )
        self.assertEqual(return_tweet, {})

        # Tweet contains medias
        self.tweet_template["entities"] = {"media": {}}
        return_tweet = self.twitter_bot.get_tweet_containing_medias(
            tweet=self.tweet_template
        )
        self.assertEqual(return_tweet, self.tweet_template)

    def test_download_media_from_url(self):
        pass

    def test_mustachize_medias(self):
        pass

    def test_get_tweet_object(self):
        pass

    def test_id_str(self):
        self.assertEqual(self.twitter_bot.id_str, "bot_id_str")

    def test_name(self):
        self.assertEqual(self.twitter_bot.name, "bot_name")

    def test_screen_name(self):
        self.assertEqual(self.twitter_bot.screen_name, "bot_screen_name")


if __name__ == "__main__":
    unittest.main()
