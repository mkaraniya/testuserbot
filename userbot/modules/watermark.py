#imported from ravana69/pornhub to userbot by @heyworld 
import requests
import bs4 
import re
import os
import asyncio
import zipfile
import time
from io import BytesIO
from PyPDF2 import PdfFileWriter, PdfFileReader
from telethon import *
from userbot.events import register 
from pySmartDL import SmartDL
from userbot import CMD_HELP, bot, TEMP_DOWNLOAD_DIRECTORY
from telethon import events
from telethon.tl import functions, types
from urllib.parse import quote
from datetime import datetime, timedelta
from telethon.tl.types import UserStatusEmpty, UserStatusLastMonth, UserStatusLastWeek, UserStatusOffline, UserStatusOnline, UserStatusRecently, ChannelParticipantsKicked, ChatBannedRights
from time import sleep
from telethon.tl.functions.photos import GetUserPhotosRequest
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.types import MessageEntityMentionName
from telethon.utils import get_input_location
from telethon.tl.types import DocumentAttributeAudio, DocumentAttributeVideo
from telethon.tl.types import DocumentAttributeFilename
from userbot.modules.upload_download import progress, humanbytes, time_formatter
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from telethon.errors import PhotoInvalidDimensionsError
from telethon.errors.rpcerrorlist import YouBlockedUserError
from telethon.tl.functions.account import UpdateNotifySettingsRequest

from telethon.tl.functions.messages import SendMediaRequest


import logging


LOGS = getLogger(__name__)



if 1 == 1:
    name = "Profile Photos"
    client = bot




@register(outgoing=True, pattern="^.watermark(?: |$)(.*)")
async def water(mark):
    if mark.fwd_from:
        return
    mone = await mark.edit("Processing ...")
    if not os.path.isdir(TEMP_DOWNLOAD_DIRECTORY):
        os.makedirs(TEMP_DOWNLOAD_DIRECTORY)
    if not os.path.isdir("./downloads/"):
        os.makedirs("./downloads/")
    if mark.reply_to_msg_id:
        start = datetime.now()
        reply_message = await mark.get_reply_message()
        try:
            c_time = time.time()
            downloaded_file_name = await bot.download_media(
                reply_message,
                TEMP_DOWNLOAD_DIRECTORY,
                progress_callback=lambda d, t: asyncio.get_event_loop().create_task(
                    progress(d, t, mone, c_time, "trying to download")
                )
            )
        except Exception as e:  # pylint:disable=C0103,W0703
            await mone.edit(str(e))
        else:
            end = datetime.now()
            ms = (end - start).seconds
            await mone.edit("Stored the pdf to `{}` in {} seconds.".format(downloaded_file_name, ms))
            watermark(
                inputpdf=downloaded_file_name,
                outputpdf='./downloads/' + reply_message.file.name,
                watermarkpdf='./bin/watermark.pdf'
            )
        # filename = sorted(get_lst_of_files('./ravana/watermark/' + reply_message.file.name, []))
        #filename = filename + "/"
        await mark.edit("Uploading now")
        caption_rts = os.path.basename(watermark_path + reply_message.file.name)
        await bot.send_file(
            mark.chat_id,
            watermark_path + reply_message.file.name,
            reply_to=mark.message.id,
            progress_callback=lambda d, t: asyncio.get_event_loop().create_task(
                progress(d, t, event, c_time, "trying to upload")
            )
        )
        # r=root, d=directories, f = files
        # for single_file in filename:
        #     if os.path.exists(single_file):
        #         # https://stackoverflow.com/a/678242/4723940
        #         caption_rts = os.path.basename(single_file)
        #         force_document = False
        #         supports_streaming = True
        #         document_attributes = []
        #         if single_file.endswith((".mp4", ".mp3", ".flac", ".webm")):
        #             metadata = extractMetadata(createParser(single_file))
        #             duration = 0
        #             width = 0
        #             height = 0
        #             if metadata.has("duration"):
        #                 duration = metadata.get('duration').seconds
        #             if os.path.exists(thumb_image_path):
        #                 metadata = extractMetadata(createParser(thumb_image_path))
        #                 if metadata.has("width"):
        #                     width = metadata.get("width")
        #                 if metadata.has("height"):
        #                     height = metadata.get("height")
        #             document_attributes = [
        #                 DocumentAttributeVideo(
        #                     duration=duration,
        #                     w=width,
        #                     h=height,
        #                     round_message=False,
        #                     supports_streaming=True
        #                 )
        #             ]
        #         try:
        #             await borg.send_file(
        #                 event.chat_id,
        #                 single_file,
        #                 caption=f"`{caption_rts}`",
        #                 force_document=force_document,
        #                 supports_streaming=supports_streaming,
        #                 allow_cache=False,
        #                 reply_to=event.message.id,
        #                 attributes=document_attributes,
        #                 # progress_callback=lambda d, t: asyncio.get_event_loop().create_task(
        #                 #     progress(d, t, event, c_time, "trying to upload")
        #                 # )
        #             )
        #         except Exception as e:
        #             await borg.send_message(
        #                 event.chat_id,
        #                 "{} caused `{}`".format(caption_rts, str(e)),
        #                 reply_to=event.message.id
        #             )
        #             # some media were having some issues
        #             continue
        #         os.remove(single_file)
        # os.remove(downloaded_file_name)

def watermark(inputpdf, outputpdf, watermarkpdf):
    watermark = PdfFileReader(watermarkpdf)
    watermarkpage = watermark.getPage(0)
    pdf = PdfFileReader(inputpdf)
    pdfwrite = PdfFileWriter()
    for page in range(pdf.getNumPages()):
        pdfpage = pdf.getPage(page)
        pdfpage.mergePage(watermarkpage)
        pdfwrite.addPage(pdfpage)
    with open(outputpdf, 'wb') as fh:
        pdfwrite.write(fh)

def get_lst_of_files(input_directory, output_lst):
    filesinfolder = os.listdir(input_directory)
    for file_name in filesinfolder:
        current_file_name = os.path.join(input_directory, file_name)
        if os.path.isdir(current_file_name):
            return get_lst_of_files(current_file_name, output_lst)
        output_lst.append(current_file_name)
    return output_lst
