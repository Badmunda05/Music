import asyncio
import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pyrogram import filters
from pyrogram.types import Message
from pytgcalls.types import JoinedGroupCallParticipant, LeftGroupCallParticipant, Update
from pytgcalls.types.stream import StreamAudioEnded

from config import Config
from Music.core.calls import PbxMusic
from Music.core.clients import PbxBot
from Music.core.database import db
from Music.core.logger import LOGS
from Music.helpers.buttons import Buttons
from Music.utils.leaderboard import leaders
from Music.utils.queue import Queue


@PbxBot.app.on_message(filters.private, group=2)
async def new_users(_, msg: Message):
    
    chat_id = msg.from_user.id
    user_name = msg.from_user.first_name
    
    if not await db.is_user_exist(chat_id):
        BOT_USERNAME = PbxBot.app.username
        await db.add_user(chat_id, user_name)
        
        if Config.LOGGER_ID:
            await PbxBot.logit(
                "newuser",
                f"**⤷ ᴜsᴇʀ:** {msg.from_user.mention(style='md')}\n**⤷ ɪᴅ:** `{chat_id}`\n__⤷ sᴛᴀʀᴛᴇᴅ @{BOT_USERNAME} !!__",
            )
        else:
            LOGS.info(f"#ɴᴇᴡᴜsᴇʀ: \n\nɴᴀᴍᴇ: {user_name} \nɪᴅ: {chat_id}")
    
    else:
        try:
            await db.update_user(chat_id, "user_name", user_name)
        except:
            pass
    
    await msg.continue_propagation()


@PbxBot.app.on_message(filters.group, group=3)
async def new_chats(_, msg: Message):
    
    chat_id = msg.chat.id
    
    if not await db.is_chat_exist(chat_id):
        BOT_USERNAME = PbxBot.app.username
        await db.add_chat(chat_id)
        
        if Config.LOGGER_ID:
            await PbxBot.logit(
                "newchat",
                f"**⤷ ᴄʜᴀᴛ ᴛɪᴛʟᴇ:** {msg.chat.title} \n**⤷ ᴄʜᴀᴛ ᴜɴ:** @{msg.chat.username or None} \n**⤷ ᴄʜᴀᴛ ɪᴅ:** `{chat_id}` \n__⤷ ᴀᴅᴅᴇᴅ @{BOT_USERNAME} !!__",
            )
        else:
            LOGS.info(
                f"#ɴᴇᴡᴄʜᴀᴛ: \n\nᴄʜᴀᴛ ᴛɪᴛʟᴇ: {msg.chat.title} \nᴄʜᴀᴛ ᴜɴ: @{msg.chat.username} \nᴄʜᴀᴛ ɪᴅ: {chat_id} \n\nᴀᴅᴅᴇᴅ @{BOT_USERNAME} !!",
            )
    
    await msg.continue_propagation()


@PbxBot.app.on_message(filters.video_chat_ended, group=4)
async def vc_end(_, msg: Message):
    
    chat_id = msg.chat.id
    
    try:
        await PbxMusic.leave_vc(chat_id)
        await db.set_loop(chat_id, 0)
    except:
        pass
    
    await msg.continue_propagation()


@PbxMusic.music.on_kicked()
@PbxMusic.music.on_left()
async def end_streaming(_, chat_id: int):
    
    await PbxMusic.leave_vc(chat_id)
    await db.set_loop(chat_id, 0)


@PbxMusic.music.on_stream_end()
async def changed(_, update: Update):
    
    if isinstance(update, StreamAudioEnded):
        await PbxMusic.change_vc(update.chat_id)


@PbxMusic.music.on_participants_change()
async def members_change(_, update: Update):
    
    if not isinstance(update, JoinedGroupCallParticipant) and not isinstance(
        update, LeftGroupCallParticipant
    ):
        return
    
    try:
        chat_id = update.chat_id
        audience = PbxMusic.audience.get(chat_id)
        users = await PbxMusic.vc_participants(chat_id)
        user_ids = [user.user_id for user in users]
        
        if not audience:
            await PbxMusic.autoend(chat_id, user_ids)
        
        else:
            new = (
                audience + 1
                if isinstance(update, JoinedGroupCallParticipant)
                else audience - 1
            )
            PbxMusic.audience[chat_id] = new
            await PbxMusic.autoend(chat_id, user_ids)
    
    except:
        return


async def update_played():
    
    while not await asyncio.sleep(1):
        active_chats = await db.get_active_vc()
        
        for x in active_chats:
            chat_id = int(x["chat_id"])
            
            if chat_id == 0:
                continue
            
            is_paused = await db.get_watcher(chat_id, "pause")
            
            if is_paused:
                continue
            
            que = Queue.get_queue(chat_id)
            
            if que == []:
                continue
            
            Queue.update_duration(chat_id, 1, 1)


asyncio.create_task(update_played())


async def end_inactive_vc():
    
    while not await asyncio.sleep(10):
        for chat_id in db.inactive:
            dur = db.inactive.get(chat_id)
            
            if dur == {}:
                continue
            
            if datetime.datetime.now() > dur:
                if not await db.is_active_vc(chat_id):
                    db.inactive[chat_id] = {}
                    continue
                
                db.inactive[chat_id] = {}
                
                try:
                    await PbxMusic.leave_vc(chat_id)
                except:
                    continue
                
                try:
                    await PbxBot.app.send_message(
                        chat_id,
                        "⚡ **ɪɴᴀᴄᴛɪᴠᴇ ᴠᴄ:** sᴛʀᴇᴀᴍɪɴɢ ʜᴀs ʙᴇᴇɴ sᴛᴏᴘᴘᴇᴅ!",
                    )
                except:
                    continue


asyncio.create_task(end_inactive_vc())


async def leaderboard():
    
    context = {
        "mention": PbxBot.app.mention,
        "username": PbxBot.app.username,
        "client": PbxBot.app,
    }
    
    text = await leaders.generate(context)
    btns = Buttons.close_markup()
    
    await leaders.broadcast(PbxBot, text, btns)


hrs = leaders.get_hrs()
min = leaders.get_min()

scheduler = AsyncIOScheduler()
scheduler.add_job(leaderboard, "cron", hour=hrs, minute=min, timezone=Config.TZ)
scheduler.start()
