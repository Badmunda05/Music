import asyncio

from pyrogram import filters
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup

from config import Config
from Music.core.calls import PbxMusic
from Music.core.clients import PbxBot
from Music.core.database import db
from Music.helpers.buttons import Buttons
from Music.helpers.formatters import formatter
from Music.helpers.strings import TEXTS
from Music.utils.admins import get_auth_users
from Music.utils.play import player
from Music.utils.queue import Queue
from Music.utils.youtube import ytube


@PbxBot.app.on_callback_query(filters.regex(r"close") & ~Config.BANNED_USERS)
async def close_cb(_, cb: CallbackQuery):
    
    try:
        await cb.message.delete()
        await cb.answer("**ᴄʟᴏsᴇᴅ!**", show_alert=True)
    
    except:
        pass


@PbxBot.app.on_callback_query(filters.regex(r"controls") & ~Config.BANNED_USERS)
async def controls_cb(_, cb: CallbackQuery):
    
    video_id = cb.data.split("|")[1]
    chat_id = int(cb.data.split("|")[2])
    
    btns = Buttons.controls_markup(video_id, chat_id)
    
    try:
        await cb.message.edit_reply_markup(InlineKeyboardMarkup(btns))
    
    except:
        return


@PbxBot.app.on_callback_query(filters.regex(r"player") & ~Config.BANNED_USERS)
async def player_cb(_, cb: CallbackQuery):
    
    _, video_id, chat_id = cb.data.split("|")
    
    btns = Buttons.player_markup(chat_id, video_id, PbxBot.app.username)
    
    try:
        await cb.message.edit_reply_markup(InlineKeyboardMarkup(btns))
    
    except:
        return


