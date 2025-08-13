import random
import asyncio

from telethon.sync import events, Button

from utils.cambd import get_definitions
from utils.helper import get_question
from utils.constants import NUMBER_EMOJI, UPSKILL_ENGLISH_PROMPT

from engine.vocab import Vocabulary
from engine.telegram import BotTelegram, CustomMarkdown


class Buttons:
    UPSKILL         = Button.inline("🚀 Upskill", "upskill_english")
    UPSKILL_SHUFFLE = Button.inline("🔀 Shuffle", "upskill_english")

    VOCAB         = Button.inline("🔠 Vocabulary", "shuffle")
    VOCAB_SHUFFLE = Button.inline("🔀 Shuffle", "shuffle")
    
    CLEAR   = Button.inline("🗑️ Clear", "clear")
    LOADING = Button.inline("⏳ Loading...", "")

    ANSWER_A = Button.inline("A", "answer_a")
    ANSWER_B = Button.inline("B", "answer_b")
    ANSWER_C = Button.inline("C", "answer_c")
    ANSWER_D = Button.inline("D", "answer_d")


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
        self.question = None
        self.list_vocabulary: list[Vocabulary] = self.get_list_vocabulary()

        self.register_commands()

    def get_list_vocabulary(self):
        vocab = Vocabulary()
        list_vocabulary = []
        list_message = self.tele_engine.client.get_messages(self.admin_id, limit=None)
        for message in list_message:
            text = message.text
            if text and "#" in text:
                vocab.init_from_markdown(text)
                list_vocabulary.append(vocab)
        return list_vocabulary

    def question_text(self, has_explain: bool = False):
        text = f"**{self.question['question']}**\n\n"
        text += f"A. {self.question['optionA']}\n"
        text += f"B. {self.question['optionB']}\n"
        text += f"C. {self.question['optionC']}\n"
        text += f"D. {self.question['optionD']}\n\n"
        if has_explain:
            text += f"**Explain:** {self.question['explain']}\n\n"
        return text

    def register_commands(self):
        bot = self.tele_engine.bot

        @bot.on(events.NewMessage(pattern="/start"))
        async def start_handler(event: events.CallbackQuery.Event):
            chat_id = event.chat_id
            random_vocabulary = random.choice(self.list_vocabulary)
            text = random_vocabulary.convert_to_markdown(with_hashtag=False, with_spoilers=True)
            buttons = [[Buttons.UPSKILL, Buttons.VOCAB_SHUFFLE, Buttons.CLEAR]]
            await bot.send_message(chat_id, text, parse_mode=CustomMarkdown(), buttons=buttons)
        
        @bot.on(events.CallbackQuery(pattern=Buttons.VOCAB_SHUFFLE.data))
        async def shuffle_handler(event: events.CallbackQuery.Event):
            chat_id = event.chat_id
            message = await event.get_message()
            mess_id = message.id
            await bot.delete_messages(chat_id, mess_id)
            await start_handler(event)

        @bot.on(events.CallbackQuery(pattern=Buttons.UPSKILL.data))
        async def upskill_english_handler(event: events.CallbackQuery.Event):
            chat_id = event.chat_id
            message = await event.get_message()
            mess_id = message.id

            text = message.text.replace(" ", " ​")
            buttons = message.buttons

            for index, row in enumerate(buttons):
                for index_button, button in enumerate(row):
                    if button.data in [Buttons.UPSKILL.data, Buttons.UPSKILL_SHUFFLE.data]:
                        buttons[index][index_button] = Buttons.LOADING
            
            await bot.edit_message(chat_id, mess_id, text, parse_mode=CustomMarkdown(), buttons=buttons)

            for _ in range(3):
                try:
                    self.question = get_question(UPSKILL_ENGLISH_PROMPT)
                    if self.question: break
                except Exception as e:
                    await bot.send_message(chat_id, f"Error: {e}")
                    return

            text = self.question_text()
            buttons = [
                [Buttons.ANSWER_A, Buttons.ANSWER_B],
                [Buttons.ANSWER_C, Buttons.ANSWER_D],
                [Buttons.VOCAB, Buttons.UPSKILL_SHUFFLE, Buttons.CLEAR],
            ]

            await bot.edit_message(chat_id, mess_id, text, parse_mode="Markdown", buttons=buttons)

        @bot.on(events.CallbackQuery(pattern=b"^answer_.+$"))
        async def answer_handler(event: events.CallbackQuery.Event):
            chat_id = event.chat_id
            message = await event.get_message()
            mess_id = message.id

            data = event.data.decode("utf-8")
            answer = data.split("_")[1]

            text = self.question_text(has_explain=True)
            buttons = [
                [
                    Button.inline(answer == "a" and (self.question["answer"] == "a" and "✅" or "❌") or "A", ""),
                    Button.inline(answer == "b" and (self.question["answer"] == "b" and "✅" or "❌") or "B", ""),
                ],
                [
                    Button.inline(answer == "c" and (self.question["answer"] == "c" and "✅" or "❌") or "C", ""),
                    Button.inline(answer == "d" and (self.question["answer"] == "d" and "✅" or "❌") or "D", ""),
                ],
                [Buttons.VOCAB, Buttons.UPSKILL_SHUFFLE, Buttons.CLEAR],
            ]

            await bot.edit_message(chat_id, mess_id, text, parse_mode="Markdown", buttons=buttons)

        @bot.on(events.NewMessage(pattern="/search"))
        async def search_handler(event: events.NewMessage.Event):
            chat_id = event.chat_id
            message: str = event.message.message
            word = message.replace("/search", "").strip().replace(" ", "-")

            try:
                definitions = get_definitions(word)
            except Exception as e:
                await bot.send_message(f"Error getting definitions: {e}", err)
                return

            self.last_search_definitions = definitions

            text = ""
            buttons = []
            for index in range(len(definitions)):
                definition = definitions[index]
                text += f"{NUMBER_EMOJI[index]} {definition.definition}\n"
                buttons.append(Button.inline(f"{NUMBER_EMOJI[index]} Add {index + 1}", f"add_{index + 1}"))
                if index >= 3: break
            
            await bot.send_message(chat_id, text, buttons=buttons)

        @bot.on(events.CallbackQuery(pattern=b"^add_\\d+$"))
        async def add_handler(event: events.CallbackQuery.Event):
            chat_id = event.chat_id
            message = await event.get_message()
            mess_id = message.id

            data  = event.data.decode("utf-8")
            index = int(data.split("_")[1])

            await bot.delete_messages(chat_id, mess_id)

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

        @bot.on(events.CallbackQuery(pattern=Buttons.CLEAR.data))
        async def upskill_english_handler(event: events.CallbackQuery.Event):
            list_id = []
            chat = await self.tele_engine.client.get_entity(event.chat_id)
            async for message in self.tele_engine.client.iter_messages(chat, limit= None):
                if message.text and "#" not in message.text:
                    list_id.append(message.id)
            await self.tele_engine.client.delete_messages(chat, message_ids=list_id)
            
    def run_until_disconnect(self):
        self.tele_engine.run_until_disconnect()
