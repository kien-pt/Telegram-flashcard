import os
import sys
import requests

from telethon.sync import TelegramClient

BOT_URL = "https://api.telegram.org/bot"
session = "hustle_session"

class TelegramEngine:
    def __init__(self, bot_token, api_id, api_hash, session_id="", loop=None):
        self.bot_token = bot_token
        self.client = TelegramClient(f"{session}_{session_id}", api_id, api_hash, loop=loop)
        self.client.start()
        self.auth_id = self.client.get_me().id

    def get_dialogs(self):
        """
        Trả về danh sách chat
        """
        async def _get_dialogs():
            dialogs = await self.client.get_dialogs()
            return dialogs
        with self.client:
            return self.client.loop.run_until_complete(_get_dialogs())
        
    def get_messages(self, chat_id, limit=None):
        """
        Trả về danh sách messages của chat
        """
        async def _get_messages():
            list_message = []
            chat = await self.client.get_entity(chat_id)
            async for message in self.client.iter_messages(chat, limit):
                list_message.append(message)
            return list_message
        with self.client:
            return self.client.loop.run_until_complete(_get_messages())
        
    def send_message(self, chat_id, text, parse_mode=None):
        """
        Gửi message
        """
        return requests.post(
            url=f"{BOT_URL}{self.bot_token}/sendMessage",
            data={
                "chat_id": chat_id,
                "text": text,
                "parse_mode": parse_mode,
            }
        )
    
    def forward_message(self, chat_id, message):
        async def _forward_message():
            await self.client.send_message(chat_id, message)
        with self.client:
            return self.client.loop.run_until_complete(_forward_message())
        
    def edit_message(self, chat_id, message_id, text):
        """
        Edit message
        """
        url = f"{BOT_URL}{self.bot_token}/editMessageText"
        return requests.post(url, data={
            "text": text,
            "chat_id": chat_id,
            "message_id": message_id,
        })
        
    def delete_messages(self, chat_id, list_ids):
        async def _delete_messages(list_ids):
            chat = await self.client.get_entity(chat_id)
            await self.client.delete_messages(chat, message_ids=list_ids)
        with self.client:
            return self.client.loop.run_until_complete(_delete_messages(list_ids))