@PbxBot.app.on_callback_query(filters.regex(r"ctrl") & ~Config.BANNED_USERS)
async def controler_cb(_, cb: CallbackQuery):
    
    _, action, *params = cb.data.split("|")
    chat_id = int(params[-1])
    
    if int(chat_id) != cb.message.chat.id:
        return await cb.answer("**ᴛʜɪs ᴍᴇssᴀɢᴇ ɪs ɴᴏᴛ ꜰᴏʀ ᴛʜɪs ᴄʜᴀᴛ!**", show_alert=True)
    
    is_active = await db.is_active_vc(int(chat_id))
    
    if not is_active:
        return await cb.answer("**ᴠᴏɪᴄᴇ ᴄʜᴀᴛ ɪs ɴᴏᴛ ᴀᴄᴛɪᴠᴇ!**", show_alert=True)
    
    is_authchat = await db.is_authchat(cb.message.chat.id)
    
    if not is_authchat:
        if cb.from_user.id not in Config.SUDO_USERS:
            try:
                admins = await get_auth_users(int(chat_id))
            
            except Exception as e:
                return await cb.answer(
                    f"**ᴇʀʀᴏʀ ꜰᴇᴛᴄʜɪɴɢ ᴀᴅᴍɪɴ ʟɪsᴛ:**\n\n{e}",
                    show_alert=True,
                )
            
            if not admins:
                return await cb.answer("**ɴᴇᴇᴅ ᴛᴏ ʀᴇꜰʀᴇsʜ ᴀᴅᴍɪɴ ʟɪsᴛ!**", show_alert=True)
            
            else:
                if cb.from_user.id not in admins:
                    return await cb.answer(
                        "**ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ɪs ᴏɴʟʏ ꜰᴏʀ ᴀᴜᴛʜᴏʀɪᴢᴇᴅ ᴜsᴇʀs ᴀɴᴅ ᴀᴅᴍɪɴs!**",
                        show_alert=True,
                    )
    
    if action == "play":
        is_paused = await db.get_watcher(cb.message.chat.id, "pause")
        
        if is_paused:
            await db.set_watcher(cb.message.chat.id, "pause", False)
            await PbxMusic.resume_vc(cb.message.chat.id)
            await cb.answer("**ʀᴇsᴜᴍᴇᴅ!**", show_alert=True)
            return await cb.message.reply_text(
                f"__ᴠᴄ ʀᴇsᴜᴍᴇᴅ ʙʏ:__ {cb.from_user.mention}"
            )
        
        else:
            await db.set_watcher(cb.message.chat.id, "pause", True)
            await PbxMusic.pause_vc(cb.message.chat.id)
            await cb.answer("**ᴘᴀᴜsᴇᴅ!**", show_alert=True)
            return await cb.message.reply_text(
                f"__ᴠᴄ ᴘᴀᴜsᴇᴅ ʙʏ:__ {cb.from_user.mention}"
            )
    
    elif action == "mute":
        is_muted = await db.get_watcher(cb.message.chat.id, "mute")
        
        if is_muted:
            return await cb.answer("**ᴀʟʀᴇᴀᴅʏ ᴍᴜᴛᴇᴅ!**", show_alert=True)
        
        else:
            await db.set_watcher(cb.message.chat.id, "mute", True)
            await PbxMusic.mute_vc(cb.message.chat.id)
            await cb.answer("**ᴍᴜᴛᴇᴅ!**", show_alert=True)
            return await cb.message.reply_text(
                f"__ᴠᴄ ᴍᴜᴛᴇᴅ ʙʏ:__ {cb.from_user.mention}"
            )
    
    elif action == "unmute":
        is_muted = await db.get_watcher(cb.message.chat.id, "mute")
        
        if is_muted:
            await db.set_watcher(cb.message.chat.id, "mute", False)
            await PbxMusic.unmute_vc(cb.message.chat.id)
            await cb.answer("**ᴜɴᴍᴜᴛᴇᴅ!**", show_alert=True)
            return await cb.message.reply_text(
                f"__ᴠᴄ ᴜɴᴍᴜᴛᴇᴅ ʙʏ:__ {cb.from_user.mention}"
            )
        
        else:
            return await cb.answer("**ᴀʟʀᴇᴀᴅʏ ᴜɴᴍᴜᴛᴇᴅ!**", show_alert=True)
    
    elif action == "end":
        await PbxMusic.leave_vc(cb.message.chat.id)
        await db.set_loop(cb.message.chat.id, 0)
        await cb.answer("**ʟᴇꜰᴛ ᴛʜᴇ ᴠᴄ!**", show_alert=True)
        return await cb.message.reply_text(f"__ᴠᴄ sᴛᴏᴘᴘᴇᴅ ʙʏ:__ {cb.from_user.mention}")
    
    elif action == "loop":
        is_loop = await db.get_loop(cb.message.chat.id)
        final = is_loop + 3
        final = 10 if final > 10 else final
        await db.set_loop(cb.message.chat.id, final)
        await cb.answer(f"**ʟᴏᴏᴘ sᴇᴛ ᴛᴏ {final}**", show_alert=True)
        return await cb.message.reply_text(
            f"__ʟᴏᴏᴘ sᴇᴛ ᴛᴏ {final}__ ʙʏ: {cb.from_user.mention}\n\n**ᴘʀᴇᴠɪᴏᴜs ʟᴏᴏᴘ:** {is_loop}"
        )
    
    elif action == "replay":
        Pbx = await cb.message.reply_text("**ᴘʀᴏᴄᴇssɪɴɢ...**")
        que = Queue.get_queue(cb.message.chat.id)
        
        if que == []:
            await Pbx.delete()
            return await cb.answer("**ɴᴏ sᴏɴɢs ɪɴ ᴄʜᴀᴛ ᴏʀ ᴘʟᴀʏʟɪsᴛ ᴛᴏ ʀᴇᴘʟᴀʏ!**", show_alert=True)
        
        await cb.answer("**ʀᴇᴘʟᴀʏɪɴɢ!**", show_alert=True)
        await player.replay(cb.message.chat.id, Pbx)
    
    elif action == "skip":
        Pbx = await cb.message.reply_text("**ᴘʀᴏᴄᴇssɪɴɢ...**")
        que = Queue.get_queue(cb.message.chat.id)
        
        if que == []:
            await Pbx.delete()
            return await cb.answer("**ɴᴏ sᴏɴɢs ɪɴ ᴄʜᴀᴛ ᴏʀ ᴘʟᴀʏʟɪsᴛ ᴛᴏ sᴋɪᴘ!**", show_alert=True)
        
        if len(que) == 1:
            await Pbx.delete()
            return await cb.answer(
                "**ɴᴏ ᴍᴏʀᴇ sᴏɴɢs ɪɴ ᴄʜᴀᴛ ᴏʀ ᴘʟᴀʏʟɪsᴛ ᴛᴏ sᴋɪᴘ!** ᴜsᴇ `/end` ᴏʀ `/stop` ᴛᴏ sᴛᴏᴘ ᴛʜᴇ ᴠᴄ.",
                show_alert=True,
            )
        
        is_loop = await db.get_loop(cb.message.chat.id)
        
        if is_loop != 0:
            await db.set_loop(cb.message.chat.id, 0)
        
        await player.skip(cb.message.chat.id, Pbx)
    
    elif action == "bseek":
        que = Queue.get_queue(cb.message.chat.id)
        
        if que == []:
            return await cb.answer("**ɴᴏ sᴏɴɢs ɪɴ ᴄʜᴀᴛ ᴏʀ ᴘʟᴀʏʟɪsᴛ ᴛᴏ sᴇᴇᴋ!**", show_alert=True)
        
        played = int(que[0]["played"])
        seek_time = 10
        
        if (played - seek_time) <= 10:
            return await cb.answer("**ᴄᴀɴɴᴏᴛ sᴇᴇᴋ ʙᴇʏᴏɴᴅ 10 sᴇᴄᴏɴᴅs!**", show_alert=True)
        
        to_seek = played - seek_time
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
            return await cb.answer("**sᴏᴍᴇᴛʜɪɴɢ ᴡᴇɴᴛ ᴡʀᴏɴɢ!**", show_alert=True)
        
        Queue.update_duration(cb.message.chat.id, 0, to_seek)
        await cb.message.reply_text(
            f"__sᴇᴇᴋᴇᴅ ʙᴀᴄᴋ ʙʏ {seek_time} sᴇᴄᴏɴᴅs!__ \n\n**ʙʏ:** {cb.from_user.mention}"
        )
    
    elif action == "fseek":
        que = Queue.get_queue(cb.message.chat.id)
        
        if que == []:
            return await cb.answer("**ɴᴏ sᴏɴɢs ɪɴ ᴄʜᴀᴛ ᴏʀ ᴘʟᴀʏʟɪsᴛ ᴛᴏ sᴇᴇᴋ!**", show_alert=True)
        
        played = int(que[0]["played"])
        duration = formatter.mins_to_secs(que[0]["duration"])
        seek_time = 10
        
        if (duration - (played + seek_time)) <= 10:
            return await cb.answer("**ᴄᴀɴɴᴏᴛ sᴇᴇᴋ ʙᴇʏᴏɴᴅ 10 sᴇᴄᴏɴᴅs!**", show_alert=True)
        
        to_seek = played + seek_time
        
        try:
            context = {
                "chat_id": que[0]["chat_id"],
                "file": que[0]["file"],
                "duration": que[0]["duration"],
                "seek": formatter.secs_to_mins(to_seek),
                "video": True if que[0]["vc_type"] == "video" else False,
            }
            await PbxMusic.seek_vc(context)
        
        except:
            return await cb.answer("**sᴏᴍᴇᴛʜɪɴɢ ᴡᴇɴᴛ ᴡʀᴏɴɢ!**", show_alert=True)
        
        Queue.update_duration(cb.message.chat.id, 1, to_seek)
        await cb.message.reply_text(
            f"__sᴇᴇᴋᴇᴅ ꜰᴏʀᴡᴀʀᴅ ʙʏ {seek_time} sᴇᴄᴏɴᴅs!__ \n\n**ʙʏ:** {cb.from_user.mention}"
        )
    
    elif action == "next":
        que = Queue.get_queue(chat_id)
        
        if que == []:
            return await cb.answer("**ɴᴏ sᴏɴɢ ɪs ᴄᴜʀʀᴇɴᴛʟʏ ᴘʟᴀʏɪɴɢ!**", show_alert=True)
        
        video_id = que[0]["video_id"]
        rand_key = formatter.gen_key(str(cb.from_user.id), 5)
        
        track_data = await ytube.get_data(video_id, False, 1)
        
        if not track_data:
            return await cb.answer("**ꜰᴀɪʟᴇᴅ ᴛᴏ ꜰᴇᴛᴄʜ sᴏɴɢ ᴅᴀᴛᴀ!**", show_alert=True)
        
        Config.SONG_CACHE[rand_key] = track_data
        btns = Buttons.speed_bass_markup(chat_id, rand_key)
        
        try:
            await cb.message.edit_reply_markup(InlineKeyboardMarkup(btns))
            await cb.answer("**ʙᴀss, sᴘᴇᴇᴅ & ᴅᴏᴡɴʟᴏᴀᴅ ᴄᴏɴᴛʀᴏʟs**", show_alert=True)
        
        except:
            return
    
    elif action == "controls":
        video_id = "telegram" if not Queue.get_queue(chat_id) else Queue.get_queue(chat_id)[0]["video_id"]
        btns = Buttons.controls_markup(video_id, chat_id)
        
        try:
            await cb.message.edit_reply_markup(InlineKeyboardMarkup(btns))
            await cb.answer("**ʙᴀᴄᴋ ᴛᴏ ᴄᴏɴᴛʀᴏʟs**", show_alert=True)
        
        except:
            return
    
    elif action == "bass":
        bass_level = int(params[0])
        que = Queue.get_queue(cb.message.chat.id)
        
        if que == []:
            return await cb.answer("**ɴᴏ sᴏɴɢs ɪɴ ᴄʜᴀᴛ ᴏʀ ᴘʟᴀʏʟɪsᴛ ᴛᴏ ᴀᴘᴘʟʏ ʙᴀss ʙᴏᴏsᴛ!**", show_alert=True)
        
        Pbx = await cb.message.reply_text("**ᴀᴅᴊᴜsᴛɪɴɢ ʙᴀss ʙᴏᴏsᴛ...**")
        PbxMusic.bass_boost[cb.message.chat.id] = bass_level
        video = True if que[0]["vc_type"] == "video" else False
        file_path = que[0]["file"] if que[0]["file"] == que[0]["video_id"] else await ytube.download(que[0]["video_id"], True, video)
        
        try:
            await PbxMusic.replay_vc(cb.message.chat.id, file_path, video)
            await Pbx.edit_text(
                f"__ʙᴀss ʙᴏᴏsᴛ sᴇᴛ ᴛᴏ:__ `{bass_level}` ʙʏ {cb.from_user.mention}"
            )
            await cb.answer(f"**ʙᴀss sᴇᴛ ᴛᴏ {bass_level}**", show_alert=True)
        
        except Exception as e:
            await Pbx.edit_text(f"**ᴇʀʀᴏʀ ᴀᴘᴘʟʏɪɴɢ ʙᴀss ʙᴏᴏsᴛ:** {e}")
            return await cb.answer("**ᴇʀʀᴏʀ ᴀᴘᴘʟʏɪɴɢ ʙᴀss ʙᴏᴏsᴛ!**", show_alert=True)
    
    elif action == "speed":
        speed = float(params[0])
        que = Queue.get_queue(cb.message.chat.id)
        
        if que == []:
            return await cb.answer("**ɴᴏ sᴏɴɢs ɪɴ ᴄʜᴀᴛ ᴏʀ ᴘʟᴀʏʟɪsᴛ ᴛᴏ ᴀᴅᴊᴜsᴛ sᴘᴇᴇᴅ!**", show_alert=True)
        
        Pbx = await cb.message.reply_text("**ᴀᴅᴊᴜsᴛɪɴɢ ᴘʟᴀʏʙᴀᴄᴋ sᴘᴇᴇᴅ...**")
        PbxMusic.speed[cb.message.chat.id] = speed
        video = True if que[0]["vc_type"] == "video" else False
        file_path = que[0]["file"] if que[0]["file"] == que[0]["video_id"] else await ytube.download(que[0]["video_id"], True, video)
        
        try:
            await PbxMusic.replay_vc(cb.message.chat.id, file_path, video)
            await Pbx.edit_text(
                f"__ᴘʟᴀʏʙᴀᴄᴋ sᴘᴇᴇᴅ sᴇᴛ ᴛᴏ:__ `{speed}x` ʙʏ {cb.from_user.mention}"
            )
            await cb.answer(f"**sᴘᴇᴇᴅ sᴇᴛ ᴛᴏ {speed}x**", show_alert=True)
        
        except Exception as e:
            await Pbx.edit_text(f"**ᴇʀʀᴏʀ ᴀᴅᴊᴜsᴛɪɴɢ sᴘᴇᴇᴅ:** {e}")
            return await cb.answer("**ᴇʀʀᴏʀ ᴀᴅᴊᴜsᴛɪɴɢ sᴘᴇᴇᴅ!**", show_alert=True)


