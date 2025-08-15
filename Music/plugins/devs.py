import asyncio
import io
import os
import re
import shutil
import socket
import subprocess
import sys
import traceback
import logging
from datetime import datetime

import aiohttp
from git import Repo
from git.exc import GitCommandError, InvalidGitRepositoryError
from pyrogram import filters
from pyrogram.types import Message
from pyrogram.errors import MessageDeleteForbidden

from config import Config, all_vars
from Music.core.clients import PbxBot
from Music.core.database import db


# Configure logging
logging.basicConfig(
    filename="bot.log",
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

BASE = "https://batbin.me/"


async def post(url: str, *args, **kwargs):
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, *args, **kwargs) as resp:
            try:
                data = await resp.json()
            except Exception:
                data = await resp.text()
            return data


async def BadBin(text):
    
    resp = await post(f"{BASE}api/v2/paste", data=text)
    
    if not resp["success"]:
        return None
    
    link = BASE + resp["message"]
    return link


async def aexec(code, client, message):
    
    exec(
        "async def __aexec(client, message): "
        + "".join(f"\n {l_}" for l_ in code.split("\n"))
    )
    return await locals()["__aexec"](client, message)


@PbxBot.app.on_message(filters.command(["eval", "run"]) & Config.GOD_USERS)
async def eval(_, message: Message):
    
    try:
        await message.delete()
    
    except MessageDeleteForbidden:
        logger.warning("**ꜰᴀɪʟᴇᴅ ᴛᴏ ᴅᴇʟᴇᴛᴇ ᴇᴠᴀʟ ᴄᴏᴍᴍᴀɴᴅ ᴍᴇssᴀɢᴇ**")
    
    Pbx = await message.reply_text("**ᴘʀᴏᴄᴇssɪɴɢ...**")
    lists = message.text.split(" ", 1)
    
    if len(lists) != 2:
        return await Pbx.edit_text("**ʀᴇᴄᴇɪᴠᴇᴅ ᴇᴍᴘᴛʏ ᴍᴇssᴀɢᴇ!**")
    
    cmd = lists[1].strip()
    reply_to = message.reply_to_message or message
    
    old_stderr = sys.stderr
    old_stdout = sys.stdout
    redirected_output = sys.stdout = io.StringIO()
    redirected_error = sys.stderr = io.StringIO()
    stdout, stderr, exc = None, None, None
    
    try:
        await aexec(cmd, PbxBot, message)
    
    except Exception:
        exc = traceback.format_exc()
    
    stdout = redirected_output.getvalue()
    stderr = redirected_error.getvalue()
    sys.stdout = old_stdout
    sys.stderr = old_stderr
    evaluation = ""
    
    if exc:
        evaluation = exc
    elif stderr:
        evaluation = stderr
    elif stdout:
        evaluation = stdout
    else:
        evaluation = "Success"
    
    final_output = "<b>ᴇᴠᴀʟ</b>: "
    final_output += f"<code>{cmd}</code>\n\n"
    final_output += "<b>ᴏᴜᴛᴘᴜᴛ</b>:\n"
    final_output += f"<code>{evaluation.strip()}</code> \n"
    
    if len(final_output) > 4096:
        with io.BytesIO(str.encode(final_output)) as out_file:
            out_file.name = "eval.txt"
            await reply_to.reply_document(
                document=out_file, caption=cmd[:1000], disable_notification=True
            )
    
    else:
        await reply_to.reply_text(final_output)
    
    await Pbx.delete()


