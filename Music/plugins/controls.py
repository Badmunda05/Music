import asyncio

from pyrogram import filters
from pyrogram.types import Message

from config import Config
from Music.core.calls import PbxMusic
from Music.core.clients import PbxBot
from Music.core.database import db
from Music.core.decorators import AuthWrapper, check_mode
from Music.helpers.formatters import formatter
from Music.utils.play import player
from Music.utils.queue import Queue
from Music.utils.youtube import ytube


@PbxBot.app.on_message(
    filters.command(["mute", "unmute"]) & filters.group & ~Config.BANNED_USERS
)
@check_mode
@AuthWrapper
async def mute_unmute(_, message: Message):
    
    is_muted = await db.get_watcher(message.chat.id, "mute")
    
    if message.command[0][0] == "u":
        if is_muted:
            await db.set_watcher(message.chat.id, "mute", False)
            await PbxMusic.unmute_vc(message.chat.id)
            return await message.reply_text(
                f"__ᴠᴄ ᴜɴᴍᴜᴛᴇᴅ ʙʏ:__ {message.from_user.mention}"
            )
        else:
            return await message.reply_text("**ᴠᴏɪᴄᴇ ᴄʜᴀᴛ ɪs ɴᴏᴛ ᴍᴜᴛᴇᴅ!**")
    
    else:
        if is_muted:
            return await message.reply_text("**ᴠᴏɪᴄᴇ ᴄʜᴀᴛ ɪs ᴀʟʀᴇᴀᴅʏ ᴍᴜᴛᴇᴅ!**")
        else:
            await db.set_watcher(message.chat.id, "mute", True)
            await PbxMusic.mute_vc(message.chat.id)
            return await message.reply_text(
                f"__ᴠᴄ ᴍᴜᴛᴇᴅ ʙʏ:__ {message.from_user.mention}"
            )


@PbxBot.app.on_message(
    filters.command(["pause", "resume"]) & filters.group & ~Config.BANNED_USERS
)
@check_mode
@AuthWrapper
async def pause_resume(_, message: Message):
    
    is_paused = await db.get_watcher(message.chat.id, "pause")
    
    if message.command[0][0] == "r":
        if is_paused:
            await db.set_watcher(message.chat.id, "pause", False)
            await PbxMusic.resume_vc(message.chat.id)
            return await message.reply_text(
                f"__ᴠᴄ ʀᴇsᴜᴍᴇᴅ ʙʏ:__ {message.from_user.mention}"
            )
        else:
            return await message.reply_text("**ᴠᴏɪᴄᴇ ᴄʜᴀᴛ ɪs ɴᴏᴛ ᴘᴀᴜsᴇᴅ!**")
    
    else:
        if is_paused:
            return await message.reply_text("**ᴠᴏɪᴄᴇ ᴄʜᴀᴛ ɪs ᴀʟʀᴇᴀᴅʏ ᴘᴀᴜsᴇᴅ!**")
        else:
            await db.set_watcher(message.chat.id, "pause", True)
            await PbxMusic.pause_vc(message.chat.id)
            return await message.reply_text(
                f"__ᴠᴄ ᴘᴀᴜsᴇᴅ ʙʏ:__ {message.from_user.mention}"
            )


@PbxBot.app.on_message(
    filters.command(["stop", "end"]) & filters.group & ~Config.BANNED_USERS
)
@check_mode
@AuthWrapper
async def stop_end(_, message: Message):
    
    await PbxMusic.leave_vc(message.chat.id)
    await db.set_loop(message.chat.id, 0)
    await message.reply_text(f"__ᴠᴄ sᴛᴏᴘᴘᴇᴅ ʙʏ:__ {message.from_user.mention}")


