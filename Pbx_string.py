import os
import base64
import random
import struct
import sys

try:
    from pyrogram import Client as PClient
except:
    os.system("pip install pyrogram")
    from pyrogram import Client as PClient


def main():
    print("ᴛ ᴇ ᴀ ᴍ    ᴘ ʙ x   ! !")
    print("ʜᴇʟʟᴏ!! ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ ᴘʙxʙᴏᴛ sᴇssɪᴏɴ ɢᴇɴᴇʀᴀᴛᴏʀ\n")
    print("ʜᴜᴍᴀɴ ᴠᴇʀɪꜰɪᴄᴀᴛɪᴏɴ ʀᴇQᴜɪʀᴇᴅ !!")
    while True:
        verify = int(random.randint(1, 50))
        okvai = int(input(f"ᴇɴᴛᴇʀ {verify} ᴛᴏ ᴄᴏɴᴛɪɴᴜᴇ: "))
        if okvai == verify:
            generate_pyro_session()
            break
        else:
            print("ᴠᴇʀɪꜰɪᴄᴀᴛɪᴏɴ ꜰᴀɪʟᴇᴅ! ᴛʀʏ ᴀɢᴀɪɴ:")


def generate_pyro_session():
    print("ᴘʏʀᴏɢʀᴀᴍ sᴇssɪᴏɴ ꜰᴏʀ ᴘʙxᴍᴜsɪᴄ ʙᴏᴛ!")
    APP_ID = int(input("\nᴇɴᴛᴇʀ ᴀᴘᴘ ɪᴅ ʜᴇʀᴇ: "))
    API_HASH = input("\nᴇɴᴛᴇʀ ᴀᴘɪ ʜᴀsʜ ʜᴇʀᴇ: ")
    with PClient(name="pbxuser", api_id=APP_ID, api_hash=API_HASH, in_memory=True) as pbxbot:
        print("\nʏᴏᴜʀ ᴘʙxʙᴏᴛ sᴇssɪᴏɴ ɪs sᴇɴᴛ ɪɴ ʏᴏᴜʀ ᴛᴇʟᴇɢʀᴀᴍ sᴀᴠᴇᴅ ᴍᴇssᴀɢᴇs.")
        session = pbxbot.export_session_string()
        pbx_session = pbxbot_session(session)
        pbxbot.send_message(
            "me",
            f"#PBXBOT #PYROGRAM\n\n`{pbx_session}`",
        )


def pbxbot(text):
    res = ''.join(
        map(
            random.choice,
            zip(text.lower(), text.upper()),
        )
    )
    return res.strip()


def pbxbot_session(session):
    # ᴄᴏɴꜰɪɢᴜʀɪɴɢ ᴘʏʀᴏɢʀᴀᴍ sᴇssɪᴏɴ ꜰᴏʀᴍᴀᴛ
    pyro_format = {
        351: ">B?256sI?",
        356: ">B?256sQ?",
        362: ">BI?256sQ?",
    }

    # ᴇʀʀᴏʀ ᴍᴇssᴀɢᴇ ꜰᴏʀ sᴇssɪᴏɴ ɢᴇɴᴇʀᴀᴛɪᴏɴ ꜰᴀɪʟᴜʀᴇ
    error_msg = "ᴇʀʀᴏʀ ɪɴ ɢᴇɴᴇʀᴀᴛɪɴɢ sᴇssɪᴏɴ! ʀᴇᴘᴏʀᴛ ɪᴛ ɪɴ ᴘʙx ᴄʜᴀᴛs @ᴘʙx_ᴄʜᴀᴛ"

    # ᴄᴏɴᴠᴇʀᴛɪɴɢ ᴘʏʀᴏɢʀᴀᴍ sᴇssɪᴏɴ
    if len(session) in pyro_format.keys():
        if len(session) in [351, 356]:
            dc_id, _, auth_key, _, _ = struct.unpack(
                pyro_format[len(session)],
                base64.urlsafe_b64decode(session + "=" * (-len(session) % 4)),
            )
        else:
            dc_id, _, _, auth_key, _, _ = struct.unpack(
                pyro_format[len(session)],
                base64.urlsafe_b64decode(session + "=" * (-len(session) % 4)),
            )

        # ᴄᴏɴᴠᴇʀᴛ ᴛᴏ ᴀ ᴄᴏᴍᴘᴀᴛɪʙʟᴇ sᴇssɪᴏɴ sᴛʀɪɴɢ
        new_session = base64.urlsafe_b64encode(
            struct.pack(">B256s", dc_id, auth_key)
        ).decode().rstrip("=")

        # ✅ ꜰɪxᴇᴅ ꜰᴏʀᴍᴀᴛ: ==ʙᴏᴛ <sᴇssɪᴏɴ> ʙᴀᴅ==
        return f"==Bot {new_session} Bad=="

    else:
        print(error_msg)
        sys.exit()


if __name__ == "__main__":
    main()
