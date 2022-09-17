#!/usr/bin/env python3
import asyncio
from environs import Env
import json
import logging
import logging.config
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse
import PIL
from PIL import Image
from pathlib import Path
from pyrogram import Client as TelegramClient
import re
import sqlalchemy
from sqlmodel import SQLModel, create_engine, Field, Session, select, Relationship
from typing import Union, Optional
import uvloop
import uvicorn


default_app_path = Path(__file__).parent
env = Env(expand_vars=True)
env.read_env(default_app_path/"main.env")
default_app_path = default_app_path/"run"
# configure logging
with env.prefixed('P2PMARKET_'):
    base = Path(env('PATH', default_app_path))
    logs = base.joinpath('logs')
logs.mkdir(parents=True, exist_ok=True)
logging.config.fileConfig(
        'logging.conf',
        defaults={'logpath': logs},
        disable_existing_loggers=False
)
# for pyrogram speedup
uvloop.install()


app = FastAPI()


with env.prefixed('P2PMARKET_'):
    origins = env.list('CORS_ALLOW', 'http://localhost:3000')
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


def make_thumb_aspect(impath: Path, im: Image, size: tuple):
    '''
    Create a square thumbnail of image with preserved aspect ratio.
    '''
    final_size = size[0]
    ratio = float(final_size) / max(im.size)
    new_image_size = tuple([int(x*ratio) for x in im.size])
    im = im.resize(new_image_size, PIL.Image.ANTIALIAS)
    thumb = PIL.Image.new("RGB", (final_size, final_size))
    thumb.paste(im, ((final_size-new_image_size[0])//2, (final_size-new_image_size[1])//2))
    thumb_path = impath.parent.joinpath(f'thumb-{impath.stem}.jpg')
    thumb.save(thumb_path, 'JPEG', quality=90)
    return thumb_path


def make_thumb_stretch(impath: Path, im: PIL.Image, size: tuple):
    '''
    Creates a stretched square thumbnail of image.
    '''
    logger.info(f'Creating {size} thumb of {impath}')
    thumb = im.resize(size, PIL.Image.ANTIALIAS)
    thumb_path = impath.parent.joinpath(f'thumb-{impath.stem}.jpg')
    thumb.save(thumb_path, 'JPEG', quality=90)
    return thumb_path


def make_thumb(impath, size=(360, 360)):
    logger = logging.getLogger("main")
    if impath.name.startswith("thumb-") and (impath.suffix == '.jpg'):
        return impath
    try:
        im = PIL.Image.open(impath)
    except PIL.UnidentifiedImageError as e:
        logger.info(e)
        return None
    logger.info(f'Creating thumb of {impath}')
    return make_thumb_aspect(impath, im, size)


async def progress(current, total):
    print(f"{current * 100 / total:.1f}%")


class Media(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: Union[str, None]
    size: Union[int, None] # TODO
    thumb_size: Union[int, None] # TODO
    type: Union[str, None]
    path: str = Union[str, None]
    # owned by either a message or a user, but not both
    message_id: Optional[int] = Field(default=None, foreign_key="message.id")
    message: Optional["Message"] = Relationship(back_populates="media")
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    user: Optional["User"] = Relationship(back_populates="media")


class Reaction(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    emoji: Union[str, None]
    count: int
    message_id: Optional[int] = Field(index=True, default=None, foreign_key="message.id")
    message: Optional["Message"] = Relationship(back_populates="reactions")


class HashtagMessageLink(SQLModel, table=True):
    hashtag_id: Optional[int] = Field(
        default=None, foreign_key="message.id", primary_key=True
    )
    message_id: Optional[int] = Field(
        default=None, foreign_key="hashtag.id", primary_key=True
    )


class Hashtag(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True) # lower case #hashtag
    messages: Optional[list["Message"]] = Relationship(
        back_populates="hashtags",
        link_model=HashtagMessageLink
    )


class User(SQLModel, table=True):
    id: int = Field(primary_key=True)
    first_name: Union[str, None]
    last_name: Union[str, None]
    username: Union[str, None]
    is_deleted: bool = False
    status: Union[str, None] # will not remain optional
    last_online_date: Union[str, None] # will not remain optional, is this str
    thumb_name: Union[str, None] # using telegram's thumb for now
    media: Optional[list["Media"]] = Relationship(back_populates="user")
    messages: Optional[list["Message"]] = Relationship(back_populates="user")


class Message(SQLModel, table=True):
    id: int = Field(primary_key=True)
    caption: str = "" # caption or text
    date: Union[str, None] # is this str
    edit_date: Union[str, None] # is this str
    is_deleted: bool = False
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    user: Optional[User] = Relationship(back_populates="messages")
    media: Optional[list["Media"]] = Relationship(back_populates="message")
    reactions: Optional[list["Reaction"]] = Relationship(back_populates="message")
    hashtags: Optional[list[Hashtag]] = Relationship(
        back_populates="messages",
        link_model=HashtagMessageLink
    )


# configure database
with env.prefixed('P2PMARKET_'):
    db_path = Path(env('PATH', default_app_path)).joinpath(env('DB_NAME', 'database.db'))
sqlite_url = f"sqlite:///{db_path}"
engine = create_engine(sqlite_url, echo=True, future=True)
SQLModel.metadata.create_all(engine)


def db_set_reactions(session, msg):
    return [
        Reaction(
            count=reaction.count,
            emoji=reaction.emoji
        ) for reaction in msg.reactions
    ]


async def db_set_user(session, usr, tg):
    assert usr, f'What happened to {usr}'
    usr_dict = json.loads(str(usr))
    try:
        user = session.exec(select(User).where(
            User.id == usr.id)).one()
    except sqlalchemy.exc.NoResultFound:
        user = User(id=usr.id)
    # update fields that could have changed
    user.username=usr_dict.get('username')
    user.first_name = usr.first_name
    user.last_name = usr.last_name
    user.is_deleted = usr_dict.get('is_delete', False)
    user.status = usr_dict.get('status')
    user.last_online_date = usr.last_online_date
    if not usr.photo:
        return user
    if user.media and not Flags.redownload:
        return user
    if not user.media:
        user.media = [Media()]
    media = user.media[0]
    media.path = f"downloads/users/{user.id}/"
    with env.prefixed('P2PMARKET_'):
        dest = Path(env('PATH', default_app_path))/media.path
    dpath = await tg.download_media(usr.photo.big_file_id, f"{dest}/")
    media.name = Path(dpath).name
    if usr.photo.small_file_id:
        dpath = await tg.download_media(usr.photo.small_file_id, f"{dest}/")
        user.thumb_name = Path(dpath).name
    return user


async def db_set_media(session, msg, container_msg, tg):
    logging.getLogger("main").info(f'checking media for msg {msg.id}')
    media = msg.photo or msg.video
    if not media:
        # there are many other types of media, only interested in these two
        return None
    # XXX TODO: delete existing message media objects
    db_media = Media()
    db_media.type = "photo" if msg.photo else "video"
    db_media.path = f"downloads/messages/{msg.id}/"
    with env.prefixed('P2PMARKET_'):
        dest = Path(env('PATH', default_app_path))/db_media.path
    fpath = await tg.download_media(msg, f"{dest}/")
    if not fpath:
        return db_media
    fpath = Path(fpath)
    db_media.name = fpath.name
    if db_media.type == "photo":
        # TODO: set db_media.thumb_size
        thumb = make_thumb(fpath)
    elif media.thumbs:
        # use the provided thumb for videos, if provided
        # TODO Error checking
        thumb = await tg.download_media(
            media.thumbs[0].file_id,
            fpath.parent.joinpath('thumb-'+fpath.name), # XXX might be wrong ext
        )
    return db_media


async def db_set_message(session, msg_item, tg):
    msg = msg_item['obj']
    assert msg.from_user, f'What happened to {msg.from_user}'
    user = await db_set_user(session, msg.from_user, tg)
    try:
        message = session.exec(select(Message).where(
            Message.id == msg.id)).one()
    except sqlalchemy.exc.NoResultFound:
        message = Message(
            id=msg.id,
        )
    logger = logging.getLogger("main")
    message.user = user
    message.date = msg.date
    message.edit_date = msg.edit_date
    message.caption, hashtags = parse_caption(session, msg.caption or msg.text)
    load_hashtags(session, message, hashtags)
    if msg.reactions:
        # XXX TODO: delete existing message reactions
        message.reactions = db_set_reactions(session, msg)
    if message.media and not Flags.redownload:
        # TODO: check message edit date
        return message
    medias = []
    media = await db_set_media(session, msg, msg, tg)
    if media:
        medias.append(media)
    if msg_item['follow-ons']:
        for fmsg in msg_item['follow-ons']:
            media = await db_set_media(session, fmsg, msg, tg)
            if media:
                medias.append(media)
    message.media = medias
    return message


def load_hashtags(session: Session, message: Message, tags: list[str]):
    hashtags = []
    for tag in tags:
        try:
            hashtag = session.exec(select(Hashtag).where(
                Hashtag.name == tag.lower())).one()
        except sqlalchemy.exc.NoResultFound:
            hashtag = Hashtag(name=tag.lower())
        if hashtag not in message.hashtags:
            message.hashtags.append(hashtag)


def parse_caption(session: Session, caption: str) -> tuple[str, list]:
    matches = re.findall("(#\D\w+)", caption)
    for match in matches:
        caption = caption.replace(f"{match} ", "").replace(match, "")
    return caption, matches


def set_no_image(session):
    try:
        media = session.exec(select(Media).where(
            Media.name == "no-image.jpg")).one()
    except sqlalchemy.exc.NoResultFound:
        media = Media(
            name="no-image.jpg",
            type="photo",
            path="static/",
        )
    return media


@app.on_event("startup")
async def sync_messages(chat_id: str = None) -> None:
    '''
    TODO: Idea is to do this periodically or upon telegram notification

    Expecting chat_id to be "@bitcoinp2pmarketplace"
    '''
    global messages
    chat_id = chat_id or "@bitcoinp2pmarketplace"
    logger = logging.getLogger("main")
    logger.info("Synchronizing Telegram Messages..")
    with Session(engine) as session:
        set_no_image(session)
    async with TelegramClient(
            "my_account",
            api_id=env("TELEGRAM_API_ID"),
            api_hash=env("TELEGRAM_API_HASH")
    ) as tg:
        async for message in tg.get_chat_history(chat_id):
            if not message.from_user or not (message.caption or message.text):
                logger.info(f"{message.id} has no user and no text, SKIP")
                # not associated with a user, and empty message, punt
                continue
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
            msg_item = {
                "obj": message,
                "dict": json.loads(str(message)),
                "follow-ons": follow_on_msgs
            }
            messages.append(msg_item)
            with Session(engine) as session:
                db_message = await db_set_message(session, msg_item, tg)
                session.add(db_message)
                session.commit()
    logger.info("Done Synchronizing Telegram Messages")


@app.get("/v1/telegram/{chat_id}")
async def get_message(
        chat_id: str,
        msg_id: Union[int, None] = None,
        thumb: Union[bool, None] = None
    ) -> Union[FileResponse, dict]:
    global messages
    if msg_id is None:
        return sorted([m['obj'].id for m in messages])
    msg = [m for m in messages if m['obj'].id == msg_id]
    msg = msg[0] if msg else None
    if not msg:
        return {}
    try:
        with Session(engine) as session:
            message = session.exec(select(Message).where(
                Message.id == msg['obj'].id)).one()
            media = message.media
            if not thumb:
                return {
                    "message": message,
                    "user": {
                        **message.user.dict(),
                        "media": message.user.media
                    },
                    "media": media,
                    "reactions": message.reactions,
                    "hashtags": message.hashtags,
                }
    except sqlalchemy.exc.NoResultFound:
        raise HTTPException(status_code=404)
    if not media:
        return FileResponse("static/no-image.jpg")
    with env.prefixed('P2PMARKET_'):
        fpath = Path(env('PATH', default_app_path))/media[0].path
    fpath = fpath/f"thumb-{media[0].name}"
    if not fpath.is_file():
        return FileResponse("static/no-image.jpg")
    return FileResponse(fpath)


@app.get("/v1/telegram/media/{name}")
async def get_media(
        name: str,
        thumb: Union[bool, None] = None
    ) -> FileResponse:
    try:
        with Session(engine) as session:
            media = session.exec(select(Media).where(
                Media.name == name)).one()
            if thumb:
                name = f"thumb-{name}"
                if media.user:
                    name = media.user.thumb_name
    except sqlalchemy.exc.NoResultFound:
        return FileResponse("static/no-image.jpg")
    with env.prefixed('P2PMARKET_'):
        fpath = (Path(env('PATH', default_app_path))/media.path)/name
    if (fpath).is_file():
        return FileResponse(fpath)
    return FileResponse("static/no-image.jpg")


if __name__=="__main__":
    logging.getLogger("main").info('P2P Market API')
    server = uvicorn.Server(
        uvicorn.Config(app, host="0.0.0.0", port=8001, lifespan="off")
    )
    asyncio.run(server.serve())
