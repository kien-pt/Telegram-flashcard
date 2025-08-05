import pandas as pd
import random
import asyncio

from telethon.sync import events, Button

from engine.vocab import Vocabulary
from engine.telegram import BotTelegram

from utils import cambd as UTILS_CAMBD
from utils.constants import NUMBER_EMOJI


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

        self.tele_engine = BotTelegram(bot_token, api_id, api_hash)
        self.last_search_definitions = None

        self.admin_id = admin_id
        self.list_vocabulary: list[Vocabulary] = self.get_list_vocabulary()

        self.register_commands()

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

    def random_a_vocabulary(self):
        len_random_vocabulary = min(4, len(self.list_vocabulary))
        random_vocabulary = random.sample(self.list_vocabulary, len_random_vocabulary)
        return random_vocabulary

    def get_bot_buttons(self):
        random_vocabulary = self.random_a_vocabulary()
        buttons = []
        for index in range(len(random_vocabulary)):
            word = random_vocabulary[index].word
            if index % 2 == 0: buttons.append([])
            buttons[-1].append(Button.inline(f"{NUMBER_EMOJI[index]} {word}", f"review_{word.replace(' ', '_')}"))
        buttons.append([Button.inline("🔀 Shuffle", "shuffle")])
        return buttons

    def register_commands(self):
        bot = self.tele_engine.bot

        @bot.on(events.NewMessage(pattern="/search"))
        async def search_handler(event: events.NewMessage.Event):
            chat_id = event.chat_id
            message: str = event.message.message
            word = message.replace("/search", "").strip().replace(" ", "-")

            try:
                definitions = UTILS_CAMBD.get_definitions(word)
            except Exception as e:
                err = f"Error getting definitions: {e}"
                await bot.send_message(chat_id, err)
                return

            self.last_search_definitions = definitions

            text = ""
            buttons = []
            for index in range(len(definitions)):
                definition = definitions[index]
                text += f"{NUMBER_EMOJI[index]} {definition.definition}\n"
                buttons.append(Button.inline(f"{NUMBER_EMOJI[index]}", f"add_{index + 1}"))
                if index >= 3: break
            
            await bot.send_message(chat_id, text, buttons=buttons)

        @bot.on(events.CallbackQuery(pattern=b"^add_\\d+$"))
        async def add_handler(event: events.CallbackQuery.Event):
            chat_id = event.chat_id
            data = event.data.decode("utf-8")
            index = int(data.split("_")[1])

            if index < len(self.last_search_definitions):
                definition: Vocabulary = self.last_search_definitions[index]
                try:
                    text = definition.convert_to_markdown()
                    self.list_vocabulary.append(definition)
                    await bot.send_message(chat_id, text, parse_mode="Markdown")
                except Exception as e:
                    await bot.send_message(chat_id, f"Internal error, try /search again!\nError: {e}")
            else:
                await bot.send_message(chat_id, "Index out of range, try /search again!")

        @bot.on(events.NewMessage(pattern="/shuffle"))
        async def shuffle_handler(event: events.NewMessage.Event):
            chat_id = event.chat_id
            buttons = self.get_bot_buttons()
            await bot.send_message(chat_id, "Choose a selection", parse_mode="Markdown", buttons=buttons)

        @bot.on(events.CallbackQuery(pattern=b"^review_.+$"))
        async def review_handler(event: events.CallbackQuery.Event):
            chat_id = event.chat_id
            message = await event.get_message()
            mess_id = message.id
            buttons = message.buttons

            data = event.data.decode("utf-8")
            word = data.split("_")[1]

            list_found = [w for w in self.list_vocabulary if w.word.replace(" ", "_") == word]
            if len(list_found) == 1:
                await bot.edit_message(chat_id, mess_id, list_found[0].convert_to_markdown(False), parse_mode="Markdown", buttons=buttons)

        @bot.on(events.CallbackQuery(pattern=b"^shuffle$"))
        async def shuffle_handler(event: events.CallbackQuery.Event):
            chat_id = event.chat_id
            message = await event.get_message()
            mess_id = message.id
            buttons = self.get_bot_buttons()
            await bot.edit_message(chat_id, mess_id, "Choose a selection", buttons=buttons)
            
    def run_until_disconnect(self):
        self.tele_engine.run_until_disconnect()
