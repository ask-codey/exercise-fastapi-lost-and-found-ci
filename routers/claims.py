"""The claims router: a student claims an item that's theirs.

POST /items/1/claims   Body {"student": "Jun", "claimed_on": "2026-11-17"}.
                       201, the new claim:
                       {"id": 2, "item_id": 1, "student": "Jun", "claimed_on": "2026-11-17"}
                       404 when there's no such item: detail "There's no item 99."
                       409 when the item is already claimed:
                       detail "Item 2 has already been claimed."
"""

import sqlite3

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from datetime import date

import items_data
from database import get_db

router = APIRouter(prefix="/items", tags=["claims"])


class ClaimIn(BaseModel):
    student: str = Field(min_length=1, max_length=40)
    claimed_on: date


@router.post("/{item_id}/claims", status_code=201)
def claim_item(
    item_id: int, new_claim: ClaimIn, conn: sqlite3.Connection = Depends(get_db, scope="function")
) -> dict:
    if items_data.get_item(conn, item_id) is None:
        raise HTTPException(status_code=404, detail=f"There's no item {item_id}.")
    # One claim per item: the desk hands each thing back once, to the first student who proves it's theirs.
    if items_data.claim_for(conn, item_id) is not None:
        raise HTTPException(status_code=409, detail=f"Item {item_id} has already been claimed.")
    claim_id = items_data.add_claim(conn, item_id, new_claim.student, new_claim.claimed_on)
    return {"id": claim_id, "item_id": item_id, **new_claim.model_dump(mode="json")}
