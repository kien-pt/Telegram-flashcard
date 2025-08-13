import asyncio

from telethon import TelegramClient, events, types
from telethon.extensions import markdown

class CustomMarkdown:
    @staticmethod
    def parse(text):
        text, entities = markdown.parse(text)
        for i, e in enumerate(entities):
            if isinstance(e, types.MessageEntityTextUrl):
                if e.url == 'spoiler':
                    entities[i] = types.MessageEntitySpoiler(e.offset, e.length)
                elif e.url.startswith('emoji/'):
                    entities[i] = types.MessageEntityCustomEmoji(e.offset, e.length, int(e.url.split('/')[1]))
        return text, entities

    @staticmethod
    def unparse(text, entities):
        for i, e in enumerate(entities or []):
            if isinstance(e, types.MessageEntityCustomEmoji):
                entities[i] = types.MessageEntityTextUrl(e.offset, e.length, f'emoji/{e.document_id}')
            if isinstance(e, types.MessageEntitySpoiler):
                entities[i] = types.MessageEntityTextUrl(e.offset, e.length, 'spoiler')
        return markdown.unparse(text, entities)


class BotTelegram:
    def __init__(self, bot_token: str, api_id: str, api_hash: str, session_id: str = ""):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        
        self.bot = TelegramClient("bot_vocabulary" + session_id, api_id, api_hash).start(bot_token=bot_token)
        self.client = TelegramClient("client_vocabulary" + session_id, api_id, api_hash).start()
        
    def run_until_disconnect(self):
        async def async_run_events():
            await self.bot.run_until_disconnected()
        self.loop.run_until_complete(async_run_events())