@PbxBot.app.on_message(filters.command("loop") & filters.group & ~Config.BANNED_USERS)
@check_mode
@AuthWrapper
async def loop(_, message: Message):
    
    if len(message.command) < 2:
        return await message.reply_text(
            "**ᴘʟᴇᴀsᴇ sᴘᴇᴄɪꜰʏ ᴛʜᴇ ɴᴜᴍʙᴇʀ ᴏꜰ ᴛɪᴍᴇs ᴛᴏ ʟᴏᴏᴘ ᴛʜᴇ sᴏɴɢ!** \n\n**ᴍᴀxɪᴍᴜᴍ ʟᴏᴏᴘ ʀᴀɴɢᴇ ɪs 10.** ᴜsᴇ **0** ᴛᴏ ᴅɪsᴀʙʟᴇ ʟᴏᴏᴘ."
        )
    
    try:
        loop = int(message.command[1])
    
    except Exception:
        return await message.reply_text(
            "**ᴘʟᴇᴀsᴇ ᴇɴᴛᴇʀ ᴀ ᴠᴀʟɪᴅ ɴᴜᴍʙᴇʀ!** \n\n**ᴍᴀxɪᴍᴜᴍ ʟᴏᴏᴘ ʀᴀɴɢᴇ ɪs 10.** ᴜsᴇ **0** ᴛᴏ ᴅɪsᴀʙʟᴇ ʟᴏᴏᴘ."
        )
    
    is_loop = await db.get_loop(message.chat.id)
    
    if loop == 0:
        if is_loop == 0:
            return await message.reply_text("**ᴛʜᴇʀᴇ ɪs ɴᴏ ᴀᴄᴛɪᴠᴇ ʟᴏᴏᴘ ɪɴ ᴛʜɪs ᴄʜᴀᴛ!**")
        
        await db.set_loop(message.chat.id, 0)
        return await message.reply_text(
            f"__ʟᴏᴏᴘ ᴅɪsᴀʙʟᴇᴅ ʙʏ:__ {message.from_user.mention}\n\n**ᴘʀᴇᴠɪᴏᴜs ʟᴏᴏᴘ:** `{is_loop}`"
        )
    
    if 1 <= loop <= 10:
        final = is_loop + loop
        final = 10 if final > 10 else final
        await db.set_loop(message.chat.id, final)
        await message.reply_text(
            f"__ʟᴏᴏᴘ sᴇᴛ ᴛᴏ:__ `{final}`\n__ʙʏ:__ {message.from_user.mention}\n\n**ᴘʀᴇᴠɪᴏᴜs ʟᴏᴏᴘ:** `{is_loop}`"
        )
    
    else:
        return await message.reply_text(
            "**ᴘʟᴇᴀsᴇ ᴇɴᴛᴇʀ ᴀ ᴠᴀʟɪᴅ ɴᴜᴍʙᴇʀ!** \n\n**ᴍᴀxɪᴍᴜᴍ ʟᴏᴏᴘ ʀᴀɴɢᴇ ɪs 10.** ᴜsᴇ **0** ᴛᴏ ᴅɪsᴀʙʟᴇ ʟᴏᴏᴘ."
        )


@PbxBot.app.on_message(
    filters.command("replay") & filters.group & ~Config.BANNED_USERS
)
@check_mode
@AuthWrapper
async def replay(_, message: Message):
    
    is_active = await db.is_active_vc(message.chat.id)
    
    if not is_active:
        return await message.reply_text("**ɴᴏ ᴀᴄᴛɪᴠᴇ ᴠᴏɪᴄᴇ ᴄʜᴀᴛ ꜰᴏᴜɴᴅ ʜᴇʀᴇ!**")
    
    Pbx = await message.reply_text("**ʀᴇᴘʟᴀʏɪɴɢ...**")
    que = Queue.get_queue(message.chat.id)
    
    if que == []:
        return await Pbx.edit("**ɴᴏ sᴏɴɢs ɪɴ ᴛʜᴇ ᴄʜᴀᴛ ᴏʀ ᴘʟᴀʏʟɪsᴛ ᴛᴏ ʀᴇᴘʟᴀʏ!**")
    
    await player.replay(message.chat.id, Pbx)


