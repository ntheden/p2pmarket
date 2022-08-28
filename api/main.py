#!/usr/bin/env python3
import asyncio
import json
import logging
import logging.config
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pathlib import Path
from pyrogram import Client as TelegramClient
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
        await tg.download_media(message, progress=progress)
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


@app.get("/providers/tg/{chat_id}")
async def get_message_ids(chat_id: str):
    global messages
    if not messages:
        await synch_messages(chat_id)
    return sorted([message.id for message in messages])


@app.get("/providers/tg/{chat_id}/{id}")
async def get_message(chat_id: str, id: int):
    global messages
    if not messages:
        await synch_messages(chat_id)
    items = [m for m in messages if m.id == id]
    if not items:
        return
    return json.loads(str(items[0]))


@app.get("/providers/tg/media/{name}/{placeholder}")
async def get_media(name: str, placeholder: int) -> StreamingResponse:
#@app.get("/providers/tg/media/{name}")
#async def get_media(name: str):
    '''
    Returns streamed media

    XXX placeholder(use anything): why am i getting
    "422 Unprocessable Entity" without this
    '''
    async with TelegramClient("my_account") as tg:
        fobj = await tg.download_media(name, in_memory=True)
    def iterfile():
        yield from fobj
    return StreamingResponse(iterfile())


if __name__=="__main__":
    init()
    logging.getLogger("main").info('P2P Store API')
    server = uvicorn.Server(
        uvicorn.Config(app, host="0.0.0.0", port=8001, lifespan="off")
    )
    asyncio.run(server.serve())
