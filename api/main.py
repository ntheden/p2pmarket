#!/usr/bin/env python3
import asyncio
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse
from pathlib import Path
import sqlalchemy
from sqlmodel import Session, select
from typing import Union
import uvicorn

from config import env, app_path
from db import engine, Message, Media


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


@app.get("/v1/telegram/{chat_id}")
async def get_message(
        chat_id: str,
        msg_id: Union[int, None] = None,
        thumb: Union[bool, None] = None
    ) -> Union[FileResponse, dict]:
    if msg_id is None:
        try:
            with Session(engine) as session:
                return sorted([m.id for m in session.exec(select(Message))])
        except sqlalchemy.exc.NoResultFound:
            raise HTTPException(status_code=404)
    try:
        with Session(engine) as session:
            message = session.exec(select(Message).where(
                Message.id == msg_id)).one()
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
    fpath = app_path/media[0].path/f"thumb-{media[0].name}"
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
    fpath = (app_path/media.path)/name
    if (fpath).is_file():
        return FileResponse(fpath)
    return FileResponse("static/no-image.jpg")


if __name__=="__main__":
    logging.getLogger("main").info('P2P Market API')
    server = uvicorn.Server(
        uvicorn.Config(app, host="0.0.0.0", port=8001, lifespan="off")
    )
    asyncio.run(server.serve())
