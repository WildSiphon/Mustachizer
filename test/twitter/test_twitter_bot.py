import datetime
import logging
import unittest
from io import BytesIO
from pathlib import Path
from unittest.mock import Mock, patch

from dateutil.tz import tzutc

from mustachizer.errors import ImageIncorrectError, NoFaceFoundError
from mustachizer.logging.configuration import ConfigureLogger
from mustachizer.mustache_applicator import MustacheApplicator
from mustachizer.twitter.errors import TwitterConnectionError, TwitterTokenError
from mustachizer.twitter.tweepy_wrapper import TweepyWrapper
from mustachizer.twitter.twitter_bot import BotTwitter
from mustachizer.utilities.sentence_provider import SentenceProvider

# Create logger at the correct level
ConfigureLogger(console_level="DEBUG")
logger = logging.getLogger("stachlog")

IMG_STREAM = open(Path("test", "resources", "twitter", "img_stream.jpg"), "rb")


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
        patched_TweepyWrapper.reply_to_status.side_effect = NotImplementedError
        patched_tweet_object = Mock()
        patched_tweet_object._json = "tweet_object"
        patched_TweepyWrapper.api.lookup_statuses.return_value = [patched_tweet_object]
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

        # Media template
        self.media_template = {
            "type": None,
            "media_url_https": "photo/url",
            "video_info": {"variants": [{"url": "animated_gif/url"}]},
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

    @patch.object(BotTwitter, "mustachize_medias")
    @patch.object(BotTwitter, "get_tweet_containing_medias")
    def test_process_mentions(
        self, patch_get_tweet_containing_medias, patch_mustachize_medias
    ):
        mentions = [
            {"created_at": "Sat Dec 25 16:14:02 +0000 2100", "id_str": "This is id"}
        ]

        # No media to mustachize
        patch_get_tweet_containing_medias.return_value = {}
        with self.assertLogs("stachlog", "INFO"):
            self.twitter_bot.process_mentions(mentions=mentions)

        # Last datetime has been updated
        self.assertEqual(
            self.twitter_bot.last_datetime,
            datetime.datetime(2100, 12, 25, 16, 14, 2, tzinfo=tzutc()),
        )

        # Tweet containing medias
        patch_get_tweet_containing_medias.return_value = {
            "extended_entities": {"media": {}}
        }

        # No media mustachized
        patch_mustachize_medias.return_value = []
        self.twitter_bot.process_mentions(mentions=mentions)

        # Medias mustachized
        patch_mustachize_medias.return_value = [{"mustachized_media": "something"}]
        self.twitter_bot.process_mentions(mentions=mentions)

        # Mustachization of media not implemented
        patch_mustachize_medias.side_effect = NotImplementedError
        with self.assertLogs("stachlog", "ERROR"):
            self.twitter_bot.process_mentions(mentions=mentions)

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

    @patch("mustachizer.twitter.twitter_bot.open")
    @patch("mustachizer.twitter.twitter_bot.urlopen")
    def test_download_media_from_url(self, patch_urlopen, patch_open):
        patch_urlopen.return_value = IMG_STREAM

        # Download photo
        file = self.twitter_bot.download_media_from_url(url="url", media_type="photo")
        self.assertEqual(file, IMG_STREAM.read())

        tmp_folder_test = Path("this/is/tmp/folder")
        # Download animated gif OK
        with patch(
            "mustachizer.twitter.twitter_bot.VideoFileClip"
        ) as patch_VideoFileClip:
            file = self.twitter_bot.download_media_from_url(
                url="url",
                media_type="animated_gif",
                tmp_folder=tmp_folder_test,
            )
            patch_VideoFileClip.assert_called_with(
                filename="this/is/tmp/folder/video_to_gif",
                audio=False,
            )

        # Download animated gif KO: wrong temporary files folder
        file = self.twitter_bot.download_media_from_url(
            url="url",
            media_type="animated_gif",
            tmp_folder=tmp_folder_test,
        )
        self.assertIsInstance(file, BytesIO)

    @patch.object(BotTwitter, "download_media_from_url")
    def test_mustachize_medias(self, patch_download_media_from_url):
        # Mock stream media downloaded
        patch_download_media_from_url.return_value = IMG_STREAM.read()

        # Media is video
        with self.assertRaises(NotImplementedError):
            self.media_template["type"] = "video"
            self.twitter_bot.mustachize_medias(medias=[self.media_template])

        # Mock MustacheApplicator for next tests
        self.twitter_bot.mustachizer = Mock()

        # Media is animated_gif
        self.media_template["type"] = "animated_gif"
        medias = self.twitter_bot.mustachize_medias(medias=[self.media_template])
        patch_download_media_from_url.assert_called_with(
            url="animated_gif/url",
            media_type="animated_gif",
        )
        self.assertIsInstance(medias, list)

        # Media is photo
        self.media_template["type"] = "photo"
        self.twitter_bot.mustachize_medias(medias=[self.media_template])
        patch_download_media_from_url.assert_called_with(
            url="photo/url",
            media_type="photo",
        )

        # NoFaceFoundError
        self.twitter_bot.mustachizer.mustachize.side_effect = NoFaceFoundError()
        with self.assertLogs("stachlog", "WARNING"):
            self.twitter_bot.mustachize_medias(medias=[self.media_template])

        # ImageIncorrectError
        self.twitter_bot.mustachizer.mustachize.side_effect = ImageIncorrectError()
        with self.assertLogs("stachlog", "WARNING"):
            self.twitter_bot.mustachize_medias(medias=[self.media_template])

    def test_get_tweet_object(self):
        tweet_object = self.twitter_bot.get_tweet_object(id="id")
        self.twitter_bot.tweepy_wrapper.api.lookup_statuses.assert_called_with(
            id=["id"]
        )
        self.assertEqual(tweet_object, "tweet_object")

    def test_id_str(self):
        self.assertEqual(self.twitter_bot.id_str, "bot_id_str")

    def test_name(self):
        self.assertEqual(self.twitter_bot.name, "bot_name")

    def test_screen_name(self):
        self.assertEqual(self.twitter_bot.screen_name, "bot_screen_name")


if __name__ == "__main__":
    unittest.main()
