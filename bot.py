from pyrogram import Client
from pyrogram.raw.types import (
    UpdateGroupCallParticipants,
)
import asyncio

api_id = 32218311
api_hash = "f64e1a0fc206f1ac94d11cc699ad1080"
string_session = "YOUR_SESSION_STRING_HERE"

# Your group only
TARGET_GROUP_ID = -1002385742084

app = Client(
    "vc_alert_fixed",
    api_id=api_id,
    api_hash=api_hash,
    session_string=string_session
)


@app.on_raw_update()
async def vc_alert_handler(client, update, users, chats):

    # -- Only handle participant events --
    if not isinstance(update, UpdateGroupCallParticipants):
        return

    # Extract chat/channel from raw update (safe way)
    chat_raw = update.call.default_subscriber and update.call.default_subscriber.peer

    if not chat_raw:
        return

    # Convert raw peer → normal chat_id
    if hasattr(chat_raw, "channel_id"):
        chat_id = int(f"-100{chat_raw.channel_id}")
    elif hasattr(chat_raw, "chat_id"):
        chat_id = chat_raw.chat_id
    else:
        return

    # Ignore all other chats
    if chat_id != TARGET_GROUP_ID:
        return

    # Loop participants
    for p in update.participants:
        if getattr(p, "just_joined", False):

            # Get user info
            try:
                u = await client.get_users(p.user_id)
            except:
                continue

            if u.username:
                tag = f"@{u.username}"
            else:
                tag = f"[{u.first_name}](tg://user?id={u.id})"

            # Send message
            try:
                await client.send_message(
                    TARGET_GROUP_ID,
                    f"🎧 **VC Join Alert:** {tag} VC me join hua!"
                )
            except Exception as e:
                print("Send Error:", e)


print("🔥 VC Alert Userbot Running — Only Your Group, No Errors")
app.run()