@PbxBot.app.on_message(
    filters.command("skip") & filters.group & ~Config.BANNED_USERS
)
@check_mode
@AuthWrapper
async def skip(_, message: Message):
    
    is_active = await db.is_active_vc(message.chat.id)
    
    if not is_active:
        return await message.reply_text("**ɴᴏ ᴀᴄᴛɪᴠᴇ ᴠᴏɪᴄᴇ ᴄʜᴀᴛ ꜰᴏᴜɴᴅ ʜᴇʀᴇ!**")
    
    Pbx = await message.reply_text("**ᴘʀᴏᴄᴇssɪɴɢ...**")
    que = Queue.get_queue(message.chat.id)
    
    if que == []:
        return await Pbx.edit("**ɴᴏ sᴏɴɢs ɪɴ ᴛʜᴇ ᴄʜᴀᴛ ᴏʀ ᴘʟᴀʏʟɪsᴛ ᴛᴏ sᴋɪᴘ!**")
    
    if len(que) == 1:
        return await Pbx.edit_text(
            "**ɴᴏ ᴍᴏʀᴇ sᴏɴɢs ɪɴ ᴄʜᴀᴛ ᴏʀ ᴘʟᴀʏʟɪsᴛ ᴛᴏ sᴋɪᴘ!** ᴜsᴇ `/end` ᴏʀ `/stop` ᴛᴏ sᴛᴏᴘ ᴛʜᴇ ᴠᴄ."
        )
    
    is_loop = await db.get_loop(message.chat.id)
    
    if is_loop != 0:
        await Pbx.edit_text("**ᴅɪsᴀʙʟᴇᴅ ʟᴏᴏᴘ ᴛᴏ sᴋɪᴘ ᴛʜᴇ ᴄᴜʀʀᴇɴᴛ sᴏɴɢ!**")
        await db.set_loop(message.chat.id, 0)
    
    await player.skip(message.chat.id, Pbx)


@PbxBot.app.on_message(
    filters.command("seek") & filters.group & ~Config.BANNED_USERS
)
@check_mode
@AuthWrapper
async def seek(_, message: Message):
    
    is_active = await db.is_active_vc(message.chat.id)
    
    if not is_active:
        return await message.reply_text("**ɴᴏ ᴀᴄᴛɪᴠᴇ ᴠᴏɪᴄᴇ ᴄʜᴀᴛ ꜰᴏᴜɴᴅ ʜᴇʀᴇ!**")
    
    if len(message.command) < 2:
        return await message.reply_text(
            "**ᴘʟᴇᴀsᴇ sᴘᴇᴄɪꜰʏ ᴛʜᴇ ᴛɪᴍᴇ ᴛᴏ sᴇᴇᴋ!** \n\n**ᴇxᴀᴍᴘʟᴇ:** \n__sᴇᴇᴋ 10 sᴇᴄs ꜰᴏʀᴡᴀʀᴅ >__ `/seek 10` \n__sᴇᴇᴋ 10 sᴇᴄs ʙᴀᴄᴋᴡᴀʀᴅ >__ `/seek -10`"
        )
    
    Pbx = await message.reply_text("**sᴇᴇᴋɪɴɢ...**")
    
    try:
        if message.command[1][0] == "-":
            seek_time = int(message.command[1][1:])
            seek_type = 0  # backward
        else:
            seek_time = int(message.command[1])
            seek_type = 1  # forward
    
    except:
        return await Pbx.edit_text("**ᴘʟᴇᴀsᴇ ᴇɴᴛᴇʀ ɴᴜᴍᴇʀɪᴄ ᴄʜᴀʀᴀᴄᴛᴇʀs ᴏɴʟʏ!**")
    
    que = Queue.get_queue(message.chat.id)
    
    if que == []:
        return await Pbx.edit_text("**ɴᴏ sᴏɴɢs ɪɴ ᴛʜᴇ ᴄʜᴀᴛ ᴏʀ ᴘʟᴀʏʟɪsᴛ ᴛᴏ sᴇᴇᴋ!**")
    
    played = int(que[0]["played"])
    duration = formatter.mins_to_secs(que[0]["duration"])
    
    if seek_type == 0:
        if (played - seek_time) <= 10:
            return await Pbx.edit_text(
                "**ᴄᴀɴɴᴏᴛ sᴇᴇᴋ ᴡʜᴇɴ ᴏɴʟʏ 10 sᴇᴄᴏɴᴅs ᴀʀᴇ ʟᴇꜰᴛ!** ᴜsᴇ ᴀ ʟᴇssᴇʀ ᴠᴀʟᴜᴇ."
            )
        to_seek = played - seek_time
    
    else:
        if (duration - (played + seek_time)) <= 10:
            return await Pbx.edit_text(
                "**ᴄᴀɴɴᴏᴛ sᴇᴇᴋ ᴡʜᴇɴ ᴏɴʟʏ 10 sᴇᴄᴏɴᴅs ᴀʀᴇ ʟᴇꜰᴛ!** ᴜsᴇ ᴀ ʟᴇssᴇʀ ᴠᴀʟᴜᴇ."
            )
        to_seek = played + seek_time
    
    video = True if que[0]["vc_type"] == "video" else False
    
    if que[0]["file"] == que[0]["video_id"]:
        file_path = await ytube.download(que[0]["video_id"], True, video)
    
    else:
        file_path = que[0]["file"]
    
    try:
        context = {
            "chat_id": que[0]["chat_id"],
            "file": file_path,
            "duration": que[0]["duration"],
            "seek": formatter.secs_to_mins(to_seek),
            "video": video,
        }
        await PbxMusic.seek_vc(context)
    
    except:
        return await Pbx.edit_text("**sᴏᴍᴇᴛʜɪɴɢ ᴡᴇɴᴛ ᴡʀᴏɴɢ!**")
    
    Queue.update_duration(message.chat.id, seek_type, seek_time)
    await Pbx.edit_text(
        f"**sᴇᴇᴋᴇᴅ `{seek_time}` sᴇᴄᴏɴᴅs {'ꜰᴏʀᴡᴀʀᴅ' if seek_type == 1 else 'ʙᴀᴄᴋᴡᴀʀᴅ'}!**"
    )


