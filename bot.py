from pyrogram import Client
from pyrogram.raw.types import UpdateGroupCallParticipants

api_id = 32218311
api_hash = "f64e1a0fc206f1ac94d11cc699ad1080"
string_session = ""

# 👉 Only this group will receive VC notifications
TARGET_GROUP_ID = -1002385742084      # ← yaha apna group id daal

app = Client(
    "userbot_vc",
    api_id=api_id,
    api_hash=api_hash,
    session_string=string_session
)


def extract_chat_id(update):
    """Extract chat id safely"""
    try:
        # convert to -100xxxxxxxxxx format
        if update.chat_id < 0:
            return int(f"-100{abs(update.chat_id)}")
        return update.chat_id
    except:
        return None


@app.on_raw_update()
async def vc_handler(client, update, users, chats):
    # Handle only VC participant update
    if isinstance(update, UpdateGroupCallParticipants):

        chat_id = extract_chat_id(update)
        if not chat_id:
            return

        # ❌ Ignore other groups
        if chat_id != TARGET_GROUP_ID:
            return

        # load peer data (fix Peer ID invalid)
        try:
            await client.resolve_peer(chat_id)
        except:
            pass

        for p in update.participants:
            if getattr(p, "just_joined", False):

                try:
                    user = await client.get_users(p.user_id)
                except:
                    return

                username_link = (
                    f"@{user.username}"
                    if user.username
                    else f"[{user.first_name}](tg://user?id={user.id})"
                )

                await client.send_message(
                    chat_id,
                    f"🎧 **VC Join Alert:** {username_link} VC me join hua!"
                )


print("🔥 Userbot VC Alert (Only Specific Group) Running…")
app.run()