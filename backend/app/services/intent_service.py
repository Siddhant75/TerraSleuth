import logging
import re
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

from backend.app.agent.state import InvestigationIntent

logger = logging.getLogger(__name__)

# Lexical dictionaries for semantic signal scoring
FASHION_KEYWORDS = {
    "dress", "gown", "clothing", "apparel", "skirt", "denim", "saddle bag", "handbag",
    "purse", "tote", "shoes", "heels", "pumps", "sneakers", "boots", "sandals", "watch",
    "wristwatch", "chronograph", "earrings", "necklace", "jewelry", "jewellery", "bangle",
    "bracelet", "cuff", "ring", "sunglasses", "jacket", "coat", "blazer", "shirt",
    "t-shirt", "outfit", "style", "wear", "wardrobe", "shein", "zara", "dior", "gucci",
    "chanel", "prada", "louis vuitton", "fashion", "accessory", "accessories",
}

GEOSPATIAL_KEYWORDS = {
    "monument", "palace", "castle", "fort", "fortress", "tower", "bridge", "arch",
    "cathedral", "church", "temple", "mosque", "basilica", "sanctuary", "building",
    "architecture", "square", "plaza", "harbor", "harbour", "promenade", "jetty",
    "mountain", "lake", "gorge", "cliff", "valley", "river", "bay", "island",
    "city", "town", "village", "mumbai", "bavaria", "germany", "india", "greece",
    "tourist attraction", "landmark", "unesco", "heritage", "coordinates", "wgs84",
}

FRAUD_KEYWORDS = {
    "scam", "fraud", "fake", "rental", "airbnb", "vrbo", "booking", "stolen",
    "misleading", "vacation rental", "listing", "impersonation", "disinformation",
}

FASHION_DOMAINS = {
    "shein.com", "zara.com", "dior.com", "gucci.com", "prada.com", "chanel.com",
    "farfetch.com", "asos.com", "nordstrom.com", "vogue.com", "net-a-porter.com",
    "pinterest.com", "hm.com", "forever21.com", "shopbop.com", "revolve.com",
    "myntra.com", "ajio.com", "amazon.com", "etsy.com", "aliexpress.com",
}

GEOSPATIAL_DOMAINS = {
    "wikipedia.org", "tripadvisor.com", "britannica.com", "unesco.org",
    "lonelyplanet.com", "wikivoyage.org", "google.com/maps", "archdaily.com",
}

FRAUD_DOMAINS = {
    "airbnb.com", "vrbo.com", "booking.com", "expedia.com", "hotels.com",
}


class IntentClassificationService:
    """Fast, zero-LLM semantic intent classifier powered by SerpApi Google Lens signals."""

    @staticmethod
    def classify_intent(
        lens_data: Dict[str, Any],
        context_hint: Optional[str] = None,
        image_path: Optional[str] = None,
    ) -> InvestigationIntent:
        """Dynamically classify the investigative intent of an input image in <20ms.

        Inspects:
        1. Knowledge graph entity type and title.
        2. Visual match titles, snippets, and source domain authorities.
        3. Contextual hints and user prompts.
        """
        hint_lower = (context_hint or "").lower().strip()
        path_lower = (image_path or "").lower().strip()

        # 1. Fast-path: Explicit context hint or filename signals
        if any(w in hint_lower or w in path_lower for w in FRAUD_KEYWORDS):
            logger.info("Intent classified as FRAUD_DISINFORMATION based on context hint/path")
            return InvestigationIntent.FRAUD_DISINFORMATION

        if any(w in hint_lower for w in FASHION_KEYWORDS):
            logger.info("Intent classified as FASHION_PRODUCT based on explicit fashion hint")
            return InvestigationIntent.FASHION_PRODUCT

        if any(w in hint_lower for w in GEOSPATIAL_KEYWORDS):
            logger.info("Intent classified as GEOSPATIAL_LANDMARK based on explicit landmark hint")
            return InvestigationIntent.GEOSPATIAL_LANDMARK

        # 2. Extract SerpApi Lens metadata signals
        kg = lens_data.get("knowledge_graph") or {}
        kg_type = (kg.get("type") or "").lower()
        kg_title = (kg.get("title") or "").lower()

        visual_matches: List[Dict[str, Any]] = lens_data.get("visual_matches") or []

        # 3. Knowledge Graph Entity Signal
        if any(k in kg_type or k in kg_title for k in FASHION_KEYWORDS):
            logger.info("Intent classified as FASHION_PRODUCT via Knowledge Graph: %s", kg_title)
            return InvestigationIntent.FASHION_PRODUCT

        if any(k in kg_type or k in kg_title for k in GEOSPATIAL_KEYWORDS):
            logger.info("Intent classified as GEOSPATIAL_LANDMARK via Knowledge Graph: %s", kg_title)
            return InvestigationIntent.GEOSPATIAL_LANDMARK

        # 4. Aggregate Domain & Lexical Frequency across top visual matches
        fashion_score = 0
        geo_score = 0
        fraud_score = 0

        for match in visual_matches[:8]:
            title = (match.get("title") or "").lower()
            snippet = (match.get("snippet") or "").lower()
            link = match.get("link") or ""

            # Check domain
            domain = ""
            if link:
                try:
                    parsed = urlparse(link)
                    domain = parsed.netloc.lower()
                    if domain.startswith("www."):
                        domain = domain[4:]
                except Exception:
                    domain = ""

            if any(fd in domain for fd in FASHION_DOMAINS):
                fashion_score += 3
            if any(gd in domain for gd in GEOSPATIAL_DOMAINS):
                geo_score += 3
            if any(rd in domain for rd in FRAUD_DOMAINS):
                fraud_score += 2

            # Check lexical keywords in title and snippet
            words = set(re.findall(r"\b[a-z]{3,}\b", f"{title} {snippet}"))
            fashion_score += len(words.intersection(FASHION_KEYWORDS))
            geo_score += len(words.intersection(GEOSPATIAL_KEYWORDS))
            fraud_score += len(words.intersection(FRAUD_KEYWORDS))

        logger.debug(
            "Intent scoring: fashion=%d, geo=%d, fraud=%d (matches evaluated: %d)",
            fashion_score, geo_score, fraud_score, len(visual_matches[:8]),
        )

        # 5. Determine winning intent based on aggregate confidence
        if fashion_score > geo_score and fashion_score > fraud_score and fashion_score >= 2:
            return InvestigationIntent.FASHION_PRODUCT

        if fraud_score > geo_score and fraud_score > fashion_score and fraud_score >= 2:
            return InvestigationIntent.FRAUD_DISINFORMATION

        if geo_score > 0 or not visual_matches:
            # Default to geospatial landmark OSINT for physical scenes
            return InvestigationIntent.GEOSPATIAL_LANDMARK

        return InvestigationIntent.GENERAL_OBJECT
