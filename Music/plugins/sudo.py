import asyncio
import os
import shutil

from pyrogram import filters
from pyrogram.errors import FloodWait
from pyrogram.types import Message

from config import Config
from Music.core.calls import PbxMusic
from Music.core.clients import PbxBot
from Music.core.database import db
from Music.core.decorators import UserWrapper
from Music.core.users import user_data
from Music.helpers.broadcast import Gcast
from Music.helpers.formatters import formatter


@PbxBot.app.on_message(filters.command("autoend") & Config.SUDO_USERS)
@UserWrapper
async def auto_end_stream(_, message: Message):
    
    if len(message.command) != 2:
        return await message.reply_text(
            "**ᴜsᴀɢᴇ:**\n\n__ᴛᴏ ᴛᴜʀɴ ᴏꜰꜰ ᴀᴜᴛᴏᴇɴᴅ:__ `/autoend off`\n__ᴛᴏ ᴛᴜʀɴ ᴏɴ ᴀᴜᴛᴏᴇɴᴅ:__ `/autoend on`"
        )
    
    cmd = message.command[1].lower()
    autoend = await db.get_autoend()
    
    if cmd == "on":
        if autoend:
            await message.reply_text("**ᴀᴜᴛᴏᴇɴᴅ ɪs ᴀʟʀᴇᴀᴅʏ ᴇɴᴀʙʟᴇᴅ.**")
        else:
            await db.set_autoend(True)
            await message.reply_text(
                "**ᴀᴜᴛᴏᴇɴᴅ ᴇɴᴀʙʟᴇᴅ!** ᴛʜᴇ ʙᴏᴛ ᴡɪʟʟ ɴᴏᴡ ᴇɴᴅ ᴛʜᴇ sᴛʀᴇᴀᴍ ᴀꜰᴛᴇʀ 5 ᴍɪɴᴜᴛᴇs ᴡʜᴇɴ ᴛʜᴇ ᴠᴄ ɪs ᴇᴍᴘᴛʏ."
            )
    
    elif cmd == "off":
        if autoend:
            await db.set_autoend(False)
            await message.reply_text("**ᴀᴜᴛᴏᴇɴᴅ ᴅɪsᴀʙʟᴇᴅ!**")
        else:
            await message.reply_text("**ᴀᴜᴛᴏᴇɴᴅ ɪs ᴀʟʀᴇᴀᴅʏ ᴅɪsᴀʙʟᴇᴅ.**")
    
    else:
        await message.reply_text(
            "**ᴜsᴀɢᴇ:**\n\n__ᴛᴏ ᴛᴜʀɴ ᴏꜰꜰ ᴀᴜᴛᴏᴇɴᴅ:__ `/autoend off`\n__ᴛᴏ ᴛᴜʀɴ ᴏɴ ᴀᴜᴛᴏᴇɴᴅ:__ `/autoend on`"
        )


@PbxBot.app.on_message(filters.command(["gban", "block"]) & Config.SUDO_USERS)
@UserWrapper
async def gban(_, message: Message):
    
    if not message.reply_to_message:
        if len(message.command) != 2:
            return await message.reply_text(
                "**ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴜsᴇʀ's ᴍᴇssᴀɢᴇ ᴏʀ ɢɪᴠᴇ ᴛʜᴇɪʀ ɪᴅ.**"
            )
        user = await PbxBot.app.get_users(message.command[1])
        user_id = user.id
        mention = user.mention
    
    else:
        user_id = message.reply_to_message.from_user.id
        mention = message.reply_to_message.from_user.mention
    
    if user_id == message.from_user.id:
        return await message.reply_text(f"**ʏᴏᴜ ᴄᴀɴ'ᴛ {message.command[0]} ʏᴏᴜʀsᴇʟꜰ.**")
    
    elif user_id == PbxBot.app.id:
        return await message.reply_text(
            f"**ʏᴏ! ɪ'ᴍ ɴᴏᴛ sᴛᴜᴘɪᴅ ᴇɴᴏᴜɢʜ ᴛᴏ {message.command[0]} ᴍʏsᴇʟꜰ.**"
        )
    
    elif user_id in Config.SUDO_USERS:
        return await message.reply_text(f"**ɪ ᴄᴀɴ'ᴛ {message.command[0]} ᴍʏ sᴜᴅᴏ ᴜsᴇʀs.**")
    
    is_gbanned = await db.is_gbanned_user(user_id)
    
    if is_gbanned:
        return await message.reply_text(
            f"**{mention} ɪs ᴀʟʀᴇᴀᴅʏ ɪɴ {message.command[0]} ʟɪsᴛ.**"
        )
    
    if user_id not in Config.BANNED_USERS:
        Config.BANNED_USERS.add(user_id)
    
    if message.command[0] == "gban":
        all_chats = []
        chats = await db.get_all_chats()
        async for chat in chats:
            all_chats.append(int(chat["chat_id"]))
        
        eta = formatter.get_readable_time(len(all_chats))
        Pbx = await message.reply_text(
            f"**{mention} ɪs ʙᴇɪɴɢ ɢʙᴀɴɴᴇᴅ ʙʏ ᴛʜᴇ ʙᴏᴛ. ᴛʜɪs ᴍɪɢʜᴛ ᴛᴀᴋᴇ ᴀʙᴏᴜᴛ {eta}.**"
        )
        
        count = 0
        for chat_id in all_chats:
            try:
                await PbxBot.app.ban_chat_member(chat_id, user_id)
                count += 1
            except FloodWait as e:
                await asyncio.sleep(int(e.x))
            except Exception:
                pass
        
        await db.add_gbanned_user(user_id)
        await message.reply_text(
            f"**ɢʙᴀɴɴᴇᴅ sᴜᴄᴄᴇssꜰᴜʟʟʏ!**\n\n**ᴜsᴇʀ:** {mention}\n**ᴄʜᴀᴛs:** `{count} ᴄʜᴀᴛs`"
        )
        await Pbx.delete()
    
    else:
        await db.add_blocked_user(user_id)
        await message.reply_text(f"**ʙʟᴏᴄᴋᴇᴅ sᴜᴄᴄᴇssꜰᴜʟʟʏ!**\n\n**ᴜsᴇʀ:** {mention}")


