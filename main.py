from pyrogram import Client
from pyrogram.raw.types import UpdateGroupCallParticipants

# ====== CONFIG ======
api_id = 32218311
api_hash = "f64e1a0fc206f1ac94d11cc699ad1080"

# Your string session (PASTE HERE)
string_session = ""
# =====================

app = Client(
    name="vc_userbot",
    api_id=api_id,
    api_hash=api_hash,
    session_string=string_session
)

@app.on_raw_update()
async def vc_handler(client, update, users, chats):
    try:
        if isinstance(update, UpdateGroupCallParticipants):

            chat_id = update.chat_id

            for p in update.participants:

                # detect new join
                if getattr(p, "just_joined", False):

                    user = await client.get_users(p.user_id)

                    username_link = (
                        f"@{user.username}"
                        if user.username
                        else f"[{user.first_name}](tg://user?id={user.id})"
                    )

                    await client.send_message(
                        chat_id,
                        f"🎧 **VC Join Alert:** {username_link} VC me join hua!"
                    )

    except Exception as e:
        print("Error:", e)

print("🔥 USERBOT VC ALERT IS RUNNING…")
app.run()