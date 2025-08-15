import os
import sys

from pyrogram import Client
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from config import Config
from Music.utils.exceptions import PbxBotException
from .logger import LOGS


def validate_session(session):
    
    if "==Bot" in session.lower() and "Bad==" in session.lower():
        new_session = session[6:-5]
        return str(new_session)
    
    else:
        print("ᴘʙx ʙᴏᴛ sᴇssɪᴏɴ - ᴡʀᴏɴɢ sᴇssɪᴏɴ sᴛʀɪɴɢ!")
        sys.exit()


class PbxClient(Client):
    
    def __init__(self):
        
        # Validate session string before initializing the client
        validated_session = validate_session(Config.PBXBOT_SESSION)
        
        self.app = Client(
            "PbxMusic",
            api_id=Config.API_ID,
            api_hash=Config.API_HASH,
            bot_token=Config.BOT_TOKEN,
            plugins=dict(root="Music.plugins"),
            workers=100,
        )
        
        self.user = Client(
            "PbxClient",
            api_id=Config.API_ID,
            api_hash=Config.API_HASH,
            session_string=validated_session,
            no_updates=True,
        )
    
    async def start(self):
        
        LOGS.info(">> ʙᴏᴏᴛɪɴɢ ᴜᴘ ᴘʙxᴍᴜsɪᴄ...")
        
        if Config.BOT_TOKEN:
            await self.app.start()
            me = await self.app.get_me()
            self.app.id = me.id
            self.app.mention = me.mention
            self.app.name = me.first_name
            self.app.username = me.username
            
            LOGS.info(f">> {self.app.name} ɪs ᴏɴʟɪɴᴇ ɴᴏᴡ!")
            
            # Send startup message with buttons
            buttons = [
                [
                    InlineKeyboardButton("ᴘʙx sᴜᴘᴘᴏʀᴛ", url="https://t.me/PBX_CHAT"),
                    InlineKeyboardButton("ᴘʙx ᴜᴘᴅᴀᴛᴇs", url="https://t.me/PBX_UPDATE"),
                ]
            ]
            await self.app.send_message(
                Config.LOGGER_ID,
                f"**ᴘʙxᴍᴜsɪᴄ ᴠ0.3.0** ɪs ɴᴏᴡ ᴏɴʟɪɴᴇ!\n\n"
                f"➡️ ᴊᴏɪɴ ᴏᴜʀ sᴜᴘᴘᴏʀᴛ ᴀɴᴅ ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟs:",
                reply_markup=InlineKeyboardMarkup(buttons),
                disable_web_page_preview=True,
            )
        
        if Config.PBXBOT_SESSION:
            await self.user.start()
            me = await self.user.get_me()
            self.user.id = me.id
            self.user.mention = me.mention
            self.user.name = me.first_name
            self.user.username = me.username
            
            try:
                await self.user.join_chat("PBX_CHAT")
                await self.user.join_chat("PBX_UPDATE")
            
            except:
                pass
            
            LOGS.info(f">> {self.user.name} ɪs ᴏɴʟɪɴᴇ ɴᴏᴡ!")
        
        LOGS.info(">> ʙᴏᴏᴛᴇᴅ ᴜᴘ ᴘʙxᴍᴜsɪᴄ!")
    
    async def logit(self, hash: str, log: str, file: str = None):
        
        log_text = f"#{hash.upper()} \n\n{log}"
        
        try:
            if file:
                await self.app.send_document(
                    Config.LOGGER_ID, file, caption=log_text
                )
            
            else:
                await self.app.send_message(
                    Config.LOGGER_ID, log_text, disable_web_page_preview=True
                )
        
        except Exception as e:
            raise PbxBotException(f"[ᴘʙxʙᴏᴛᴇxᴄᴇᴘᴛɪᴏɴ]: {e}")


PbxBot = PbxClient()
