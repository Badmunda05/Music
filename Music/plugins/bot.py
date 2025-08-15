import asyncio
import datetime
import speedtest

from pyrogram import filters
from pyrogram.enums import ChatType
from pyrogram.types import InlineKeyboardMarkup, Message

from config import Config
from Music.core.calls import PbxMusic
from Music.core.clients import PbxBot
from Music.core.database import db
from Music.core.decorators import UserWrapper, check_mode
from Music.helpers.buttons import Buttons
from Music.helpers.formatters import formatter
from Music.helpers.strings import TEXTS
from Music.helpers.users import MusicUser
from Music.utils.youtube import ytube


@PbxBot.app.on_message(filters.command(["start", "alive"]) & ~Config.BANNED_USERS)
@check_mode
async def start(_, message: Message):
    # Delete the user's command message
    await message.delete()
    
    accha = await message.reply_text("**sᴛᴀʀᴛɪɴɢ....**")
    await asyncio.sleep(0.5)
    await accha.edit("**__ꨄ︎ ѕ__**")
    await asyncio.sleep(0.01)
    await accha.edit("**__ꨄ sт__**")
    await asyncio.sleep(0.01)
    await accha.edit("**__ꨄ︎ ѕтα__**")
    await asyncio.sleep(0.01)
    await accha.edit("**__ꨄ sтαя__**")
    await asyncio.sleep(0.01)
    await accha.edit("**__ꨄ︎ sтαят__**")
    await asyncio.sleep(0.01)
    await accha.edit("**__ꨄ sтαятι__**")
    await asyncio.sleep(0.01)
    await accha.edit("**__ꨄ sтαятιи__**")
    await asyncio.sleep(0.01)
    await accha.edit("**__ꨄ sтαятιиg__**")
    await asyncio.sleep(0.01)
    await accha.edit("**__ꨄ︎ ѕтαятιиg.__**")
    await asyncio.sleep(0.1)
    await accha.edit("**__ꨄ sтαятιиg.....__**")
    await asyncio.sleep(0.1)
    await accha.edit("**__ꨄ︎ ѕтαятιиg.__**")
    await asyncio.sleep(0.1)
    await accha.edit("**__ꨄ sтαятιиg.....__**")
    await accha.delete()
    
    if message.chat.type == ChatType.PRIVATE:
        if len(message.command) > 1:
            deep_cmd = message.text.split(None, 1)[1]
            if deep_cmd.startswith("song"):
                results = await ytube.get_data(deep_cmd.split("_", 1)[1], True)
                about = TEXTS.ABOUT_SONG.format(
                    results[0]["title"],
                    results[0]["channel"],
                    results[0]["published"],
                    results[0]["views"],
                    results[0]["duration"],
                    PbxBot.app.mention,
                )
                await message.reply_photo(
                    results[0]["thumbnail"],
                    caption=about,
                    reply_markup=InlineKeyboardMarkup(
                        Buttons.song_details_markup(
                            results[0]["link"],
                            results[0]["ch_link"],
                        )
                    ),
                )
                return
            elif deep_cmd.startswith("user"):
                userid = int(deep_cmd.split("_", 1)[1])
                userdbs = await db.get_user(userid)
                songs = userdbs["songs_played"]
                level = MusicUser.get_user_level(int(songs))
                to_send = TEXTS.ABOUT_USER.format(
                    userdbs["user_name"],
                    userdbs["user_id"],
                    level,
                    songs,
                    userdbs["join_date"],
                    PbxBot.app.mention,
                )
                await message.reply_text(
                    to_send,
                    reply_markup=InlineKeyboardMarkup(Buttons.close_markup()),
                    disable_web_page_preview=True,
                )
                return
            elif deep_cmd.startswith("help"):
                await message.reply_photo(
                    Config.HELP_PIC,
                    caption=TEXTS.HELP_PM.format(PbxBot.app.mention),
                    reply_markup=InlineKeyboardMarkup(Buttons.help_pm_markup()),
                )
                return
        await message.reply_photo(
            Config.START_PIC,
            caption=TEXTS.START_PM.format(
                message.from_user.first_name,
                PbxBot.app.mention,
                PbxBot.app.username,
            ),
            has_spoiler=True,
            reply_markup=InlineKeyboardMarkup(Buttons.start_pm_markup(PbxBot.app.username)),
        )
    elif message.chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]:
        await message.reply_text(TEXTS.START_GC)


