import asyncio

from telethon import TelegramClient, events

class BotTelegram:
    def __init__(self, bot_token: str, api_id: str, api_hash: str, session_id: str = ""):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        
        self.bot = TelegramClient("bot_vocabulary" + session_id, api_id, api_hash).start(bot_token=bot_token)
        self.client = TelegramClient("client_vocabulary" + session_id, api_id, api_hash).start()

        self._register_default_commands()

    def _register_default_commands(self):
        @self.bot.on(events.NewMessage(pattern="/start"))
        async def start_handler(event: events.NewMessage.Event):
            await self.bot.send_message(event.chat_id, "Hello, world!")
       
    def run_until_disconnect(self):
        async def async_run_events():
            await self.bot.run_until_disconnected()
        self.loop.run_until_complete(async_run_events())