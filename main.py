from pyrogram import Client
from pyrogram.raw.types import UpdateGroupCallParticipants

# Your Telegram API credentials
api_id = 32218311
api_hash = "f64e1a0fc206f1ac94d11cc699ad1080"

# Userbot (no bot token)
app = Client(
    "userbot_vc_session",
    api_id=api_id,
    api_hash=api_hash
)

@app.on_raw_update()
async def vc_event_handler(client, update, users, chats):
    try:
        # Detect only VC participants update
        if isinstance(update, UpdateGroupCallParticipants):

            chat_id = update.chat_id

            for p in update.participants:
                if getattr(p, "just_joined", False):

                    u = await client.get_users(p.user_id)

                    username_link = (
                        f"@{u.username}" if u.username
                        else f"[{u.first_name}](tg://user?id={u.id})"
                    )

                    await client.send_message(
                        chat_id,
                        f"🎧 **VC Join Alert:** {username_link} VC me join hua!"
                    )

    except Exception as e:
        print("Error:", e)


print("Userbot is running…")
app.run()