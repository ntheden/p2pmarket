#!/usr/bin/env python3
import asyncio
from environs import Env
import json
import logging
import logging.config
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse
from pathlib import Path
from pyrogram import Client as TelegramClient
import sqlalchemy
from sqlmodel import SQLModel, create_engine, Field, Session, select, Relationship
from typing import Union, Optional
import uvloop
import uvicorn


env = Env(expand_vars=True)
env.read_env(".env")
# configure logging
with env.prefixed('P2PSTORE_'):
    logs = Path(env('PATH', '.')).joinpath('logs')
logs.mkdir(parents=True, exist_ok=True)
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


class MessageMedia(SQLModel, table=True):
    '''
    Deprecated
    '''
    id: int = Field(primary_key=True)
    name: Union[str, None]
    thumb_name: Union[str, None]
    type: str = "photo"


class Media(SQLModel, table=True):
    id: int = Field(primary_key=True)
    name: Union[str, None]
    thumb_name: Union[str, None]
    type: str = "photo"
    path: str = Union[str, None]
    message_id: Optional[int] = Field(default=None, foreign_key="message.id")
    message: Optional["Message"] = Relationship(back_populates="media")


class Reaction(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    emoji: Union[str, None]
    count: int
    message_id: Optional[int] = Field(default=None, foreign_key="message.id")
    message: Optional["Message"] = Relationship(back_populates="reactions")


class User(SQLModel, table=True):
    id: int = Field(primary_key=True)
    first_name: Union[str, None]
    last_name: Union[str, None]
    username: str
    is_deleted: bool = False
    status: Union[str, None] # will not remain optional
    last_online_date: Union[str, None] # will not remain optional, is this str
    media_name: Union[str, None]
    thumb_name: Union[str, None]
    media_type: str = "photo"
    messages: Optional[list["Message"]] = Relationship(back_populates="user")


class Message(SQLModel, table=True):
    id: int = Field(primary_key=True)
    caption: str = "" # caption or text
    date: str # is this str
    is_deleted: bool = False
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    user: Optional[User] = Relationship(back_populates="messages")
    media: Optional[list["Media"]] = Relationship(back_populates="message")
    reactions: Optional[list["Reaction"]] = Relationship(back_populates="message")


# configure database
with env.prefixed('P2PSTORE_'):
    db_path = Path(env('PATH', '.')).joinpath(env('DB_NAME', 'database.db'))
sqlite_url = f"sqlite:///{db_path}"
engine = create_engine(sqlite_url, echo=True, future=True)
SQLModel.metadata.create_all(engine)


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
        media_dict["file_name"] = media.name
        media_dict["thumb_name"] = media.thumb_name
    return msg_dict


def db_set_media(msg_dict):
    '''
    Creates database entry holding the media filename
    associated with this message. Also updates :msg_dict:
    '''
    media_dict = msg_dict[msg_dict["media_type"]]
    if not media_dict:
        return msg_dict
    with Session(engine) as session:
        try:
            media = session.exec(select(MessageMedia).where(
                MessageMedia.id == msg_dict['id'])).one()
            return msg_dict
        except sqlalchemy.exc.NoResultFound:
            pass
        media = MessageMedia(
            id=msg_dict['id'],
            name=media_dict["file_name"],
            thumb_name=media_dict["thumb_name"],
            type=msg_dict["media_type"],
        )
        session.add(media)
        session.commit()
    return msg_dict


async def download_and_update_media(tg, message) -> dict:
    msg_dict = json.loads(str(message))
    del msg_dict['chat'] # remove redundant field
    with env.prefixed('P2PSTORE_'):
        files = Path(env('PATH', '.'))/f"downloads/{message.id}/"
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
        "file_name": None,
        "thumb_name": None,
    })
    fpath = await tg.download_media(message, f'{files}/', progress=progress)
    if not fpath:
        return msg_dict
    fpath = Path(fpath)
    media_dict["file_name"] = fpath.name
    if media.thumbs:
        thumb_dict = media_dict["thumbs"][0]
        thumb_dict["file_name"] = 'thumb-'+fpath.name
        thumb = await tg.download_media(
            media.thumbs[0].file_id,
            fpath.parent.joinpath(thumb_dict["file_name"]),
        )
    return db_set_media(msg_dict)


def db_set_message(session, msg):
    if not msg.caption:
        pass
    try:
        message = session.exec(select(Message).where(
            Message.id == msg.id)).one()
    except sqlalchemy.exc.NoResultFound:
        #message = Message(
        pass


@app.on_event("startup")
async def sync_messages(chat_id: str = None):
    '''
    TODO: Idea is to do this periodically or upon telegram notification

    Expecting chat_id to be "@bitcoinp2pmarketplace"
    '''
    global messages
    chat_id = chat_id or "@bitcoinp2pmarketplace"
    logger = logging.getLogger("main")
    logger.info("Synchronizing Telegram Messages..")
    with Session(engine) as session:
        async with TelegramClient("my_account") as tg:
            async for message in tg.get_chat_history(chat_id):
                follow_on_msgs = []
                if message.caption or message.text and message.from_user:
                    for m in reversed([m["obj"] for m in messages]):
                        if not m.caption and not m.text and m.from_user and (
                                m.from_user.username == message.from_user.username):
                            follow_on_msgs.append(m)
                        else:
                            break
                if follow_on_msgs:
                    messages = messages[:-len(follow_on_msgs)]
                messages.append({
                    "obj": message,
                    "dict": await download_and_update_media(tg, message),
                    "follow-ons": follow_on_msgs
                })
    logger.info("Done Synchronizing Telegram Messages")


@app.get("/telegram/{chat_id}")
async def get_message(
        chat_id: str,
        msg_id: Union[int, None] = None,
        thumb: Union[bool, None] = None,
        photo: Union[bool, None] = None
    ) -> Union[FileResponse, dict]:
    global messages
    if msg_id is None:
        return sorted([message['obj'].id for message in messages])
    msg = [m for m in messages if m['obj'].id == msg_id]
    msg = msg[0] if msg else None
    if not msg:
        return {}
    if not thumb and not photo:
        return msg['dict']
    with env.prefixed('P2PSTORE_'):
        fpath = Path(env('PATH', '.'))/f"downloads/{msg['obj'].id}/"
    if fpath.is_dir() and any(fpath.iterdir()):
        thumb_name = None
        path = None
        for fname in fpath.iterdir():
            if fname.name.startswith('thumb-'):
                thumb_name = fname
            else:
                path = fname
        if photo or not thumb_name:
            return FileResponse(path)
        return FileResponse(thumb_name)
    return FileResponse("downloads/shopping-bag.png")


if __name__=="__main__":
    logging.getLogger("main").info('P2P Store API')
    server = uvicorn.Server(
        uvicorn.Config(app, host="0.0.0.0", port=8001, lifespan="off")
    )
    asyncio.run(server.serve())
