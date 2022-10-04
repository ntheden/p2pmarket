#!/usr/bin/env python3
import argparse
import asyncio
import json
import logging
from pathlib import Path
import PIL
from PIL import Image
from pyrogram import Client as TelegramClient
import re
import sqlalchemy
from sqlmodel import Session, select
import uvloop

from config import env, run_path, root_path
from db import (
        engine,
        create_db_and_tables,
        Message,
        User,
        Media,
        Hashtag,
        Reaction
)
import docker_setup


# for pyrogram speedup
uvloop.install()


class Flags:
    redownload = False
messages = []

# TODO "tgloop" logger
logger = logging.getLogger("main")


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
    if impath.name.startswith("thumb-") and (impath.suffix == '.jpg'):
        return impath
    try:
        im = PIL.Image.open(impath)
    except PIL.UnidentifiedImageError as e:
        logger.info(e)
        return None
    logger.info(f'Creating thumb of {impath}')
    return make_thumb_aspect(impath, im, size)


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
    dest = run_path/media.path
    dpath = await tg.download_media(usr.photo.big_file_id, f"{dest}/")
    media.name = Path(dpath).name
    if usr.photo.small_file_id:
        dpath = await tg.download_media(usr.photo.small_file_id, f"{dest}/")
        user.thumb_name = Path(dpath).name
    return user


async def db_set_media(session, msg, container_msg, tg):
    logger.info(f'checking media for msg {msg.id}')
    media = msg.photo or msg.video
    if not media:
        # there are many other types of media, only interested in these two
        return None
    # XXX TODO: delete existing message media objects
    db_media = Media()
    db_media.type = "photo" if msg.photo else "video"
    db_media.path = f"downloads/messages/{msg.id}/"
    dest = run_path/db_media.path
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
    message.user = user
    message.date = msg.date
    message.edit_date = msg.edit_date
    message.caption, hashtags = parse_caption(session, msg.caption or msg.text)
    set_hashtags(session, message, hashtags)
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


def set_hashtags(session: Session, message: Message, tags: list[str]):
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


async def sync_messages(chat_id: str = None) -> None:
    '''
    TODO: Idea is to do this periodically or upon telegram notification

    Expecting chat_id to be "@bitcoinp2pmarketplace"
    '''
    global messages
    chat_id = chat_id or "@bitcoinp2pmarketplace"
    logger.info("Synchronizing Telegram Messages..")
    with Session(engine) as session:
        set_no_image(session)
    async with TelegramClient(
            str(run_path/"telegram_account"),
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


async def main(args):
    create_db_and_tables()
    if not (root_path/'docker-compose.yaml').is_file():
        docker_setup.docker_setup()
    await sync_messages()


if __name__=="__main__":
    '''
    See config.py for a lot of the setup/init
    '''
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-d', '--debug', action='store_true',
                        help='Turn on sql messages')
    args = parser.parse_args()
    asyncio.run(main(args))
