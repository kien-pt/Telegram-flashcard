import random
import asyncio

from telethon.sync import events

from engine.vocab import Vocabulary
from engine.telegram import TelegramEngine

from utils.cambd import get_definitions
from utils.helper import *


class BotVocabulary:
    def __init__(
        self,
        bot_token: str,
        api_id: str,
        api_hash: str,
        admin_id: int,
        session_id: str = ""
    ):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

        self.tele_engine = TelegramEngine(bot_token, api_id, api_hash, session_id, self.loop)

        self.admin_id = admin_id
        self.latest_vocabulary: list[Vocabulary] = self.get_list_vocabulary()
        self.temporary_definitions: list[Vocabulary] = []

    def search_word(self, word):
        try:
            definitions = get_definitions(word)
        except Exception as e:
            err = f"Error getting definitions: {e}"
            self.tele_engine.send_message(self.admin_id, err)
            print(err)
            return
        
        self.definitions = definitions

        text = ""
        for index in range(len(definitions)):
            definition = definitions[index]
            text += f"/add_{index + 1}: {definition.definition}\n"

        self.tele_engine.send_message(self.admin_id, text)

    def add_word(self, index):
        if index < len(self.definitions):
            definition: Vocabulary = self.definitions[index]
            try:
                text = definition.convert_to_markdown()
                self.latest_vocabulary.append(definition)
                self.tele_engine.send_message(self.admin_id, text, "Markdown")
            except:
                self.tele_engine.send_message(self.admin_id, "Internal error, try /search again!")
                raise
        else:
            self.tele_engine.send_message(self.admin_id, "Index error!")

    def random_ask(self):
        text = ""

        len_random_vocabulary = min(4, len(self.latest_vocabulary))
        random_vocabulary = random.sample(self.latest_vocabulary, len_random_vocabulary)

        text += "\n".join(["/" + w.word.replace(" ", "_") for w in random_vocabulary])
        text += "\n----------------"
        text += "\n/shuffle"
        text += "\n/clear"

        self.tele_engine.send_message(self.admin_id, text)

    def get_list_vocabulary(self):
        list_vocabulary = []
        list_message = self.tele_engine.client.get_messages(self.admin_id, limit=None)
        for message in list_message:
            text = message.text
            if text and "#" in text:
                vocab = Vocabulary()
                vocab.init_from_markdown(text)
                list_vocabulary.append(vocab)
        return list_vocabulary

    async def async_run_events(self):
        await self.tele_engine.client.run_until_disconnected()

    def run_until_disconnected(self):
        @self.tele_engine.client.on(events.NewMessage(chats=self.admin_id, pattern="/ping"))
        async def pong_handler(event):
            message = event.message
            if message.text != "/ping": return
            self.tele_engine.send_message(self.admin_id, "pong")

        self.loop.run_until_complete(self.async_run_events())