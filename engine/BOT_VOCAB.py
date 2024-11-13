import random
import asyncio

from telethon.sync import events
from engine.telegram import TelegramEngine

from utils.cambd import get_definitions
from utils.helper import *


class BotVocabulary:
    def __init__(self, bot_token, api_id, api_hash, admin_id, session_id=""):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

        self.admin_id = admin_id
        self.tele_engine = TelegramEngine(bot_token, api_id, api_hash, session_id, self.loop)
        self.definitions = []

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
            text += f"/add_{index + 1}: {definition['definition']}\n"

        self.tele_engine.send_message(self.admin_id, text)

    def add_word(self, index):
        if index < len(self.definitions):
            definition = self.definitions[index]
            try:
                text = get_message_md(
                    word=definition["word"],
                    ipa=definition["ipa"] or "",
                    definition=definition["definition"],
                    example="\n".join(definition["examples"])
                )
                self.tele_engine.send_message(self.admin_id, text, "Markdown")
            except:
                self.tele_engine.send_message(self.admin_id, "Internal error, try /search again!")

    def random_ask(self, list_vocabulary):
        random_vocabulary = random.sample(list_vocabulary, 4)
        text = ""
        for word in random_vocabulary:
            text += "/" + word + "\n"
        text += "----------------\n"
        text += "/shuffle\n"
        text += "/clear\n"
        self.tele_engine.send_message(self.admin_id, text)

    async def get_list_vocabulary(self):
        list_vocabulary = []
        chat = await self.tele_engine.client.get_entity(self.admin_id)
        async for message in self.tele_engine.client.iter_messages(chat, limit= None):
            text = message.text
            if text and "#" in text:
                obj = convert_message_to_dict(text)
                list_vocabulary.append(obj["word"])
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