@PbxBot.app.on_message(
    filters.command(["bass"]) & filters.group & ~Config.BANNED_USERS
)
@check_mode
@AuthWrapper
async def bass_boost(_, message: Message):
    
    is_active = await db.is_active_vc(message.chat.id)
    
    if not is_active:
        return await message.reply_text("**ɴᴏ ᴀᴄᴛɪᴠᴇ ᴠᴏɪᴄᴇ ᴄʜᴀᴛ ꜰᴏᴜɴᴅ ʜᴇʀᴇ!**")
    
    if len(message.command) < 2:
        return await message.reply_text(
            "**ᴘʟᴇᴀsᴇ sᴘᴇᴄɪꜰʏ ᴛʜᴇ ʙᴀss ʙᴏᴏsᴛ ʟᴇᴠᴇʟ (0 ᴛᴏ 100).** \n\n**ᴇxᴀᴍᴘʟᴇ:** `/bass 50` ᴛᴏ sᴇᴛ ʙᴀss ʙᴏᴏsᴛ ᴛᴏ 50%. ᴜsᴇ `/bass 0` ᴛᴏ ᴅɪsᴀʙʟᴇ."
        )
    
    try:
        bass_level = int(message.command[1])
        if not 0 <= bass_level <= 100:
            return await message.reply_text(
                "**ᴘʟᴇᴀsᴇ ᴇɴᴛᴇʀ ᴀ ᴠᴀʟɪᴅ ʙᴀss ʟᴇᴠᴇʟ ʙᴇᴛᴡᴇᴇɴ 0 ᴀɴᴅ 100!**"
            )
    
    except ValueError:
        return await message.reply_text("**ᴘʟᴇᴀsᴇ ᴇɴᴛᴇʀ ᴀ ᴠᴀʟɪᴅ ɴᴜᴍʙᴇʀ ꜰᴏʀ ʙᴀss ʟᴇᴠᴇʟ!**")
    
    Pbx = await message.reply_text("**ᴀᴅᴊᴜsᴛɪɴɢ ʙᴀss ʙᴏᴏsᴛ...**")
    que = Queue.get_queue(message.chat.id)
    
    if que == []:
        return await Pbx.edit_text("**ɴᴏ sᴏɴɢs ɪɴ ᴛʜᴇ ᴄʜᴀᴛ ᴏʀ ᴘʟᴀʏʟɪsᴛ ᴛᴏ ᴀᴘᴘʟʏ ʙᴀss ʙᴏᴏsᴛ!**")
    
    PbxMusic.bass_boost[message.chat.id] = bass_level
    video = True if que[0]["vc_type"] == "video" else False
    file_path = que[0]["file"] if que[0]["file"] == que[0]["video_id"] else await ytube.download(que[0]["video_id"], True, video)
    
    try:
        await PbxMusic.replay_vc(message.chat.id, file_path, video)
        await Pbx.edit_text(
            f"__ʙᴀss ʙᴏᴏsᴛ sᴇᴛ ᴛᴏ:__ `{bass_level}` ʙʏ {message.from_user.mention}"
        )
    
    except Exception as e:
        await Pbx.edit_text(f"**ᴇʀʀᴏʀ ᴀᴘᴘʟʏɪɴɢ ʙᴀss ʙᴏᴏsᴛ:** {e}")


