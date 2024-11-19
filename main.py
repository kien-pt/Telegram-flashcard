import os
import threading

from time import sleep
from datetime import datetime

from utils.constants import TELEGRAM_BOT_TOKEN, TELETHON_API_HASH, TELETHON_API_ID
from engine.BOT_VOCAB import BotVocabulary, events


BOT_VOCAB = BotVocabulary(
    bot_token=TELEGRAM_BOT_TOKEN,
    api_id=TELETHON_API_ID,
    api_hash=TELETHON_API_HASH,
    admin_id=-4275314255,
    session_id="vocab",
)


@BOT_VOCAB.tele_engine.client.on(events.NewMessage(chats=BOT_VOCAB.admin_id, pattern="/shuffle", from_users=BOT_VOCAB.tele_engine.auth_id))
async def shuffle_handler(event):
    BOT_VOCAB.random_ask()


@BOT_VOCAB.tele_engine.client.on(events.NewMessage(chats=BOT_VOCAB.admin_id, pattern="/search", from_users=BOT_VOCAB.tele_engine.auth_id))
async def search_handler(event):
    message = event.message.message
    word = message.replace("/search", "").strip().replace(" ", "-")
    BOT_VOCAB.search_word(word)


@BOT_VOCAB.tele_engine.client.on(events.NewMessage(chats=BOT_VOCAB.admin_id, pattern="/add_", from_users=BOT_VOCAB.tele_engine.auth_id))
async def add_handler(event):
    message = event.message.message
    index_str = message.replace("/add_", "")
    try:
        index = int(index_str) - 1
    except:
        BOT_VOCAB.tele_engine.send_message(
            BOT_VOCAB.admin_id,
            "Internal error, try /add again!"
        )
        return
    BOT_VOCAB.add_word(index)


@BOT_VOCAB.tele_engine.client.on(events.NewMessage(chats=BOT_VOCAB.admin_id, pattern="/clear", from_users=BOT_VOCAB.tele_engine.auth_id))
async def clear_handler(event):
    list_id = []
    chat = await BOT_VOCAB.tele_engine.client.get_entity(event.message.chat_id)
    async for message in BOT_VOCAB.tele_engine.client.iter_messages(chat, limit= None):
        if message.text and "#" not in message.text:
            list_id.append(message.id)
    await BOT_VOCAB.tele_engine.client.delete_messages(chat, message_ids=list_id)


@BOT_VOCAB.tele_engine.client.on(events.NewMessage(chats=BOT_VOCAB.admin_id, pattern="/", from_users=1283551985))
async def search_v2_handler(event):
    message = event.message
    text = message.text.strip("/")

    list_found = [w for w in BOT_VOCAB.latest_vocabulary if w.word.replace(" ", "_") == text]
    if len(list_found) == 1:
        word = list_found[0]
        BOT_VOCAB.tele_engine.send_message(BOT_VOCAB.admin_id, word.convert_to_markdown(False), "Markdown")


if __name__ != '__main__': os._exit(0)


t1 = threading.Thread(target=BOT_VOCAB.run_until_disconnected)
t1.start()


try:
    while True:
        now = datetime.now().time()

        morning_start = now.replace(hour=9, minute=0, second=0, microsecond=0)
        morning_end = now.replace(hour=12, minute=0, second=0, microsecond=0)
        afternoon_start = now.replace(hour=14, minute=0, second=0, microsecond=0)
        afternoon_end = now.replace(hour=18, minute=0, second=0, microsecond=0)

        # Only send messages in working hours
        is_working_hour = morning_start <= now <= morning_end or afternoon_start <= now <= afternoon_end
        if is_working_hour: BOT_VOCAB.random_ask()

        sleep(20 * 60)
except KeyboardInterrupt:
    print("Stopped the bot!")
except Exception as e:
    raise
    print(e)
finally:
    while t1.is_alive():
        if t1.is_alive(): t1.join(0.1)
        os._exit(0)