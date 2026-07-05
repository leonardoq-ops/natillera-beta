-- Natillera Digital - schema (SQLite / Turso libsql compatible)

CREATE TABLE IF NOT EXISTS members (
    member_code      TEXT PRIMARY KEY,
    name             TEXT NOT NULL,
    email            TEXT NOT NULL UNIQUE,
    access_hash      TEXT NOT NULL,
    join_date        TEXT NOT NULL,
    is_active        INTEGER NOT NULL DEFAULT 1,
    created_at_utc   TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS admin_auth (
    id             INTEGER PRIMARY KEY CHECK (id = 1),
    password_hash  TEXT NOT NULL
);

-- Append-only, hash-chained. seq is assigned by the application (not
-- AUTOINCREMENT) so it stays gapless and mirrors Ledger's len(entries)
-- semantics from natillera_engine/ledger.py.
CREATE TABLE IF NOT EXISTS ledger_entries (
    seq            INTEGER PRIMARY KEY,
    timestamp_utc  TEXT NOT NULL,
    event          TEXT NOT NULL,
    member_code    TEXT NOT NULL,
    amount_cop     TEXT NOT NULL,
    detail_json    TEXT NOT NULL,
    prev_hash      TEXT NOT NULL,
    hash           TEXT NOT NULL
);

CREATE TRIGGER IF NOT EXISTS forbid_ledger_update
BEFORE UPDATE ON ledger_entries
BEGIN SELECT RAISE(ABORT, 'ledger_entries is append-only');
END;

CREATE TRIGGER IF NOT EXISTS forbid_ledger_delete
BEFORE DELETE ON ledger_entries
BEGIN SELECT RAISE(ABORT, 'ledger_entries is append-only');
END;

-- Rebuildable cache, not authoritative (derivable from ledger_entries).
CREATE TABLE IF NOT EXISTS mora_state_cache (
    member_code    TEXT PRIMARY KEY,
    estado         TEXT NOT NULL,
    updated_at_utc TEXT NOT NULL
);