@PbxBot.app.on_callback_query(filters.regex(r"speed") & ~Config.BANNED_USERS)
async def speed_cb(_, cb: CallbackQuery):
    
    _, action, chat_id = cb.data.split("|")
    chat_id = int(chat_id)
    
    if int(chat_id) != cb.message.chat.id:
        return await cb.answer("**ᴛʜɪs ᴍᴇssᴀɢᴇ ɪs ɴᴏᴛ ꜰᴏʀ ᴛʜɪs ᴄʜᴀᴛ!**", show_alert=True)
    
    is_active = await db.is_active_vc(int(chat_id))
    
    if not is_active:
        return await cb.answer("**ᴠᴏɪᴄᴇ ᴄʜᴀᴛ ɪs ɴᴏᴛ ᴀᴄᴛɪᴠᴇ!**", show_alert=True)
    
    is_authchat = await db.is_authchat(cb.message.chat.id)
    
    if not is_authchat:
        if cb.from_user.id not in Config.SUDO_USERS:
            try:
                admins = await get_auth_users(int(chat_id))
            
            except Exception as e:
                return await cb.answer(
                    f"**ᴇʀʀᴏʀ ꜰᴇᴛᴄʜɪɴɢ ᴀᴅᴍɪɴ ʟɪsᴛ:**\n\n{e}",
                    show_alert=True,
                )
            
            if not admins:
                return await cb.answer("**ɴᴇᴇᴅ ᴛᴏ ʀᴇꜰʀᴇsʜ ᴀᴅᴍɪɴ ʟɪsᴛ!**", show_alert=True)
            
            else:
                if cb.from_user.id not in admins:
                    return await cb.answer(
                        "**ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ɪs ᴏɴʟʏ ꜰᴏʀ ᴀᴜᴛʜᴏʀɪᴢᴇᴅ ᴜsᴇʀs ᴀɴᴅ ᴀᴅᴍɪɴs!**",
                        show_alert=True,
                    )
    
    if action == "menu":
        btns = Buttons.speed_menu_markup(chat_id)
        
        try:
            await cb.message.edit_reply_markup(InlineKeyboardMarkup(btns))
            await cb.answer("**sᴘᴇᴇᴅ ᴄᴏɴᴛʀᴏʟs**", show_alert=True)
        
        except:
            return


