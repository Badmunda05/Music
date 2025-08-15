import asyncio

from pyrogram import filters
from pyrogram.types import CallbackQuery, Message

from config import Config
from Music.core.clients import PbxBot
from Music.core.decorators import UserWrapper, check_mode
from Music.helpers.formatters import formatter
from Music.utils.pages import MakePages
from Music.utils.youtube import ytube


@PbxBot.app.on_message(filters.command("song") & ~Config.BANNED_USERS)
@check_mode
@UserWrapper
async def songs(_, message: Message):
    
    if len(message.command) == 1:
        return await message.reply_text("**ɴᴏᴛʜɪɴɢ ɢɪᴠᴇɴ ᴛᴏ sᴇᴀʀᴄʜ.**")
    
    query = message.text.split(None, 1)[1]
    Pbx = await message.reply_photo(
        Config.BLACK_IMG, caption=f"<b><i>sᴇᴀʀᴄʜɪɴɢ</i></b> “`{query}`” ..."
    )
    
    all_tracks = await ytube.get_data(query, False, 10)
    rand_key = formatter.gen_key(str(message.from_user.id), 5)
    Config.SONG_CACHE[rand_key] = all_tracks
    
    await MakePages.song_page(Pbx, rand_key, 0)


@PbxBot.app.on_message(filters.command("lyrics") & ~Config.BANNED_USERS)
@check_mode
@UserWrapper
async def lyrics(_, message: Message):
    
    if not Config.LYRICS_API:
        return await message.reply_text("**ʟʏʀɪᴄs ᴍᴏᴅᴜʟᴇ ɪs ᴅɪsᴀʙʟᴇᴅ!**")
    
    lists = message.text.split(" ", 1)
    
    if not len(lists) == 2:
        return await message.reply_text(
            "**ɴᴏᴛʜɪɴɢ ɢɪᴠᴇɴ ᴛᴏ sᴇᴀʀᴄʜ.** \n**ᴇxᴀᴍᴘʟᴇ:** `/lyrics loose yourself - eminem`"
        )
    
    _input_ = lists[1].strip()
    query = _input_.split("-", 1)
    
    if len(query) == 2:
        song = query[0].strip()
        artist = query[1].strip()
    else:
        song = query[0].strip()
        artist = ""
    
    text = f"**sᴇᴀʀᴄʜɪɴɢ ʟʏʀɪᴄs...** \n\n__sᴏɴɢ:__ `{song}`"
    
    if artist != "":
        text += f"\n__ᴀʀᴛɪsᴛ:__ `{artist}`"
    
    Pbx = await message.reply_text(text)
    results = await ytube.get_lyrics(song, artist)
    
    if results:
        title = results["title"]
        image = results["image"]
        lyrics = results["lyrics"]
        final = f"<b><i>• sᴏɴɢ:</b></i> <code>{title}</code> \n<b><i>• ʟʏʀɪᴄs:</b></i> \n<code>{lyrics}</code>"
        
        if len(final) >= 4095:
            page_name = f"{title}"
            to_paste = f"<img src='{image}'/> \n{final} \n<img src='https://files.catbox.moe/65layt.jpg'/>"
            link = await formatter.telegraph_paste(page_name, to_paste)
            await Pbx.edit_text(
                f"**ʟʏʀɪᴄs ᴛᴏᴏ ʙɪɢ! ɢᴇᴛ ɪᴛ ꜰʀᴏᴍ ʜᴇʀᴇ:** \n\n• [{title}]({link})",
                disable_web_page_preview=True,
            )
        
        else:
            await Pbx.edit_text(final)
        
        chat = message.chat.title or message.chat.first_name
        await PbxBot.logit(
            "lyrics",
            f"**⤷ ʟʏʀɪᴄs:** `{title}`\n**⤷ ᴄʜᴀᴛ:** {chat} [`{message.chat.id}`]\n**⤷ ᴜsᴇʀ:** {message.from_user.mention} [`{message.from_user.id}`]",
        )
    
    else:
        await Pbx.edit_text("**ᴜɴᴇxᴘᴇᴄᴛᴇᴅ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ.**")


@PbxBot.app.on_callback_query(filters.regex(r"song_dl(.*)$") & ~Config.BANNED_USERS)
async def song_cb(_, cb: CallbackQuery):
    
    _, action, key, rand_key = cb.data.split("|")
    user = rand_key.split("_")[0]
    key = int(key)
    
    if cb.from_user.id != int(user):
        await cb.answer("**ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀʟʟᴏᴡᴇᴅ ᴛᴏ ᴅᴏ ᴛʜᴀᴛ!**", show_alert=True)
        return
    
    if action == "adl":
        await ytube.send_song(cb, rand_key, key, False)
        return
    
    elif action == "vdl":
        await ytube.send_song(cb, rand_key, key, True)
        return
    
    elif action == "close":
        Config.SONG_CACHE.pop(rand_key)
        await cb.message.delete()
        return
    
    else:
        all_tracks = Config.SONG_CACHE[rand_key]
        length = len(all_tracks)
        
        if key == 0 and action == "prev":
            key = length - 1
        elif key == length - 1 and action == "next":
            key = 0
        else:
            key = key + 1 if action == "next" else key - 1
        
        await MakePages.song_page(cb, rand_key, key)
