import random
import asyncio

from telethon.sync import events, Button

from utils.cambd import get_definitions
from utils.helper import get_question
from utils.constants import NUMBER_EMOJI, UPSKILL_ENGLISH_PROMPT

from engine.vocab import Vocabulary
from engine.telegram import BotTelegram, CustomMarkdown


class Buttons:
    UPSKILL_DATA = b"upskill_english"
    SHUFFLE_DATA = b"shuffle"
    CLEAR_DATA = b"clear"
    ANSWER_A_DATA = b"answer_a"
    ANSWER_B_DATA = b"answer_b"
    ANSWER_C_DATA = b"answer_c"
    ANSWER_D_DATA = b"answer_d"

    UPSKILL         = Button.inline("🚀 Upskill", UPSKILL_DATA)
    UPSKILL_SHUFFLE = Button.inline("🔀 Shuffle", UPSKILL_DATA)

    VOCAB         = Button.inline("🔠 Vocabulary", SHUFFLE_DATA)
    VOCAB_SHUFFLE = Button.inline("🔀 Shuffle", SHUFFLE_DATA)
    
    CLEAR   = Button.inline("🗑️ Clear", CLEAR_DATA)
    LOADING = Button.inline("⏳ Loading...", b"loading")

    ANSWER_A = Button.inline("A", ANSWER_A_DATA)
    ANSWER_B = Button.inline("B", ANSWER_B_DATA)
    ANSWER_C = Button.inline("C", ANSWER_C_DATA)
    ANSWER_D = Button.inline("D", ANSWER_D_DATA)

    NOTE_IELTS_DATA = b"show_note_ielts"
    NOTE_SD_DATA = b"show_note_sd"
    NOTE_IELTS = Button.inline("📝 Ghi chú IELTS", NOTE_IELTS_DATA)
    NOTE_SD    = Button.inline("💻 Ghi chú System Design", NOTE_SD_DATA)


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
        self.last_search_definitions_by_chat: dict[int, list[Vocabulary]] = {}

        self.admin_id = admin_id
        self.questions_by_chat: dict[int, dict] = {}
        
        self.list_vocabulary: list[Vocabulary] = []
        self.list_notes_ielts: list[str] = []
        self.list_notes_system_design: list[str] = []
        self.load_data()

        self.register_commands()

    def load_data(self):
        list_message = self.tele_engine.client.get_messages(self.admin_id, limit=None)
        for message in list_message:
            text = message.text
            if not text:
                continue

            if "#note_ielts" in text:
                self.list_notes_ielts.append(text)
            elif "#note_system_design" in text or "#note_sd" in text:
                self.list_notes_system_design.append(text)
            elif "#" in text:
                vocab = Vocabulary()
                try:
                    if vocab.init_from_markdown(text):
                        self.list_vocabulary.append(vocab)
                    else:
                        print(f"Skipping invalid vocabulary message {message.id}")
                except Exception as e:
                    print(f"Skipping vocabulary message {message.id}: {e}")

    def question_text(self, question: dict, has_explain: bool = False):
        text = f"**{question['question']}**\n\n"
        text += f"A. {question['optionA']}\n"
        text += f"B. {question['optionB']}\n"
        text += f"C. {question['optionC']}\n"
        text += f"D. {question['optionD']}\n\n"
        if has_explain:
            text += f"**Explain:** {question['explain']}\n\n"
        return text

    def register_commands(self):
        bot = self.tele_engine.bot

        async def answer_callback(event: events.CallbackQuery.Event, text: str | None = None):
            try:
                await event.answer(text or "")
            except Exception:
                pass

        @bot.on(events.NewMessage(pattern="/start", chats=self.admin_id))
        async def start_handler(event: events.CallbackQuery.Event):
            chat_id = event.chat_id
            if not self.list_vocabulary:
                await bot.send_message(chat_id, "Chưa có từ vựng nào trong kho admin để hiển thị.")
                return
            random_vocabulary = random.choice(self.list_vocabulary)
            text = random_vocabulary.convert_to_markdown(with_hashtag=False, with_spoilers=True)
            buttons = [
                [Buttons.UPSKILL, Buttons.VOCAB_SHUFFLE, Buttons.CLEAR],
                [Buttons.NOTE_IELTS, Buttons.NOTE_SD]
            ]
            await bot.send_message(chat_id, text, parse_mode=CustomMarkdown(), buttons=buttons)

        @bot.on(events.NewMessage(pattern="/help", chats=self.admin_id))
        async def help_handler(event: events.NewMessage.Event):
            chat_id = event.chat_id
            help_text = (
                "**📚 Bot Flashcard & Ghi chú - Hướng dẫn sử dụng:**\n\n"
                "🔹 `/start` - Hiển thị menu học tập (Trắc nghiệm, Từ vựng, Ghi chú IELTS & System Design)\n"
                "🔹 `/search <từ khóa>` - Tra cứu nghĩa trên Cambridge Dictionary (VD: `/search vocabulary`). Có thể lưu thêm vào kho từ vựng trực tiếp tại đây!\n"
                "🔹 `/add_note_ielts` - Thêm ghi chú chủ đề IELTS mới\n"
                "🔹 `/add_note_system_design` hoặc `/add_note_sd` - Thêm ghi chú chủ đề System Design mới\n"
                "🔹 `/help` - Xem tin nhắn hướng dẫn sử dụng chi tiết này\n\n"
                "💡 **Cách thêm ghi chú mẫu:**\n"
                "Gửi tin nhắn theo cú pháp:\n"
                "/add_note_ielts\n"
                "```\n"
                "\"\"\"\n"
                "Đây là một ví dụ\n"
                "\"\"\"\n"
                "```\n\n"
                "💡 **Ghi chú:** Bạn chỉ cần nhấn trực tiếp các nút bấm giao diện để đổi từ vựng hoặc đổi ghi chú ngẫu nhiên cực nhanh nhé!"
            )
            await bot.send_message(chat_id, help_text, parse_mode="Markdown")
        
        @bot.on(events.CallbackQuery(pattern=b"^shuffle$", chats=self.admin_id))
        async def shuffle_handler(event: events.CallbackQuery.Event):
            chat_id = event.chat_id
            await answer_callback(event)
            try:
                message = await event.get_message()
                mess_id = message.id
                await bot.delete_messages(chat_id, mess_id)
                await start_handler(event)
            except Exception as e:
                await bot.send_message(chat_id, f"Không thể đổi flashcard: {e}")

        @bot.on(events.CallbackQuery(pattern=b"^upskill_english$", chats=self.admin_id))
        async def upskill_english_handler(event: events.CallbackQuery.Event):
            chat_id = event.chat_id
            await answer_callback(event, "Đang tạo câu hỏi...")
            try:
                message = await event.get_message()
                mess_id = message.id

                text = message.text.replace(" ", " ​")
                current_buttons = message.buttons or []
                loading_buttons = []
                for row in current_buttons:
                    loading_row = []
                    for button in row:
                        if getattr(button, "data", None) in [Buttons.UPSKILL.data, Buttons.UPSKILL_SHUFFLE.data]:
                            loading_row.append(Buttons.LOADING)
                        else:
                            loading_row.append(button)
                    loading_buttons.append(loading_row)
                
                await bot.edit_message(chat_id, mess_id, text, parse_mode=CustomMarkdown(), buttons=loading_buttons)

                question = None
                for _ in range(3):
                    question = get_question(UPSKILL_ENGLISH_PROMPT)
                    if question:
                        break

                if not question:
                    await bot.send_message(chat_id, "Không tạo được câu hỏi mới, bạn bấm lại giúp mình nhé.")
                    return

                self.questions_by_chat[chat_id] = question

                text = self.question_text(question)
                buttons = [
                    [Buttons.ANSWER_A, Buttons.ANSWER_B],
                    [Buttons.ANSWER_C, Buttons.ANSWER_D],
                    [Buttons.VOCAB, Buttons.UPSKILL_SHUFFLE, Buttons.CLEAR],
                ]

                await bot.edit_message(chat_id, mess_id, text, parse_mode="Markdown", buttons=buttons)
            except Exception as e:
                await bot.send_message(chat_id, f"Lỗi khi xử lý nút Upskill: {e}")

        @bot.on(events.CallbackQuery(pattern=b"^answer_.+$", chats=self.admin_id))
        async def answer_handler(event: events.CallbackQuery.Event):
            chat_id = event.chat_id
            await answer_callback(event)
            try:
                question = self.questions_by_chat.get(chat_id)
                if not question:
                    await bot.send_message(chat_id, "Câu hỏi đã hết phiên. Bạn bấm `🚀 Upskill` để tạo câu mới nhé.", parse_mode="Markdown")
                    return

                message = await event.get_message()
                mess_id = message.id

                data = event.data.decode("utf-8")
                answer = data.split("_")[1]

                text = self.question_text(question, has_explain=True)
                buttons = [
                    [
                        Button.inline(answer == "a" and (question["answer"] == "a" and "✅" or "❌") or "A", b"answered"),
                        Button.inline(answer == "b" and (question["answer"] == "b" and "✅" or "❌") or "B", b"answered"),
                    ],
                    [
                        Button.inline(answer == "c" and (question["answer"] == "c" and "✅" or "❌") or "C", b"answered"),
                        Button.inline(answer == "b" and (question["answer"] == "d" and "✅" or "❌") or "D", b"answered"),
                    ],
                    [Buttons.VOCAB, Buttons.UPSKILL_SHUFFLE, Buttons.CLEAR],
                ]

                await bot.edit_message(chat_id, mess_id, text, parse_mode="Markdown", buttons=buttons)
            except Exception as e:
                await bot.send_message(chat_id, f"Lỗi khi chấm đáp án: {e}")

        @bot.on(events.NewMessage(pattern="/search", chats=self.admin_id))
        async def search_handler(event: events.NewMessage.Event):
            chat_id = event.chat_id

            message: str = event.message.message
            word = message.replace("/search", "").strip().replace(" ", "-")
            if not word:
                await bot.send_message(chat_id, "Cú pháp đúng: `/search <word>`", parse_mode="Markdown")
                return

            try:
                definitions = get_definitions(word)
            except Exception as e:
                await bot.send_message(chat_id, f"Error getting definitions: {e}")
                return

            self.last_search_definitions_by_chat[chat_id] = definitions
            if not definitions:
                await bot.send_message(
                    chat_id,
                    f"Không tìm thấy định nghĩa nào cho `{word}` trên Cambridge.",
                    parse_mode="Markdown",
                )
                return

            text = ""
            buttons = []
            for index in range(len(definitions)):
                definition = definitions[index]
                text += f"{NUMBER_EMOJI[index]} {definition.definition}\n"
                buttons.append(Button.inline(f"{NUMBER_EMOJI[index]} Add {index + 1}", f"add_{index + 1}"))
                if index >= 3: break
            
            await bot.send_message(chat_id, text, buttons=buttons)

        @bot.on(events.CallbackQuery(pattern=b"^add_\\d+$", chats=self.admin_id))
        async def add_handler(event: events.CallbackQuery.Event):
            chat_id = event.chat_id
            await answer_callback(event)
            try:
                message = await event.get_message()
                mess_id = message.id

                data  = event.data.decode("utf-8")
                index = int(data.split("_")[1]) - 1

                await bot.delete_messages(chat_id, mess_id)

                definitions = self.last_search_definitions_by_chat.get(chat_id, [])
                if 0 <= index < len(definitions):
                    definition: Vocabulary = definitions[index]
                    text = definition.convert_to_markdown()
                    self.list_vocabulary.append(definition)
                    await bot.send_message(chat_id, text, parse_mode="Markdown")
                else:
                    await bot.send_message(chat_id, "Không tìm thấy kết quả đã chọn, bạn hãy `/search` lại nhé.", parse_mode="Markdown")
            except Exception as e:
                await bot.send_message(chat_id, f"Lỗi khi thêm từ vựng: {e}")

        @bot.on(events.CallbackQuery(pattern=b"^clear$", chats=self.admin_id))
        async def clear_handler(event: events.CallbackQuery.Event):
            await answer_callback(event, "Đang dọn chat...")
            try:
                list_id = []
                chat = await self.tele_engine.client.get_entity(event.chat_id)
                async for message in self.tele_engine.client.iter_messages(chat, limit=None):
                    if message.text and "#" not in message.text:
                        list_id.append(message.id)
                if list_id:
                    await self.tele_engine.client.delete_messages(chat, message_ids=list_id)
            except Exception as e:
                await bot.send_message(event.chat_id, f"Lỗi khi clear chat: {e}")

        # Commands for adding IELTS & System Design notes
        @bot.on(events.NewMessage(chats=self.admin_id))
        async def add_note_handler(event: events.NewMessage.Event):
            text = event.message.message
            if not text:
                return

            is_ielts = text.startswith("/add_note_ielts")
            is_sd = text.startswith("/add_note_system_design") or text.startswith("/add_note_sd")

            if not (is_ielts or is_sd):
                return

            import re
            match = re.search(r'"""([\s\S]*?)"""', text)
            if not match:
                await event.reply('Vui lòng nhập nội dung ghi chú trong cặp dấu """!')
                return

            content = match.group(1).strip()
            hashtag = "#note_ielts" if is_ielts else "#note_system_design"
            message_to_send = f"{content}\n\n{hashtag}"

            # Post the note back to the chat
            await bot.send_message(event.chat_id, message_to_send)

            # Store in local memory list
            if is_ielts:
                self.list_notes_ielts.append(message_to_send)
            else:
                self.list_notes_system_design.append(message_to_send)

            # Delete the user's original command message
            try:
                chat = await self.tele_engine.client.get_entity(event.chat_id)
                async for msg in self.tele_engine.client.iter_messages(chat, limit=20):
                    if msg.text == text:
                        await self.tele_engine.client.delete_messages(chat, message_ids=[msg.id])
                        break
            except Exception as e:
                print(f"Cảnh báo: Không thể xóa tin nhắn command: {e}")

        # Callbacks for displaying IELTS & System Design notes
        @bot.on(events.CallbackQuery(pattern=b"^show_note_ielts$", chats=self.admin_id))
        async def show_note_ielts_handler(event: events.CallbackQuery.Event):
            await answer_callback(event)
            try:
                chat_id = event.chat_id
                message = await event.get_message()
                mess_id = message.id

                await bot.delete_messages(chat_id, mess_id)

                if not self.list_notes_ielts:
                    text = "Hiện tại chưa có ghi chú IELTS nào. Hãy thêm bằng lệnh `/add_note_ielts`!"
                else:
                    text = random.choice(self.list_notes_ielts)
                    text = text.replace("#note_ielts", "").strip()

                buttons = [
                    [Buttons.UPSKILL, Buttons.VOCAB_SHUFFLE, Buttons.CLEAR],
                    [Buttons.NOTE_IELTS, Buttons.NOTE_SD]
                ]
                await bot.send_message(chat_id, text, parse_mode=CustomMarkdown(), buttons=buttons)
            except Exception as e:
                await bot.send_message(event.chat_id, f"Lỗi: {e}")

        @bot.on(events.CallbackQuery(pattern=b"^show_note_sd$", chats=self.admin_id))
        async def show_note_sd_handler(event: events.CallbackQuery.Event):
            await answer_callback(event)
            try:
                chat_id = event.chat_id
                message = await event.get_message()
                mess_id = message.id

                await bot.delete_messages(chat_id, mess_id)

                if not self.list_notes_system_design:
                    text = "Hiện tại chưa có ghi chú System Design nào. Hãy thêm bằng lệnh `/add_note_system_design` hoặc `/add_note_sd`!"
                else:
                    text = random.choice(self.list_notes_system_design)
                    text = text.replace("#note_system_design", "").replace("#note_sd", "").strip()

                buttons = [
                    [Buttons.UPSKILL, Buttons.VOCAB_SHUFFLE, Buttons.CLEAR],
                    [Buttons.NOTE_IELTS, Buttons.NOTE_SD]
                ]
                await bot.send_message(chat_id, text, parse_mode=CustomMarkdown(), buttons=buttons)
            except Exception as e:
                await bot.send_message(event.chat_id, f"Lỗi: {e}")
            
    def run_until_disconnect(self):
        from telethon import functions, types
        async def setup_commands():
            try:
                # Ghi đè UI gợi ý dấu / (Set /help và /start cho riêng Group Admin_ID)
                entity = await self.tele_engine.bot.get_input_entity(self.admin_id)
                await self.tele_engine.bot(functions.bots.SetBotCommandsRequest(
                    scope=types.BotCommandScopePeer(peer=entity),
                    lang_code='',
                    commands=[
                        types.BotCommand(command='start', description='Hiển thị menu chính'),
                        types.BotCommand(command='help', description='Mở file Hướng dẫn')
                    ]
                ))
                # Set các lệnh mặc định cho mọi nơi khác ẩn hết
                await self.tele_engine.bot(functions.bots.SetBotCommandsRequest(
                    scope=types.BotCommandScopeDefault(),
                    lang_code='',
                    commands=[]
                ))
                print("Đã nạp thành công Popup Menu cho dấu / !")
            except Exception as e:
                print("Cảnh báo khi cài Popup Menu:", e)

        self.tele_engine.run_until_disconnect(startup_hook=setup_commands)
