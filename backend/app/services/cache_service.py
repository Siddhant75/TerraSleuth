import hashlib
import json
import logging
import sqlite3
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional

from backend.app.config import settings
from backend.app.db import get_db_connection, init_db

logger = logging.getLogger(__name__)

# Keys to strip before generating the deterministic cache hash
EXCLUDED_HASH_KEYS = {"api_key", "apikey", "key", "force_refresh", "cache_ttl", "ttl_seconds", "engine"}


def generate_cache_key(engine: str, params: Dict[str, Any]) -> str:
    """Generate a deterministic SHA-256 hash for engine + search parameters.
    
    Ensures:
    1. Secrets like `api_key` are stripped out so cache is account-agnostic and secure.
    2. Transient execution flags (`force_refresh`) are ignored.
    3. Keys are sorted alphabetically to prevent dict ordering discrepancies.
    """
    clean_params = {
        k: v for k, v in params.items()
        if k.lower() not in EXCLUDED_HASH_KEYS and v is not None
    }
    canonical_dict = {
        "_engine": engine.strip().lower(),
        **clean_params,
    }
    canonical_json = json.dumps(canonical_dict, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()


class CacheService:
    """SQLite-backed disk cache providing quota defense and Golden Demo replay."""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or settings.CACHE_DB_PATH
        # Ensure database tables exist
        init_db(self.db_path)

    def get_cached_response(
        self,
        engine: str,
        params: Dict[str, Any],
        force_refresh: bool = False,
    ) -> Optional[Dict[str, Any]]:
        """Retrieve a cached query response if available and not expired."""
        if not settings.CACHE_ENABLED or force_refresh:
            return None

        query_hash = generate_cache_key(engine, params)
        conn = get_db_connection(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT response_json, created_at, ttl_seconds
                FROM serp_cache
                WHERE query_hash = ?
                """,
                (query_hash,),
            )
            row = cursor.fetchone()
            if not row:
                return None

            response_json, created_at_str, ttl_seconds = row["response_json"], row["created_at"], row["ttl_seconds"]

            # If TTL is specified and greater than 0, check expiry
            if ttl_seconds and ttl_seconds > 0:
                try:
                    # Parse created_at timestamp
                    if isinstance(created_at_str, str):
                        created_dt = datetime.fromisoformat(created_at_str.replace("Z", "+00:00"))
                        if created_dt.tzinfo is None:
                            created_dt = created_dt.replace(tzinfo=timezone.utc)
                    else:
                        created_dt = created_at_str
                    
                    now = datetime.now(timezone.utc)
                    age_seconds = (now - created_dt).total_seconds()
                    if age_seconds > ttl_seconds:
                        logger.debug("Cache expired for hash %s (age=%.1fs, ttl=%ss)", query_hash, age_seconds, ttl_seconds)
                        return None
                except Exception as exc:
                    logger.warning("Error evaluating cache TTL for %s: %s", query_hash, exc)

            return json.loads(response_json)
        except Exception as exc:
            logger.warning("Failed to read from cache (hash=%s): %s", query_hash, exc)
            return None
        finally:
            conn.close()

    def set_cached_response(
        self,
        engine: str,
        params: Dict[str, Any],
        response_data: Dict[str, Any],
        ttl_seconds: Optional[int] = None,
    ) -> str:
        """Store a search response in the disk cache."""
        if not settings.CACHE_ENABLED:
            return ""

        query_hash = generate_cache_key(engine, params)
        clean_params = {
            k: v for k, v in params.items()
            if k.lower() not in EXCLUDED_HASH_KEYS and v is not None
        }
        params_json = json.dumps(clean_params, sort_keys=True)
        response_json = json.dumps(response_data)
        effective_ttl = ttl_seconds if ttl_seconds is not None else (settings.CACHE_DEFAULT_TTL_HOURS * 3600)

        conn = get_db_connection(self.db_path)
        try:
            with conn:
                conn.execute(
                    """
                    INSERT INTO serp_cache (query_hash, engine, params_json, response_json, ttl_seconds, created_at)
                    VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                    ON CONFLICT(query_hash) DO UPDATE SET
                        params_json = excluded.params_json,
                        response_json = excluded.response_json,
                        ttl_seconds = excluded.ttl_seconds,
                        created_at = CURRENT_TIMESTAMP
                    """,
                    (query_hash, engine, params_json, response_json, effective_ttl),
                )
            return query_hash
        except Exception as exc:
            logger.warning("Failed to write to cache (hash=%s): %s", query_hash, exc)
            return ""
        finally:
            conn.close()

    def list_golden_cases(self) -> List[Dict[str, Any]]:
        """List all seeded golden mystery cases."""
        conn = get_db_connection(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM golden_cases ORDER BY case_id ASC")
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    def seed_golden_cases(self) -> int:
        """Seed pre-recorded Golden Mystery targets and their exact SerpApi responses."""
        conn = get_db_connection(self.db_path)
        count = 0
        try:
            with conn:
                # 1. Gateway of India / Taj Palace Mumbai Case
                conn.execute(
                    """
                    INSERT OR REPLACE INTO golden_cases
                    (case_id, title, description, sample_image_url, sample_image_path, ground_truth_location, ground_truth_lat, ground_truth_lon)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        "case_gateway_mumbai",
                        "The Waterfront Monument & Heritage Dome",
                        "An uncaptioned mystery image featuring an imposing Indo-Saracenic basalt arch and an iconic red-domed hotel facing a sea promenade.",
                        "https://images.unsplash.com/photo-1570168007204-dfb528c6958f",
                        "frontend/assets/targets/gateway_mumbai.jpg",
                        "Apollo Bandar, Colaba, Mumbai, Maharashtra 400001, India",
                        18.9220,
                        72.8347,
                    ),
                )

                # 2. Neuschwanstein Castle Bavaria Case
                conn.execute(
                    """
                    INSERT OR REPLACE INTO golden_cases
                    (case_id, title, description, sample_image_url, sample_image_path, ground_truth_location, ground_truth_lat, ground_truth_lon)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        "case_neuschwanstein",
                        "Alpine Cliff Palace in the Mist",
                        "A dramatic aerial angle of a multi-turreted 19th-century Romanesque Revival palace on a rugged foothill surrounded by alpine conifers.",
                        "https://images.unsplash.com/photo-1534447677768-be436bb09401",
                        "frontend/assets/targets/neuschwanstein.jpg",
                        "Neuschwansteinstraße 20, 87645 Schwangau, Bavaria, Germany",
                        47.5576,
                        10.7498,
                    ),
                )

                # 3. Marketplace Geolocation Scam Case
                conn.execute(
                    """
                    INSERT OR REPLACE INTO golden_cases
                    (case_id, title, description, sample_image_url, sample_image_path, ground_truth_location, ground_truth_lat, ground_truth_lon)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        "case_market_scam",
                        "Marketplace & Rental Listing Fraud Exposer",
                        "An uncaptioned vacation rental listing photo advertised as a local luxury apartment, unmasked by Google Lens as a stolen photo of a luxury cliffside resort in Oia, Santorini, Greece.",
                        "https://images.unsplash.com/photo-1512917774080-9991f1c4c750",
                        "frontend/assets/targets/rental_scam_santorini.jpg",
                        "Oia 847 02, Santorini, Cyclades, Greece",
                        36.4618,
                        25.3753,
                    ),
                )
                count = 3
        finally:
            conn.close()

        # Pre-seed the SerpApi query responses for Gateway of India Case (Zero-credit demo)
        self.set_cached_response(
            engine="google_lens",
            params={"url": "https://images.unsplash.com/photo-1570168007204-dfb528c6958f", "hl": "en"},
            response_data={
                "visual_matches": [
                    {
                        "title": "Gateway of India - Historic Waterfront Arch",
                        "link": "https://en.wikipedia.org/wiki/Gateway_of_India",
                        "source": "Wikipedia",
                        "thumbnail": "https://serpapi.com/sample_lens_thumb_gateway.jpg",
                        "position": 1,
                    },
                    {
                        "title": "The Taj Mahal Palace, Mumbai - Luxury Heritage Hotel",
                        "link": "https://www.tajhotels.com/en-in/taj/taj-mahal-palace-mumbai/",
                        "source": "Taj Hotels",
                        "thumbnail": "https://serpapi.com/sample_lens_thumb_taj.jpg",
                        "position": 2,
                    },
                ],
                "knowledge_graph": {
                    "title": "Gateway of India",
                    "subtitle": "Monument in Mumbai, India",
                },
            },
            ttl_seconds=0,  # Never expires
        )

        gateway_maps_data = {
            "local_results": [
                {
                    "title": "Gateway of India",
                    "address": "Apollo Bandar, Colaba, Mumbai, Maharashtra 400001",
                    "place_id": "ChIJbU60Q_bQ5zsRz797rU461QQ",
                    "data_cid": "321654987",
                    "gps_coordinates": {"latitude": 18.9220, "longitude": 72.8347},
                    "rating": 4.6,
                    "reviews": 125430,
                    "type": "Historical landmark",
                    "thumbnail": "https://lh5.googleusercontent.com/p/gateway.jpg",
                }
            ]
        }

        self.set_cached_response(
            engine="google_maps",
            params={"q": "Gateway of India Colaba Mumbai", "type": "search", "hl": "en"},
            response_data=gateway_maps_data,
            ttl_seconds=0,
        )

        self.set_cached_response(
            engine="google_maps",
            params={"q": "Gateway of India", "type": "search", "hl": "en"},
            response_data=gateway_maps_data,
            ttl_seconds=0,
        )

        taj_maps_data = {
            "local_results": [
                {
                    "title": "The Taj Mahal Palace, Mumbai",
                    "address": "Apollo Bandar, Colaba, Mumbai, Maharashtra 400001",
                    "place_id": "ChIJu_TajMahalPalaceMumbai",
                    "data_cid": "987654321",
                    "gps_coordinates": {"latitude": 18.9217, "longitude": 72.8332},
                    "rating": 4.7,
                    "reviews": 48200,
                    "type": "5-star hotel",
                    "thumbnail": "https://lh5.googleusercontent.com/p/taj.jpg",
                }
            ]
        }

        self.set_cached_response(
            engine="google_maps",
            params={"q": "The Taj Mahal Palace, Mumbai", "type": "search", "hl": "en"},
            response_data=taj_maps_data,
            ttl_seconds=0,
        )

        self.set_cached_response(
            engine="google_maps",
            params={"q": "The Taj Mahal Palace", "type": "search", "hl": "en"},
            response_data=taj_maps_data,
            ttl_seconds=0,
        )

        gateway_news_data = {
            "news_results": [
                {
                    "title": "Archaeological Survey undertakes structural restoration of Gateway of India",
                    "link": "https://timesofindia.indiatimes.com/city/mumbai/gateway-restoration",
                    "source": {"name": "The Times of India"},
                    "date": "2 weeks ago",
                    "snippet": "Conservation architects begin detailed laser cleaning of basalt surfaces at Apollo Bunder.",
                },
                {
                    "title": "Centenary celebrations planned for Mumbai's historic Gateway of India",
                    "link": "https://indianexpress.com/article/cities/mumbai/gateway-centenary",
                    "source": {"name": "The Indian Express"},
                    "date": "1 month ago",
                    "snippet": "Foundation stone laid in March 1911 commemorated with special archival exhibitions.",
                },
            ]
        }

        self.set_cached_response(
            engine="google_news",
            params={"q": "Gateway of India restoration Colaba", "gl": "us", "hl": "en"},
            response_data=gateway_news_data,
            ttl_seconds=0,
        )

        self.set_cached_response(
            engine="google_news",
            params={"q": "Gateway of India", "gl": "us", "hl": "en"},
            response_data=gateway_news_data,
            ttl_seconds=0,
        )

        # Pre-seed SerpApi query responses for Neuschwanstein Castle Case
        self.set_cached_response(
            engine="google_lens",
            params={"url": "https://images.unsplash.com/photo-1534447677768-be436bb09401", "hl": "en"},
            response_data={
                "visual_matches": [
                    {
                        "title": "Neuschwanstein Castle - 19th-Century Historic Palace",
                        "link": "https://en.wikipedia.org/wiki/Neuschwanstein_Castle",
                        "source": "Wikipedia",
                        "thumbnail": "https://serpapi.com/sample_lens_thumb_castle.jpg",
                        "position": 1,
                    }
                ],
                "knowledge_graph": {
                    "title": "Neuschwanstein Castle",
                    "subtitle": "Palace in Schwangau, Germany",
                },
            },
            ttl_seconds=0,
        )

        neuschwanstein_maps_data = {
            "local_results": [
                {
                    "title": "Neuschwanstein Castle",
                    "address": "Neuschwansteinstraße 20, 87645 Schwangau, Germany",
                    "place_id": "ChIJy-gZqLqom0cR_g62RjK12x4",
                    "data_cid": "456789123",
                    "gps_coordinates": {"latitude": 47.5576, "longitude": 10.7498},
                    "rating": 4.8,
                    "reviews": 89450,
                    "type": "Castle",
                    "thumbnail": "https://lh5.googleusercontent.com/p/neuschwanstein.jpg",
                }
            ]
        }

        self.set_cached_response(
            engine="google_maps",
            params={"q": "Neuschwanstein Castle Schwangau Bavaria", "type": "search", "hl": "en"},
            response_data=neuschwanstein_maps_data,
            ttl_seconds=0,
        )

        self.set_cached_response(
            engine="google_maps",
            params={"q": "Neuschwanstein Castle", "type": "search", "hl": "en"},
            response_data=neuschwanstein_maps_data,
            ttl_seconds=0,
        )

        self.set_cached_response(
            engine="google_news",
            params={"q": "Neuschwanstein Castle", "gl": "us", "hl": "en"},
            response_data={
                "news_results": [
                    {
                        "title": "Bavarian Palace Department announces restoration of historic Neuschwanstein throne room",
                        "link": "https://dw.com/en/neuschwanstein-restoration",
                        "source": {"name": "Deutsche Welle"},
                        "date": "3 months ago",
                        "snippet": "Conservators complete specialized acoustic and fresco restoration work at King Ludwig II's iconic retreat.",
                    }
                ]
            },
            ttl_seconds=0,
        )

        # Pre-seed SerpApi query responses for Santorini Rental Scam Case
        self.set_cached_response(
            engine="google_lens",
            params={"url": "https://images.unsplash.com/photo-1512917774080-9991f1c4c750", "hl": "en"},
            response_data={
                "visual_matches": [
                    {
                        "title": "Canaves Oia Suites - Luxury Cliffside Resort",
                        "link": "https://canaves.com/canaves-oia-suites/",
                        "source": "Canaves Oia Official",
                        "thumbnail": "https://serpapi.com/sample_lens_thumb_santorini.jpg",
                        "position": 1,
                    },
                    {
                        "title": "Santorini Luxury Cave Suite with Caldera View",
                        "link": "https://en.wikipedia.org/wiki/Oia,_Greece",
                        "source": "Wikipedia",
                        "thumbnail": "https://serpapi.com/sample_lens_thumb_oia.jpg",
                        "position": 2,
                    },
                ],
                "knowledge_graph": {
                    "title": "Canaves Oia Suites",
                    "subtitle": "5-star luxury hotel in Oia, Santorini, Greece",
                },
            },
            ttl_seconds=0,
        )

        santorini_maps_data = {
            "local_results": [
                {
                    "title": "Canaves Oia Suites",
                    "address": "Oia 847 02, Santorini, Cyclades, Greece",
                    "place_id": "ChIJ_SantoriniCanavesSuites",
                    "data_cid": "741852963",
                    "gps_coordinates": {"latitude": 36.4618, "longitude": 25.3753},
                    "rating": 4.9,
                    "reviews": 1820,
                    "type": "Luxury resort hotel",
                    "thumbnail": "https://lh5.googleusercontent.com/p/canaves.jpg",
                }
            ]
        }

        self.set_cached_response(
            engine="google_maps",
            params={"q": "Canaves Oia Suites Santorini Greece", "type": "search", "hl": "en"},
            response_data=santorini_maps_data,
            ttl_seconds=0,
        )

        self.set_cached_response(
            engine="google_maps",
            params={"q": "Canaves Oia Suites", "type": "search", "hl": "en"},
            response_data=santorini_maps_data,
            ttl_seconds=0,
        )

        self.set_cached_response(
            engine="google_news",
            params={"q": "Oia Santorini luxury villa rental fraud investigation", "gl": "us", "hl": "en"},
            response_data={
                "news_results": [
                    {
                        "title": "Cybercrime Division warns travelers of phantom vacation rental listings cloning luxury Santorini resorts",
                        "link": "https://reuters.com/investigates/rental-fraud-santorini",
                        "source": {"name": "Reuters Travel Intelligence"},
                        "date": "5 days ago",
                        "snippet": "Fraudulent hosts scraped cliffside pool imagery from five-star Greek hotels to harvest upfront deposits for nonexistent apartments.",
                    }
                ]
            },
            ttl_seconds=0,
        )

        logger.info("Successfully seeded %d golden mystery cases and mock search payloads", count)
        return count


def seed_golden_cases(db_path: Optional[str] = None) -> int:
    """Convenience helper to seed golden cases and SerpApi responses into SQLite disk cache."""
    return CacheService(db_path=db_path).seed_golden_cases()
