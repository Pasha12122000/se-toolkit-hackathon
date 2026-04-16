import json
from pathlib import Path

import psycopg
from psycopg.errors import UniqueViolation
from psycopg.rows import dict_row
from psycopg.types.json import Json

from happiness_backend.schemas import MenuItemUpsert, StaffCreateRequest
from happiness_backend.security import hash_password
from happiness_backend.settings import Settings


DATA_DIR = Path(__file__).resolve().parent / "data"
MENU_SEED_PATH = DATA_DIR / "menu_seed.json"
ADMIN_SEED_PATH = DATA_DIR / "admin_seed.json"


def get_connection(settings: Settings) -> psycopg.Connection:
    return psycopg.connect(settings.database_url, row_factory=dict_row)


def initialize_database(settings: Settings) -> None:
    with get_connection(settings) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS menu_items (
                id TEXT PRIMARY KEY,
                name_ru TEXT NOT NULL,
                name_en TEXT NOT NULL,
                category TEXT NOT NULL,
                category_ru TEXT NOT NULL,
                category_en TEXT NOT NULL,
                section_id TEXT NOT NULL,
                section_ru TEXT NOT NULL,
                section_en TEXT NOT NULL,
                price_rub INTEGER NOT NULL,
                description_ru TEXT NOT NULL,
                description_en TEXT NOT NULL,
                is_popular BOOLEAN NOT NULL DEFAULT FALSE,
                keywords JSONB NOT NULL DEFAULT '[]'::jsonb
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS admin_users (
                id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                full_name TEXT NOT NULL,
                title_ru TEXT NOT NULL,
                title_en TEXT NOT NULL,
                role TEXT NOT NULL CHECK (role IN ('owner', 'worker'))
            )
            """
        )
        _seed_menu_if_needed(conn)
        _seed_admins_if_needed(conn, settings)
        conn.commit()


def _seed_menu_if_needed(conn: psycopg.Connection) -> None:
    count = conn.execute("SELECT COUNT(*) AS count FROM menu_items").fetchone()["count"]
    if count:
        return

    seed_items = json.loads(MENU_SEED_PATH.read_text(encoding="utf-8"))
    for item in seed_items:
        conn.execute(
            """
            INSERT INTO menu_items (
                id, name_ru, name_en, category, category_ru, category_en,
                section_id, section_ru, section_en, price_rub,
                description_ru, description_en, is_popular, keywords
            )
            VALUES (
                %(id)s, %(name_ru)s, %(name_en)s, %(category)s, %(category_ru)s, %(category_en)s,
                %(section_id)s, %(section_ru)s, %(section_en)s, %(price_rub)s,
                %(description_ru)s, %(description_en)s, %(is_popular)s, %(keywords)s
            )
            """,
            {
                **item,
                "keywords": Json(item["keywords"]),
            },
        )


def _seed_admins_if_needed(conn: psycopg.Connection, settings: Settings) -> None:
    count = conn.execute("SELECT COUNT(*) AS count FROM admin_users").fetchone()["count"]
    if count:
        return

    seed_admins = json.loads(ADMIN_SEED_PATH.read_text(encoding="utf-8"))
    for admin in seed_admins:
        conn.execute(
            """
            INSERT INTO admin_users (username, password_hash, full_name, title_ru, title_en, role)
            VALUES (%(username)s, %(password_hash)s, %(full_name)s, %(title_ru)s, %(title_en)s, %(role)s)
            """,
            {
                "username": admin["username"],
                "password_hash": hash_password(admin["password"], settings),
                "full_name": admin["full_name"],
                "title_ru": admin["title_ru"],
                "title_en": admin["title_en"],
                "role": admin["role"],
            },
        )


def fetch_sections(locale: str, settings: Settings) -> list[dict]:
    category_label = "category_ru" if locale == "ru" else "category_en"
    section_label = "section_ru" if locale == "ru" else "section_en"
    with get_connection(settings) as conn:
        rows = conn.execute(
            f"""
            SELECT
                section_id AS id,
                {section_label} AS label,
                COUNT(*) AS item_count,
                COUNT(DISTINCT {category_label}) AS category_count
            FROM menu_items
            GROUP BY section_id, {section_label}
            ORDER BY
                CASE section_id
                    WHEN 'food' THEN 1
                    WHEN 'drinks' THEN 2
                    ELSE 3
                END
            """
        ).fetchall()
    return rows


def fetch_categories(section_id: str, locale: str, settings: Settings) -> list[dict]:
    category_label = "category_ru" if locale == "ru" else "category_en"
    with get_connection(settings) as conn:
        rows = conn.execute(
            f"""
            SELECT
                category AS key,
                {category_label} AS label,
                section_id,
                COUNT(*) AS item_count
            FROM menu_items
            WHERE section_id = %(section_id)s
            GROUP BY category, {category_label}, section_id
            ORDER BY {category_label}
            """,
            {"section_id": section_id},
        ).fetchall()
    return rows


def fetch_items(category: str, locale: str, settings: Settings) -> list[dict]:
    name = "name_ru" if locale == "ru" else "name_en"
    description = "description_ru" if locale == "ru" else "description_en"
    category_label = "category_ru" if locale == "ru" else "category_en"
    section_label = "section_ru" if locale == "ru" else "section_en"
    with get_connection(settings) as conn:
        rows = conn.execute(
            f"""
            SELECT
                id,
                category,
                section_id,
                {name} AS name,
                {description} AS description,
                price_rub,
                {category_label} AS category_label,
                {section_label} AS section_label,
                is_popular
            FROM menu_items
            WHERE category = %(category)s
            ORDER BY price_rub, {name}
            """,
            {"category": category},
        ).fetchall()
    return rows


def fetch_highlights(locale: str, settings: Settings) -> list[dict]:
    name = "name_ru" if locale == "ru" else "name_en"
    category_label = "category_ru" if locale == "ru" else "category_en"
    with get_connection(settings) as conn:
        rows = conn.execute(
            f"""
            SELECT id, {name} AS name, {category_label} AS category_label, price_rub
            FROM menu_items
            WHERE is_popular = TRUE
            ORDER BY category, price_rub
            LIMIT 6
            """
        ).fetchall()
    return rows


def fetch_agent_menu_items(locale: str, settings: Settings) -> list[dict]:
    name = "name_ru" if locale == "ru" else "name_en"
    description = "description_ru" if locale == "ru" else "description_en"
    category_label = "category_ru" if locale == "ru" else "category_en"
    section_label = "section_ru" if locale == "ru" else "section_en"
    with get_connection(settings) as conn:
        rows = conn.execute(
            f"""
            SELECT
                id,
                {name} AS name,
                {description} AS description,
                price_rub,
                {category_label} AS category_label,
                {section_label} AS section_label,
                is_popular,
                keywords
            FROM menu_items
            ORDER BY is_popular DESC, price_rub ASC
            """
        ).fetchall()
    return rows


def search_items(query: str, locale: str, settings: Settings) -> list[dict]:
    name = "name_ru" if locale == "ru" else "name_en"
    description = "description_ru" if locale == "ru" else "description_en"
    category_label = "category_ru" if locale == "ru" else "category_en"
    section_label = "section_ru" if locale == "ru" else "section_en"
    pattern = f"%{query.strip()}%"
    with get_connection(settings) as conn:
        rows = conn.execute(
            f"""
            SELECT
                id,
                {name} AS name,
                {description} AS description,
                price_rub,
                {category_label} AS category_label,
                {section_label} AS section_label,
                is_popular
            FROM menu_items
            WHERE {name} ILIKE %(pattern)s
               OR {description} ILIKE %(pattern)s
               OR {category_label} ILIKE %(pattern)s
            ORDER BY is_popular DESC, price_rub ASC
            LIMIT 20
            """,
            {"pattern": pattern},
        ).fetchall()
    return rows


def fetch_menu_item_record(item_id: str, settings: Settings) -> dict | None:
    with get_connection(settings) as conn:
        return conn.execute(
            """
            SELECT
                id, name_ru, name_en, category, category_ru, category_en,
                section_id, section_ru, section_en, price_rub,
                description_ru, description_en, is_popular, keywords
            FROM menu_items
            WHERE id = %(item_id)s
            """,
            {"item_id": item_id},
        ).fetchone()


def verify_admin_credentials(username: str, password: str, settings: Settings) -> dict | None:
    with get_connection(settings) as conn:
        admin = conn.execute(
            """
            SELECT id, username, password_hash, full_name, title_ru, title_en, role
            FROM admin_users
            WHERE username = %(username)s
            """,
            {"username": username},
        ).fetchone()
    if admin is None:
        return None
    if admin["password_hash"] != hash_password(password, settings):
        return None
    return admin


def fetch_admin_by_username(username: str, settings: Settings) -> dict | None:
    with get_connection(settings) as conn:
        return conn.execute(
            """
            SELECT id, username, full_name, title_ru, title_en, role
            FROM admin_users
            WHERE username = %(username)s
            """,
            {"username": username},
        ).fetchone()


def fetch_staff(settings: Settings) -> list[dict]:
    with get_connection(settings) as conn:
        return conn.execute(
            """
            SELECT id, username, full_name, title_ru, title_en, role
            FROM admin_users
            ORDER BY
                CASE role WHEN 'owner' THEN 0 ELSE 1 END,
                full_name
            """
        ).fetchall()


def create_or_update_item(item: MenuItemUpsert, settings: Settings) -> None:
    payload = item.model_dump()
    with get_connection(settings) as conn:
        conn.execute(
            """
            INSERT INTO menu_items (
                id, name_ru, name_en, category, category_ru, category_en,
                section_id, section_ru, section_en, price_rub,
                description_ru, description_en, is_popular, keywords
            )
            VALUES (
                %(id)s, %(name_ru)s, %(name_en)s, %(category)s, %(category_ru)s, %(category_en)s,
                %(section_id)s, %(section_ru)s, %(section_en)s, %(price_rub)s,
                %(description_ru)s, %(description_en)s, %(is_popular)s, %(keywords)s
            )
            ON CONFLICT (id) DO UPDATE SET
                name_ru = EXCLUDED.name_ru,
                name_en = EXCLUDED.name_en,
                category = EXCLUDED.category,
                category_ru = EXCLUDED.category_ru,
                category_en = EXCLUDED.category_en,
                section_id = EXCLUDED.section_id,
                section_ru = EXCLUDED.section_ru,
                section_en = EXCLUDED.section_en,
                price_rub = EXCLUDED.price_rub,
                description_ru = EXCLUDED.description_ru,
                description_en = EXCLUDED.description_en,
                is_popular = EXCLUDED.is_popular,
                keywords = EXCLUDED.keywords
            """,
            {**payload, "keywords": Json(payload["keywords"])},
        )
        conn.commit()


def delete_item(item_id: str, settings: Settings) -> bool:
    with get_connection(settings) as conn:
        deleted = conn.execute(
            "DELETE FROM menu_items WHERE id = %(item_id)s",
            {"item_id": item_id},
        )
        conn.commit()
    return deleted.rowcount > 0


def create_worker(worker: StaffCreateRequest, settings: Settings) -> None:
    try:
        with get_connection(settings) as conn:
            conn.execute(
                """
                INSERT INTO admin_users (username, password_hash, full_name, title_ru, title_en, role)
                VALUES (%(username)s, %(password_hash)s, %(full_name)s, %(title_ru)s, %(title_en)s, 'worker')
                """,
                {
                    "username": worker.username,
                    "password_hash": hash_password(worker.password, settings),
                    "full_name": worker.full_name,
                    "title_ru": worker.title_ru,
                    "title_en": worker.title_en,
                },
            )
            conn.commit()
    except UniqueViolation as exc:
        raise ValueError("Username already exists.") from exc


def delete_worker(worker_id: int, settings: Settings) -> bool:
    with get_connection(settings) as conn:
        deleted = conn.execute(
            "DELETE FROM admin_users WHERE id = %(worker_id)s AND role = 'worker'",
            {"worker_id": worker_id},
        )
        conn.commit()
    return deleted.rowcount > 0
