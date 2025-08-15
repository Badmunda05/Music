import os
import re
import time
import logging
import random
import requests
import yt_dlp
from lyricsgenius import Genius
from pyrogram.types import CallbackQuery
from youtubesearchpython.__future__ import VideosSearch
import httpx

from config import Config
from Music.core.clients import PbxBot
from Music.core.logger import LOGS
from Music.helpers.strings import TEXTS

class YouTube:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.listbase = "https://youtube.com/playlist?list="
        self.regex = (
            r"(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:watch\?v=|embed\/|v\/|shorts\/)|"
            r"youtu\.be\/|youtube\.com\/playlist\?list=)"
        )

        # Config
        self.USE_API = getattr(Config, "USE_API", False)
        self.USE_COOKIES = getattr(Config, "USE_COOKIES", True)
        self.YOUR_API_KEY = getattr(Config, "YOUR_API_KEY", None)
        self.YOUR_API_URL = getattr(Config, "YOUR_API_URL", None)
        self.COOKIES_URL = getattr(Config, "COOKIES_URL", None)

        # cookies local filename
        self.cookies_file = "cookies.txt"

        # if cookies enabled, try to download and save locally (overwrite)
        if self.USE_COOKIES:
            if self.COOKIES_URL:
                try:
                    LOGS.info(f"Downloading cookies from {self.COOKIES_URL}")
                    r = requests.get(self.COOKIES_URL, timeout=30)
                    r.raise_for_status()
                    with open(self.cookies_file, "wb") as fh:
                        fh.write(r.content)
                    LOGS.info("Cookies saved to " + self.cookies_file)
                except Exception as e:
                    LOGS.warning(f"Could not download cookies from {self.COOKIES_URL}: {e}")
                    if os.path.exists(self.cookies_file):
                        LOGS.info("Existing cookies file present, will attempt to use it.")
                    else:
                        LOGS.warning("No local cookies file available; disabling cookie usage for yt-dlp.")
                        self.USE_COOKIES = False
            else:
                if not os.path.exists(self.cookies_file):
                    LOGS.warning("USE_COOKIES is True but COOKIES_URL not provided and cookies.txt not found. Disabling cookies.")
                    self.USE_COOKIES = False

        # Build yt-dlp options, only add cookiefile key when cookies are available
        def _maybe_cookie(opts: dict):
            if self.USE_COOKIES and os.path.exists(self.cookies_file):
                opts["cookiefile"] = self.cookies_file
            return opts

        self.audio_opts = _maybe_cookie({
            "format": "bestaudio[ext=m4a]/bestaudio/best",
            "quiet": True,
            "no_warnings": True,
        })

        self.video_opts = _maybe_cookie({
            "format": "(bestvideo[height<=?720][width<=?1280][ext=mp4]+bestaudio[ext=m4a])/best",
            "addmetadata": True,
            "prefer_ffmpeg": True,
            "geo_bypass": True,
            "nocheckcertificate": True,
            "postprocessors": [{"key": "FFmpegVideoConvertor", "preferedformat": "mp4"}],
            "outtmpl": "downloads/%(id)s.%(ext)s",
            "quiet": True,
            "no_warnings": True,
        })

        self.yt_opts_audio = _maybe_cookie({
            "format": "bestaudio[ext=m4a]/bestaudio/best",
            "outtmpl": "downloads/%(id)s.%(ext)s",
            "geo_bypass": True,
            "nocheckcertificate": True,
            "quiet": True,
            "no_warnings": True,
        })

        self.yt_opts_video = _maybe_cookie({
            "format": "(bestvideo[height<=?720][width<=?1280][ext=mp4]+bestaudio[ext=m4a])/best",
            "outtmpl": "downloads/%(id)s.%(ext)s",
            "geo_bypass": True,
            "nocheckcertificate": True,
            "quiet": True,
            "no_warnings": True,
        })

        self.yt_playlist_opts = _maybe_cookie({
            "extract_flat": True,
            "quiet": True,
            "no_warnings": True,
        })

        # Lyrics
        self.lyrics = getattr(Config, "LYRICS_API", None)
        try:
            self.client = Genius(self.lyrics, remove_section_headers=True) if self.lyrics else None
        except Exception as e:
            LOGS.warning(f"[Exception in Lyrics API]: {e}")
            self.client = None

        # ensure downloads dir exists
        os.makedirs("downloads", exist_ok=True)

        # final check: at least one method should be available
        if not self.USE_API and not self.USE_COOKIES:
            LOGS.warning("Both API and cookies disabled — downloads will fail unless you enable one.")

    def shorten_title(self, title: str) -> str:
        title = re.sub(r"\(.*?\)|\[.*?\]", "", title)
        remove_words = [
            r"full video", r"official video", r"lyrics", r"video song",
            r"audio song", r"punjabi songs \d{4}", r"song \d{4}", r"hd", r"4k"
        ]
        for word in remove_words:
            title = re.sub(word, "", title, flags=re.IGNORECASE)
        title = re.sub(r"\b(ft|feat)\.?.*", "", title, flags=re.IGNORECASE)
        title = title.split("|")[0]
        title = re.sub(r"\s+", " ", title).strip()
        if "-" in title:
            parts = [p.strip() for p in title.split("-")]
            if len(parts) >= 2:
                return f"{parts[0]} - {parts[1]}"
        return title

    def check(self, link: str):
        return bool(re.match(self.regex, link))

    async def format_link(self, link: str, video_id: bool) -> str:
        link = link.strip()
        if video_id:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        return link

    async def get_file_from_api(self, video_id: str, audio: bool = True) -> str:
        if not self.USE_API or not self.YOUR_API_URL:
            return None
        endpoint = "/download/audio" if audio else "/download/video"
        url = f"{self.YOUR_API_URL.rstrip('/')}{endpoint}"
        params = {"video_id": video_id}
        headers = {"x-api-key": self.YOUR_API_KEY} if self.YOUR_API_KEY else {}
        try:
            async with httpx.AsyncClient(timeout=180) as client:
                response = await client.get(url, params=params, headers=headers)
                if response.status_code == 200:
                    ext = "m4a" if audio else "mp4"
                    os.makedirs("downloads", exist_ok=True)
                    file_path = f"downloads/{video_id}.{ext}"
                    with open(file_path, "wb") as f:
                        f.write(response.content)
                    return file_path
                else:
                    LOGS.error(f"API Error: {response.status_code} {response.text}")
                    return None
        except Exception as e:
            LOGS.error(f"API download failed for video_id {video_id}: {e}")
            return None

    async def get_data(self, link: str, video_id: bool, limit: int = 1) -> list:
        yt_url = await self.format_link(link, video_id)
        collection = []
        if self.USE_API and self.YOUR_API_KEY and self.YOUR_API_URL:
            try:
                params = {
                    "key": self.YOUR_API_KEY,
                    "part": "snippet,contentDetails,statistics",
                    "id": yt_url.split("v=")[1] if "watch?v=" in yt_url else yt_url.split("/")[-1]
                }
                response = requests.get(self.YOUR_API_URL, params=params, timeout=30)
                response.raise_for_status()
                data = response.json()
                if not data.get("items"):
                    LOGS.warning(f"No items found in API response for {yt_url}")
                    return []

                for item in data["items"]:
                    snippet = item["snippet"]
                    content_details = item["contentDetails"]
                    stats = item["statistics"]
                    vid = item["id"]
                    channel = snippet["channelTitle"]
                    channel_url = f"https://www.youtube.com/channel/{snippet['channelId']}"
                    duration = content_details["duration"]
                    published = snippet["publishedAt"]
                    thumbnail = snippet["thumbnails"]["high"]["url"]
                    title = self.shorten_title(snippet["title"])
                    views = stats.get("viewCount", "0")
                    duration_match = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", content_details["duration"])
                    if duration_match:
                        hours = int(duration_match.group(1) or 0)
                        minutes = int(duration_match.group(2) or 0)
                        seconds = int(duration_match.group(3) or 0)
                        duration = f"{hours:02d}:{minutes:02d}:{seconds:02d}" if hours else f"{minutes}:{seconds:02d}"

                    from datetime import datetime
                    publish_time = datetime.strptime(published, "%Y-%m-%dT%H:%M:%SZ")
                    publish_time = publish_time.strftime('%d{} of %B, %Y').format(
                        'th' if 4 <= publish_time.day <= 20 or 24 <= publish_time.day <= 30 else ['st', 'nd', 'rd'][(publish_time.day - 1) % 10 % 3]
                    )

                    context = {
                        "id": vid,
                        "ch_link": channel_url,
                        "channel": channel,
                        "duration": duration,
                        "link": yt_url,
                        "published": publish_time,
                        "thumbnail": thumbnail,
                        "title": title,
                        "views": f"{int(views):,}",
                    }
                    collection.append(context)
            except Exception as e:
                LOGS.error(f"Error in YouTube API for {yt_url}: {e}")
                # Fallback to youtubesearchpython
        try:
            results = VideosSearch(yt_url, limit=limit)
            for result in (await results.next())["result"]:
                required_fields = ["id", "channel", "duration", "publishedTime", "title", "link", "viewCount"]
                if not all(field in result for field in required_fields) or not all(
                    field in result["channel"] for field in ["name", "link"]
                ) or not isinstance(result["viewCount"], dict) or "short" not in result["viewCount"]:
                    LOGS.warning(f"Malformed result for {yt_url}: Missing fields in {result}")
                    continue

                vid = result["id"]
                channel = result["channel"]["name"]
                channel_url = result["channel"]["link"]
                duration = result["duration"]
                published = result["publishedTime"]
                thumbnail = f"https://i.ytimg.com/vi/{result['id']}/hqdefault.jpg"
                title = self.shorten_title(result["title"])
                url = result["link"]
                views = result["viewCount"]["short"]

                publish_time = "Unknown"
                try:
                    ydl_opts = {"quiet": True}
                    if self.USE_COOKIES and os.path.exists(self.cookies_file):
                        ydl_opts["cookiefile"] = self.cookies_file
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        info = ydl.extract_info(url, download=False)
                        upload_date = info.get("upload_date")
                        if upload_date:
                            from datetime import datetime
                            date_obj = datetime.strptime(upload_date, "%Y%m%d")
                            publish_time = date_obj.strftime('%d{} of %B, %Y').format(
                                'th' if 4 <= date_obj.day <= 20 or 24 <= date_obj.day <= 30 else ['st', 'nd', 'rd'][(date_obj.day - 1) % 10 % 3]
                            )
                except Exception as e:
                    LOGS.error(f"Failed to fetch publish date for {url}: {e}")

                context = {
                    "id": vid,
                    "ch_link": channel_url,
                    "channel": channel,
                    "duration": duration,
                    "link": url,
                    "published": publish_time,
                    "thumbnail": thumbnail,
                    "title": title,
                    "views": views,
                }
                collection.append(context)
        except Exception as e:
            LOGS.error(f"Error in get_data for {yt_url}: {e}")
            return []
        return collection[:limit]

    async def get_playlist(self, link: str) -> list:
        yt_url = await self.format_link(link, False)
        if self.USE_API and self.YOUR_API_KEY and self.YOUR_API_URL:
            try:
                playlist_id = yt_url.split("list=")[1] if "list=" in yt_url else yt_url
                params = {
                    "key": self.YOUR_API_KEY,
                    "part": "contentDetails",
                    "playlistId": playlist_id,
                    "maxResults": 50
                }
                playlist = []
                while True:
                    response = requests.get(f"{self.YOUR_API_URL}/playlistItems", params=params, timeout=30)
                    response.raise_for_status()
                    data = response.json()
                    playlist.extend([item["contentDetails"]["videoId"] for item in data["items"]])
                    if "nextPageToken" not in data:
                        break
                    params["pageToken"] = data["nextPageToken"]
                return playlist
            except Exception as e:
                LOGS.error(f"Failed to extract playlist via API: {e}")
        try:
            with yt_dlp.YoutubeDL(self.yt_playlist_opts) as ydl:
                results = ydl.extract_info(yt_url, download=False)
                playlist = [video['id'] for video in results['entries'] if video.get('id')]
            return playlist
        except Exception as e:
            LOGS.error(f"Failed to extract playlist: {e}")
            return []

    async def download(self, link: str, video_id: bool, video: bool = False) -> str:
        yt_url = await self.format_link(link, video_id)
        vid_token = yt_url.split("v=")[-1] if "v=" in yt_url else yt_url.rstrip("/").split("/")[-1]

        use_api = False
        if self.USE_API and self.USE_COOKIES:
            use_api = random.choice([True, False])
        elif self.USE_API:
            use_api = True

        if use_api:
            file_path = await self.get_file_from_api(vid_token, audio=not video)
            if file_path:
                return file_path
            else:
                LOGS.error("API download failed, falling back to yt-dlp")

        try:
            opts = dict(self.yt_opts_video if video else self.yt_opts_audio)
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(yt_url, download=True)
                filename = ydl.prepare_filename(info)
                if os.path.exists(filename):
                    return filename
                else:
                    candidate = None
                    base = os.path.join("downloads", info.get("id", vid_token))
                    for f in os.listdir("downloads"):
                        if f.startswith(info.get("id", vid_token)):
                            candidate = os.path.join("downloads", f)
                            break
                    if candidate:
                        return candidate
                    return filename
        except Exception as e:
            LOGS.error(f"Download failed for {yt_url}: {e}")
            raise

    async def send_song(
        self, message: CallbackQuery, rand_key: str, key: int, video: bool = False
    ) -> None:
        track_list = Config.SONG_CACHE.get(rand_key, [])
        if key >= len(track_list):
            LOGS.error(f"Invalid key {key} for rand_key {rand_key}")
            await message.message.reply_text("Invalid song data, please try again.")
            return
        track = track_list[key]
        required_fields = ["id", "link", "thumbnail", "title", "views", "duration"]
        if not isinstance(track, dict) or not all(field in track for field in required_fields):
            LOGS.error(f"Invalid track data for rand_key {rand_key}, key {key}: {track}")
            await message.message.reply_text("Invalid song data! Please try again.")
            return

        Pbx = await message.message.reply_text("Downloading...")
        try:
            thumb_path = None
            try:
                thumb_path = f"{track['id']}_{int(time.time())}.jpg"
                r = requests.get(track["thumbnail"], timeout=20)
                r.raise_for_status()
                with open(thumb_path, "wb") as th:
                    th.write(r.content)
            except Exception:
                thumb_path = None

            output = await self.download(track["link"], video_id=False, video=video)

            try:
                with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
                    info = ydl.extract_info(track["link"], download=False)
            except Exception:
                info = {"duration": int(track.get("duration", 0) or 0), "title": track.get("title", "")}

            if not video:
                await message.message.reply_audio(
                    audio=output,
                    caption=TEXTS.SONG_CAPTION.format(
                        track["title"],
                        track["link"],
                        track["views"],
                        track["duration"],
                        message.from_user.mention,
                        PbxBot.app.mention,
                    ),
                    duration=int(info.get("duration", 0) or 0),
                    performer=TEXTS.PERFORMER,
                    title=info.get("title", track["title"]),
                    thumb=thumb_path,
                )
            else:
                await message.message.reply_video(
                    video=output,
                    caption=TEXTS.SONG_CAPTION.format(
                        track["title"],
                        track["link"],
                        track["views"],
                        track["duration"],
                        message.from_user.mention,
                        PbxBot.app.mention,
                    ),
                    duration=int(info.get("duration", 0) or 0),
                    thumb=thumb_path,
                    supports_streaming=True,
                )

            chat = message.message.chat.title or message.message.chat.first_name
            await PbxBot.logit(
                "Video" if video else "Audio",
                f"**⤷ User:** {message.from_user.mention} [`{message.from_user.id}`]\n"
                f"**⤷ Chat:** {chat} [`{message.message.chat.id}`]\n"
                f"**⤷ Link:** [{track['title']}]({track['link']})",
            )
            await Pbx.delete()
        except Exception as e:
            LOGS.error(f"Error in send_song for rand_key {rand_key}, key {key}: {e}")
            try:
                await Pbx.edit_text(f"**Error:**\n`{e}`")
            except Exception:
                pass
        finally:
            try:
                Config.SONG_CACHE.pop(rand_key, None)
            except Exception:
                pass
            for path in (thumb_path if isinstance(thumb_path, str) else [], [output] if isinstance(output, str) else []):
                try:
                    if isinstance(path, str) and os.path.exists(path):
                        os.remove(path)
                except Exception:
                    pass

    async def get_lyrics(self, song: str, artist: str) -> dict:
        context = {}
        if not self.client:
            return context
        try:
            results = self.client.search_song(song, artist)
            if results:
                data = results.to_dict() if hasattr(results, "to_dict") else results
                context = {
                    "title": data.get("full_title"),
                    "image": data.get("song_art_image_url"),
                    "lyrics": data.get("lyrics"),
                }
        except Exception as e:
            LOGS.warning(f"Failed to fetch lyrics: {e}")
        return context

ytube = YouTube()
 
