import datetime

import os

import subprocess

from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import (
    ChatAdminRequired,
    UserAlreadyParticipant,
    UserNotParticipant,
)
from pyrogram.types import InlineKeyboardMarkup
from pytgcalls import PyTgCalls, StreamType
from pytgcalls.exceptions import AlreadyJoinedError, NoActiveGroupCall
from pytgcalls.types.input_stream import AudioPiped, AudioVideoPiped
from pytgcalls.types.input_stream.quality import MediumQualityAudio, MediumQualityVideo

from config import Config
from Music.helpers.buttons import Buttons
from Music.helpers.strings import TEXTS
from Music.utils.exceptions import (
    ChangeVCException,
    JoinGCException,
    JoinVCException,
    UserException,
)
from Music.utils.queue import Queue
from Music.utils.thumbnail import thumb
from Music.utils.youtube import ytube

from .clients import PbxBot
from .database import db
from .logger import LOGS


async def __clean__(chat_id: int, force: bool):
    
    if force:
        Queue.rm_queue(chat_id, 0)
    
    else:
        Queue.clear_queue(chat_id)
    
    await db.remove_active_vc(chat_id)


class PbxMusic(PyTgCalls):
    
    def __init__(self):
        
        self.music = PyTgCalls(PbxBot.user)
        self.audience = {}
        self.bass_boost = {}  # Store bass boost settings per chat
        self.speed = {}  # Store speed settings per chat
    
    async def autoend(self, chat_id: int, users: list):
        
        autoend = await db.get_autoend()
        
        if autoend:
            if len(users) == 1:
                get = await PbxBot.app.get_users(users[0])
                if get.id == PbxBot.user.id:
                    db.inactive[chat_id] = datetime.datetime.now() + datetime.timedelta(
                        minutes=5
                    )
            else:
                db.inactive[chat_id] = {}
    
    async def autoclean(self, file: str):
        
        try:
            os.remove(file)
            os.remove(f"downloads/{file}.webm")
            os.remove(f"downloads/{file}.mp4")
        
        except:
            pass
    
    async def start(self):
        
        LOGS.info(">> ʙᴏᴏᴛɪɴɢ ᴘʏᴛɢᴄᴀʟʟs ᴄʟɪᴇɴᴛ...")
        
        if Config.PbxBot_SESSION:
            await self.music.start()
            LOGS.info(">> ʙᴏᴏᴛᴇᴅ ᴘʏᴛɢᴄᴀʟʟs ᴄʟɪᴇɴᴛ!")
        
        else:
            LOGS.error(">> ᴘʏᴛɢᴄᴀʟʟs ᴄʟɪᴇɴᴛ ɴᴏᴛ ʙᴏᴏᴛᴇᴅ!")
            quit(1)
    
    async def ping(self):
        
        return await self.music.ping
    
    async def vc_participants(self, chat_id: int):
        
        return await self.music.get_participants(chat_id)
    
    async def mute_vc(self, chat_id: int):
        
        await self.music.mute_stream(chat_id)
    
    async def unmute_vc(self, chat_id: int):
        
        await self.music.unmute_stream(chat_id)
    
    async def pause_vc(self, chat_id: int):
        
        await self.music.pause_stream(chat_id)
    
    async def resume_vc(self, chat_id: int):
        
        await self.music.resume_stream(chat_id)
    
    async def leave_vc(self, chat_id: int, force: bool = False):
        
        try:
            await __clean__(chat_id, force)
            await self.music.leave_group_call(chat_id)
            self.bass_boost.pop(chat_id, None)
            self.speed.pop(chat_id, None)
        
        except:
            pass
        
        previous = Config.PLAYER_CACHE.get(chat_id)
        
        if previous:
            try:
                await previous.delete()
            
            except:
                pass
    
    async def apply_audio_effects(self, file_path: str, chat_id: int, video: bool = False):
        
        if video:
            return file_path
        
        bass = self.bass_boost.get(chat_id, 0)
        speed = self.speed.get(chat_id, 1.0)
        output_file = f"downloads/{os.path.basename(file_path)}_processed.mp3"
        
        ffmpeg_cmd = ["ffmpeg", "-i", file_path]
        
        if bass > 0:
            ffmpeg_cmd.extend(["-af", f"bass=g={bass}"])
        
        if speed != 1.0:
            ffmpeg_cmd.extend(["-filter:a", f"atempo={speed}"])
        
        ffmpeg_cmd.extend(["-y", output_file])
        
        try:
            subprocess.run(ffmpeg_cmd, check=True)
            return output_file
        
        except subprocess.CalledProcessError as e:
            LOGS.error(f"ᴇʀʀᴏʀ ᴀᴘᴘʟʏɪɴɢ ᴀᴜᴅɪᴏ ᴇꜰꜰᴇᴄᴛs: {e}")
            return file_path
    
    async def seek_vc(self, context: dict):
        
        chat_id, file_path, duration, to_seek, video = context.values()
        processed_file = await self.apply_audio_effects(file_path, chat_id, video)
        
        if video:
            input_stream = AudioVideoPiped(
                processed_file,
                MediumQualityAudio(),
                MediumQualityVideo(),
                additional_ffmpeg_parameters=f"-ss {to_seek} -to {duration}",
            )
        
        else:
            input_stream = AudioPiped(
                processed_file,
                MediumQualityAudio(),
                additional_ffmpeg_parameters=f"-ss {to_seek} -to {duration}",
            )
        
        await self.music.change_stream(chat_id, input_stream)
    
    async def invited_vc(self, chat_id: int):
        
        try:
            await PbxBot.app.send_message(
                chat_id, "ᴛʜᴇ ʙᴏᴛ ᴡɪʟʟ ᴊᴏɪɴ ᴠᴄ ᴏɴʟʏ ᴡʜᴇɴ ʏᴏᴜ ɢɪᴠᴇ sᴏᴍᴇᴛʜɪɴɢ ᴛᴏ ᴘʟᴀʏ!"
            )
        
        except:
            return
    
    async def replay_vc(self, chat_id: int, file_path: str, video: bool = False):
        
        processed_file = await self.apply_audio_effects(file_path, chat_id, video)
        
        if video:
            input_stream = AudioVideoPiped(
                processed_file, MediumQualityAudio(), MediumQualityVideo()
            )
        
        else:
            input_stream = AudioPiped(processed_file, MediumQualityAudio())
        
        await self.music.change_stream(chat_id, input_stream)
    
    async def change_vc(self, chat_id: int):
        
        try:
            get = Queue.get_queue(chat_id)
            
            if get == []:
                return await self.leave_vc(chat_id)
            
            loop = await db.get_loop(chat_id)
            
            if loop == 0:
                file = Queue.rm_queue(chat_id, 0)
                await self.autoclean(file)
            
            else:
                await db.set_loop(chat_id, loop - 1)
        
        except Exception as e:
            LOGS.error(e)
            return await self.leave_vc(chat_id)
        
        get = Queue.get_queue(chat_id)
        
        if get == []:
            return await self.leave_vc(chat_id)
        
        chat_id = get[0]["chat_id"]
        duration = get[0]["duration"]
        queue = get[0]["file"]
        title = get[0]["title"]
        user_id = get[0]["user_id"]
        vc_type = get[0]["vc_type"]
        video_id = get[0]["video_id"]
        
        try:
            user = (await PbxBot.app.get_users(user_id)).mention(style="md")
        
        except:
            user = get[0]["user"]
        
        if queue:
            tg = True if video_id == "telegram" else False
            
            if tg:
                to_stream = queue
            
            else:
                to_stream = await ytube.download(
                    video_id, True, True if vc_type == "video" else False
                )
            
            to_stream = await self.apply_audio_effects(to_stream, chat_id, vc_type == "video")
            
            if vc_type == "video":
                input_stream = AudioVideoPiped(
                    to_stream, MediumQualityAudio(), MediumQualityVideo()
                )
            
            else:
                input_stream = AudioPiped(to_stream, MediumQualityAudio())
            
            try:
                photo = thumb.generate((359), (297, 302), video_id)
                await self.music.change_stream(int(chat_id), input_stream)
                
                btns = Buttons.player_markup(
                    chat_id,
                    "None" if video_id == "telegram" else video_id,
                    PbxBot.app.username,
                )
                
                chat_name = (await PbxBot.app.get_chat(chat_id)).title
                
                if photo:
                    sent = await PbxBot.app.send_photo(
                        int(chat_id),
                        photo,
                        TEXTS.PLAYING.format(
                            PbxBot.app.mention,
                            title,
                            duration,
                            user,
                            chat_name,
                        ),
                        reply_markup=InlineKeyboardMarkup(btns),
                    )
                    os.remove(photo)
                
                else:
                    sent = await PbxBot.app.send_message(
                        int(chat_id),
                        TEXTS.PLAYING.format(
                            PbxBot.app.mention,
                            title,
                            duration,
                            user,
                            chat_name,
                        ),
                        disable_web_page_preview=True,
                        reply_markup=InlineKeyboardMarkup(btns),
                    )
                
                previous = Config.PLAYER_CACHE.get(chat_id)
                
                if previous:
                    try:
                        await previous.delete()
                    
                    except:
                        pass
                
                Config.PLAYER_CACHE[chat_id] = sent
                await db.update_songs_count(1)
                await db.update_user(user_id, "songs_played", 1)
                
                await PbxBot.logit(
                    f"ᴘʟᴀʏ {vc_type}",
                    f"**⤷ sᴏɴɢ:** `{title}` \n**⤷ ᴄʜᴀᴛ:** {chat_name} [`{chat_id}`] \n**⤷ ᴜsᴇʀ:** {user}",
                )
            
            except Exception as e:
                raise ChangeVCException(f"[ᴄʜᴀɴɢᴇᴠᴄᴇxᴄᴇᴘᴛɪᴏɴ]: {e}")
    
    async def join_vc(self, chat_id: int, file_path: str, video: bool = False):
        
        processed_file = await self.apply_audio_effects(file_path, chat_id, video)
        
        if video:
            input_stream = AudioVideoPiped(
                processed_file, MediumQualityAudio(), MediumQualityVideo()
            )
        
        else:
            input_stream = AudioPiped(processed_file, MediumQualityAudio())
        
        try:
            await self.music.join_group_call(
                chat_id, input_stream, stream_type=StreamType().pulse_stream
            )
        
        except NoActiveGroupCall:
            try:
                await self.join_gc(chat_id)
            
            except Exception as e:
                await self.leave_vc(chat_id)
                raise JoinGCException(e)
            
            try:
                await self.music.join_group_call(
                    chat_id, input_stream, stream_type=StreamType().pulse_stream
                )
            
            except Exception as e:
                await self.leave_vc(chat_id)
                raise JoinVCException(f"[ᴊᴏɪɴᴠᴄᴇxᴄᴇᴘᴛɪᴏɴ]: {e}")
        
        except AlreadyJoinedError:
            raise UserException(
                f"[ᴜsᴇʀᴇxᴄᴇᴘᴛɪᴏɴ]: ᴀʟʀᴇᴀᴅʏ ᴊᴏɪɴᴇᴅ ɪɴ ᴛʜᴇ ᴠᴏɪᴄᴇ ᴄʜᴀᴛ. ɪꜰ ᴛʜɪs ɪs ᴀ ᴍɪsᴛᴀᴋᴇ ᴛʜᴇɴ ᴛʀʏ ᴛᴏ ʀᴇsᴛᴀʀᴛ ᴛʜᴇ ᴠᴏɪᴄᴇ ᴄʜᴀᴛ."
            )
        
        except Exception as e:
            raise UserException(f"[ᴜsᴇʀᴇxᴄᴇᴘᴛɪᴏɴ]: {e}")
        
        await db.add_active_vc(chat_id, "video" if video else "voice")
        
        self.audience[chat_id] = {}
        self.bass_boost[chat_id] = 0
        self.speed[chat_id] = 1.0
        
        users = await self.vc_participants(chat_id)
        user_ids = [user.user_id for user in users]
        
        await self.autoend(chat_id, user_ids)
    
    async def join_gc(self, chat_id: int):
        
        try:
            try:
                get = await PbxBot.app.get_chat_member(chat_id, PbxBot.user.id)
            
            except ChatAdminRequired:
                raise UserException(
                    f"[ᴜsᴇʀᴇxᴄᴇᴘᴛɪᴏɴ]: ʙᴏᴛ ɪs ɴᴏᴛ ᴀᴅᴍɪɴ ɪɴ ᴄʜᴀᴛ {chat_id}"
                )
            
            #  Auto Unban Assistant if Banned/Restricted
            if (
                get.status == ChatMemberStatus.RESTRICTED
                or get.status == ChatMemberStatus.BANNED
            ):
                try:
                    me = await PbxBot.app.get_chat_member(chat_id, (await PbxBot.app.get_me()).id)
                    
                    if me.privileges and me.privileges.can_restrict_members:
                        await PbxBot.app.unban_chat_member(chat_id, PbxBot.user.id)
                        
                        await PbxBot.app.send_message(
                            chat_id,
                            "✅ ᴀssɪsᴛᴀɴᴛ ᴡᴀs ʙᴀɴɴᴇᴅ/ʀᴇsᴛʀɪᴄᴛᴇᴅ, ʙᴜᴛ ɪ ʜᴀᴠᴇ ᴜɴʙᴀɴɴᴇᴅ ɪᴛ ᴀᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟʏ!"
                        )
                    
                    else:
                        raise UserException(
                            f"[ᴜsᴇʀᴇxᴄᴇᴘᴛɪᴏɴ]: ᴀssɪsᴛᴀɴᴛ ɪs ʀᴇsᴛʀɪᴄᴛᴇᴅ ᴏʀ ʙᴀɴɴᴇᴅ ɪɴ ᴄʜᴀᴛ {chat_id} ᴀɴᴅ ɪ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴜɴʙᴀɴ ʀɪɢʜᴛs."
                        )
                
                except ChatAdminRequired:
                    raise UserException(
                        f"[ᴜsᴇʀᴇxᴄᴇᴘᴛɪᴏɴ]: ʙᴏᴛ ɪs ɴᴏᴛ ᴀᴅᴍɪɴ ɪɴ ᴄʜᴀᴛ {chat_id}, ᴄᴀɴɴᴏᴛ ᴜɴʙᴀɴ ᴀssɪsᴛᴀɴᴛ."
                    )
                
                except Exception as e:
                    raise UserException(f"[ᴜsᴇʀᴇxᴄᴇᴘᴛɪᴏɴ]: ꜰᴀɪʟᴇᴅ ᴛᴏ ᴜɴʙᴀɴ ᴀssɪsᴛᴀɴᴛ → {e}")
        
        except UserNotParticipant:
            chat = await PbxBot.app.get_chat(chat_id)
            
            if chat.username:
                try:
                    await PbxBot.user.join_chat(chat.username)
                
                except UserAlreadyParticipant:
                    pass
                
                except Exception as e:
                    raise UserException(f"[ᴜsᴇʀᴇxᴄᴇᴘᴛɪᴏɴ]: {e}")
            
            else:
                try:
                    try:
                        link = chat.invite_link
                        
                        if link is None:
                            link = await PbxBot.app.export_chat_invite_link(chat_id)
                    
                    except ChatAdminRequired:
                        raise UserException(
                            f"[ᴜsᴇʀᴇxᴄᴇᴘᴛɪᴏɴ]: ʙᴏᴛ ɪs ɴᴏᴛ ᴀᴅᴍɪɴ ɪɴ ᴄʜᴀᴛ {chat_id}"
                        )
                    
                    except Exception as e:
                        raise UserException(f"[ᴜsᴇʀᴇxᴄᴇᴘᴛɪᴏɴ]: {e}")
                    
                    Pbx = await PbxBot.app.send_message(
                        chat_id, "ɪɴᴠɪᴛɪɴɢ ᴀssɪsᴛᴀɴᴛ ᴛᴏ ᴄʜᴀᴛ..."
                    )
                    
                    if link.startswith("https://t.me/+"):
                        link = link.replace("https://t.me/+", "https://t.me/joinchat/")
                    
                    await PbxBot.user.join_chat(link)
                    
                    await Pbx.edit_text("ᴀssɪsᴛᴀɴᴛ ᴊᴏɪɴᴇᴅ ᴛʜᴇ ᴄʜᴀᴛ! ᴇɴᴊᴏʏ ʏᴏᴜʀ ᴍᴜsɪᴄ!")
                
                except UserAlreadyParticipant:
                    pass
                
                except Exception as e:
                    raise UserException(f"[ᴜsᴇʀᴇxᴄᴇᴘᴛɪᴏɴ]: {e}")


PbxMusic = PbxMusic()
