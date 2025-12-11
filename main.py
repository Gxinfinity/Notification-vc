# main.py
import logging
from datetime import datetime
import requests
from pyrogram import Client
from pyrogram.raw.types import UpdateGroupCallParticipants, PeerChannel

# ------------ CONFIG ------------
API_ID = 32218311
API_HASH = "f64e1a0fc206f1ac94d11cc699ad1080"
STRING_SESSION = ""            # put your string session here
BOT_TOKEN = ""                 # optional
TARGET_GROUP_ID = -1002385742084
ADMIN_USER_IDS = [7990456522]
# --------------------------------

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s"
)
log = logging.getLogger("vc")

# Create client (NO extra args)
app = Client(
    "vc_fixed2",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=STRING_SESSION
)


# BOT sender
def bot_send(chat, text):
    if not BOT_TOKEN:
        return False

    try:
        r = requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data={"chat_id": chat, "text": text, "parse_mode": "Markdown"},
            timeout=7
        )
        return r.status_code == 200
    except Exception as e:
        log.warning("Bot send failed: %s", e)
        return False


# Safe extraction of chat_id (raw only)
def safe_chat(update):
    try:
        peer = update.call.peer
        if isinstance(peer, PeerChannel):
            return int(f"-100{peer.channel_id}")
    except:
        return None
    return None


# Format user
def fmt_user(u):
    uname = f"@{u.username}" if u.username else f"[{u.first_name}](tg://user?id={u.id})"
    return (
        f"👤 **User Joined VC**\n"
        f"Name: {u.first_name}\n"
        f"Username: {uname}\n"
        f"User ID: `{u.id}`\n"
        f"Link: tg://user?id={u.id}"
    )


@app.on_raw_update()
async def raw_handler(client, update, users, chats):

    if not isinstance(update, UpdateGroupCallParticipants):
        return

    chat_id = safe_chat(update)
    if chat_id != TARGET_GROUP_ID:
        return

    for p in update.participants:
        if not getattr(p, "just_joined", False):
            continue

        try:
            u = await client.get_users(p.user_id)
        except:
            continue

        time_utc = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

        msg = (
            f"{fmt_user(u)}\n\n"
            f"Group: `{chat_id}`\n"
            f"Time: {time_utc}"
        )

        # try bot
        if bot_send(chat_id, msg):
            log.info("Group sent via bot")
        else:
            try:
                await client.send_message(chat_id, msg)
                log.info("Group sent via user")
            except Exception as e:
                log.warning("Group send failed: %s", e)

        # DM admins
        for admin in ADMIN_USER_IDS:
            try:
                await client.send_message(admin, msg)
            except:
                pass

        log.info("Handled VC join for %s", u.id)


if __name__ == "__main__":
    log.info("🔥 VC Userbot Started - Pyrogram v2 Stable Mode")
    app.run()