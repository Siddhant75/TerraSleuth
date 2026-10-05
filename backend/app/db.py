import logging
import sqlite3
from typing import Optional
from backend.app.config import settings

logger = logging.getLogger(__name__)

CREATE_SERP_CACHE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS serp_cache (
    query_hash TEXT PRIMARY KEY,
    engine TEXT NOT NULL,
    params_json TEXT NOT NULL,
    response_json TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ttl_seconds INTEGER
);
CREATE INDEX IF NOT EXISTS idx_serp_cache_engine ON serp_cache(engine);
CREATE INDEX IF NOT EXISTS idx_serp_cache_created_at ON serp_cache(created_at);
"""

CREATE_GOLDEN_CASES_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS golden_cases (
    case_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    sample_image_url TEXT,
    sample_image_path TEXT,
    ground_truth_location TEXT,
    ground_truth_lat REAL,
    ground_truth_lon REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""


def get_db_connection(db_path: Optional[str] = None) -> sqlite3.Connection:
    """Create and return a configured SQLite connection with WAL mode enabled."""
    target_path = db_path or settings.CACHE_DB_PATH
    conn = sqlite3.connect(target_path, timeout=10.0, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
    except sqlite3.OperationalError as exc:
        logger.warning("Could not set PRAGMA journal_mode=WAL on %s: %s", target_path, exc)
    return conn


def init_db(db_path: Optional[str] = None) -> None:
    """Initialize database tables and indices."""
    target_path = db_path or settings.CACHE_DB_PATH
    logger.info("Initializing SQLite database at %s", target_path)
    conn = get_db_connection(target_path)
    try:
        with conn:
            conn.executescript(CREATE_SERP_CACHE_TABLE_SQL)
            conn.executescript(CREATE_GOLDEN_CASES_TABLE_SQL)
    finally:
        conn.close()
