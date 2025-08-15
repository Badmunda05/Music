import asyncio

from pyrogram import idle

from config import Config
from Music.core.calls import PbxMusic
from Music.core.clients import PbxBot
from Music.core.database import db
from Music.core.logger import LOGS
from Music.core.users import user_data
from Music.helpers.strings import TEXTS
from Music.version import __version__


async def start_bot():
    
    hmusic_version = __version__["Pbx Music"]
    py_version = __version__["Python"]
    pyro_version = __version__["Pyrogram"]
    pycalls_version = __version__["PyTgCalls"]
    
    LOGS.info(
        "ᴀʟʟ ᴄʜᴇᴄᴋs ᴄᴏᴍᴘʟᴇᴛᴇᴅ! ʟᴇᴛ's sᴛᴀʀᴛ ᴘʙx-ᴍᴜsɪᴄ..."
    )
    
    await user_data.setup()
    await PbxBot.start()
    await PbxMusic.start()
    await db.connect()
    
    try:
        if Config.BOT_PIC:
            await PbxBot.app.send_photo(
                int(Config.LOGGER_ID),
                Config.BOT_PIC,
                TEXTS.BOOTED.format(
                    Config.BOT_NAME,
                    hmusic_version,
                    py_version,
                    pyro_version,
                    pycalls_version,
                    PbxBot.app.mention(style="md"),
                ),
            )
        
        else:
            await PbxBot.app.send_message(
                int(Config.LOGGER_ID),
                TEXTS.BOOTED.format(
                    Config.BOT_NAME,
                    hmusic_version,
                    py_version,
                    pyro_version,
                    pycalls_version,
                    PbxBot.app.mention(style="md"),
                ),
            )
    
    except Exception as e:
        LOGS.warning(
            f"ᴇʀʀᴏʀ ɪɴ ʟᴏɢɢᴇʀ: {e}"
        )
    
    LOGS.info(
        f">> ᴘʙx-ᴍᴜsɪᴄ [{hmusic_version}] ɪs ɴᴏᴡ ᴏɴʟɪɴᴇ!"
    )
    
    await idle()
    
    await PbxBot.app.send_message(
        Config.LOGGER_ID,
        f"#sᴛᴏᴘ\n\n**ᴘʙx-ᴍᴜsɪᴄ [{hmusic_version}] ɪs ɴᴏᴡ ᴏꜰꜰʟɪɴᴇ!**",
    )
    
    LOGS.info(
        f"ᴘʙx-ᴍᴜsɪᴄ [{hmusic_version}] ɪs ɴᴏᴡ ᴏꜰꜰʟɪɴᴇ!"
    )


if __name__ == "__main__":
    
    loop = asyncio.get_event_loop()
    
    try:
        loop.run_until_complete(start_bot())
    
    finally:
        loop.run_until_complete(PbxBot.app.stop())
        loop.close()