@PbxBot.app.on_message(
    filters.command(["speed", "playback"]) & filters.group & ~Config.BANNED_USERS
)
@check_mode
@AuthWrapper
async def speed_control(_, message: Message):
    
    is_active = await db.is_active_vc(message.chat.id)
    
    if not is_active:
        return await message.reply_text("**ɴᴏ ᴀᴄᴛɪᴠᴇ ᴠᴏɪᴄᴇ ᴄʜᴀᴛ ꜰᴏᴜɴᴅ ʜᴇʀᴇ!**")
    
    if len(message.command) < 2:
        return await message.reply_text(
            "**ᴘʟᴇᴀsᴇ sᴘᴇᴄɪꜰʏ ᴛʜᴇ ᴘʟᴀʏʙᴀᴄᴋ sᴘᴇᴇᴅ (0.5 ᴛᴏ 4.0).** \n\n**ᴇxᴀᴍᴘʟᴇ:** `/speed 2.0` ᴛᴏ sᴇᴛ sᴘᴇᴇᴅ ᴛᴏ 2.0x. ᴜsᴇ `/speed 1.0` ᴛᴏ ʀᴇsᴇᴛ."
        )
    
    try:
        speed = float(message.command[1])
        if not 0.5 <= speed <= 4.0:
            return await message.reply_text(
                "**ᴘʟᴇᴀsᴇ ᴇɴᴛᴇʀ ᴀ ᴠᴀʟɪᴅ sᴘᴇᴇᴅ ʙᴇᴛᴡᴇᴇɴ 0.5 ᴀɴᴅ 4.0!**"
            )
    
    except ValueError:
        return await message.reply_text("**ᴘʟᴇᴀsᴇ ᴇɴᴛᴇʀ ᴀ ᴠᴀʟɪᴅ ɴᴜᴍʙᴇʀ ꜰᴏʀ sᴘᴇᴇᴅ!**")
    
    Pbx = await message.reply_text("**ᴀᴅᴊᴜsᴛɪɴɢ ᴘʟᴀʏʙᴀᴄᴋ sᴘᴇᴇᴅ...**")
    que = Queue.get_queue(message.chat.id)
    
    if que == []:
        return await Pbx.edit_text("**ɴᴏ sᴏɴɢs ɪɴ ᴛʜᴇ ᴄʜᴀᴛ ᴏʀ ᴘʟᴀʏʟɪsᴛ ᴛᴏ ᴀᴅᴊᴜsᴛ sᴘᴇᴇᴅ!**")
    
    PbxMusic.speed[message.chat.id] = speed
    video = True if que[0]["vc_type"] == "video" else False
    file_path = que[0]["file"] if que[0]["file"] == que[0]["video_id"] else await ytube.download(que[0]["video_id"], True, video)
    
    try:
        await PbxMusic.replay_vc(message.chat.id, file_path, video)
        await Pbx.edit_text(
            f"__ᴘʟᴀʏʙᴀᴄᴋ sᴘᴇᴇᴅ sᴇᴛ ᴛᴏ:__ `{speed}x` ʙʏ {message.from_user.mention}"
        )
    
    except Exception as e:
        await Pbx.edit_text(f"**ᴇʀʀᴏʀ ᴀᴅᴊᴜsᴛɪɴɢ sᴘᴇᴇᴅ:** {e}")
