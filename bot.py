from pyrogram import Client, errors
from pyrogram.raw.types import (
    UpdateGroupCallParticipants,
    PeerChannel,
)

api_id = 32218311
api_hash = "f64e1a0fc206f1ac94d11cc699ad1080"
string_session = "YOUR_SESSION_STRING_HERE"

TARGET_GROUP_ID = -1002385742084   # Your group

app = Client(
    "vc_alert_fixed",
    api_id=api_id,
    api_hash=api_hash,
    session_string=string_session
)


def extract_raw_chat_id(update):
    """
    Extract chat ID directly from the VC raw update.
    """
    try:
        call = update.call
        peer = call.call
        chat = peer.peer

        if isinstance(chat, PeerChannel):
            return int(f"-100{chat.channel_id}")
    except:
        return None

    return None


@app.on_raw_update()
async def handler(client, update, users, chats):

    try:

        # -------- HANDLE VC JOIN UPDATE --------
        if isinstance(update, UpdateGroupCallParticipants):

            chat_id = extract_raw_chat_id(update)

            # If chat detection fails → ignore update
            if not chat_id:
                return

            # Only your group
            if chat_id != TARGET_GROUP_ID:
                return

            for p in update.participants:

                if getattr(p, "just_joined", False):

                    try:
                        u = await client.get_users(p.user_id)
                    except:
                        continue

                    tag = (
                        f"@{u.username}" if u.username
                        else f"[{u.first_name}](tg://user?id={u.id})"
                    )

                    try:
                        await client.send_message(
                            chat_id,
                            f"🎧 **VC Join Alert:** {tag} VC me join hua!"
                        )
                    except:
                        pass

    except:
        pass


print("🔥 VC Alert Userbot Running — 100% VC Detection Enabled…")
app.run()