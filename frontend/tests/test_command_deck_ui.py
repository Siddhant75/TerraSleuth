import pytest
import folium

from backend.app.models.case import GeoCandidate
from frontend.components.geo_map import create_folium_map, render_telemetry_bar_html


def test_create_folium_map_tiles():
    """Verify that create_folium_map generates map with CartoDB Dark Matter tiles."""
    m = create_folium_map(None)
    assert isinstance(m, folium.Map)
    
    # Check that CartoDB dark matter tilelayer is present in children
    tile_layers = [c for c in m._children.values() if isinstance(c, folium.raster_layers.TileLayer)]
    assert len(tile_layers) > 0, "No TileLayer found in Folium map"
    tile_name = tile_layers[0].tile_name.lower() if hasattr(tile_layers[0], "tile_name") and tile_layers[0].tile_name else ""
    tile_url = str(tile_layers[0].tiles).lower() if hasattr(tile_layers[0], "tiles") else ""
    assert any(k in tile_name or k in tile_url for k in ["cartodb", "dark", "satellite", "esri", "arcgis"]), \
        f"Tile layer does not appear to be tactical or satellite: name={tile_name}, url={tile_url}"


def test_create_folium_map_with_candidate():
    """Verify that providing a candidate adds the marker and accuracy radius circle."""
    candidate = GeoCandidate(
        name="Gateway of India",
        latitude=18.9220,
        longitude=72.8347,
        address="Apollo Bunder, Colaba, Mumbai",
        match_score=0.96,
        engine_source="google_maps",
    )
    m = create_folium_map(candidate)
    
    # Verify circle and marker exist
    circles = [c for c in m._children.values() if isinstance(c, folium.vector_layers.Circle)]
    markers = [c for c in m._children.values() if isinstance(c, folium.map.Marker)]
    
    assert len(circles) >= 1, "Expected at least 1 Circle layer for accuracy radius"
    assert len(markers) >= 1, "Expected at least 1 Marker for pinpoint coordinate"


def test_telemetry_badge_rendering():
    """Verify that render_telemetry_bar_html renders full coordinates without truncation."""
    target_name = "Gateway of India (Apollo Bunder, Colaba)"
    coords_str = "18.9220°N, 72.8347°E"
    confidence_pct = 96
    queries_count = 4
    cache_status = "ZERO CREDIT BURN"
    
    html_output = render_telemetry_bar_html(
        target_name=target_name,
        coords_str=coords_str,
        confidence_pct=confidence_pct,
        queries_count=queries_count,
        cache_status=cache_status,
    )
    
    assert "telemetry-container" in html_output
    assert "telemetry-badge" in html_output
    assert target_name in html_output
    assert coords_str in html_output
    assert "96%" in html_output
    assert "4 / 8 BUDGET" in html_output
    assert cache_status in html_output


def test_telemetry_badge_dynamic_budget_and_null_coords():
    """Verify dynamic budget rendering and handling of N/A coordinates."""
    html_output = render_telemetry_bar_html(
        target_name="Unidentified Target",
        coords_str="N/A",
        confidence_pct=30,
        queries_count=5,
        max_budget=12,
        cache_status="OFFLINE CACHE",
    )
    assert "Unidentified Target" in html_output
    assert "N/A" in html_output
    assert "30%" in html_output
    assert "5 / 12 BUDGET" in html_output
    assert "OFFLINE CACHE" in html_output
