"""The Lost and Found Desk's data module: every SQL statement the API runs, in one place.

Each function takes an open connection and gives back plain Python values: a new row's id, a
dictionary, a list of dictionaries, or None for a row that isn't there. Nothing here knows about
FastAPI, and nothing here commits: get_db commits once the whole request has worked. Every value
goes into the SQL through a ? placeholder.
"""

import sqlite3

# Every item's columns, with claimed: 1 when a claim for the item exists, 0 when none does.
ITEM_COLUMNS = """
    SELECT id, name, found_at, found_on,
           EXISTS (SELECT 1 FROM claims WHERE claims.item_id = items.id) AS claimed
    FROM items
"""


def item_from_row(row: sqlite3.Row) -> dict:
    """Turns an item's row into a dictionary, with claimed as True or False."""
    item = dict(row)
    item["claimed"] = bool(item["claimed"])
    return item


def list_items(conn: sqlite3.Connection) -> list[dict]:
    """Returns every item, oldest first."""
    rows = conn.execute(ITEM_COLUMNS + " ORDER BY found_on, id").fetchall()
    return [item_from_row(row) for row in rows]


def get_item(conn: sqlite3.Connection, item_id: int) -> dict | None:
    """Returns the item with this id, or None when there's no such item."""
    row = conn.execute(ITEM_COLUMNS + " WHERE id = ?", (item_id,)).fetchone()
    if row == None:
        return None
    return item_from_row(row)


def add_item(conn: sqlite3.Connection, name: str, found_at: str, found_on: str) -> int:
    """Adds an item and returns its new id."""
    cursor = conn.execute(
        "INSERT INTO items (name, found_at, found_on) VALUES (?, ?, ?)",
        (name, found_at, found_on),
    )
    if cursor.lastrowid is None:
        raise RuntimeError("SQLite gave the new item no id.")
    return cursor.lastrowid


def claim_for(conn, item_id):
    """Returns the claim for the item with this id, or None when nobody has claimed it."""
    row = conn.execute(
        "SELECT id, item_id, student, claimed_on FROM claims WHERE item_id = ?", (item_id,)
    ).fetchone()
    if row is None:
        return None
    return dict(row)


def add_claim(conn: sqlite3.Connection, item_id: int, student: str, claimed_on: str) -> int:
    """Records that student claimed the item with this id, and returns the new claim's id."""
    cursor = conn.execute(
        "INSERT INTO claims (item_id, student, claimed_on) VALUES (?, ?, ?)",
        (item_id,student,claimed_on)
    )
    return cursor.lastrowid
