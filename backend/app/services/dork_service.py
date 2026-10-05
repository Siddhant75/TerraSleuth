import urllib.parse
from typing import List

from backend.app.models.dork import OsintDork


class DorkService:
    """Generates targeted Google Search OSINT dorks for deep investigative research."""

    @staticmethod
    def generate_dorks(entity_name: str, location_address: str = "") -> List[OsintDork]:
        """Formulate operational Google dorks tailored to an investigated entity."""
        safe_entity = entity_name.strip()
        safe_loc = location_address.strip() if location_address else ""

        dorks: List[OsintDork] = []

        # 1. Municipal & Public Records (PDFs / Government Docs)
        query_docs = f'filetype:pdf ("{safe_entity}") ("permit" OR "zoning" OR "property" OR "architectural" OR "report")'
        dorks.append(
            OsintDork(
                category="Municipal & Property Records",
                query=query_docs,
                explanation="Searches indexed government or municipal PDF archives for construction permits, property deeds, and zoning documentation.",
                search_url=f"https://www.google.com/search?q={urllib.parse.quote_plus(query_docs)}",
            )
        )

        # 2. Historical & Investigative News Archives
        query_news = f'"{safe_entity}" ("investigation" OR "controversy" OR "renovation" OR "history" OR "lawsuit")'
        dorks.append(
            OsintDork(
                category="Investigative Press & Archives",
                query=query_news,
                explanation="Exposes deep investigative journalism, regulatory controversies, architectural renovations, or litigation.",
                search_url=f"https://www.google.com/search?q={urllib.parse.quote_plus(query_news)}",
            )
        )

        # 3. Official Regulatory & Government Registries
        query_gov = f'site:gov OR site:org OR site:edu ("{safe_entity}")'
        dorks.append(
            OsintDork(
                category="Government & Academic Registries",
                query=query_gov,
                explanation="Restricts search to verified educational, non-profit heritage, and governmental domains.",
                search_url=f"https://www.google.com/search?q={urllib.parse.quote_plus(query_gov)}",
            )
        )

        # 4. Open Directories & Unindexed File Trees
        query_dir = f'intitle:"index of" "{safe_entity}"'
        dorks.append(
            OsintDork(
                category="Exposed Web Directories",
                query=query_dir,
                explanation="Discovers unindexed server storage directories containing raw blueprints, uncaptioned photos, or internal dossiers.",
                search_url=f"https://www.google.com/search?q={urllib.parse.quote_plus(query_dir)}",
            )
        )

        return dorks
