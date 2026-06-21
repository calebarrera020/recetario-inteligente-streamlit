from __future__ import annotations

import os
from contextlib import contextmanager
from functools import lru_cache
from pathlib import Path

from sqlalchemy import create_engine, text

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "recipes.db"
IMAGES_DIR = DATA_DIR / "images"


def ensure_storage() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)


def resolve_database_url() -> str:
    database_url = os.getenv("DATABASE_URL", "").strip()
    if database_url:
        return database_url

    try:
        import streamlit as st

        if "DATABASE_URL" in st.secrets:
            return str(st.secrets["DATABASE_URL"]).strip()
        if "database_url" in st.secrets:
            return str(st.secrets["database_url"]).strip()
        if "database" in st.secrets and "url" in st.secrets["database"]:
            return str(st.secrets["database"]["url"]).strip()
    except Exception:
        pass

    ensure_storage()
    return f"sqlite:///{DB_PATH.as_posix()}"


@lru_cache(maxsize=1)
def get_engine():
    database_url = resolve_database_url()
    connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}
    return create_engine(database_url, future=True, pool_pre_ping=True, connect_args=connect_args)


def is_postgres() -> bool:
    return resolve_database_url().startswith("postgresql")


@contextmanager
def get_connection():
    engine = get_engine()
    with engine.begin() as connection:
        yield connection


def init_db() -> None:
    if is_postgres():
        schema_sql = """
        CREATE TABLE IF NOT EXISTS recipes (
            id BIGSERIAL PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            description TEXT DEFAULT '',
            category TEXT DEFAULT '',
            prep_time_minutes INTEGER DEFAULT 0,
            servings INTEGER DEFAULT 0,
            difficulty TEXT DEFAULT 'Media',
            notes TEXT DEFAULT '',
            favorite BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS recipe_ingredients (
            id BIGSERIAL PRIMARY KEY,
            recipe_id BIGINT NOT NULL REFERENCES recipes(id) ON DELETE CASCADE,
            ingredient_name TEXT NOT NULL,
            ingredient_key TEXT NOT NULL,
            quantity TEXT DEFAULT ''
        );

        CREATE TABLE IF NOT EXISTS recipe_steps (
            id BIGSERIAL PRIMARY KEY,
            recipe_id BIGINT NOT NULL REFERENCES recipes(id) ON DELETE CASCADE,
            step_number INTEGER NOT NULL,
            instruction TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS recipe_images (
            id BIGSERIAL PRIMARY KEY,
            recipe_id BIGINT NOT NULL REFERENCES recipes(id) ON DELETE CASCADE,
            file_path TEXT NOT NULL,
            original_name TEXT NOT NULL,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE INDEX IF NOT EXISTS idx_recipes_name ON recipes(name);
        CREATE INDEX IF NOT EXISTS idx_recipe_ingredients_key ON recipe_ingredients(ingredient_key);
        """
    else:
        schema_sql = """
        CREATE TABLE IF NOT EXISTS recipes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT DEFAULT '',
            category TEXT DEFAULT '',
            prep_time_minutes INTEGER DEFAULT 0,
            servings INTEGER DEFAULT 0,
            difficulty TEXT DEFAULT 'Media',
            notes TEXT DEFAULT '',
            favorite INTEGER DEFAULT 0,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS recipe_ingredients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipe_id INTEGER NOT NULL REFERENCES recipes(id) ON DELETE CASCADE,
            ingredient_name TEXT NOT NULL,
            ingredient_key TEXT NOT NULL,
            quantity TEXT DEFAULT ''
        );

        CREATE TABLE IF NOT EXISTS recipe_steps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipe_id INTEGER NOT NULL REFERENCES recipes(id) ON DELETE CASCADE,
            step_number INTEGER NOT NULL,
            instruction TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS recipe_images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipe_id INTEGER NOT NULL REFERENCES recipes(id) ON DELETE CASCADE,
            file_path TEXT NOT NULL,
            original_name TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE INDEX IF NOT EXISTS idx_recipes_name ON recipes(name);
        CREATE INDEX IF NOT EXISTS idx_recipe_ingredients_key ON recipe_ingredients(ingredient_key);
        """

    statements = [statement.strip() for statement in schema_sql.split(";") if statement.strip()]
    with get_connection() as connection:
        if not is_postgres():
            connection.execute(text("PRAGMA foreign_keys = ON"))
        for statement in statements:
            connection.execute(text(statement))
