import json
import logging

from datetime import datetime
from dateutil import parser
from pathlib import Path
from tweepy import API
from tweepy import OAuthHandler

# PATH = Path("/home/pi/Bots/Stachebot/")
PATH = Path("./")


def open_json(filepath: Path) -> dict:
    """
    Load a json file.

    :param filepath: path to a json file
    """
    try:
        with open(filepath) as file:
            return json.load(file)
    except json.decoder.JSONDecodeError:
        error = f"Could not read {filepath}."
        raise JSONFilepathError(error)
    except IOError:
        error = f"{filepath} does not appear to exist."
        raise JSONFilepathError(error)


class TweepyWrapper:
    """
    Homemade wrapper for Tweepy.
    """

    def __init__(self):
        # Get token
        credentials_filepath = PATH / "modules" / "twitter" / "credentials.json"
        try:
            self.token = open_json(filepath=credentials_filepath)
        except JSONFilepathError as error:
            raise TweepyWrapperError(error)

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

        logging.info(f"Connected to '{self.name}' @{self.screen_name}")

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

    def reply_to_status(self, medias: dict = [], msg: str = "", status_id: str = ""):
        """
        Reply to a tweet.

        :param medias: list of medias to post
        :param msg: text to post
        :param in_reply_to_status_id: tweet's id to reply to
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
            logging.info("Replied.")
            return

        # No medias
        if msg == "":
            status = "No face found. Can't mustachize :("

        self.api.update_status(
            status=status,
            in_reply_to_status_id=status_id,
            auto_populate_reply_metadata=True,
        )
        logging.info("Replied.")

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


class JSONFilepathError(Exception):
    pass


class TweepyWrapperError(Exception):
    pass
