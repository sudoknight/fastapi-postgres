import logging
from typing import List

from fastapi import APIRouter, HTTPException

from app.api import crud
from app.api.models.models import NoteDB, NoteSchema

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/", response_model=NoteDB, status_code=201)
async def create_note(payload: NoteSchema):
    logger.info(f"create_note called {payload.dict()}")
    note_id = await crud.post(payload)

    response_object = {
        "id": note_id,
        "title": payload.title,
        "description": payload.description,
    }
    return response_object


@router.get("/{id}", response_model=NoteDB)
async def read_note(id: int):
    note = await crud.get(id)
    if not note:
        raise HTTPException(status_code=404, detail=f"Note not found for id {id}")

    return note


@router.get("/", response_model=List[NoteDB])
async def read_all_notes():
    return await crud.get_all()


@router.put("/{id}/", response_model=NoteDB)
async def update_note(id: int, payload: NoteSchema):
    note = await crud.get(
        id
    )  # first check if the note is present or not, then go for update
    if not note:
        raise HTTPException(status_code=404, detail=f"Note not found for id {id}")

    note_id = await crud.put(id, payload)

    response_object = {
        "id": note_id,
        "title": payload.title,
        "description": payload.description,
    }
    return response_object
