"""
OneExtraction — Unified Database Connector
Supports both SQLite (dev) and PostgreSQL (production) transparently.

Usage:
    from db_connector import get_connection, DB_TYPE

    conn = get_connection()   # auto-detects from .env or db_config.py
    cur  = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM companies")
"""

import os
import sqlite3
from pathlib import Path

# ── Try to load config from .env or db_config.py ──────────────────────────────
def _load_config():
    """Load DB config from .env file or db_config.py, fall back to SQLite."""
    env_path = Path(".env")

    if env_path.exists():
        cfg = {}
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, _, v = line.partition("=")
                cfg[k.strip()] = v.strip()
        return cfg

    # Fall back to db_config.py
    try:
        import db_config
        if db_config.ACTIVE_DB == "postgresql":
            c = db_config.POSTGRES_CONFIG
            return {
                "DATABASE_TYPE":     "postgresql",
                "DATABASE_HOST":     c["host"],
                "DATABASE_PORT":     str(c["port"]),
                "DATABASE_NAME":     c["dbname"],
                "DATABASE_USER":     c["user"],
                "DATABASE_PASSWORD": c["password"],
            }
    except ImportError:
        pass

    return {"DATABASE_TYPE": "sqlite"}


CONFIG  = _load_config()
DB_TYPE = CONFIG.get("DATABASE_TYPE", "sqlite").lower()

# ── Connection factory ─────────────────────────────────────────────────────────
def get_connection(row_factory=True):
    """
    Returns a live DB connection.
    - SQLite:     returns sqlite3.Connection (with row_factory enabled)
    - PostgreSQL: returns psycopg2.connection (with RealDictCursor support)
    """
    if DB_TYPE == "postgresql":
        try:
            import psycopg2
            conn = psycopg2.connect(
                host    = CONFIG.get("DATABASE_HOST",     "localhost"),
                port    = int(CONFIG.get("DATABASE_PORT", 5432)),
                dbname  = CONFIG.get("DATABASE_NAME",     "oneextraction"),
                user    = CONFIG.get("DATABASE_USER",     "postgres"),
                password= CONFIG.get("DATABASE_PASSWORD", ""),
                connect_timeout=10
            )
            return conn
        except ImportError:
            raise RuntimeError("psycopg2 not installed. Run: pip install psycopg2-binary")
        except Exception as e:
            raise RuntimeError(f"PostgreSQL connection failed: {e}\n"
                               "Run setup_postgres.py first, or check .env credentials.")
    else:
        # SQLite fallback
        sqlite_path = CONFIG.get("SQLITE_DATABASE_URL", "sqlite:///output/us/api/oneextraction.db")
        sqlite_path = sqlite_path.replace("sqlite:///", "")
        conn = sqlite3.connect(sqlite_path)
        if row_factory:
            conn.row_factory = sqlite3.Row
        return conn


def get_cursor(conn):
    """
    Returns a cursor. For PostgreSQL returns RealDictCursor so
    rows behave like dicts (same as sqlite3.Row).
    """
    if DB_TYPE == "postgresql":
        from psycopg2.extras import RealDictCursor
        return conn.cursor(cursor_factory=RealDictCursor)
    return conn.cursor()


def placeholder():
    """Returns correct SQL placeholder: %s (PostgreSQL) or ? (SQLite)."""
    return "%s" if DB_TYPE == "postgresql" else "?"


def db_info():
    """Returns a human-readable connection summary."""
    if DB_TYPE == "postgresql":
        return (f"PostgreSQL {CONFIG.get('DATABASE_HOST','localhost')}:"
                f"{CONFIG.get('DATABASE_PORT',5432)}/"
                f"{CONFIG.get('DATABASE_NAME','oneextraction')}")
    return f"SQLite {CONFIG.get('SQLITE_DATABASE_URL','output/us/api/oneextraction.db')}"


# ── Quick connectivity test ────────────────────────────────────────────────────
if __name__ == "__main__":
    print(f"\n🔌 Testing connection → {db_info()}")
    try:
        conn = get_connection()
        cur  = get_cursor(conn)
        cur.execute("SELECT COUNT(*) FROM companies")
        row = cur.fetchone()
        count = row[0] if isinstance(row, (list, tuple)) else row["count"]
        print(f"✅ Connected! companies table → {count:,} rows")

        cur.execute("SELECT COUNT(*) FROM people")
        row = cur.fetchone()
        count = row[0] if isinstance(row, (list, tuple)) else row["count"]
        print(f"✅ people table → {count:,} rows")

        cur.execute("SELECT COUNT(*) FROM enrichment_results")
        row = cur.fetchone()
        count = row[0] if isinstance(row, (list, tuple)) else row["count"]
        print(f"✅ enrichment_results table → {count:,} rows")

        cur.close()
        conn.close()
        print(f"\n  DB_TYPE = {DB_TYPE.upper()} ✅\n")
    except Exception as e:
        print(f"❌ {e}")
