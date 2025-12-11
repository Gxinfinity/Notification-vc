# main.py
import logging
from datetime import datetime
import requests
from pyrogram import Client, errors
from pyrogram.raw.types import UpdateGroupCallParticipants, PeerChannel

# ---------------- CONFIG -----------------
API_ID = 32218311
API_HASH = "f64e1a0fc206f1ac94d11cc699ad1080"
STRING_SESSION = ""        # your session string
BOT_TOKEN = ""             # optional

TARGET_GROUP_ID = -1002385742084   # VC group
ADMIN_USER_IDS = [7990456522]      # DM admins
# -----------------------------------------

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
log = logging.getLogger("vc")

# 🚀 FIX: disable Pyrogram auto-parsers to stop Peer ID crashes
app = Client(
    "vc_fixed",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=STRING_SESSION,
    handle_updates=False,    # <<< MOST IMPORTANT FIX
    parse_mode=None,
    workers=1
)

# Safe bot sender
def bot_send(chat, text):
    if not BOT_TOKEN:
        return False
    try:
        r = requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data={"chat_id": chat, "text": text, "parse_mode": "Markdown"},
            timeout=5
        )
        return r.status_code == 200
    except:
        return False

# Extract chat_id safely (NO CRASH)
def safe_chat_id(update):
    try:
        call = update.call
        peer = getattr(call, "peer", None)
        if peer and isinstance(peer, PeerChannel):
            return int(f"-100{peer.channel_id}")
    except:
        return None
    return None

# Format user info
def format_user(u):
    uname = f"@{u.username}" if u.username else f"[{u.first_name}](tg://user?id={u.id})"
    return (
        f"👤 **User Joined VC**\n"
        f"Name: {u.first_name}\n"
        f"Username: {uname}\n"
        f"User ID: `{u.id}`\n"
        f"Link: tg://user?id={u.id}"
    )

# RAW VC UPDATE HANDLER
@app.on_raw_update()
async def raw_handler(client, update, users, chats):

    if not isinstance(update, UpdateGroupCallParticipants):
        return

    chat_id = safe_chat_id(update)
    if chat_id != TARGET_GROUP_ID:
        return

    for p in update.participants:
        if not getattr(p, "just_joined", False):
            continue

        try:
            u = await client.get_users(p.user_id)
        except:
            continue

        ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

        msg = (
            f"{format_user(u)}\n\n"
            f"Group: `{chat_id}`\n"
            f"Time: {ts}"
        )

        # SEND TO GROUP
        if bot_send(chat_id, msg):
            log.info("Sent via bot")
        else:
            try:
                await client.send_message(chat_id, msg)
                log.info("Sent via user fallback")
            except Exception as e:
                log.warning(f"Group send failed: {e}")

        # DM ADMINS
        for admin in ADMIN_USER_IDS:
            try:
                await client.send_message(admin, msg)
            except:
                pass

        log.info(f"Handled VC join for {u.id}")

if __name__ == "__main__":
    log.info("🔥 VC Hybrid Userbot Started — Crash-Proof Mode")
    app.run()