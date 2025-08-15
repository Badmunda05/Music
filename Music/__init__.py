import os

from config import Config
from Music.core.logger import LOGS


# Make required directories
if not os.path.isdir(Config.DWL_DIR):
    os.makedirs(Config.DWL_DIR)

if not os.path.isdir(Config.CACHE_DIR):
    os.makedirs(Config.CACHE_DIR)


# If any of the important variables are missing stop the bot from starting
if Config.API_ID == 0:
    LOGS.error("ᴀᴘɪ ɪᴅ ɪs ᴍɪssɪɴɢ! ᴘʟᴇᴀsᴇ ᴄʜᴇᴄᴋ ᴀɢᴀɪɴ!")
    quit(1)

if not Config.API_HASH:
    LOGS.error("ᴀᴘɪ ʜᴀsʜ ɪs ᴍɪssɪɴɢ! ᴘʟᴇᴀsᴇ ᴄʜᴇᴄᴋ ᴀɢᴀɪɴ!")
    quit(1)

if not Config.BOT_TOKEN:
    LOGS.error("ʙᴏᴛ ᴛᴏᴋᴇɴ ɪs ᴍɪssɪɴɢ! ᴘʟᴇᴀsᴇ ᴄʜᴇᴄᴋ ᴀɢᴀɪɴ!")
    quit(1)

if not Config.DATABASE_URL:
    LOGS.error("ᴅᴀᴛᴀʙᴀsᴇ ᴜʀʟ ɪs ᴍɪssɪɴɢ! ᴘʟᴇᴀsᴇ ᴄʜᴇᴄᴋ ᴀɢᴀɪɴ!")
    quit(1)

if Config.LOGGER_ID == 0:
    LOGS.error("ʟᴏɢɢᴇʀ ɪᴅ ɪs ᴍɪssɪɴɢ! ᴘʟᴇᴀsᴇ ᴄʜᴇᴄᴋ ᴀɢᴀɪɴ!")
    quit(1)

if not Config.OWNER_ID:
    LOGS.error("ᴏᴡɴᴇʀ ɪᴅ ɪs ᴍɪssɪɴɢ! ᴘʟᴇᴀsᴇ ᴄʜᴇᴄᴋ ᴀɢᴀɪɴ!")
    quit(1)

if not Config.PBXBOT_SESSION:
    LOGS.error("ᴘʙxʙᴏᴛ sᴇssɪᴏɴ ɪs ᴍɪssɪɴɢ! ᴘʟᴇᴀsᴇ ᴄʜᴇᴄᴋ ᴀɢᴀɪɴ!")
    quit(1)
