import logging
import os

from pyrogram import filters
from pyrogram.types import Message

from config import Config
from Music.core.clients import PbxBot


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@PbxBot.app.on_message(
    filters.command(["boosted"]) & filters.group & ~Config.BANNED_USERS
)
async def bass_boost(_, message: Message):
    
    replied = message.reply_to_message
    
    # Check if the command is a reply to an audio file
    if not (replied and replied.audio and replied.audio.mime_type == "audio/mpeg"):
        return await message.reply_text("**ᴘʟᴇᴀsᴇ ʀᴇᴘʟʏ ᴛᴏ ᴀɴ ᴍᴘ3 ꜰɪʟᴇ ᴡɪᴛʜ ᴛʜᴇ ᴄᴏᴍᴍᴀɴᴅ!**")
    
    # Check if bass level is provided
    if len(message.command) < 2:
        return await message.reply_text(
            "**ᴘʟᴇᴀsᴇ sᴘᴇᴄɪꜰʏ ᴛʜᴇ ʙᴀss ʙᴏᴏsᴛ ʟᴇᴠᴇʟ (0 ᴛᴏ 100).** \n\n**ᴇxᴀᴍᴘʟᴇ:** `/bass 50` ᴛᴏ sᴇᴛ ʙᴀss ʙᴏᴏsᴛ ᴛᴏ 50%. ᴜsᴇ `/bass 0` ᴛᴏ ᴅɪsᴀʙʟᴇ."
        )
    
    # Validate bass level
    try:
        bass_level = int(message.command[1])
        if not 0 <= bass_level <= 100:
            return await message.reply_text(
                "**ᴘʟᴇᴀsᴇ ᴇɴᴛᴇʀ ᴀ ᴠᴀʟɪᴅ ʙᴀss ʟᴇᴠᴇʟ ʙᴇᴛᴡᴇᴇɴ 0 ᴀɴᴅ 100!**"
            )
    
    except ValueError:
        return await message.reply_text("**ᴘʟᴇᴀsᴇ ᴇɴᴛᴇʀ ᴀ ᴠᴀʟɪᴅ ɴᴜᴍʙᴇʀ ꜰᴏʀ ʙᴀss ʟᴇᴠᴇʟ!**")
    
    Pbx = await message.reply_text("**ᴘʀᴏᴄᴇssɪɴɢ ʙᴀss ʙᴏᴏsᴛ ꜰᴏʀ ᴛʜᴇ ʀᴇᴘʟɪᴇᴅ ᴀᴜᴅɪᴏ...**")
    
    # Download the replied MP3 file
    try:
        file_path = await replied.download()
        
        if not file_path:
            return await Pbx.edit_text("**ꜰᴀɪʟᴇᴅ ᴛᴏ ᴅᴏᴡɴʟᴏᴀᴅ ᴛʜᴇ ᴀᴜᴅɪᴏ ꜰɪʟᴇ!**")
        
        # Ensure downloads directory exists
        os.makedirs("downloads", exist_ok=True)
        
        # Apply bass boost using the provided method
        from Music.core.calls import PbxMusic
        
        PbxMusic.bass_boost[message.chat.id] = bass_level
        processed_file = await PbxMusic.apply_audio_effects(file_path, message.chat.id)
        
        if processed_file == file_path:
            return await Pbx.edit_text("**ꜰᴀɪʟᴇᴅ ᴛᴏ ᴀᴘᴘʟʏ ʙᴀss ʙᴏᴏsᴛ!**")
        
        # Send the bass-boosted file
        await message.reply_audio(
            audio=processed_file,
            caption=f"__ʙᴀss ʙᴏᴏsᴛᴇᴅ ᴛᴏ:__ `{bass_level}%` ʙʏ {message.from_user.mention}",
            title=f"ʙᴀss ʙᴏᴏsᴛᴇᴅ ᴀᴜᴅɪᴏ ({bass_level}%)",
            performer="ᴘʙxʙᴏᴛ",
        )
        
        # Clean up
        os.remove(file_path)
        
        if processed_file != file_path:
            os.remove(processed_file)
        
        await Pbx.delete()
    
    except Exception as e:
        logger.error(f"ᴇʀʀᴏʀ ᴘʀᴏᴄᴇssɪɴɢ ʙᴀss ʙᴏᴏsᴛ: {e}")
        await Pbx.edit_text(f"**ᴇʀʀᴏʀ ᴀᴘᴘʟʏɪɴɢ ʙᴀss ʙᴏᴏsᴛ:** {e}")
        
        if os.path.exists(file_path):
            os.remove(file_path)
