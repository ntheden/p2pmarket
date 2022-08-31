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
import sqlalchemy
from sqlmodel import SQLModel, create_engine, Field, Session, select
from typing import Union, Optional
import uvloop
import uvicorn


# configure logging
logs = Path('.').joinpath('logs')
logs.mkdir(exist_ok=True)
logging.config.fileConfig(
        'logging.conf',
        defaults={'logfilename': logs/'api.log'},
        disable_existing_loggers=False
)
# for pyrogram speedup
uvloop.install()


app = FastAPI()


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


def db_get_media(msg_dict):
    msg_dict["media_type"] = None
    with Session(engine) as session:
        try:
            media = session.exec(select(MessageMedia).where(
                MessageMedia.id == msg_dict['id'])).one()
        except sqlalchemy.exc.NoResultFound:
            return msg_dict
        msg_dict["media_type"] = media.type
        media_dict = msg_dict[media.type]
        media_dict["file_path"] = media.path
        media_dict["thumb_path"] = media.thumb_path
    return msg_dict


class MessageMedia(SQLModel, table=True):
    id: int = Field(primary_key=True)
    path: Union[str, None]
    thumb_path: Union[str, None]
    type: str = "photo"


# configure database
sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
engine = create_engine(sqlite_url, echo=True, future=True)
SQLModel.metadata.create_all(engine)


def db_set_media(msg_dict):
    media_dict = msg_dict[msg_dict["media_type"]]
    if not media_dict:
        return msg_dict
    with Session(engine) as session:
        media = MessageMedia(
            id=msg_dict['id'],
            path=media_dict["file_path"],
            thumb_path=media_dict["thumb_path"],
            type=msg_dict["media_type"],
        )
        print(media)
        session.add(media)
        session.commit()
    return msg_dict


async def download_and_update_media(tg, message) -> dict:
    msg_dict = json.loads(str(message))
    del msg_dict['chat'] # remove redundant field
    files = Path(f"downloads/{message.id}")
    # TODO: check both db and filesystem
    msg_dict = db_get_media(msg_dict)
    if files.is_dir() and any(files.iterdir()):
        # already something there. can't verify they are all there or file
        # integrity, good enough though
        if not Flags.redownload:
            return msg_dict
    media = message.photo or message.video
    if not media:
        # there are many other types of media, only interested in these two
        return msg_dict
    key = "photo" if message.photo else "video"
    msg_dict["media_type"] = key
    media_dict = msg_dict[key]
    media_dict.update({
        "file_path": None,
        "thumb_path": None,
    })
    fpath = await tg.download_media(message, f"downloads/{message.id}/", progress=progress)
    if not fpath:
        return msg_dict
    media_dict["file_path"] = fpath
    if media.thumbs:
        thumb_dict = media_dict["thumbs"][0]
        fpath = Path(fpath)
        thumb_dict["file_path"] = fpath.parent.joinpath('thumb-'+fpath.name)
        thumb = await tg.download_media(
            media.thumbs[0].file_id,
            thumb_dict["file_path"],
        )
    return db_set_media(msg_dict)


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
            messages.append({
                'obj': message,
                'dict': await download_and_update_media(tg, message),
            })
    logger.info("Done Synchronizing Telegram Messages")


@app.get("/telegram/{chat_id}")
async def get_message(
        chat_id: str,
        msg_id: Union[int, None] = None,
        thumb: Union[bool, None] = None
    ) -> Union[FileResponse, dict]:
    global messages
    if not messages:
        await synch_messages(chat_id)
    if not msg_id:
        return sorted([message['obj'].id for message in messages])
    msg = [m for m in messages if m['obj'].id == msg_id]
    msg = msg[0]['obj'] if msg else None
    if not thumb:
        return msg_dict
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
    return FileResponse("downloads/shopping-bag.png")


if __name__=="__main__":
    logging.getLogger("main").info('P2P Store API')
    server = uvicorn.Server(
        uvicorn.Config(app, host="0.0.0.0", port=8001, lifespan="off")
    )
    asyncio.run(server.serve())
