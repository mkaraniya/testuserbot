# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.c (the "License");
# you may not use this file except in compliance with the License.
# cpin courtesy Uniborg.
"""
Userbot module to help you manage a group
"""

from asyncio import sleep
from os import remove
from telethon import events
from telethon.tl import functions, types
from platform import python_version, uname
from telethon.errors import (BadRequestError, ChatAdminRequiredError,
                             ImageProcessFailedError, PhotoCropSizeSmallError,
                             UserAdminInvalidError)
from telethon.errors.rpcerrorlist import (UserIdInvalidError,
                                          MessageTooLongError)
from telethon.tl.functions.channels import (EditAdminRequest,
                                            EditBannedRequest,
                                            EditPhotoRequest)
from telethon.tl.functions.messages import UpdatePinnedMessageRequest
from telethon.tl.types import (PeerChannel, ChannelParticipantsAdmins,
                               ChatAdminRights, ChatBannedRights,
                               MessageEntityMentionName, MessageMediaPhoto,
                               ChannelParticipantsBots)

from userbot import BOTLOG, BOTLOG_CHATID, CMD_HELP, bot
from userbot.events import register

# =================== CONSTANT ===================
PP_TOO_SMOL = "`The image is too small`"
PP_ERROR = "`Failure while processing the image`"
NO_ADMIN = "`I am not an admin!`"
NO_PERM = "`I don't have sufficient permissions!`"
NO_SQL = "`Running on Non-SQL mode!`"

CHAT_PP_CHANGED = "`Chat Picture Changed`"
CHAT_PP_ERROR = "`Some issue with updating the pic,`" \
                "`maybe coz I'm not an admin,`" \
                "`or don't have enough rights.`"
INVALID_MEDIA = "`Invalid Extension`"

BANNED_RIGHTS = ChatBannedRights(
    until_date=None,
    view_messages=True,
    send_messages=True,
    send_media=True,
    send_stickers=True,
    send_gifs=True,
    send_games=True,
    send_inline=True,
    embed_links=True,
)

UNBAN_RIGHTS = ChatBannedRights(
    until_date=None,
    send_messages=None,
    send_media=None,
    send_stickers=None,
    send_gifs=None,
    send_games=None,
    send_inline=None,
    embed_links=None,
)

MUTE_RIGHTS = ChatBannedRights(until_date=None, send_messages=True)

UNMUTE_RIGHTS = ChatBannedRights(until_date=None, send_messages=False)
# ================================================



@register(outgoing=True, pattern="^.ban(?: |$)(.*)")
async def ban(bon):
    """ For .ban command, bans the replied/tagged person """
    # Here laying the sanity check
    chat = await bon.get_chat()
    admin = chat.admin_rights
    creator = chat.creator

    # Well
    if not admin and not creator:
        await bon.edit(NO_ADMIN)
        return

    user, reason = await get_user_from_event(bon)
    if user:
        pass
    else:
        return

    # Announce that we're going to whack the pest
    await bon.edit("`Whacking the pest!`")

    try:
        await bon.client(EditBannedRequest(bon.chat_id, user.id,
                                           BANNED_RIGHTS))
    except BadRequestError:
        await bon.edit(NO_PERM)
        return
    # Helps ban group join spammers more easily
    try:
        reply = await bon.get_reply_message()
        if reply:
            await reply.delete()
    except BadRequestError:
        await bon.edit(
            "`I dont have message nuking rights! But still he was banned!`")
        return
    # Delete message and then tell that the command
    # is done gracefully
    # Shout out the ID, so that fedadmins can fban later
    if reason:
        await bon.edit(f"`{str(user.id)}` was banned !!\nReason: {reason}")
    else:
        await bon.edit(f"`{str(user.id)}` was banned !!")
    # Announce to the logging group if we have banned the person
    # successfully!
    if BOTLOG:
        await bon.client.send_message(
            BOTLOG_CHATID, "#BAN\n"
            f"USER: [{user.first_name}](tg://user?id={user.id})\n"
            f"CHAT: {bon.chat.title}(`{bon.chat_id}`)")


@register(outgoing=True, pattern="^.unban(?: |$)(.*)")
async def nothanos(unbon):
    """ For .unban command, unbans the replied/tagged person """
    # Here laying the sanity check
    chat = await unbon.get_chat()
    admin = chat.admin_rights
    creator = chat.creator

    # Well
    if not admin and not creator:
        await unbon.edit(NO_ADMIN)
        return

    # If everything goes well...
    await unbon.edit("`Unbanning...`")

    user = await get_user_from_event(unbon)
    user = user[0]
    if user:
        pass
    else:
        return

    try:
        await unbon.client(
            EditBannedRequest(unbon.chat_id, user.id, UNBAN_RIGHTS))
        await unbon.edit("```Unbanned Successfully```")

        if BOTLOG:
            await unbon.client.send_message(
                BOTLOG_CHATID, "#UNBAN\n"
                f"USER: [{user.first_name}](tg://user?id={user.id})\n"
                f"CHAT: {unbon.chat.title}(`{unbon.chat_id}`)")
    except UserIdInvalidError:
        await unbon.edit("`Uh oh my unban logic broke!`")

