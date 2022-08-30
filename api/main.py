#!/usr/bin/env python3
import asyncio
import json
import logging
import logging.config
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse
from pathlib import Path
from pyrogram import Client as TelegramClient
from typing import Union
import uvloop
import uvicorn


app = FastAPI()


def init():
    logs = Path(__file__).parents[1].joinpath('logs')
    logs.mkdir(exist_ok=True)
    logging.config.fileConfig(
            'logging.conf',
            defaults={'logfilename': logs/'api.log'},
            disable_existing_loggers=False
    )
    uvloop.install()
    origins = ["http://localhost:3000", "http://localhost:3001"]
    app.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
    )


class Flags:
    redownload = False
messages = []


async def progress(current, total):
    print(f"{current * 100 / total:.1f}%")


async def download_media(tg, message):
    files = Path(f"downloads/{message.id}")
    if files.is_dir() and any(files.iterdir()):
        # already something there. can't verify they are all there or file
        # integrity, good enough though
        if not Flags.redownload:
            return
    media = message.photo or message.video
    if not media:
        # there are many other types of media, only interested in these two for now
        return
    fpath = await tg.download_media(message, f"downloads/{message.id}/", progress=progress)
    if fpath and media.thumbs:
        fpath = Path(fpath)
        thumb = await tg.download_media(
            media.thumbs[0].file_id,
            fpath.parent.joinpath('thumb-'+fpath.name)
        )


@app.on_event("startup")
async def synch_messages(chat_id: str = None):
    '''
    TODO: Idea is to do this periodically or upon telegram notification

    Expecting chat_id to be "@bitcoinp2pmarketplace"
    '''
    chat_id = chat_id or "@bitcoinp2pmarketplace"
    logger = logging.getLogger("main")
    logger.info("Synchronizing Telegram Messages..")
    async with TelegramClient("my_account") as tg:
        async for message in tg.get_chat_history(chat_id):
            await download_media(tg, message)
            messages.append(message)
    logger.info("Done Synchronizing Telegram Messages")


@app.get("/telegram/{chat_id}")
async def get_message(chat_id: str, msg_id: Union[int, None] = None, thumb: Union[bool, None] = None):
    global messages
    if not messages:
        await synch_messages(chat_id)
    if not msg_id:
        return sorted([message.id for message in messages])
    msg = [m for m in messages if m.id == msg_id]
    msg = msg[0] if msg else None
    if not thumb:
        return json.loads(str(msg)) if msg else {}
    fpath = Path(f"downloads/{msg.id}")
    if fpath.is_dir() and any(fpath.iterdir()):
        # If more than one, the order will likely be first in at
        # last place, pick the first one
        # Find a thumb, if any
        files = list(reversed(list(fpath.iterdir())))
        for fname in files:
            if fname.name.startswith('thumb-'):
                return FileResponse(fname)
        # did not find a thumb
        return FileResponse(files[0])


if __name__=="__main__":
    init()
    logging.getLogger("main").info('P2P Store API')
    server = uvicorn.Server(
        uvicorn.Config(app, host="0.0.0.0", port=8001, lifespan="off")
    )
    asyncio.run(server.serve())
