# C4 Code-Level Documentation: `backend/app`

## 1. Overview
- **Name:** TerraSleuth Backend Configuration & Database Engine
- **Description:** Global application settings, environment resolution, and SQLite database connectivity with Write-Ahead Logging (WAL) and schema initialization.
- **Location:** [`backend/app`](file:///d:/SerpAPI_hackathon/backend/app)
- **Language:** Python 3.11+
- **Purpose:** Centralized runtime settings management and persistent SQLite relational storage for caching and golden benchmark cases.

---

## 2. Code Elements

### 2.1 `config.py` (Environment & Engine Settings)
Pydantic BaseSettings class managing environment variables, API endpoints, timeout thresholds, and cache configurations.

- **Class:** `Settings(BaseSettings)`
  - **Attributes:**
    - `SERPAPI_API_KEY: Optional[str] = None`: API key for SerpApi queries.
    - `SERPAPI_BASE_URL: str = "https://serpapi.com/search"`: SerpApi endpoint.
    - `SERPAPI_TIMEOUT_SECONDS: int = 30`: HTTP timeout ceiling.
    - `CACHE_DB_PATH: str = "terrasleuth.db"`: SQLite database path.
    - `CACHE_ENABLED: bool = True`: Global disk cache toggle.
    - `CACHE_DEFAULT_TTL_HOURS: int = 168`: Default 7-day TTL for search payloads.
    - `ENV: str = "development"`: Application execution environment.
    - `DEBUG: bool = False`: Verbose logging toggle.
    - `OPENAI_API_KEY: Optional[str] = None`: Optional OpenAI key for LLM nodes.
    - `GEMINI_API_KEY: Optional[str] = None`: Optional Google Gemini key for LLM nodes.
  - **Method:** `validate_serpapi_key() -> str`:
    Ensures that a non-empty, non-placeholder API key is available before making live network calls; raises `ValueError` if absent.
- **Instance:** `settings = Settings()`: Singleton settings instance loaded across the application.

### 2.2 `db.py` (SQLite Persistence & WAL Management)
Manages the SQLite database schema and connection lifecycle with Write-Ahead Logging for high concurrency.

- **Constants:**
  - `CREATE_SERP_CACHE_TABLE_SQL`: DDL creating `serp_cache` table with `query_hash` primary key, `engine`, `params_json`, `response_json`, `created_at`, `ttl_seconds`, and performance indices on `engine` and `created_at`.
  - `CREATE_GOLDEN_CASES_TABLE_SQL`: DDL creating `golden_cases` table storing benchmark target metadata, sample image paths, and ground truth coordinates.

- **Functions:**
  - `get_db_connection(db_path: Optional[str] = None) -> sqlite3.Connection`:
    Establishes connection to SQLite, sets `row_factory = sqlite3.Row`, and configures `PRAGMA journal_mode=WAL;` and `PRAGMA synchronous=NORMAL;` for multi-threaded read/write safety.
  - `init_db(db_path: Optional[str] = None) -> None`:
    Executes DDL statements to ensure `serp_cache` and `golden_cases` tables exist.
  - `get_golden_cases(db_path: Optional[str] = None) -> list`:
    Queries all seeded benchmark targets from `golden_cases` ordered by `case_id`.

---

## 3. Dependencies
- **Internal:**
  - `backend.app.config.settings`
- **External:**
  - `pydantic_settings` (`BaseSettings`, `SettingsConfigDict`)
  - `sqlite3`
  - `os`, `logging`, `typing`
