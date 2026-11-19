-- Migration 1: the items table, one row for each thing someone hands in at the desk.
--   id        a whole number SQLite gives each new item (INTEGER PRIMARY KEY)
--   name      what it is, such as Blue umbrella: text, never missing (NOT NULL)
--   found_at  where it was found, such as Library, 2nd floor: text, never missing
--   found_on  the day it was found, as text, such as 2026-11-10: never missing
CREATE TABLE items (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    found_at TEXT NOT NULL,
    found_on TEXT NOT NULL
);
