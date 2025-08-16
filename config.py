import random
from os import getenv
from dotenv import load_dotenv
from pyrogram import filters

load_dotenv()


class Config(object):
    # ==================== REQUIRED CONFIG VARIABLES ==================== #

    API_HASH = getenv("API_HASH", None)                                # Get from my.telegram.org
    
    API_ID = int(getenv("API_ID", 0))                                 # Get from my.telegram.org
    
    BOT_TOKEN = getenv("BOT_TOKEN", None)                             # Get from @BotFather
    
    DATABASE_URL = getenv("DATABASE_URL", None)                       # From https://cloud.mongodb.com/
    
    PBXBOT_SESSION = getenv("PBXBOT_SESSION", None)                  # Enter your session string here
    
    LOGGER_ID = int(getenv("LOGGER_ID", 0))                          # Make a channel and get its ID
    
    OWNER_ID = getenv("OWNER_ID", "")                                 # Enter your Telegram ID here
    

    # ==================== OPTIONAL CONFIG VARIABLES ==================== #

    UPSTREAM_BRANCH = "Bad"                                        # Default branch for git pull (e.g., "main" or "master")
    
    UPSTREAM_REPO = "https://github.com/Badmunda05/Music"               # Your repository URL without .git
    
    GITHUB_TOKEN = None                                               # Optional: GitHub token for private repos
    
    

    # ==================== API / COOKIES ==================== #

    YOUR_API_KEY = getenv("YOUR_API_KEY", "")  # Your custom API key
    
    YOUR_API_URL = getenv("YOUR_API_URL", "")        # Your custom API URL
    
    COOKIES_URL = getenv("COOKIES_URL", "https://raw.githubusercontent.com/")  # Cookies file link (if required)
    
    USE_API = getenv("USE_API", "False").lower() == "true"            # True = Stream on api
    
    USE_COOKIES = getenv("USE_COOKIES", "True").lower() == "true"     # True = cookies.txt use, Stream on cookies
    
    

    # ==================== IMAGE LINKS ==================== #

    BLACK_IMG = getenv("BLACK_IMG", "https://telegra.ph/file/2c546060b20dfd7c1ff2d.jpg")  # Black image for progress
    

    ABHI_IMAGES = [
    
        "https://files.catbox.moe/6yol2e.jpg",
        
        "https://files.catbox.moe/0jtgzm.jpg",
        
        "https://files.catbox.moe/rx1jwu.jpg",
        
        "https://files.catbox.moe/u6afbs.jpg",
        
        'https://files.catbox.moe/29vkpe.jpg",
        
        "https://files.catbox.moe/m9v3hr.jpg",
        
        "https://files.catbox.moe/d7455d.jpg",
        
        "https://files.catbox.moe/zcp26o.jpg",
        
        "https://files.catbox.moe/wq2vky.jpg",
        
        "https://files.catbox.moe/46oi6f.jpg",
    ]
    
    BAD_IMAGES = [
    
        "https://files.catbox.moe/6yol2e.jpg",
        
        "https://files.catbox.moe/0jtgzm.jpg"
        ,
        "https://files.catbox.moe/rx1jwu.jpg",
        
        "https://files.catbox.moe/u6afbs.jpg"
        ,
        'https://files.catbox.moe/29vkpe.jpg",
        
        "https://files.catbox.moe/m9v3hr.jpg",
        
        "https://files.catbox.moe/d7455d.jpg",
        
        "https://files.catbox.moe/zcp26o.jpg",
        
        "https://files.catbox.moe/wq2vky.jpg",
        
        "https://files.catbox.moe/46oi6f.jpg",
        
    ]
    
    SHIZU_IMAGES = [
    
        "https://files.catbox.moe/enx1q3.jpg",
    ]
    

    BOT_PIC = getenv("BOT_PIC", random.choice(SHIZU_IMAGES))          # Bot profile picture
    
    HELP_PIC = getenv("HELP_PIC", random.choice(BAD_IMAGES))          # Help menu image
    
    START_PIC = getenv("START_PIC", random.choice(ABHI_IMAGES))       # Start command image
    
    TELEGRAM_IMG = getenv("TELEGRAM_IMG", None)                       # Optional Telegram image
    
    

    # ==================== BOT SETTINGS ==================== #

    BOT_NAME = getenv("BOT_NAME", "Pbx Music")                       # Keep plain text, avoid fancy fonts
    
    LEADERBOARD_TIME = getenv("LEADERBOARD_TIME", "3:00")            # Time in 24hr format for leaderboard broadcast
    
    LYRICS_API = getenv("LYRICS_API", None)                          # From https://docs.genius.com/
    
    MAX_FAVORITES = int(getenv("MAX_FAVORITES", 30))                 # Max number of favorite tracks
    
    PLAY_LIMIT = int(getenv("PLAY_LIMIT", 0))                        # Play time limit (minutes) | 0 = no limit
    
    SONG_LIMIT = int(getenv("SONG_LIMIT", 0))                        # Song duration limit (minutes) | 0 = no limit
    
    PRIVATE_MODE = getenv("PRIVATE_MODE", "off")                     # "on" or "off" for private mode
    
    

    # ==================== FILE SIZE LIMITS ==================== #

    TG_AUDIO_SIZE_LIMIT = int(getenv("TG_AUDIO_SIZE_LIMIT", 104857600))  # Audio size limit (bytes)
    
    TG_VIDEO_SIZE_LIMIT = int(getenv("TG_VIDEO_SIZE_LIMIT", 1073741824)) # Video size limit (bytes)
    
    

    # ==================== OTHER SETTINGS ==================== #

    TZ = getenv("TZ", "Asia/Kolkata")                                # Timezone (https://en.wikipedia.org/wiki/List_of_tz_database_time_zones)
    
    

    # ==================== DO NOT EDIT BELOW ==================== #

    BANNED_USERS = filters.user()
    
    CACHE = {}
    
    CACHE_DIR = "./cache/"
    
    DELETE_DICT = {}
    
    DWL_DIR = "./downloads/"
    
    GOD_USERS = filters.user()
    
    PLAYER_CACHE = {}
    
    QUEUE_CACHE = {}
    
    SONG_CACHE = {}
    
    SUDO_USERS = filters.user()
    

# Get all config variables in a list

all_vars = [i for i in Config.__dict__.keys() if not i.startswith("__")]
