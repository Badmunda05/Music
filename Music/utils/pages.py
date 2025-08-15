from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InputMediaPhoto, Message

from config import Config
from Music.core.clients import PbxBot
from Music.core.database import db
from Music.helpers.buttons import Buttons
from Music.helpers.formatters import formatter


class Pages:
    
    def __init__(self):
        pass
    
    async def song_page(self, message: Message, rand_key: str, key: int):
        
        m = message.message if isinstance(message, CallbackQuery) else message
        
        if Config.SONG_CACHE[rand_key]:
            all_tracks = Config.SONG_CACHE[rand_key]
            btns = Buttons.song_markup(rand_key, all_tracks[key]["link"], key)
            cap = f"__({key+1}/{len(all_tracks)})__ **sᴏɴɢ ᴅᴏᴡɴʟᴏᴀᴅᴇʀ:**\n\n"
            cap += f"**• ᴛɪᴛʟᴇ:** `{all_tracks[key]['title']}`\n\n"
            cap += f"🎶 {PbxBot.app.mention}"
            
            await m.edit_media(
                InputMediaPhoto(
                    all_tracks[key]["thumbnail"],
                    caption=cap,
                ),
                reply_markup=InlineKeyboardMarkup(btns),
            )
        
        else:
            await m.delete()
            return await m.reply_text("ǫᴜᴇʀʏ ᴛɪᴍᴇᴅ ᴏᴜᴛ! ᴘʟᴇᴀsᴇ sᴛᴀʀᴛ ᴛʜᴇ ᴇɴᴛɪʀᴇ ᴘʀᴏᴄᴇss ᴀɢᴀɪɴ.")
    
    async def activevc_page(
        self,
        message: Message or CallbackQuery,
        collection: list,
        page: int = 0,
        index: int = 0,
        edit: bool = False,
    ):
        
        m = message.message if isinstance(message, CallbackQuery) else message
        
        if not collection:
            text = "**ɴᴏ ᴀᴄᴛɪᴠᴇ ᴠᴏɪᴄᴇ ᴄʜᴀᴛs ꜰᴏᴜɴᴅ!**"
            if edit:
                return await m.edit_text(text)
            return await m.reply_text(text)
        
        grouped, total = formatter.group_the_list(collection, 5)
        text = f"__({page+1}/{len(grouped)})__ **{PbxBot.app.mention} ᴀᴄᴛɪᴠᴇ ᴠᴏɪᴄᴇ ᴄʜᴀᴛs:** __{total} ᴄʜᴀᴛs__\n\n"
        btns = Buttons.active_vc_markup(len(grouped), page)
        
        try:
            for active in grouped[int(page)]:
                index += 1
                text += f"**{'0' if index < 10 else ''}{index}:** {active['title']} [`{active['chat_id']}`]\n"
                text += f"    **ʟɪsᴛᴇɴᴇʀs:** __{active['participants']}__\n"
                text += f"    **ᴘʟᴀʏɪɴɢ:** __{active['playing']}__\n"
                text += f"    **ᴠᴄ ᴛʏᴘᴇ:** __{active['vc_type']}__\n"
                text += f"    **sɪɴᴄᴇ:** __{active['active_since']}__\n\n"
        
        except IndexError:
            page = 0
            for active in grouped[int(page)]:
                index += 1
                text += f"**{'0' if index < 10 else ''}{index}:** {active['title']} [`{active['chat_id']}`]\n"
                text += f"    **ʟɪsᴛᴇɴᴇʀs:** __{active['participants']}__\n"
                text += f"    **ᴘʟᴀʏɪɴɢ:** __{active['playing']}__\n"
                text += f"    **ᴠᴄ ᴛʏᴘᴇ:** __{active['vc_type']}__\n"
                text += f"    **sɪɴᴄᴇ:** __{active['active_since']}__\n\n"
        
        if edit:
            await m.edit_text(text, reply_markup=InlineKeyboardMarkup(btns))
        
        else:
            await m.reply_text(text, reply_markup=InlineKeyboardMarkup(btns))
    
    async def authusers_page(
        self,
        message: Message or CallbackQuery,
        rand_key: str,
        page: int = 0,
        index: int = 0,
        edit: bool = False,
    ):
        
        m = message.message if isinstance(message, CallbackQuery) else message
        collection = Config.CACHE[rand_key]
        
        if not collection:
            text = "**ɴᴏ ᴀᴜᴛʜᴏʀɪᴢᴇᴅ ᴜsᴇʀs ꜰᴏᴜɴᴅ!**"
            if edit:
                return await m.edit_text(text)
            return await m.reply_text(text)
        
        grouped, total = formatter.group_the_list(collection, 6)
        chat = message.chat.title or "ᴜɴᴋɴᴏᴡɴ ᴄʜᴀᴛ"
        text = f"__({page+1}/{len(grouped)})__ **ᴀᴜᴛʜᴏʀɪᴢᴇᴅ ᴜsᴇʀs ɪɴ {chat}:**\n    >> __{total} ᴜsᴇʀs__\n\n"
        btns = Buttons.authusers_markup(len(grouped), page, rand_key)
        
        try:
            for auth in grouped[int(page)]:
                index += 1
                text += f"**{'0' if index < 10 else ''}{index}:** {auth['auth_user']}\n"
                text += f"    **ᴀᴜᴛʜ ʙʏ:** {auth['admin_name']} (`{auth['admin_id']}`)\n"
                text += f"    **sɪɴᴄᴇ:** __{auth['auth_date']}__\n\n"
        
        except IndexError:
            page = 0
            for auth in grouped[int(page)]:
                index += 1
                text += f"**{'0' if index < 10 else ''}{index}:** {auth['auth_user']}\n"
                text += f"    **ᴀᴜᴛʜ ʙʏ:** {auth['admin_name']} (`{auth['admin_id']}`)\n"
                text += f"    **sɪɴᴄᴇ:** __{auth['auth_date']}__\n\n"
        
        if edit:
            await m.edit_text(text, reply_markup=InlineKeyboardMarkup(btns))
        
        else:
            await m.reply_text(text, reply_markup=InlineKeyboardMarkup(btns))
    
    async def favorite_page(
        self,
        message: Message or CallbackQuery,
        collection: list,
        user_id: int,
        mention: str,
        page: int = 0,
        index: int = 0,
        edit: bool = False,
        delete: bool = False,
    ):
        
        m = message.message if isinstance(message, CallbackQuery) else message
        
        if not collection:
            text = "**ɴᴏ ꜰᴀᴠᴏʀɪᴛᴇ ᴛʀᴀᴄᴋs ꜰᴏᴜɴᴅ!**"
            if edit:
                return await m.edit_text(text)
            return await m.reply_text(text)
        
        grouped, total = formatter.group_the_list(collection, 5)
        text = f"__({page+1}/{len(grouped)})__ {mention} **ꜰᴀᴠᴏʀɪᴛᴇs:** __{total} ᴛʀᴀᴄᴋs__\n\n"
        btns, final = await Buttons.favorite_markup(
            grouped, user_id, page, index, db, delete
        )
        
        if edit:
            await m.edit_text(f"{text}{final}", reply_markup=InlineKeyboardMarkup(btns))
        
        else:
            await m.reply_text(
                f"{text}{final}", reply_markup=InlineKeyboardMarkup(btns)
            )
    
    async def queue_page(
        self,
        message: Message or CallbackQuery,
        collection: list,
        page: int = 0,
        index: int = 0,
        edit: bool = False,
    ):
        
        m = message.message if isinstance(message, CallbackQuery) else message
        
        if not collection:
            text = "**ɴᴏ ᴛʀᴀᴄᴋs ɪɴ ᴛʜᴇ ᴇɴᴛɪʀᴇ ᴄʜᴀᴛ ᴏʀ ᴘʟᴀʏʟɪsᴛ!**"
            if edit:
                return await m.edit_text(text)
            return await m.reply_text(text)
        
        grouped, total = formatter.group_the_list(collection, 5)
        text = f"__({page+1}/{len(grouped)})__ **ɪɴ ᴛʜᴇ ᴄʜᴀᴛ ᴏʀ ᴘʟᴀʏʟɪsᴛ:** __{total} ᴛʀᴀᴄᴋs__\n\n"
        btns = Buttons.queue_markup(len(grouped), page)
        
        try:
            for que in grouped[page]:
                index += 1
                text += f"**{'0' if index < 10 else ''}{index}:** {que['title']}\n"
                text += f"    **ᴠᴄ ᴛʏᴘᴇ:** {que['vc_type']}\n"
                text += f"    **ʀᴇǫᴜᴇsᴛᴇᴅ ʙʏ:** {que['user']}\n"
                text += f"    **ᴅᴜʀᴀᴛɪᴏɴ:** __{que['duration']} ({que.get('platform', 'ᴜɴᴋɴᴏᴡɴ').capitalize()} ʟɪᴠ法
                text += "\n"
        
        except IndexError:
            return await m.edit_text("**ɴᴏ ᴍᴏʀᴇ ᴛʀᴀᴄᴋs ɪɴ ᴛʜᴇ ᴄʜᴀᴛ ᴏʀ ᴘʟᴀʏʟɪsᴛ!**")
        
        if edit:
            await m.edit_text(text, reply_markup=InlineKeyboardMarkup(btns))
        
        else:
            await m.reply_text(text, reply_markup=InlineKeyboardMarkup(btns))


MakePages = Pages()
