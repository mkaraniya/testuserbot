#fix by @heyworld for OUB


from telethon.tl.types import InputMediaDice
from telethon.tl.types import InputMediaDart
import emoji
from emoji import *
from userbot.events import register 
from userbot import BOTLOG, BOTLOG_CHATID, CMD_HELP, bot, ALIVE_NAME



@register(outgoing=True, pattern="^.dice(?: |$)(.*)")
async def _(event):
    if event.fwd_from:
        return
    input_str = event.pattern_match.group(1)
    await event.delete()
    r = await event.reply(file=InputMediaDice(''))
    if input_str:
        try:
            required_number = int(input_str)
            while not r.media.value == required_number:
                await r.delete()
                r = await event.reply(file=InputMediaDice(''))
        except:
            pass

        
@register(outgoing=True, pattern="^.dart(?: |$)(.*)")
async def _(event):
    if event.fwd_from:
        return
    reply_message = event
    if event.reply_to_msg_id:
        reply_message = await event.get_reply_message()
    emoticon = event.pattern_match.group(2)
    await event.delete()
    r = await reply_message.reply(file=InputMediaDart(emoticon=emoticon))
        pass
        
        
CMD_HELP.update({
    "dice":
    ".dice\
\nUsage: hahaha just a magic."
})    
