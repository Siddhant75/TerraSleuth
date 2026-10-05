import os
import pytest
from PIL import Image

from backend.app.db import get_golden_cases
from backend.app.services.cache_service import seed_golden_cases
from backend.app.services.quota_service import QuotaBudgetManager
from backend.app.services.serpapi_service import SerpApiService


EXPECTED_CASES = [
    {
        "case_id": "case_gateway_mumbai",
        "image_file": "gateway_mumbai.jpg",
        "lens_url": "https://images.unsplash.com/photo-1570168007204-dfb528c6958f",
        "maps_query": "Gateway of India",
        "news_query": "Gateway of India",
    },
    {
        "case_id": "case_neuschwanstein",
        "image_file": "neuschwanstein.jpg",
        "lens_url": "https://images.unsplash.com/photo-1534447677768-be436bb09401",
        "maps_query": "Neuschwanstein Castle",
        "news_query": "Neuschwanstein Castle",
    },
    {
        "case_id": "case_market_scam",
        "image_file": "rental_scam_santorini.jpg",
        "lens_url": "https://images.unsplash.com/photo-1512917774080-9991f1c4c750",
        "maps_query": "Canaves Oia Suites",
        "news_query": "Oia Santorini luxury villa rental fraud investigation",
    },
]


def test_golden_assets_exist_and_valid():
    """Verify that all 3 target images exist, are valid JPEG/PNG, and meet resolution minimums."""
    assets_dir = os.path.join("frontend", "assets", "targets")
    assert os.path.exists(assets_dir), f"Assets directory {assets_dir} does not exist"

    for item in EXPECTED_CASES:
        filepath = os.path.join(assets_dir, item["image_file"])
        assert os.path.exists(filepath), f"Asset file missing: {filepath}"

        with Image.open(filepath) as img:
            assert img.width >= 400, f"Image {filepath} width {img.width} < 400"
            assert img.height >= 300, f"Image {filepath} height {img.height} < 300"
            assert img.format in ["JPEG", "PNG"], f"Invalid format {img.format} for {filepath}"


def test_golden_cases_queryable():
    """Verify that get_golden_cases returns all 3 registered targets from SQLite."""
    seed_golden_cases()
    cases = get_golden_cases()
    assert len(cases) >= 3, f"Expected at least 3 golden cases, got {len(cases)}"

    case_ids = {c["case_id"] for c in cases}
    for expected in EXPECTED_CASES:
        assert expected["case_id"] in case_ids, f"Missing case: {expected['case_id']}"
        matching = next(c for c in cases if c["case_id"] == expected["case_id"])
        assert os.path.exists(matching["sample_image_path"]), f"Image path does not exist: {matching['sample_image_path']}"


def test_serpapi_golden_cache_hits_zero_quota():
    """Verify that Lens, Maps, and News for all golden cases hit the cache with 0 live quota consumed."""
    seed_golden_cases()
    budget = QuotaBudgetManager(max_budget=8)
    service = SerpApiService(budget_manager=budget)

    initial_budget = budget.remaining_budget

    for target in EXPECTED_CASES:
        # Test Lens cached hit
        lens_res = service.search_lens(image_url=target["lens_url"])
        assert len(lens_res.visual_matches) > 0 or lens_res.knowledge_graph is not None

        # Test Maps cached hit
        maps_res = service.search_maps(query=target["maps_query"])
        assert len(maps_res.candidates) > 0

        # Test News cached hit
        news_res = service.search_news(query=target["news_query"])
        assert len(news_res.items) > 0

    # Ensure zero live credit was deducted
    assert budget.remaining_budget == initial_budget, "Budget was consumed; cache hit failed!"
    assert budget.consumed_budget() == 0, "Consumed budget should be exactly 0"
