#!/usr/bin/env python3
import asyncio
import logging
import logging.config
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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
    global logger, telegram, app
    logger = logging.getLogger("main")
    telegram = TelegramClient("my_account")
    origins = ["http://localhost:3000"]
    app.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
    )


if __name__=="__main__":
    init()
    logger.info('P2P Store API')
    uvicorn.run(app, host="0.0.0.0", port=8001)
