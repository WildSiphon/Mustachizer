import random
import json


class SentenceProvider:
    """Provide sentences for responses."""

    PATH = "./modules/mustache/sentences.json"

    def __init__(self):
        with open(self.PATH, "r") as sentence_file:
            self.__sentences = json.load(sentence_file)["sentences"]

    def provide(self):
        """Provide a random sentence.

        :return: A random sentence
        :rtype: str
        """
        return random.choice(self.__sentences)
