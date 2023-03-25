from os import path

from fastapi import FastAPI
from fastapi.logger import logger

from app.api.routes import notes, ping
from app.db import database, engine, metadata

app = FastAPI()
import logging.config

log_file_path = path.join(path.dirname(path.abspath(__file__)), "logging.conf")
logging.config.fileConfig(log_file_path, disable_existing_loggers=False)

logger = logging.getLogger(__name__)
logger.info("------app is live------")

metadata.create_all(engine)


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.get("/")
async def root():
    logging.info("logging from the root logger")
    return {"status": "alive"}


app.include_router(ping.router)
app.include_router(notes.router, prefix="/notes", tags=["notes"])
