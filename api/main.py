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
    origins = ["http://localhost:3000"]
    app.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
    )


messages = []


async def progress(current, total):
    print(f"{current * 100 / total:.1f}%")


async def download_media(tg, message):
    try:
        await tg.download_media(message, f"downloads/{message.id}/", progress=progress)
    except ValueError as e:
        if "This message doesn't contain any downloadable media" not in str(e):
            raise


async def synch_messages(chat_id):
    '''
    TODO: Idea is to do this periodically or upon telegram notification

    Expecting chat_id to be "@bitcoinp2pmarketplace"
    '''
    async with TelegramClient("my_account") as tg:
        async for message in tg.get_chat_history(chat_id):
            #await download_media(tg, message)
            messages.append(message)


@app.get("/telegram/{chat_id}")
async def get_message(chat_id: str, msg_id: Union[int, None] = None, photo: Union[bool, None] = None):
    global messages
    if not messages:
        await synch_messages(chat_id)
    if not msg_id:
        return sorted([message.id for message in messages])
    msg = [m for m in messages if m.id == msg_id]
    msg = msg[0] if msg else None
    if not photo:
        return json.loads(str(msg)) if msg else {}
    async with TelegramClient("my_account") as tg:
        fpath = await tg.download_media(msg, f"downloads/{msg.id}/")
        return FileResponse(fpath)


if __name__=="__main__":
    init()
    logging.getLogger("main").info('P2P Store API')
    server = uvicorn.Server(
        uvicorn.Config(app, host="0.0.0.0", port=8001, lifespan="off")
    )
    asyncio.run(server.serve())