@PbxBot.app.on_message(filters.command("help") & ~Config.BANNED_USERS)
async def help(_, message: Message):
    # Delete the user's command message
    await message.delete()
    
    if message.chat.type == ChatType.PRIVATE:
        await message.reply_photo(
            Config.HELP_PIC,
            caption=TEXTS.HELP_PM.format(PbxBot.app.mention),
            has_spoiler=True,
            reply_markup=InlineKeyboardMarkup(Buttons.help_pm_markup()),
        )
    elif message.chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]:
        await message.reply_text(
            TEXTS.HELP_GC,
            reply_markup=InlineKeyboardMarkup(
                Buttons.help_gc_markup(PbxBot.app.username)
            ),
        )


@PbxBot.app.on_message(filters.command("ping") & ~Config.BANNED_USERS)
async def ping(_, message: Message):
    # Delete the user's command message
    await message.delete()
    
    start_time = datetime.datetime.now()
    Pbx = await message.reply_text("Pong!")
    calls_ping = await PbxMusic.ping()
    stats = await formatter.system_stats()
    end_time = (datetime.datetime.now() - start_time).microseconds / 1000
    await Pbx.edit_text(
        TEXTS.PING_REPLY.format(end_time, stats["uptime"], calls_ping),
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup(Buttons.close_markup()),
    )


@PbxBot.app.on_message(filters.command("sysinfo") & ~Config.BANNED_USERS)
@check_mode
@UserWrapper
async def sysinfo(_, message: Message):
    # Delete the user's command message
    await message.delete()
    
    stats = await formatter.system_stats()
    await message.reply_text(
        TEXTS.SYSTEM.format(
            stats["core"],
            stats["cpu"],
            stats["disk"],
            stats["ram"],
            stats["uptime"],
            PbxBot.app.mention,
        ),
        reply_markup=InlineKeyboardMarkup(Buttons.close_markup()),
    )


def testspeed(m):
    
    try:
        test = speedtest.Speedtest()
        test.get_best_server()
        
        m = m.edit_text("**sᴛᴀʀᴛɪɴɢ sᴘᴇᴇᴅ ᴛᴇsᴛ...**")
        test.download()
        
        m = m.edit_text("**ᴍᴇᴀsᴜʀɪɴɢ ᴅᴏᴡɴʟᴏᴀᴅ sᴘᴇᴇᴅ...**")
        test.upload()
        
        m = m.edit_text("**ᴍᴇᴀsᴜʀɪɴɢ ᴜᴘʟᴏᴀᴅ sᴘᴇᴇᴅ...**")
        test.results.share()
        
        result = test.results.dict()
    
    except Exception as e:
        m.edit_text(f"**ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ:** `{e}`")
        return
    
    return result


@PbxBot.app.on_message(filters.command("spt") & ~Config.BANNED_USERS)
@check_mode
@UserWrapper
async def speedtest_function(client, message: Message):
    
    # Delete the user's command message
    await message.delete()
    
    m = await message.reply_text("**sᴛᴀʀᴛɪɴɢ sᴘᴇᴇᴅ ᴛᴇsᴛ...**")
    
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, testspeed, m)
    
    if not result:
        return
    
    output = (
        "**sᴘᴇᴇᴅᴛᴇsᴛ ʀᴇsᴜʟᴛs:**\n"
        f"**ɪsᴘ:** {result['client']['isp']}\n"
        f"**ᴄᴏᴜɴᴛʀʏ:** {result['client']['country']}\n"
        f"**sᴇʀᴠᴇʀ:** {result['server']['name']}\n"
        f"**sᴇʀᴠᴇʀ ᴄᴏᴜɴᴛʀʏ:** {result['server']['country']}\n"
        f"**sᴇʀᴠᴇʀ ᴄᴏᴅᴇ:** {result['server']['cc']}\n"
        f"**sᴘᴏɴsᴏʀ:** {result['server']['sponsor']}\n"
        f"**ʟᴀᴛᴇɴᴄʏ:** {result['server']['latency']} ᴍs\n"
        f"**ᴘɪɴɢ:** {result['ping']} ᴍs"
    )
    
    msg = await message.reply_photo(
        photo=result["share"],
        caption=output
    )
    
    await m.delete()