@register(outgoing=True, pattern="^.ungmute(?: |$)(.*)")
async def ungmoot(un_gmute):
    """ For .ungmute command, ungmutes the target in the userbot """
    # Admin or creator check
    chat = await un_gmute.get_chat()
    admin = chat.admin_rights
    creator = chat.creator

    # If not admin and not creator, return
    if not admin and not creator:
        await un_gmute.edit(NO_ADMIN)
        return

    # Check if the function running under SQL mode
    try:
        from userbot.modules.sql_helper.gmute_sql import ungmute
    except AttributeError:
        await un_gmute.edit(NO_SQL)
        return

    user = await get_user_from_event(un_gmute)
    user = user[0]
    if user:
        pass
    else:
        return

    # If pass, inform and start ungmuting
    await un_gmute.edit('```Ungmuting...```')

    if ungmute(user.id) is False:
        await un_gmute.edit("`Error! User probably not gmuted.`")
    else:
        # Inform about success
        await un_gmute.edit("```Ungmuted Successfully```")

        if BOTLOG:
            await un_gmute.client.send_message(
                BOTLOG_CHATID, "#UNGMUTE\n"
                f"USER: [{user.first_name}](tg://user?id={user.id})\n"
                f"CHAT: {un_gmute.chat.title}(`{un_gmute.chat_id}`)")


@register(outgoing=True, pattern="^.gmute(?: |$)(.*)")
async def gspider(gspdr):
    """ For .gmute command, globally mutes the replied/tagged person """
    # Admin or creator check
    chat = await gspdr.get_chat()
    admin = chat.admin_rights
    creator = chat.creator

    # If not admin and not creator, return
    if not admin and not creator:
        await gspdr.edit(NO_ADMIN)
        return

    # Check if the function running under SQL mode
    try:
        from userbot.modules.sql_helper.gmute_sql import gmute
    except AttributeError:
        await gspdr.edit(NO_SQL)
        return

    user, reason = await get_user_from_event(gspdr)
    if user:
        pass
    else:
        return

    # If pass, inform and start gmuting
    await gspdr.edit("`Grabs a huge, sticky duct tape!`")
    if gmute(user.id) is False:
        await gspdr.edit(
            '`Error! User probably already gmuted.\nRe-rolls the tape.`')
    else:
        if reason:
            await gspdr.edit(f"`Globally taped!`Reason: {reason}")
        else:
            await gspdr.edit("`Globally taped!`")

        if BOTLOG:
            await gspdr.client.send_message(
                BOTLOG_CHATID, "#GMUTE\n"
                f"USER: [{user.first_name}](tg://user?id={user.id})\n"
                f"CHAT: {gspdr.chat.title}(`{gspdr.chat_id}`)")


async def get_user_from_event(event):
    """ Get the user from argument or replied message. """
    args = event.pattern_match.group(1).split(' ', 1)
    extra = None
    if event.reply_to_msg_id and not len(args) == 2:
        previous_message = await event.get_reply_message()
        user_obj = await event.client.get_entity(previous_message.from_id)
        extra = event.pattern_match.group(1)
    elif args:
        user = args[0]
        if len(args) == 2:
            extra = args[1]

        if user.isnumeric():
            user = int(user)

        if not user:
            await event.edit("`Pass the user's username, id or reply!`")
            return

        if event.message.entities is not None:
            probable_user_mention_entity = event.message.entities[0]

            if isinstance(probable_user_mention_entity,
                          MessageEntityMentionName):
                user_id = probable_user_mention_entity.user_id
                user_obj = await event.client.get_entity(user_id)
                return user_obj
        try:
            user_obj = await event.client.get_entity(user)
        except (TypeError, ValueError) as err:
            await event.edit(str(err))
            return None

    return user_obj, extra


async def get_user_from_id(user, event):
    if isinstance(user, str):
        user = int(user)

    try:
        user_obj = await event.client.get_entity(user)
    except (TypeError, ValueError) as err:
        await event.edit(str(err))
        return None

    return user_obj


@register(incoming=True)
async def muter(moot):
    """ Used for deleting the messages of muted people """
    try:
        from userbot.modules.sql_helper.spam_mute_sql import is_muted
        from userbot.modules.sql_helper.gmute_sql import is_gmuted
    except AttributeError:
        return
    muted = is_muted(moot.chat_id)
    gmuted = is_gmuted(moot.sender_id)
    rights = ChatBannedRights(
        until_date=None,
        send_messages=True,
        send_media=True,
        send_stickers=True,
        send_gifs=True,
        send_games=True,
        send_inline=True,
        embed_links=True,
    )
    if muted:
        for i in muted:
            if str(i.sender) == str(moot.sender_id):
                await moot.delete()
                await moot.client(
                    EditBannedRequest(moot.chat_id, moot.sender_id, rights))
    for i in gmuted:
        if i.sender == str(moot.sender_id):
            await moot.delete()

