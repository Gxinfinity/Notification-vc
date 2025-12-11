from pyrogram import Client
from pytgcalls import PyTgCalls
from pytgcalls.types.events import ChatMemberUpdated
from pytgcalls.types import GroupCallParticipant


api_id = 27209067
api_hash = "0bb2571bd490320a5c9209d4bf07902e"
bot_token = ""   # <-- Yaha apna BOT TOKEN daalo


app = Client(
    "vcbot",
    api_id=api_id,
    api_hash=api_hash,
    bot_token=bot_token
)

call = PyTgCalls(app)


@call.on_chat_member_updated()
async def vc_listener(_, update: ChatMemberUpdated):

    # Sirf VC join walon ko detect karega
    if isinstance(update.new_participant, GroupCallParticipant):

        user_id = update.user_id
        chat_id = update.chat_id

        user = await app.get_users(user_id)

        username = (
            f"@{user.username}" if user.username
            else f"[{user.first_name}](tg://user?id={user.id})"
        )

        msg = f"🎧 **VC Join Alert:** {username} VC me join hua!"

        await app.send_message(chat_id, msg)


app.start()
call.start()
print("Bot is running...")
app.idle()