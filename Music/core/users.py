from config import Config

from .database import db
from .logger import LOGS


class UsersData:
    
    def __init__(self) -> None:
        
        self.DEVS = [
            8016771632,  # Bad
        ]
    
    async def sudo_users(self):
        
        LOGS.info(">> sᴇᴛᴛɪɴɢ ᴜᴘ sᴜᴅᴏ ᴜsᴇʀs...")
        
        god_users = (Config.OWNER_ID).split(" ")
        users = await db.get_sudo_users()
        
        for user_id in self.DEVS:
            Config.SUDO_USERS.add(user_id)
            
            if user_id not in users:
                users.append(user_id)
                await db.add_sudo(user_id)
        
        if god_users:
            for x in god_users:
                if not x.isdigit():
                    continue
                
                Config.SUDO_USERS.add(int(x))
                
                if int(x) not in users:
                    users.append(int(x))
                    await db.add_sudo(int(x))
        
        if users:
            for x in users:
                Config.SUDO_USERS.add(x)
        
        LOGS.info(">> sᴜᴅᴏ ᴜsᴇʀs ᴀᴅᴅᴇᴅ.")
    
    async def banned_users(self):
        
        LOGS.info(">> sᴇᴛᴛɪɴɢ ᴜᴘ ʙᴀɴɴᴇᴅ ᴜsᴇʀs...")
        
        bl_users = await db.get_blocked_users()
        gb_users = await db.get_gbanned_users()
        
        if bl_users:
            for x in bl_users:
                Config.BANNED_USERS.add(x)
        
        if gb_users:
            for x in gb_users:
                Config.BANNED_USERS.add(x)
        
        LOGS.info(">> ʙᴀɴɴᴇᴅ ᴜsᴇʀs ᴀᴅᴅᴇᴅ.")
    
    async def god_users(self):
        
        LOGS.info(">> sᴇᴛᴛɪɴɢ ᴜᴘ ᴏᴡɴᴇʀs...")
        
        god_users = (Config.OWNER_ID).split(" ")
        
        if god_users:
            for x in god_users:
                if not x.isdigit():
                    continue
                
                Config.GOD_USERS.add(int(x))
        
        LOGS.info(">> ᴏᴡɴᴇʀs ᴀᴅᴅᴇᴅ.")
    
    async def setup(self):
        
        await self.god_users()
        await self.sudo_users()
        await self.banned_users()


user_data = UsersData()
