import pytest
from backend.app.agent.tools import (
    tool_lens_search,
    tool_maps_triangulate,
    tool_news_audit,
    tool_google_dork,
    tool_crop_region,
)

def test_tools_registered_and_callable():
    assert callable(tool_lens_search.invoke)
    assert callable(tool_maps_triangulate.invoke)
    assert callable(tool_news_audit.invoke)
    assert callable(tool_google_dork.invoke)
    assert callable(tool_crop_region.invoke)

def test_tool_maps_triangulate_cached_execution():
    result = tool_maps_triangulate.invoke({"query": "Gateway of India"})
    assert isinstance(result, dict)
    assert "candidates" in result
    assert len(result["candidates"]) > 0
    candidate = result["candidates"][0]
    assert "18.92" in str(candidate.get("latitude"))

def test_tool_lens_search_zero_quota_on_golden_target():
    result = tool_lens_search.invoke({
        "image_url": "https://images.unsplash.com/photo-1570168007204-dfb528c6958f"
    })
    assert isinstance(result, dict)
    assert "visual_matches" in result
    assert len(result["visual_matches"]) > 0

def test_tool_news_audit_cached_execution():
    result = tool_news_audit.invoke({"query": "Gateway of India"})
    assert isinstance(result, dict)
    assert "articles" in result
    assert len(result["articles"]) > 0

def test_tool_crop_region_valid():
    result = tool_crop_region.invoke({
        "image_path": "frontend/assets/targets/gateway_mumbai.jpg",
        "bbox": [0.15, 0.25, 0.70, 0.75],
        "label": "arch_crop",
    })
    assert isinstance(result, str)
    assert "crop" in result
