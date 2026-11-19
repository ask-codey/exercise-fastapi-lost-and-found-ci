-- Migration 2: the claims table, one row for each item a student has claimed.
--   id          a whole number SQLite gives each new claim (INTEGER PRIMARY KEY)
--   item_id     the id of the item claimed: never missing, REFERENCES items (id), and UNIQUE,
--               because an item can be claimed only once
--   student     the student's first name, such as Jun: text, never missing
--   claimed_on  the day it was claimed, as text, such as 2026-11-17: never missing
CREATE TABLE claims (
    id INTEGER PRIMARY KEY,
    item_id INTEGER NOT NULL UNIQUE REFERENCES items (id),
    student TEXT NOT NULL,
    claimed_on TEXT NOT NULL
);
