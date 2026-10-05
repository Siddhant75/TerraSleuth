from pydantic import BaseModel, Field


class OsintDork(BaseModel):
    """A targeted advanced Google Search dork query for deep investigative research."""
    category: str = Field(description="Dork objective category (e.g., Municipal Records, Ownership, News Archives)")
    query: str = Field(description="The exact search string with operators (e.g., filetype:pdf site:...)")
    explanation: str = Field(description="What an investigator uncovers with this query")
    search_url: str = Field(description="Direct clickable Google Search URL for the dork")
