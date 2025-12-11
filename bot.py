from pyrogram import Client
from pyrogram.raw.types import (
    UpdateGroupCallParticipants,
    UpdateNewMessage,
    PeerChannel,
    PeerChat,
)

api_id = 32218311
api_hash = "f64e1a0fc206f1ac94d11cc699ad1080"

string_session = "YOUR_SESSION_STRING_HERE"

# Only detect this group
TARGET_GROUP_ID = -1002385742084

app = Client(
    name="vc_alert_fixed",
    api_id=api_id,
    api_hash=api_hash,
    session_string=string_session
)

last_chat_id = None


def extract_chat_id(peer):
    """Safely extract chat ID"""
    try:
        if isinstance(peer, PeerChannel):
            return int("-100" + str(peer.channel_id))
        if isinstance(peer, PeerChat):
            return peer.chat_id
    except:
        return None
    return None


async def safe_handler(client, update, users, chats):
    global last_chat_id

    # -------- Store latest chat id from messages ----------
    if isinstance(update, UpdateNewMessage):
        try:
            peer = update.message.peer_id
            cid = extract_chat_id(peer)
            if cid:
                last_chat_id = cid
        except:
            return

    # -------- Handle VC participant join ----------
    if isinstance(update, UpdateGroupCallParticipants):

        if not last_chat_id:
            return

        chat_id = last_chat_id

        if chat_id != TARGET_GROUP_ID:
            return

        for p in update.participants:
            if getattr(p, "just_joined", False):
                try:
                    user = await client.get_users(p.user_id)
                except:
                    continue

                username_link = (
                    f"@{user.username}" if user.username
                    else f"[{user.first_name}](tg://user?id={user.id})"
                )

                await client.send_message(
                    chat_id,
                    f"🎧 **VC Join Alert:** {username_link} VC me join hua!"
                )


@app.on_raw_update()
async def vc_handler(client, update, users, chats):
    """Wrapper to safely ignore all Pyrogram internal errors."""
    try:
        await safe_handler(client, update, users, chats)
    except Exception:
        return


print("🔥 VC Alert Userbot Running (Crash-Proof)…")
app.run()