@PbxBot.app.on_message(filters.command(["ungban", "unblock"]) & Config.SUDO_USERS)
@UserWrapper
async def gungabn(_, message: Message):
    
    if not message.reply_to_message:
        if len(message.command) != 2:
            return await message.reply_text(
                "**ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴜsᴇʀ's ᴍᴇssᴀɢᴇ ᴏʀ ɢɪᴠᴇ ᴛʜᴇɪʀ ɪᴅ.**"
            )
        user = await PbxBot.app.get_users(message.command[1])
        user_id = user.id
        mention = user.mention
    
    else:
        user_id = message.reply_to_message.from_user.id
        mention = message.reply_to_message.from_user.mention
    
    is_gbanned = await db.is_gbanned_user(user_id)
    
    if not is_gbanned:
        return await message.reply_text(
            f"**{mention} ɪs ɴᴏᴛ ɪɴ {message.command[0][2:]} ʟɪsᴛ.**"
        )
    
    if user_id in Config.BANNED_USERS:
        Config.BANNED_USERS.remove(user_id)
    
    if message.command[0] == "ungban":
        all_chats = []
        chats = await db.get_all_chats()
        async for chat in chats:
            all_chats.append(int(chat["chat_id"]))
        
        eta = formatter.get_readable_time(len(all_chats))
        Pbx = await message.reply_text(
            f"**{mention} ɪs ʙᴇɪɴɢ ᴜɴɢʙᴀɴɴᴇᴅ ʙʏ ᴛʜᴇ ʙᴏᴛ. ᴛʜɪs ᴍɪɢʜᴛ ᴛᴀᴋᴇ ᴀʙᴏᴜᴛ {eta}.**"
        )
        
        count = 0
        for chat_id in all_chats:
            try:
                await PbxBot.app.unban_chat_member(chat_id, user_id)
                count += 1
            except FloodWait as e:
                await asyncio.sleep(int(e.x))
            except Exception:
                pass
        
        await db.remove_gbanned_users(user_id)
        await message.reply_text(
            f"**ᴜɴɢʙᴀɴɴᴇᴅ sᴜᴄᴄᴇssꜰᴜʟʟʏ!**\n\n**ᴜsᴇʀ:** {mention}\n**ᴄʜᴀᴛs:** `{count}`"
        )
        await Pbx.delete()
    
    else:
        await db.remove_blocked_user(user_id)
        await message.reply_text(f"**ᴜɴʙʟᴏᴄᴋᴇᴅ sᴜᴄᴄᴇssꜰᴜʟʟʏ!**\n\n**ᴜsᴇʀ:** {mention}")


