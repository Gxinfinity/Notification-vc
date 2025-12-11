from pyrogram import Client, filters

api_id = 27209067
api_hash = "0bb2571bd490320a5c9209d4bf07902e"
bot_token = ""

app = Client("vc_notify",
             api_id=api_id,
             api_hash=api_hash,
             bot_token=bot_token)

# VC join event
@app.on_raw_update()
async def vc_event_handler(client, update, users, chats):
    try:
        # Only catch voice chat participant updates
        if update._ == "updateGroupCallParticipants":
            chat_id = update.chat_id
            for p in update.participants:
                if p.just_joined:
                    u = await app.get_users(p.user_id)
                    
                    username_link = (
                        f"@{u.username}" if u.username
                        else f"[{u.first_name}](tg://user?id={u.id})"
                    )
                    await app.send_message(
                        chat_id,
                        f"🎧 **VC Join Alert:** {username_link} VC me join hua!"
                    )
    except Exception as e:
        print("Error:", e)


print("Bot is running…")
app.run()