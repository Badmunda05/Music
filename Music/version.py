import platform

import time

from pyrogram import __version__ as pyro_version
from pytgcalls.__version__ import __version__ as pytgcalls_version


# Versions dictionary
__version__ = {
    "Pbx Music": "0.3.0",
    "Python": platform.python_version(),
    "Pyrogram": pyro_version,
    "PyTgCalls": pytgcalls_version,
}


# Store start time
__start_time__ = time.time()
