from core.BOT_VOCAB import BotVocabulary
from utils.constants import (
    TELEGRAM_BOT_TOKEN, TELETHON_API_HASH, TELETHON_API_ID, TELEGRAM_ADMIN_ID
)


if __name__ == "__main__":
    bot = BotVocabulary(
        api_id=TELETHON_API_ID,
        api_hash=TELETHON_API_HASH,
        admin_id=TELEGRAM_ADMIN_ID,
        bot_token=TELEGRAM_BOT_TOKEN,
    )
    bot.run_until_disconnect()