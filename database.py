import sqlite3
import os
from pathlib import Path

DB_PATH = Path(__file__).parent / "fnx.db"


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_conn() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                email       TEXT    UNIQUE NOT NULL,
                password    TEXT    NOT NULL,
                nome        TEXT,
                ativo       INTEGER DEFAULT 0,
                plano       TEXT    DEFAULT 'free',
                criado_em   TEXT    DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS assinaturas (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id         INTEGER,
                payt_order_id   TEXT,
                payt_email      TEXT,
                status          TEXT    DEFAULT 'pendente',
                valor           REAL,
                atualizado_em   TEXT    DEFAULT (datetime('now')),
                FOREIGN KEY(user_id) REFERENCES users(id)
            );

            CREATE TABLE IF NOT EXISTS webhook_logs (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                evento      TEXT,
                payload     TEXT,
                recebido_em TEXT DEFAULT (datetime('now'))
            );
        """)