@PbxBot.app.on_message(
    filters.command(["exec", "term", "sh", "shh"]) & Config.GOD_USERS
)
async def term(_, message: Message):
    
    try:
        await message.delete()
    
    except MessageDeleteForbidden:
        logger.warning("**ꜰᴀɪʟᴇᴅ ᴛᴏ ᴅᴇʟᴇᴛᴇ ᴛᴇʀᴍ ᴄᴏᴍᴍᴀɴᴅ ᴍᴇssᴀɢᴇ**")
    
    Pbx = await message.reply_text("**ᴘʀᴏᴄᴇssɪɴɢ...**")
    lists = message.text.split(" ", 1)
    
    if len(lists) != 2:
        return await Pbx.edit_text("**ʀᴇᴄᴇɪᴠᴇᴅ ᴇᴍᴘᴛʏ ᴍᴇssᴀɢᴇ!**")
    
    cmd = lists[1].strip()
    
    if "\n" in cmd:
        code = cmd.split("\n")
        output = ""
        
        for x in code:
            sPbx = re.split(""" (?=(?:[^'"]|'[^']*'|"[^"]*")*$)""", x)
            
            try:
                process = subprocess.Popen(
                    sPbx, stdout=subprocess.PIPE, stderr=subprocess.PIPE
                )
            
            except Exception as err:
                logger.error(f"Term command error: {err}")
                await Pbx.edit(f"**ᴇʀʀᴏʀ:** \n`{err}`")
            
            output += f"**{code}**\n"
            output += process.stdout.read()[:-1].decode("utf-8")
            output += "\n"
    
    else:
        sPbx = re.split(""" (?=(?:[^'"]|'[^']*'|"[^"]*")*$)""", cmd)
        
        for a in range(len(sPbx)):
            sPbx[a] = sPbx[a].replace('"', "")
        
        try:
            process = subprocess.Popen(
                sPbx, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
        
        except Exception as err:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            errors = traceback.format_exception(exc_type, exc_obj, exc_tb)
            logger.error(f"Term command error: {errors}")
            await Pbx.edit("**ᴇʀʀᴏʀ:**\n`{}`".format("".join(errors)))
            return
        
        output = process.stdout.read()[:-1].decode("utf-8")
    
    if str(output) == "\n":
        output = None
    
    if output:
        if len(output) > 4096:
            filename = "output.txt"
            with open(filename, "w+") as file:
                file.write(output)
            
            await message.reply_document(
                filename,
                caption=f"`{cmd}`",
            )
            os.remove(filename)
            return
        
        await Pbx.edit(f"**ᴏᴜᴛᴘᴜᴛ:**\n`{output}`")
    
    else:
        await Pbx.edit("**ᴏᴜᴛᴘᴜᴛ:**\n`ɴᴏ ᴏᴜᴛᴘᴜᴛ`")


@PbxBot.app.on_message(filters.command(["getvar", "gvar", "var"]) & Config.GOD_USERS)
async def varget_(_, message: Message):
    
    try:
        await message.delete()
    
    except MessageDeleteForbidden:
        logger.warning("**ꜰᴀɪʟᴇᴅ ᴛᴏ ᴅᴇʟᴇᴛᴇ ɢᴇᴛᴠᴀʀ ᴄᴏᴍᴍᴀɴᴅ ᴍᴇssᴀɢᴇ**")
    
    if len(message.command) != 2:
        return await message.reply_text("**ɢɪᴠᴇ ᴀ ᴠᴀʀɪᴀʙʟᴇ ɴᴀᴍᴇ ᴛᴏ ɢᴇᴛ ɪᴛs ᴠᴀʟᴜᴇ.**")
    
    check_var = message.text.split(None, 2)[1]
    
    if check_var.upper() not in all_vars:
        return await message.reply_text("**ɢɪᴠᴇ ᴀ ᴠᴀʟɪᴅ ᴠᴀʀɪᴀʙʟᴇ ɴᴀᴍᴇ ᴛᴏ ɢᴇᴛ ɪᴛs ᴠᴀʟᴜᴇ.**")
    
    output = Config.__dict__[check_var.upper()]
    
    if not output:
        await message.reply_text("**ɴᴏ ᴏᴜᴛᴘᴜᴛ ꜰᴏᴜɴᴅ!**")
    
    else:
        return await message.reply_text(f"**{check_var}:** `{str(output)}`")


@PbxBot.app.on_message(filters.command("addsudo") & Config.GOD_USERS)
async def useradd(_, message: Message):
    
    try:
        await message.delete()
    
    except MessageDeleteForbidden:
        logger.warning("**ꜰᴀɪʟᴇᴅ ᴛᴏ ᴅᴇʟᴇᴛᴇ ᴀᴅᴅsᴜᴅᴏ ᴄᴏᴍᴍᴀɴᴅ ᴍᴇssᴀɢᴇ**")
    
    if not message.reply_to_message:
        if len(message.command) != 2:
            return await message.reply_text(
                "**ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴜsᴇʀ ᴏʀ ɢɪᴠᴇ ᴀ ᴜsᴇʀ ɪᴅ ᴛᴏ ᴀᴅᴅ ᴛʜᴇᴍ ᴀs sᴜᴅᴏ.**"
            )
        
        user = message.text.split(None, 1)[1]
        
        if "@" in user:
            user = user.replace("@", "")
        
        user = await PbxBot.app.get_users(user)
        
        if user.id in Config.SUDO_USERS:
            return await message.reply_text(f"{user.mention} **ɪs ᴀʟʀᴇᴀᴅʏ ᴀ sᴜᴅᴏ ᴜsᴇʀ.**")
        
        added = await db.add_sudo(user.id)
        
        if added:
            Config.SUDO_USERS.add(user.id)
            await message.reply_text(f"{user.mention} **ɪs ɴᴏᴡ ᴀ sᴜᴅᴏ ᴜsᴇʀ.**")
        
        else:
            await message.reply_text("**ꜰᴀɪʟᴇᴅ ᴛᴏ ᴀᴅᴅ sᴜᴅᴏ ᴜsᴇʀ.**")
        
        return
    
    if message.reply_to_message.from_user.id in Config.SUDO_USERS:
        return await message.reply_text(
            f"{message.reply_to_message.from_user.mention} **ɪs ᴀʟʀᴇᴀᴅʏ ᴀ sᴜᴅᴏ ᴜsᴇʀ.**"
        )
    
    added = await db.add_sudo(message.reply_to_message.from_user.id)
    
    if added:
        Config.SUDO_USERS.add(message.reply_to_message.from_user.id)
        await message.reply_text(
            f"{message.reply_to_message.from_user.mention} **ɪs ɴᴏᴡ ᴀ sᴜᴅᴏ ᴜsᴇʀ.**"
        )
    
    else:
        await message.reply_text("**ꜰᴀɪʟᴇᴅ ᴛᴏ ᴀᴅᴅ sᴜᴅᴏ ᴜsᴇʀ.**")


@PbxBot.app.on_message(filters.command(["delsudo", "rmsudo"]) & Config.GOD_USERS)
async def userdel(_, message: Message):
    
    try:
        await message.delete()
    
    except MessageDeleteForbidden:
        logger.warning("**ꜰᴀɪʟᴇᴅ ᴛᴏ ᴅᴇʟᴇᴛᴇ ᴅᴇʟsᴜᴅᴏ ᴄᴏᴍᴍᴀɴᴅ ᴍᴇssᴀɢᴇ**")
    
    if not message.reply_to_message:
        if len(message.command) != 2:
            return await message.reply_text(
                "**ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴜsᴇʀ ᴏʀ ɢɪᴠᴇ ᴀ ᴜsᴇʀ ɪᴅ ᴛᴏ ʀᴇᴍᴏᴠᴇ ᴛʜᴇᴍ ꜰʀᴏᴍ sᴜᴅᴏ.**"
            )
        
        user = message.text.split(None, 1)[1]
        
        if "@" in user:
            user = user.replace("@", "")
        
        user = await PbxBot.app.get_users(user)
        
        if user.id not in Config.SUDO_USERS:
            return await message.reply_text(f"{user.mention} **ɪs ɴᴏᴛ ᴀ sᴜᴅᴏ ᴜsᴇʀ.**")
        
        removed = await db.remove_sudo(user.id)
        
        if removed:
            Config.SUDO_USERS.remove(user.id)
            await message.reply_text(f"{user.mention} **ɪs ɴᴏ ʟᴏɴɢᴇʀ ᴀ sᴜᴅᴏ ᴜsᴇʀ.**")
            return
        
        await message.reply_text("**ꜰᴀɪʟᴇᴅ ᴛᴏ ʀᴇᴍᴏᴠᴇ sᴜᴅᴏ ᴜsᴇʀ.**")
        return
    
    user_id = message.reply_to_message.from_user.id
    
    if user_id not in Config.SUDO_USERS:
        return await message.reply_text(
            f"{message.reply_to_message.from_user.mention} **ɪs ɴᴏᴛ ᴀ sᴜᴅᴏ ᴜsᴇʀ.**"
        )
    
    removed = await db.remove_sudo(user_id)
    
    if removed:
        Config.SUDO_USERS.remove(user_id)
        await message.reply_text(
            f"{message.reply_to_message.from_user.mention} **ɪs ɴᴏ ʟᴏɴɢᴇʀ ᴀ sᴜᴅᴏ ᴜsᴇʀ.**"
        )
        return
    
    await message.reply_text("**ꜰᴀɪʟᴇᴅ ᴛᴏ ʀᴇᴍᴏᴠᴇ sᴜᴅᴏ ᴜsᴇʀ.**")


async def is_heroku():
    
    return "heroku" in socket.getfqdn()


@PbxBot.app.on_message(filters.command(["getlog", "logs", "getlogs"]) & Config.GOD_USERS)
async def log_(_, message: Message):
    
    try:
        await message.delete()
    
    except MessageDeleteForbidden:
        logger.warning("**ꜰᴀɪʟᴇᴅ ᴛᴏ ᴅᴇʟᴇᴛᴇ ʟᴏɢs ᴄᴏᴍᴍᴀɴᴅ ᴍᴇssᴀɢᴇ**")
    
    Pbx = await message.reply_text("**ᴜᴘʟᴏᴀᴅɪɴɢ ʟᴏɢs...**")
    
    try:
        # Read logs from bot.log file
        log_file = "bot.log"
        
        if not os.path.exists(log_file):
            await Pbx.edit("**ɴᴏ ʟᴏɢ ꜰɪʟᴇ ꜰᴏᴜɴᴅ!**")
            return
        
        with open(log_file, 'r') as f:
            log_content = f.read()
        
        if not log_content.strip():
            await Pbx.edit("**ʟᴏɢ ꜰɪʟᴇ ɪs ᴇᴍᴘᴛʏ!**")
            return
        
        # Upload logs to batbin.me
        log_url = await BadBin(log_content)
        
        if not log_url:
            await Pbx.edit("**ꜰᴀɪʟᴇᴅ ᴛᴏ ᴜᴘʟᴏᴀᴅ ʟᴏɢs ᴛᴏ ʙᴀᴛʙɪɴ.ᴍᴇ**")
            return
        
        await Pbx.edit(f"**ʟᴏɢs ᴜᴘʟᴏᴀᴅᴇᴅ:** {log_url}")
    
    except Exception as e:
        logger.error(f"Error uploading logs: {str(e)}")
        await Pbx.edit(f"**ᴇʀʀᴏʀ ᴜᴘʟᴏᴀᴅɪɴɢ ʟᴏɢs:** `{str(e)}`")


@PbxBot.app.on_message(filters.command(["update", "gitpull"]) & Config.GOD_USERS)
async def update_(_, message: Message):
    
    try:
        await message.delete()
    
    except MessageDeleteForbidden:
        logger.warning("**ꜰᴀɪʟᴇᴅ ᴛᴏ ᴅᴇʟᴇᴛᴇ ᴜᴘᴅᴀᴛᴇ ᴄᴏᴍᴍᴀɴᴅ ᴍᴇssᴀɢᴇ**")
    
    response = await message.reply_text("**ᴄʜᴇᴄᴋɪɴɢ ꜰᴏʀ ᴜᴘᴅᴀᴛᴇs...**")
    
    try:
        repo = Repo()
    
    except GitCommandError as e:
        logger.error(f"Git command error: {str(e)}")
        return await response.edit("**ɢɪᴛ ᴄᴏᴍᴍᴀɴᴅ ᴇʀʀᴏʀ. ᴘʟᴇᴀsᴇ ᴄʜᴇᴄᴋ ʏᴏᴜʀ ɢɪᴛ sᴇᴛᴜᴘ.**")
    
    except InvalidGitRepositoryError as e:
        logger.error(f"Invalid git repository: {str(e)}")
        return await response.edit("**ɴᴏ ɢɪᴛ ʀᴇᴘᴏsɪᴛᴏʀʏ ꜰᴏᴜɴᴅ.**")
    
    # Construct the git fetch/pull command with token if available
    repo_url = Config.UPSTREAM_REPO
    token = Config.GITHUB_TOKEN or os.getenv("GITHUB_TOKEN")
    
    if token and "https://" in repo_url:
        repo_url = repo_url.replace("https://", f"https://{token}@")
    
    # Fetch updates
    fetch_cmd = f"git fetch origin {Config.UPSTREAM_BRANCH}"
    os.system(f"{fetch_cmd} &> /dev/null")
    await asyncio.sleep(7)
    
    # Check for updates
    verification = ""
    
    for checks in repo.iter_commits(f"HEAD..origin/{Config.UPSTREAM_BRANCH}"):
        verification = str(checks.count())
    
    if not verification:
        return await response.edit("**ɴᴏ ɴᴇᴡ ᴜᴘᴅᴀᴛᴇs ᴀᴠᴀɪʟᴀʙʟᴇ.**")
    
    # Build update message
    updates = ""
    ordinal = lambda n: "%d%s" % (
        n,
        "tsnrhtdd"[(n // 10 % 10 != 1) * (n % 10 < 4) * n % 10 :: 4],
    )
    
    for info in repo.iter_commits(f"HEAD..origin/{Config.UPSTREAM_BRANCH}"):
        updates += (
            f"<b>➣ #{info.count()}: <a href={Config.UPSTREAM_REPO}/commit/{info}>{info.summary}</a> by -> {info.author}</b>\n"
            f"\t\t\t\t<b>➥ Committed on:</b> {ordinal(int(datetime.fromtimestamp(info.committed_date).strftime('%d')))} "
            f"{datetime.fromtimestamp(info.committed_date).strftime('%b')}, {datetime.fromtimestamp(info.committed_date).strftime('%Y')}\n\n"
        )
    
    update_response = "<b>ᴀ ɴᴇᴡ ᴜᴘᴅᴀᴛᴇ ɪs ᴀᴠᴀɪʟᴀʙʟᴇ ꜰᴏʀ ᴛʜᴇ ʙᴏᴛ!</b>\n\n➣ **ᴘᴜsʜɪɴɢ ᴜᴘᴅᴀᴛᴇs ɴᴏᴡ**\n\n<b><u>ᴜᴘᴅᴀᴛᴇs:</u></b>\n\n"
    final_updates = update_response + updates
    
    # Handle large update messages
    if len(final_updates) > 4096:
        with io.BytesIO(str.encode(updates)) as out_file:
            out_file.name = "updates.txt"
            await response.edit(
                "<b>ᴀ ɴᴇᴡ ᴜᴘᴅᴀᴛᴇ ɪs ᴀᴠᴀɪʟᴀʙʟᴇ ꜰᴏʀ ᴛʜᴇ ʙᴏᴛ!</b>\n\n➣ **ᴘᴜsʜɪɴɢ ᴜᴘᴅᴀᴛᴇs ɴᴏᴡ**\n\n<u><b>ᴜᴘᴅᴀᴛᴇs:</b></u>\n\n**sᴇᴇ ᴀᴛᴛᴀᴄʜᴇᴅ ꜰɪʟᴇ.**"
            )
            await message.reply_document(document=out_file, caption="**ᴜᴘᴅᴀᴛᴇ ᴅᴇᴛᴀɪʟs**")
    
    else:
        await response.edit(final_updates, disable_web_page_preview=True)
    
    # Perform git pull
    pull_cmd = f"git pull origin {Config.UPSTREAM_BRANCH}"
    os.system("git stash &> /dev/null")
    pull_result = os.system(pull_cmd)
    
    if pull_result != 0:
        logger.error(f"Git pull failed with exit code {pull_result}")
        await response.edit("**ꜰᴀɪʟᴇᴅ ᴛᴏ ᴘᴜʟʟ ᴜᴘᴅᴀᴛᴇs. ᴄʜᴇᴄᴋ ʟᴏɢs ꜰᴏʀ ᴅᴇᴛᴀɪʟs.**")
        await PbxBot.app.send_message(
            Config.LOGGER_ID,
            f"**ɢɪᴛ ᴘᴜʟʟ ꜰᴀɪʟᴇᴅ:** `{pull_cmd}` **ʀᴇᴛᴜʀɴᴇᴅ ɴᴏɴ-ᴢᴇʀᴏ ᴇxɪᴛ ᴄᴏᴅᴇ** {pull_result}",
        )
        return
    
    # Notify active chats
    try:
        from Music.core.calls import PbxMusic
        served_chats = await PbxMusic.get_active_chats()
        
        for chat_id in served_chats:
            try:
                await PbxBot.app.send_message(
                    chat_id=int(chat_id),
                    text=f"{PbxBot.app.mention} **ʜᴀs ʙᴇᴇɴ ᴜᴘᴅᴀᴛᴇᴅ. ʏᴏᴜ ᴄᴀɴ sᴛᴀʀᴛ ᴘʟᴀʏɪɴɢ ᴀɢᴀɪɴ sʜᴏʀᴛʟʏ.**",
                )
                await PbxMusic.remove_active_chat(chat_id)
                await PbxMusic.remove_active_video_chat(chat_id)
            
            except:
                pass
        
        await response.edit(f"{final_updates}\n\n**ᴜᴘᴅᴀᴛᴇs sᴜᴄᴄᴇssꜰᴜʟʟʏ ᴀᴘᴘʟɪᴇᴅ. ʀᴇsᴛᴀʀᴛɪɴɢ...**")
    
    except Exception as e:
        logger.error(f"Error notifying chats: {str(e)}")
        await response.edit(f"{final_updates}\n\n**ᴇʀʀᴏʀ ɴᴏᴛɪꜰʏɪɴɢ ᴄʜᴀᴛs:** `{str(e)}`")
    
    # Handle restart based on environment
    if await is_heroku():
        try:
            os.system("heroku ps:restart -a $HEROKU_APP_NAME")
        
        except Exception as err:
            logger.error(f"Heroku restart failed: {str(err)}")
            await response.edit(f"**ꜰᴀɪʟᴇᴅ ᴛᴏ ʀᴇsᴛᴀʀᴛ ᴏɴ ʜᴇʀᴏᴋᴜ:** `{str(err)}`")
            await PbxBot.app.send_message(
                Config.LOGGER_ID,
                f"**ʜᴇʀᴏᴋᴜ ʀᴇsᴛᴀʀᴛ ꜰᴀɪʟᴇᴅ:** `{str(err)}`",
            )
            return
    
    else:
        os.system("pip3 install -r requirements.txt")
        os.system(f"kill -9 {os.getpid()} && bash start")
        exit()


@PbxBot.app.on_message(filters.command(["restart"]) & Config.GOD_USERS)
async def restart_(_, message: Message):
    
    try:
        await message.delete()
    
    except MessageDeleteForbidden:
        logger.warning("**ꜰᴀɪʟᴇᴅ ᴛᴏ ᴅᴇʟᴇᴛᴇ ʀᴇsᴛᴀʀᴛ ᴄᴏᴍᴍᴀɴᴅ ᴍᴇssᴀɢᴇ**")
    
    response = await message.reply_text("**ʀᴇsᴛᴀʀᴛɪɴɢ...**")
    
    try:
        from Music.core.calls import PbxMusic
        active_chats = await PbxMusic.get_active_chats()
        
        for chat_id in active_chats:
            try:
                await PbxBot.app.send_message(
                    chat_id=int(chat_id),
                    text=f"{PbxBot.app.mention} **ɪs ʀᴇsᴛᴀʀᴛɪɴɢ...**\n\n**ʏᴏᴜ ᴄᴀɴ sᴛᴀʀᴛ ᴘʟᴀʏɪɴɢ ᴀɢᴀɪɴ ᴀꜰᴛᴇʀ 15-20 sᴇᴄᴏɴᴅs.**",
                )
                await PbxMusic.remove_active_chat(chat_id)
                await PbxMusic.remove_active_video_chat(chat_id)
            
            except:
                pass
    
    except Exception as e:
        logger.error(f"Error notifying chats: {str(e)}")
        await response.edit_text(f"**ᴇʀʀᴏʀ ɴᴏᴛɪꜰʏɪɴɢ ᴄʜᴀᴛs:** `{str(e)}`")
    
    try:
        shutil.rmtree("downloads", ignore_errors=True)
        shutil.rmtree("raw_files", ignore_errors=True)
        shutil.rmtree("cache", ignore_errors=True)
    
    except Exception as e:
        logger.error(f"Error cleaning up directories: {str(e)}")
    
    await response.edit_text(
        "**ʀᴇsᴛᴀʀᴛ ᴘʀᴏᴄᴇss sᴛᴀʀᴛᴇᴅ, ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ ᴀ ꜰᴇᴡ sᴇᴄᴏɴᴅs ᴜɴᴛɪʟ ᴛʜᴇ ʙᴏᴛ sᴛᴀʀᴛs...**"
    )
    
    if await is_heroku():
        try:
            os.system("heroku ps:restart -a $HEROKU_APP_NAME")
        
        except Exception as err:
            logger.error(f"Heroku restart failed: {str(err)}")
            await response.edit(f"**ꜰᴀɪʟᴇᴅ ᴛᴏ ʀᴇsᴛᴀʀᴛ ᴏɴ ʜᴇʀᴏᴋᴜ:** `{str(err)}`")
            await PbxBot.app.send_message(
                Config.LOGGER_ID,
                f"**ʜᴇʀᴏᴋᴜ ʀᴇsᴛᴀʀᴛ ꜰᴀɪʟᴇᴅ:** `{str(err)}`",
            )
            return
    
    else:
        os.system(f"kill -9 {os.getpid()} && bash start")
        exit()
