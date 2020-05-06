"""Log PMs
Check https://t.me/tgbeta/3505"""
import asyncio
import os
from telethon.tl.functions.photos import GetUserPhotosRequest
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.types import MessageEntityMentionName
from telethon.utils import get_input_location
from telethon import events
from telethon.tl import functions, types
from userbot import BOTLOG, BOTLOG_CHATID, CMD_HELP, bot, TEMP_DOWNLOAD_DIRECTORY
from userbot.events import register


bot.NO_PM_LOG_USERS = []

async def get_user(event):
    """ Get the user from argument or replied message. """
    if event.reply_to_msg_id and not event.pattern_match.group(1):
        previous_message = await event.get_reply_message()
        replied_user = await event.client(
            GetFullUserRequest(previous_message.from_id))
    else:
        user = event.pattern_match.group(1)

        if user.isnumeric():
            user = int(user)

        if not user:
            self_user = await event.client.get_me()
            user = self_user.id

        if event.message.entities is not None:
            probable_user_mention_entity = event.message.entities[0]

            if isinstance(probable_user_mention_entity,
                          MessageEntityMentionName):
                user_id = probable_user_mention_entity.user_id
                replied_user = await event.client(GetFullUserRequest(user_id))
                return replied_user
        try:
            user_object = await event.client.get_entity(user)
            replied_user = await event.client(
                GetFullUserRequest(user_object.id))
        except (TypeError, ValueError) as err:
            await event.edit(str(err))
            return None

    return replied_user


async def fetch_info(replied_user, event):
    """ Get details from the User object. """
    replied_user_profile_photos = await event.client(
        GetUserPhotosRequest(user_id=replied_user.user.id,
                             offset=42,
                             max_id=0,
                             limit=80))
    replied_user_profile_photos_count = "Person needs help with uploading profile picture."
    try:
        replied_user_profile_photos_count = replied_user_profile_photos.count
    except AttributeError as e:
        pass
    user_id = replied_user.user.id
    first_name = replied_user.user.first_name
    last_name = replied_user.user.last_name
    try:
        dc_id, location = get_input_location(replied_user.profile_photo)
    except Exception as e:
        dc_id = "Couldn't fetch DC ID!"
        location = str(e)
    common_chat = replied_user.common_chats_count
    username = replied_user.user.username
    user_bio = replied_user.about
    is_bot = replied_user.user.bot
    restricted = replied_user.user.restricted
    verified = replied_user.user.verified
    photo = await event.client.download_profile_photo(user_id,
                                                      TEMP_DOWNLOAD_DIRECTORY +
                                                      str(user_id) + ".jpg",
                                                      download_big=True)
    first_name = first_name.replace(
        "\u2060", "") if first_name else ("This User has no First Name")
    last_name = last_name.replace(
        "\u2060", "") if last_name else ("This User has no Last Name")
    username = "@{}".format(username) if username else (
        "This User has no Username")
    user_bio = "This User has no About" if not user_bio else user_bio

    caption = "<b>USER INFO:</b>\n\n"
    caption += f"First Name: {first_name}\n"
    caption += f"Last Name: {last_name}\n"
    caption += f"Username: {username}\n"
    caption += f"Data Centre ID: {dc_id}\n"
    caption += f"Number of Profile Pics: {replied_user_profile_photos_count}\n"
    caption += f"Is Bot: {is_bot}\n"
    caption += f"Is Restricted: {restricted}\n"
    caption += f"Is Verified by Telegram: {verified}\n"
    caption += f"ID: <code>{user_id}</code>\n\n"
    caption += f"Bio: \n<code>{user_bio}</code>\n\n"
    caption += f"Common Chats with this user: {common_chat}\n"
    caption += f"Permanent Link To Profile: "
    caption += f"<a href=\"tg://user?id={user_id}\">{first_name}</a>"

    return photo, caption

#@borg.on(events.NewMessage(incoming=True, func=lambda e: e.is_private))
@bot.on(events.NewMessage(incoming=True, func=lambda e: e.is_private))
async def monito_p_m_s(event):
    sender = await event.get_sender()
    if BOTLOG and not sender.bot:
        chat = await event.get_chat()
        if chat.id not in bot.NO_PM_LOG_USERS and chat.id != user.id:
            try:
                e = await bot.get_entity(int(BOTLOG_CHATID))
                fwd_message = await bot.forward_messages(
                    e,
                    event.message,
                    silent=True
                )
            except Exception as e:
                logger.warn(str(e))


#@borg.on(admin_cmd("nolog ?(.*)"))
@register(outgoing=True, pattern="^.nolog(?: |$)(.*)")
async def approve_p_m(event):
    if event.fwd_from:
        return
    reason = event.pattern_match.group(1)
    chat = await event.get_chat()
    if BOTLOG:
        if event.is_private:
            if chat.id not in bot.NO_PM_LOG_USERS:
                bot.NO_PM_LOG_USERS.append(chat.id)
                await event.edit("Won't Log Messages from this chat")
                await asyncio.sleep(3)
                await event.delete()
