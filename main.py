#!/usr/bin/env python3
# main_single.py
"""
Notification-vc — Single-file hybrid VC join notifier (userbot + optional bot).
Paste your values into the CONFIG section and run:
    python3 main_single.py
"""

import logging
import signal
import sys
from datetime import datetime

import requests
from pyrogram import Client
from pyrogram.raw.types import UpdateGroupCallParticipants, PeerChannel

# --------------------- CONFIG (EDIT THIS) ---------------------
API_ID = 32218311
API_HASH = "f64e1a0fc206f1ac94d11cc699ad1080"

# Put YOUR USER string session here (required)
STRING_SESSION = ""   # <-- paste your Pyrogram v2 string session

# Optional: Bot token (if you want the message to appear from a bot)
BOT_TOKEN = ""        # e.g. "123456:ABC-DEF..."

# Target group to report VC joins (integer form, e.g. -1001234567890)
TARGET_GROUP_ID = -1002385742084

# Admin user ids to DM for guaranteed delivery (list of integers)
ADMIN_USER_IDS = [7990456522]

# If bot send fails, allow sending as the user account to the group
FALLBACK_SEND_AS_USER = True
# --------------------------------------------------------------

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)
log = logging.getLogger("notification-vc")

# Pyrogram client
app = Client(
    "notification_vc_single",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=STRING_SESSION
)

# Helper: send via Bot API (returns True/False)
def bot_send(chat_id: int, text: str) -> bool:
    if not BOT_TOKEN:
        return False
    try:
        r = requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data={
                "chat_id": str(chat_id),
                "text": text,
                "parse_mode": "Markdown",
                "disable_web_page_preview": True
            },
            timeout=8
        )
        return r.status_code == 200
    except Exception as e:
        log.debug("bot_send exception: %s", e)
        return False

# Safe extraction of the chat id from various raw shapes
def extract_chat_id_from_update(update) -> int | None:
    """
    Try several plausible raw paths to find the peer:
    - update.call.peer
    - update.call.call.peer
    - update.call.default_subscriber.peer
    Returns -100xxxxx integer if found, else None.
    """
    try:
        call = getattr(update, "call", None)
        if not call:
            return None

        # direct peer
        peer = getattr(call, "peer", None)
        if peer and isinstance(peer, PeerChannel):
            return int(f"-100{peer.channel_id}")

        # nested: call.call.peer
        inner = getattr(call, "call", None)
        if inner:
            peer2 = getattr(inner, "peer", None)
            if peer2 and isinstance(peer2, PeerChannel):
                return int(f"-100{peer2.channel_id}")

        # nested: default_subscriber -> peer
        ds = getattr(call, "default_subscriber", None)
        if ds:
            p3 = getattr(ds, "peer", None)
            if p3 and isinstance(p3, PeerChannel):
                return int(f"-100{p3.channel_id}")
    except Exception as e:
        log.debug("extract_chat_id_from_update error: %s", e)
        return None
    return None

# Format user info text (markdown)
def format_user_message(u) -> str:
    uname = f"@{u.username}" if getattr(u, "username", None) else f"[{u.first_name}](tg://user?id={u.id})"
    return (
        f"👤 **User Joined VC**\n"
        f"Name: {u.first_name}\n"
        f"Username: {uname}\n"
        f"User ID: `{u.id}`\n"
        f"Link: tg://user?id={u.id}"
    )

# Raw update handler (crash-proof)
@app.on_raw_update()
async def raw_vc_listener(client, update, users, chats):
    try:
        # We only care about UpdateGroupCallParticipants
        if not isinstance(update, UpdateGroupCallParticipants):
            return

        # Extract chat id safely without calling resolve_peer
        chat_id = extract_chat_id_from_update(update)
        if chat_id is None:
            return

        # Only your selected group
        if chat_id != TARGET_GROUP_ID:
            return

        # Loop participants for join events
        for p in update.participants:
            if not getattr(p, "just_joined", False):
                continue

            # get full user info safely
            try:
                u = await client.get_users(p.user_id)
            except Exception as e:
                log.warning("Could not fetch user %s: %s", getattr(p, "user_id", None), e)
                continue

            ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
            text = (
                f"{format_user_message(u)}\n\n"
                f"Group: `{chat_id}`\n"
                f"Time: {ts}\n\n"
                f"— Detected by userbot"
            )

            sent = False
            # 1) Try bot send first (preferred, appears as bot)
            if BOT_TOKEN:
                try:
                    sent = bot_send(chat_id, text)
                    if sent:
                        log.info("Notification sent via bot for user %s", u.id)
                except Exception as e:
                    log.debug("Bot send raised: %s", e)
                    sent = False

            # 2) Fallback: send as user account if allowed
            if not sent and FALLBACK_SEND_AS_USER:
                try:
                    await client.send_message(chat_id, text)
                    sent = True
                    log.info("Notification sent as user fallback for user %s", u.id)
                except Exception as e:
                    log.warning("Failed to send notification as user: %s", e)
                    sent = False

            # 3) Always DM admins via user account for guaranteed delivery
            for admin in ADMIN_USER_IDS:
                try:
                    await client.send_message(admin, text)
                except Exception as e:
                    log.debug("Failed DM admin %s: %s", admin, e)

            log.info("Handled VC join for %s (sent=%s)", u.id, sent)

    except Exception as e:
        # keep alive always; log debug details
        log.exception("raw_vc_listener exception: %s", e)
        return

# Graceful stop (to close session and exit cleanly)
def _sigint(sig, frame):
    log.info("Stop signal received. Stopping...")
    try:
        app.stop()
    except Exception:
        pass
    sys.exit(0)

signal.signal(signal.SIGINT, _sigint)
signal.signal(signal.SIGTERM, _sigint)

# ---------- Run ----------
if __name__ == "__main__":
    # quick check: ensure user filled session
    if not STRING_SESSION:
        log.error("STRING_SESSION is empty. Paste your Pyrogram string session at the top of this file.")
        sys.exit(1)

    log.info("Starting Notification-vc (single file) — Crash-proof mode")
    app.run()