@PbxBot.app.on_callback_query(filters.regex(r"bass") & ~Config.BANNED_USERS)
async def bass_cb(_, cb: CallbackQuery):
    
    _, action, chat_id = cb.data.split("|")
    chat_id = int(chat_id)
    
    if int(chat_id) != cb.message.chat.id:
        return await cb.answer("**ᴛʜɪs ᴍᴇssᴀɢᴇ ɪs ɴᴏᴛ ꜰᴏʀ ᴛʜɪs ᴄʜᴀᴛ!**", show_alert=True)
    
    is_active = await db.is_active_vc(int(chat_id))
    
    if not is_active:
        return await cb.answer("**ᴠᴏɪᴄᴇ ᴄʜᴀᴛ ɪs ɴᴏᴛ ᴀᴄᴛɪᴠᴇ!**", show_alert=True)
    
    is_authchat = await db.is_authchat(cb.message.chat.id)
    
    if not is_authchat:
        if cb.from_user.id not in Config.SUDO_USERS:
            try:
                admins = await get_auth_users(int(chat_id))
            
            except Exception as e:
                return await cb.answer(
                    f"**ᴇʀʀᴏʀ ꜰᴇᴛᴄʜɪɴɢ ᴀᴅᴍɪɴ ʟɪsᴛ:**\n\n{e}",
                    show_alert=True,
                )
            
            if not admins:
                return await cb.answer("**ɴᴇᴇᴅ ᴛᴏ ʀᴇꜰʀᴇsʜ ᴀᴅᴍɪɴ ʟɪsᴛ!**", show_alert=True)
            
            else:
                if cb.from_user.id not in admins:
                    return await cb.answer(
                        "**ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ɪs ᴏɴʟʏ ꜰᴏʀ ᴀᴜᴛʜᴏʀɪᴢᴇᴅ ᴜsᴇʀs ᴀɴᴅ ᴀᴅᴍɪɴs!**",
                        show_alert=True,
                    )
    
    if action == "menu":
        btns = Buttons.bass_menu_markup(chat_id)
        
        try:
            await cb.message.edit_reply_markup(InlineKeyboardMarkup(btns))
            await cb.answer("**ʙᴀss ᴄᴏɴᴛʀᴏʟs**", show_alert=True)
        
        except:
            return

