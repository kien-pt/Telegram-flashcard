from time import sleep
from datetime import datetime

from utils.constants import TELEGRAM_BOT_TOKEN, TELETHON_API_HASH, TELETHON_API_ID

from core.BOT_VOCAB import BotVocabulary


if __name__ == "__main__":
    bot = BotVocabulary(
        bot_token=TELEGRAM_BOT_TOKEN,
        api_id=TELETHON_API_ID,
        api_hash=TELETHON_API_HASH,
        admin_id=-1002333467815
    )
    bot.run_until_disconnect()