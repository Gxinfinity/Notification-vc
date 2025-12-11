from pyrogram import Client
from pyrogram.raw.types import (
    UpdateGroupCallParticipants,
    UpdateNewMessage,
    PeerChannel,
    PeerChat,
    PeerUser
)

api_id = 32218311
api_hash = "f64e1a0fc206f1ac94d11cc699ad1080"
string_session = ""

# Only detect this group
TARGET_GROUP_ID = -1002385742084


app = Client(
    "vc_alert_fixed",
    api_id=api_id,
    api_hash=api_hash,
    session_string=string_session
)

last_chat_id = None


def extract_chat_id(peer):
    """Extract chat ID safely from raw peer object."""
    if isinstance(peer, PeerChannel):
        return int("-100" + str(peer.channel_id))
    if isinstance(peer, PeerChat):
        return peer.chat_id
    return None


@app.on_raw_update()
async def vc_handler(client, update, users, chats):
    global last_chat_id

    # ---- STEP 1: Track latest chat id from new messages ----
    if isinstance(update, UpdateNewMessage):
        peer = update.message.peer_id
        cid = extract_chat_id(peer)
        if cid:
            last_chat_id = cid

    # ---- STEP 2: Handle VC participants update ----
    if isinstance(update, UpdateGroupCallParticipants):

        if not last_chat_id:
            return  # still no chat detected

        chat_id = last_chat_id

        # Only your selected group
        if chat_id != TARGET_GROUP_ID:
            return

        # Loop participants
        for p in update.participants:
            if getattr(p, "just_joined", False):

                try:
                    u = await client.get_users(p.user_id)
                except:
                    continue

                username_link = (
                    f"@{u.username}" if u.username
                    else f"[{u.first_name}](tg://user?id={u.id})"
                )

                await client.send_message(
                    chat_id,
                    f"🎧 **VC Join Alert:** {username_link} VC me join hua!"
                )


print("🔥 VC Alert Userbot Running without errors…")
app.run()