@PbxBot.app.on_callback_query(filters.regex(r"song_dl") & ~Config.BANNED_USERS)
async def song_cb(_, cb: CallbackQuery):
    
    _, action, key, rand_key = cb.data.split("|")
    user = rand_key.split("_")[0]
    
    if cb.from_user.id != int(user):
        await cb.answer("**ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀʟʟᴏᴡᴇᴅ ᴛᴏ ᴅᴏ ᴛʜᴀᴛ!**", show_alert=True)
        return
    
    try:
        await PbxBot.app.get_chat(cb.from_user.id)
    
    except Exception:
        btns = Buttons.start_markup(PbxBot.app.username)
        await cb.message.reply_text(
            "**ᴘʟᴇᴀsᴇ sᴛᴀʀᴛ ᴛʜᴇ ʙᴏᴛ ꜰɪʀsᴛ ᴛᴏ ᴅᴏᴡɴʟᴏᴀᴅ sᴏɴɢs!**",
            reply_markup=InlineKeyboardMarkup(btns)
        )
        await cb.answer("**sᴛᴀʀᴛ ᴛʜᴇ ʙᴏᴛ ꜰɪʀsᴛ!**", show_alert=True)
        return
    
    track_data = Config.SONG_CACHE.get(rand_key)
    
    if not track_data or len(track_data) == 0:
        await cb.answer("**sᴏɴɢ ᴅᴀᴛᴀ ɴᴏᴛ ꜰᴏᴜɴᴅ! ᴘʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ.**", show_alert=True)
        return
    
    if action == "menu":
        if key < 0 or key >= len(track_data):
            key = 0  # Reset to 0 if key is out of bounds
        
        if not isinstance(track_data[key], dict) or "link" not in track_data[key]:
            await cb.answer("**ɪɴᴠᴀʟɪᴅ sᴏɴɢ ᴅᴀᴛᴀ! ᴘʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ.**", show_alert=True)
            return
        
        url = track_data[key]["link"]
        btns = Buttons.song_markup(rand_key, url, key)
        
        try:
            await cb.message.edit_reply_markup(InlineKeyboardMarkup(btns))
            await cb.answer("**ᴅᴏᴡɴʟᴏᴀᴅ ᴍᴇɴᴜ**", show_alert=True)
        
        except:
            return
    
    elif action == "adl":
        await ytube.send_song(cb, rand_key, key, False)
        # Return to speed_bass_markup after downloading audio
        que = Queue.get_queue(int(rand_key.split("_")[1]))
        
        if que:
            video_id = que[0]["video_id"]
            track_data = await ytube.get_data(video_id, False, 1)
            
            if track_data:
                Config.SONG_CACHE[rand_key] = track_data
                btns = Buttons.speed_bass_markup(int(rand_key.split("_")[1]), rand_key)
                
                try:
                    await cb.message.edit_reply_markup(InlineKeyboardMarkup(btns))
                    await cb.answer("**ᴀᴜᴅɪᴏ ᴅᴏᴡɴʟᴏᴀᴅᴇᴅ! ʙᴀᴄᴋ ᴛᴏ ᴄᴏɴᴛʀᴏʟs.**", show_alert=True)
                
                except:
                    return
        
        else:
            await cb.answer("**ᴄʜᴀᴛ ᴏʀ ᴘʟᴀʏʟɪsᴛ ɪs ᴇᴍᴘᴛʏ, ᴄᴀɴɴᴏᴛ ʀᴇᴛᴜʀɴ ᴛᴏ ᴄᴏɴᴛʀᴏʟs!**", show_alert=True)
    
    elif action == "vdl":
        await ytube.send_song(cb, rand_key, key, True)
        # Return to speed_bass_markup after downloading video
        que = Queue.get_queue(int(rand_key.split("_")[1]))
        
        if que:
            video_id = que[0]["video_id"]
            track_data = await ytube.get_data(video_id, False, 1)
            
            if track_data:
                Config.SONG_CACHE[rand_key] = track_data
                btns = Buttons.speed_bass_markup(int(rand_key.split("_")[1]), rand_key)
                
                try:
                    await cb.message.edit_reply_markup(InlineKeyboardMarkup(btns))
                    await cb.answer("**ᴠɪᴅᴇᴏ ᴅᴏᴡɴʟᴏᴀᴅᴇᴅ! ʙᴀᴄᴋ ᴛᴏ ᴄᴏɴᴛʀᴏʟs.**", show_alert=True)
                
                except:
                    return
        
        else:
            await cb.answer("**ᴄʜᴀᴛ ᴏʀ ᴘʟᴀʏʟɪsᴛ ɪs ᴇᴍᴘᴛʏ, ᴄᴀɴɴᴏᴛ ʀᴇᴛᴜʀɴ ᴛᴏ ᴄᴏɴᴛʀᴏʟs!**", show_alert=True)
    
    elif action == "prev":
        if key < 0 or key >= len(track_data):
            key = 0  # Reset to 0 if key is out of bounds
        
        new_key = max(0, key - 1)
        
        if not isinstance(track_data[new_key], dict) or "link" not in track_data[new_key]:
            await cb.answer("**ɪɴᴠᴀʟɪᴅ sᴏɴɢ ᴅᴀᴛᴀ! ᴘʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ.**", show_alert=True)
            return
        
        url = track_data[new_key]["link"]
        btns = Buttons.song_markup(rand_key, url, new_key)
        
        try:
            await cb.message.edit_reply_markup(InlineKeyboardMarkup(btns))
            await cb.answer("**ᴘʀᴇᴠɪᴏᴜs sᴏɴɢ**", show_alert=True)
        
        except:
            return
    
    elif action == "next":
        if key < 0 or key >= len(track_data):
            key = 0  # Reset to 0 if key is out of bounds
        
        new_key = min(len(track_data) - 1, key + 1)
        
        if not isinstance(track_data[new_key], dict) or "link" not in track_data[new_key]:
            await cb.answer("**ɪɴᴠᴀʟɪᴅ sᴏɴɢ ᴅᴀᴛᴀ! ᴘʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ.**", show_alert=True)
            return
        
        url = track_data[new_key]["link"]
        btns = Buttons.song_markup(rand_key, url, new_key)
        
        try:
            await cb.message.edit_reply_markup(InlineKeyboardMarkup(btns))
            await cb.answer("**ɴᴇxᴛ sᴏɴɢ**", show_alert=True)
        
        except:
            return
    
    elif action == "close":
        Config.SONG_CACHE.pop(rand_key, None)
        await cb.message.delete()
        return
        
