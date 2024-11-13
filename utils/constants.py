import os

from dotenv import load_dotenv


HELLO_WORLD_TEXT =\
"""
 .---------------------------------.
| .-------------------------------. |
| |   _  ___          ___ _____   | |
| |  | |/ (_)___ _ _ | _ \_   _|  | |
| |  | ' <| / -_) ' \|  _/ | |    | |
| |  |_|\_\_\___|_||_|_|   |_|    | |
| |                   Bot 6868    | |
| '-------------------------------' |
 '---------------------------------'                                                        
"""

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELETHON_API_ID    = os.getenv("TELETHON_API_ID")
TELETHON_API_HASH  = os.getenv("TELETHON_API_HASH")