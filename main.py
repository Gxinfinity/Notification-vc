from pyrogram import Client
from pytgcalls import PyTgCalls
from pytgcalls.types import Update
from pytgcalls.types import UpdateGroupCallParticipants

api_id = 27209067      # Your API ID
api_hash = "0bb2571bd490320a5c9209d4bf07902e"  
bot_token = "" 

app = Client(
    "vcbot",
    api_id=api_id,
    api_hash=api_hash,
    bot_token=bot_token
)

call = PyTgCalls(app)


@call.on_update()
async def vc_listener(update: Update):
    if isinstance(update, UpdateGroupCallParticipants):
        user = update.participant
        chat_id = update.chat_id

        if user and user.user_id:
            try:
                # user full info
                u = await app.get_users(user.user_id)

                username_link = (
                    f"@{u.username}" if u.username
                    else f"[{u.first_name}](tg://user?id={u.id})"
                )

                text = f"🎧 **VC Join Alert:** {username_link} VC me join hua!"

                await app.send_message(chat_id, text)
            except Exception as e:
                print("Error:", e)


app.start()
call.start()
print("Bot is running...")
app.idle()