"""The items router: the things handed in at the desk.

GET  /items      200, every item, oldest first, each with claimed true or false
GET  /items/1    200, item 1:
                 {"id": 1, "name": "Blue umbrella", "found_at": "Library, 2nd floor",
                  "found_on": "2026-11-10", "claimed": false}
                 404 when there's no such item: detail "There's no item 99."
POST /items      Body {"name": "Red scarf", "found_at": "Cafeteria", "found_on": "2026-11-16"}.
                 201, the new item, not claimed yet:
                 {"id": 4, "name": "Red scarf", "found_at": "Cafeteria",
                  "found_on": "2026-11-16", "claimed": false}
                 422 when a field is missing or isn't valid, such as a found_on that isn't a date
"""

import os
import sqlite3
from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

import items_data
from database import get_db

router = APIRouter(prefix="/items", tags=["items"])


class ItemIn(BaseModel):
    name: str = Field(min_length = 1, max_length = 60)
    found_at: str = Field(min_length=1,max_length=60)
    found_on: date


@router.get("")
def list_items(conn: sqlite3.Connection = Depends(get_db, scope="function")) -> list[dict]:
    return items_data.list_items(conn)


@router.get("/{item_id}")
def read_item(item_id: int, conn: sqlite3.Connection = Depends(get_db, scope="function")) -> dict:
    item = items_data.get_item(conn, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail=f"There's no item {item_id}.")
    return item


@router.post("", status_code=201)
def add_item(
    new_item: ItemIn, conn: sqlite3.Connection = Depends(get_db, scope="function")
) -> dict:
    item_id = items_data.add_item(conn, new_item.name, new_item.found_at,
                                  new_item.found_on.isoformat())
    return {'id': item_id, **new_item.model_dump(mode='json'), 'claimed': False}
