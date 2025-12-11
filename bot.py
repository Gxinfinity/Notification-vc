from pyrogram import Client, errors
from pyrogram.raw.types import (
    UpdateGroupCallParticipants,
    UpdateNewMessage,
    PeerChannel,
    PeerChat,
)

api_id = 32218311
api_hash = "f64e1a0fc206f1ac94d11cc699ad1080"

string_session = "YOUR_SESSION_STRING_HERE"

TARGET_GROUP_ID = -1002385742084

app = Client(
    "vc_alert_fixed",
    api_id=api_id,
    api_hash=api_hash,
    session_string=string_session
)

last_chat_id = None


def extract_chat_id(peer):
    try:
        if isinstance(peer, PeerChannel):
            return int(f"-100{peer.channel_id}")
        if isinstance(peer, PeerChat):
            return peer.chat_id
    except:
        return None
    return None


@app.on_raw_update()
async def handler(client, update, users, chats):

    global last_chat_id

    # ------------ Ignore ALL Pyrogram internal crashes here ------------
    try:

        # Store last chat id
        if isinstance(update, UpdateNewMessage):
            try:
                cid = extract_chat_id(update.message.peer_id)
                if cid:
                    last_chat_id = cid
            except:
                pass

        # VC participants
        if isinstance(update, UpdateGroupCallParticipants):

            if not last_chat_id:
                return

            if last_chat_id != TARGET_GROUP_ID:
                return

            for p in update.participants:

                if getattr(p, "just_joined", False):

                    try:
                        u = await client.get_users(p.user_id)
                    except:
                        continue

                    tag = (
                        f"@{u.username}"
                        if u.username else
                        f"[{u.first_name}](tg://user?id={u.id})"
                    )

                    try:
                        await client.send_message(
                            TARGET_GROUP_ID,
                            f"🎧 **VC Join Alert:** {tag} VC me join hua!"
                        )
                    except errors.ChatWriteForbidden:
                        return
                    except:
                        continue

    except Exception:
        # ignore everything silently (prevent ALL crashes)
        pass


print("🔥 VC Alert Userbot Running — No More Peer Errors…")
app.run()