@PbxBot.app.on_callback_query(filters.regex(r"help") & ~Config.BANNED_USERS)
async def help_cb(_, cb: CallbackQuery):
    data = cb.data.split("|")[1]
    if data == "admin":
        return await cb.message.edit_text(
            TEXTS.HELP_ADMIN, reply_markup=InlineKeyboardMarkup(Buttons.help_back())
        )
    elif data == "user":
        return await cb.message.edit_text(
            TEXTS.HELP_USER, reply_markup=InlineKeyboardMarkup(Buttons.help_back())
        )
    elif data == "sudo":
        return await cb.message.edit_text(
            TEXTS.HELP_SUDO, reply_markup=InlineKeyboardMarkup(Buttons.help_back())
        )
    elif data == "others":
        return await cb.message.edit_text(
            TEXTS.HELP_OTHERS, reply_markup=InlineKeyboardMarkup(Buttons.help_back())
        )
    elif data == "owner":
        return await cb.message.edit_text(
            TEXTS.HELP_OWNERS, reply_markup=InlineKeyboardMarkup(Buttons.help_back())
        )
    elif data == "back":
        return await cb.message.edit_text(
            TEXTS.HELP_PM.format(PbxBot.app.mention),
            reply_markup=InlineKeyboardMarkup(Buttons.help_pm_markup()),
        )
    elif data == "start":
        return await cb.message.edit_text(
            TEXTS.START_PM.format(
                cb.from_user.first_name,
                PbxBot.app.mention,
                PbxBot.app.username,
            ),
            reply_markup=InlineKeyboardMarkup(Buttons.start_pm_markup(PbxBot.app.username)),
            disable_web_page_preview=True,
        )


@PbxBot.app.on_callback_query(filters.regex(r"source") & ~Config.BANNED_USERS)
async def source_cb(_, cb: CallbackQuery):
    await cb.message.edit_text(
        TEXTS.SOURCE.format(PbxBot.app.mention),
        reply_markup=InlineKeyboardMarkup(Buttons.source_markup()),
        disable_web_page_preview=True,
    )
