from pyrogram import Client, filters

api_id = 27209067
api_hash = "0bb2571bd490320a5c9209d4bf07902e"
bot_token = ""

app = Client(
    "vc_notify_final",
    api_id=api_id,
    api_hash=api_hash,
    bot_token=bot_token
)

# Catch voice chat participant service messages
@app.on_message(filters.group & filters.service)
async def vc_join_detector(client, message):
    try:
        # Only catch "voice chat participant joined" action
        if message.voice_chat_participants_invited:
            for user in message.voice_chat_participants_invited.users:

                username_link = (
                    f"@{user.username}" if user.username
                    else f"[{user.first_name}](tg://user?id={user.id})"
                )

                await message.chat.send_message(
                    f"🎧 **VC Join Alert:** {username_link} VC me join hua!"
                )

        # Detect single-user join event
        if message.voice_chat_started or message.video_chat_started:
            await message.chat.send_message(
                "🎧 VC Started!"
            )

    except Exception as e:
        print("Error:", e)


print("BOT RUNNING…")
app.run()