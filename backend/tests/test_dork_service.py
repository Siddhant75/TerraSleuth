from backend.app.services.dork_service import DorkService


def test_generate_dorks_produces_structured_queries():
    """Verify that DorkService formats valid Google search dork queries with category and URL."""
    dorks = DorkService.generate_dorks("Gateway of India", "Apollo Bunder, Colaba, Mumbai")

    assert len(dorks) >= 3
    # Check municipal/property dork
    pdf_dork = next((d for d in dorks if "filetype:pdf" in d.query), None)
    assert pdf_dork is not None
    assert "Gateway of India" in pdf_dork.query
    assert "google.com/search?q=" in pdf_dork.search_url

    # Check government/org dork
    gov_dork = next((d for d in dorks if "site:gov" in d.query), None)
    assert gov_dork is not None
