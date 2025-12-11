# main.py
import time
import logging
import requests
from datetime import datetime
from pyrogram import Client, errors
from pyrogram.raw.types import UpdateGroupCallParticipants, PeerChannel, PeerChat

# ----------------- CONFIG -----------------
API_ID = 32218311
API_HASH = "f64e1a0fc206f1ac94d11cc699ad1080"

# Put your Pyrogram v2 string session here (recommended)
STRING_SESSION = ""

# Optional: Bot token if you want messages to appear from a bot account too.
BOT_TOKEN = ""

# The group where you want VC alerts (must be integer like -1001234567890)
TARGET_GROUP_ID = -1002385742084

# List of admin user ids (integers) who should get DM via user account
ADMIN_USER_IDS = [7990456522]   # example, replace with your Telegram numeric ids

# Optional: whether to also send fallback group message from the user account
FALLBACK_SEND_AS_USER = True
# ------------------------------------------

# logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")
log = logging.getLogger("vc-hybrid")

# Initialize user Client (userbot)
app = Client(
    "vc_hybrid",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=STRING_SESSION
)

# small helper: send via Bot API (returns True if success)
def bot_send_message(chat_id: int, text: str, parse_mode: str = "Markdown"):
    if not BOT_TOKEN:
        return False, "no-bot-token"
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": str(chat_id), "text": text, "parse_mode": parse_mode, "disable_web_page_preview": True}
    try:
        r = requests.post(url, data=payload, timeout=10)
        if r.status_code == 200:
            return True, r.json()
        else:
            return False, f"bot-api-error:{r.status_code}:{r.text}"
    except Exception as e:
        return False, f"exception:{e}"

def format_user_line(user):
    uname = f"@{user.username}" if getattr(user, "username", None) else f"[{user.first_name}](tg://user?id={user.id})"
    return f"Name: {user.first_name}\nUsername: {uname}\nUser ID: `{user.id}`\nLink: tg://user?id={user.id}"

def extract_chat_id_from_update(update):
    # Robust extraction of chat id from raw update
    try:
        call = update.call
        # many update.call structures; try common path
        peer = getattr(call, "default_subscriber", None)
        if peer is None:
            # sometimes call has 'call' attribute with peer inside
            peer = getattr(call, "call", None)
        if peer is None:
            return None
        # peer may itself have .peer which is PeerChannel/PeerChat
        raw_peer = getattr(peer, "peer", peer)
        if isinstance(raw_peer, PeerChannel):
            return int(f"-100{raw_peer.channel_id}")
        if isinstance(raw_peer, PeerChat):
            return raw_peer.chat_id
    except Exception:
        return None
    return None

async def notify_all(chat_id: int, text: str):
    # 1) Try to send via bot (preferred, shows bot identity)
    if BOT_TOKEN:
        ok, resp = bot_send_message(chat_id, text)
        if ok:
            log.info("Sent via bot.")
            return True
        else:
            log.warning("Bot send failed: %s", resp)

    # 2) Fallback: send as user account
    if FALLBACK_SEND_AS_USER:
        try:
            await app.send_message(chat_id, text)
            log.info("Sent as user (fallback).")
            return True
        except errors.ChatWriteForbidden:
            log.warning("User account not allowed to send in chat (write forbidden).")
            return False
        except Exception as e:
            log.exception("User send failed: %s", e)
            return False
    return False

async def dm_admins(text: str):
    for admin in ADMIN_USER_IDS:
        try:
            await app.send_message(admin, text)
        except Exception as e:
            log.warning("Failed to DM admin %s: %s", admin, e)

@app.on_raw_update()
async def raw_update_handler(client, update, users, chats):
    # Only care about VC participant updates
    try:
        if not isinstance(update, UpdateGroupCallParticipants):
            return

        # Extract chat id directly
        chat_id = extract_chat_id_from_update(update)
        if chat_id is None:
            return

        # Only target group
        if chat_id != TARGET_GROUP_ID:
            return

        # For each participant event, check just_joined
        for p in update.participants:
            if getattr(p, "just_joined", False):
                # Fetch full user info
                try:
                    u = await client.get_users(p.user_id)
                except Exception as e:
                    log.warning("Could not fetch user %s: %s", p.user_id, e)
                    continue

                ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
                user_line = format_user_line(u)
                message = (
                    f"🎧 *VC Join Alert*\n\n{user_line}\n\n"
                    f"Group: `{chat_id}`\nTime: {ts}\n\n"
                    f"— Detected by userbot"
                )

                # Send to group (bot preferred) and DM admins (from user)
                sent_group = await notify_all(chat_id, message)
                # Also DM admins via user account for guaranteed delivery
                await dm_admins(message)

                log.info("Handled VC join for %s, sent_group=%s", p.user_id, sent_group)

    except Exception as exc:
        # Keep bot alive, log exception
        log.exception("raw_update_handler exception: %s", exc)
        return

if __name__ == "__main__":
    log.info("Starting VC hybrid notifier...")
    app.run()