@PbxBot.app.on_message(filters.command(["gbanlist", "blocklist"]) & Config.SUDO_USERS)
@UserWrapper
async def gbanned_list(_, message: Message):
    
    if message.command[0] == "gbanlist":
        users = await db.get_gbanned_users()
        if len(users) == 0:
            return await message.reply_text("**ɴᴏ ɢʙᴀɴɴᴇᴅ ᴜsᴇʀs ꜰᴏᴜɴᴅ!**")
        Pbx = await message.reply_text("**ꜰᴇᴛᴄʜɪɴɢ ɢʙᴀɴɴᴇᴅ ᴜsᴇʀs...**")
        msg = "**ɢʙᴀɴɴᴇᴅ ᴜsᴇʀs:**\n\n"
    
    else:
        users = await db.get_blocked_users()
        if len(users) == 0:
            return await message.reply_text("**ɴᴏ ʙʟᴏᴄᴋᴇᴅ ᴜsᴇʀs ꜰᴏᴜɴᴅ!**")
        Pbx = await message.reply_text("**ꜰᴇᴛᴄʜɪɴɢ ʙʟᴏᴄᴋᴇᴅ ᴜsᴇʀs...**")
        msg = "**ʙʟᴏᴄᴋᴇᴅ ᴜsᴇʀs:**\n\n"
    
    count = 0
    for user_id in users:
        count += 1
        try:
            user = await PbxBot.app.get_users(user_id)
            user = user.first_name if not user.mention else user.mention
            msg += f"{'0' if count <= 9 else ''}{count}: {user} `{user_id}`\n"
        except Exception:
            msg += f"{'0' if count <= 9 else ''}{count}: [ᴜsᴇʀ] `{user_id}`\n"
            continue
    
    if count == 0:
        return await Pbx.edit_text(f"**ɴᴏʙᴏᴅʏ ɪs ɪɴ {message.command[0]}!**")
    
    else:
        return await Pbx.edit_text(msg)


@PbxBot.app.on_message(filters.command("loggs") & Config.SUDO_USERS)
@UserWrapper
async def log_(_, message: Message):
    
    try:
        if os.path.exists("PbxMusic.log"):
            log = open("PbxMusic.log", "r")
            lines = log.readlines()
            logdata = ""
            try:
                limit = int(message.text.split(None, 1)[1])
            except:
                limit = 100
            
            for x in lines[-limit:]:
                logdata += x
            
            link = await formatter.bb_paste(logdata)
            return await message.reply_document(
                "PbxMusic.log",
                caption=f"**ʟᴏɢs:** {link}",
            )
        
        else:
            return await message.reply_text("**ɴᴏ ʟᴏɢs ꜰᴏᴜɴᴅ!**")
    
    except Exception as e:
        await message.reply_text(f"**ᴇʀʀᴏʀ:** \n\n`{e}`")




@PbxBot.app.on_message(filters.command("sudolist") & Config.SUDO_USERS)
@UserWrapper
async def sudoers_list(_, message: Message):
    
    text = "**⍟ ɢᴏᴅ ᴜsᴇʀs:**\n"
    gods = 0
    
    for x in Config.GOD_USERS:
        try:
            if x in user_data.DEVS:
                continue
            user = await PbxBot.app.get_users(x)
            user = user.first_name if not user.mention else user.mention
            gods += 1
        except Exception:
            continue
        text += f"{'0' if gods <= 9 else ''}{gods}: {user}\n"
    
    sudos = 0
    for user_id in Config.SUDO_USERS:
        if user_id not in user_data.DEVS:
            if user_id in Config.GOD_USERS:
                continue
            try:
                user = await PbxBot.app.get_users(user_id)
                user = user.first_name if not user.mention else user.mention
                if sudos == 0:
                    sudos += 1
                    text += "\n**⍟ sᴜᴅᴏ ᴜsᴇʀs:**\n"
                gods += 1
                text += f"{'0' if gods <= 9 else ''}{gods}: {user}\n"
            except Exception:
                continue
    
    if gods == 0:
        await message.reply_text("**ɴᴏ sᴜᴅᴏ ᴜsᴇʀs ꜰᴏᴜɴᴅ.**")
    
    else:
        await message.reply_text(text)


@PbxBot.app.on_message(filters.command("gcast") & Config.SUDO_USERS)
async def gcast(_, message: Message):
    
    if message.reply_to_message is None:
        await message.reply_text("**ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ ᴛᴏ ʙʀᴏᴀᴅᴄᴀsᴛ ɪᴛ.**")
    
    else:
        if len(message.command) == 1:
            await message.reply_text(
                "**ᴡʜᴇʀᴇ ᴛᴏ ɢᴄᴀsᴛ?** \n\n"
                "**ᴡɪᴛʜ ꜰᴏʀᴡᴀʀᴅ ᴛᴀɢ:** `/gcast chats` \n- `/gcast users` \n- `/gcast all`\n\n"
                "**ᴡɪᴛʜᴏᴜᴛ ꜰᴏʀᴡᴀʀᴅ ᴛᴀɢ:** `/gcast chats copy` \n- `/gcast users copy` \n- `/gcast all copy`"
            )
            return
        
        _list = message.text.split(" ")
        if (_list[1]).lower() == "chats":
            type = "chats"
        elif (_list[1]).lower() == "users":
            type = "users"
        elif (_list[1]).lower() == "all":
            type = "all"
        
        copy = False
        if len(_list) >= 3:
            if (_list[2]).lower() == "copy":
                copy = True
        
        await Gcast.broadcast(message, type, copy)
