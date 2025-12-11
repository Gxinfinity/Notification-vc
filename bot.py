from pyrogram import Client
from pyrogram.raw.types import UpdateGroupCallParticipants, PeerChannel
import traceback

api_id = 32218311
api_hash = "f64e1a0fc206f1ac94d11cc699ad1080"
string_session = "YOUR_SESSION_STRING"

TARGET_GROUP_ID = -1002385742084   # Your group

app = Client(
    "vc_alert",
    api_id=api_id,
    api_hash=api_hash,
    session_string=string_session
)


def get_chat_id_from_update(update):
    try:
        call = update.call
        peer = call.call.peer
        if isinstance(peer, PeerChannel):
            return int(f"-100{peer.channel_id}")
    except:
        return None
    return None


@app.on_raw_update()
async def raw_handler(client, update, users, chats):

    # -------- SILENCE ALL ERRORS --------
    try:

        if isinstance(update, UpdateGroupCallParticipants):

            chat_id = get_chat_id_from_update(update)

            if not chat_id:
                return

            if chat_id != TARGET_GROUP_ID:
                return

            for p in update.participants:
                if getattr(p, "just_joined", False):

                    try:
                        user = await client.get_users(p.user_id)
                    except:
                        continue

                    tag = (
                        f"@{user.username}" if user.username else f"[{user.first_name}](tg://user?id={user.id})"
                    )

                    try:
                        await client.send_message(
                            chat_id,
                            f"🎧 **VC Join Alert:** {tag} VC me join hua!"
                        )
                    except:
                        pass

    except Exception:
        # Background update errors ko silent ignore
        pass


print("🔥 FINAL VC ALERT BOT RUNNING — NO CRASH, NO PEER ERROR…")
app.run()