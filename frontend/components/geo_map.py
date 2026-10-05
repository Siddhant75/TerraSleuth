import html
import logging
from typing import Any, Dict, Optional
import folium
from streamlit_folium import st_folium

logger = logging.getLogger(__name__)

CARTODB_DARK_TILES = "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
CARTODB_ATTR = "&copy; <a href='https://www.openstreetmap.org/copyright'>OpenStreetMap</a> contributors &copy; <a href='https://carto.com/attributions'>CARTO</a>"


def render_telemetry_bar_html(
    target_name: str,
    coords_str: str,
    confidence_pct: int,
    queries_count: int,
    max_budget: int = 8,
    cache_status: str = "ZERO CREDIT BURN",
) -> str:
    """Generate high-contrast flexbox telemetry badges eliminating Streamlit metric truncation."""
    safe_name = html.escape(str(target_name))
    safe_coords = html.escape(str(coords_str))
    safe_cache = html.escape(str(cache_status))
    
    conf_color = "#10b981" if confidence_pct >= 80 else ("#f59e0b" if confidence_pct >= 50 else "#ef4444")
    conf_label = "HIGH VERIFIABILITY" if confidence_pct >= 80 else "MODERATE"

    return f"""
    <div class="telemetry-container" style="display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 12px; width: 100%;">
        <div class="telemetry-badge" style="background: #111622; border-left: 4px solid #3b82f6; padding: 10px 14px; border-radius: 6px; flex: 1 1 200px; min-width: 170px;">
            <div style="font-size: 11px; font-family: monospace; color: #94a3b8; text-transform: uppercase;">PRIMARY TARGET</div>
            <div style="font-size: 14px; font-weight: 700; color: #60a5fa; margin-top: 3px; word-break: break-word;">{safe_name}</div>
        </div>
        <div class="telemetry-badge" style="background: #111622; border-left: 4px solid #00f2fe; padding: 10px 14px; border-radius: 6px; flex: 1 1 200px; min-width: 170px;">
            <div style="font-size: 11px; font-family: monospace; color: #94a3b8; text-transform: uppercase;">WGS84 COORDINATES</div>
            <div style="font-size: 14px; font-weight: 700; font-family: monospace; color: #e6f1ff; margin-top: 3px; word-break: break-all;">{safe_coords}</div>
        </div>
        <div class="telemetry-badge" style="background: #111622; border-left: 4px solid {conf_color}; padding: 10px 14px; border-radius: 6px; flex: 1 1 160px; min-width: 140px;">
            <div style="font-size: 11px; font-family: monospace; color: #94a3b8; text-transform: uppercase;">CONFIDENCE SCORE</div>
            <div style="font-size: 14px; font-weight: 700; color: {conf_color}; margin-top: 3px;">{confidence_pct}% <span style="font-size: 10px; font-weight: 500;">[{conf_label}]</span></div>
        </div>
        <div class="telemetry-badge" style="background: #111622; border-left: 4px solid #8b5cf6; padding: 10px 14px; border-radius: 6px; flex: 1 1 140px; min-width: 130px;">
            <div style="font-size: 11px; font-family: monospace; color: #94a3b8; text-transform: uppercase;">SERPAPI QUERIES</div>
            <div style="font-size: 14px; font-weight: 700; font-family: monospace; color: #c4b5fd; margin-top: 3px;">{queries_count} / {max_budget} BUDGET</div>
        </div>
        <div class="telemetry-badge" style="background: #111622; border-left: 4px solid #10b981; padding: 10px 14px; border-radius: 6px; flex: 1 1 160px; min-width: 140px;">
            <div style="font-size: 11px; font-family: monospace; color: #94a3b8; text-transform: uppercase;">CACHE TELEMETRY</div>
            <div style="font-size: 13px; font-weight: 700; font-family: monospace; color: #34d399; margin-top: 3px;">⚡ {safe_cache}</div>
        </div>
    </div>
    """


def create_folium_map(
    candidate: Any,
    accuracy_radius_meters: int = 150,
) -> folium.Map:
    """Create a tactical, dark-matter Folium map centered on the resolved GeoCandidate."""
    lat = getattr(candidate, "latitude", None)
    lon = getattr(candidate, "longitude", None)
    raw_name = getattr(candidate, "name", "Triangulated Target") or "Triangulated Target"
    raw_address = getattr(candidate, "address", "Unspecified vicinity") or "Unspecified vicinity"

    safe_name = html.escape(str(raw_name))
    safe_address = html.escape(str(raw_address))

    if lat is None or lon is None:
        # Default global fallback coordinates
        lat, lon = 20.0, 0.0

    m = folium.Map(
        location=[lat, lon],
        zoom_start=15 if getattr(candidate, "latitude", None) is not None else 2,
        tiles=CARTODB_DARK_TILES,
        attr=CARTODB_ATTR,
        control_scale=True,
    )

    if getattr(candidate, "latitude", None) is not None:
        # Popup card with dark cyber styling
        popup_html = f"""
        <div style="font-family: monospace; background: #0b0e14; color: #e6f1ff; padding: 10px; border-radius: 6px; border: 1px solid #00f2fe; min-width: 200px;">
            <b style="color: #00f2fe; font-size: 13px;">🎯 {safe_name}</b><br>
            <span style="font-size: 11px; color: #94a3b8;">{safe_address}</span>
            <hr style="border: 0; border-top: 1px solid #334155; margin: 6px 0;">
            <span style="font-size: 11px; color: #10b981;"><b>WGS84:</b> {lat:.5f}°N, {lon:.5f}°E</span>
        </div>
        """
        
        # Tactical Pin Marker
        folium.Marker(
            location=[lat, lon],
            popup=folium.Popup(popup_html, max_width=320),
            tooltip=f"🎯 {safe_name} ({lat:.4f}, {lon:.4f})",
            icon=folium.Icon(color="red", icon="crosshairs", prefix="fa"),
        ).add_to(m)

        # Consensus accuracy radius with tactical cyan glow
        folium.Circle(
            location=[lat, lon],
            radius=accuracy_radius_meters,
            color="#00f2fe",
            weight=2,
            fill=True,
            fill_color="#00f2fe",
            fill_opacity=0.18,
            tooltip=f"Spatial Consensus Accuracy Radius (±{accuracy_radius_meters}m)",
        ).add_to(m)

    return m


def render_geo_map(
    candidate: Optional[Any],
    accuracy_radius_meters: int = 150,
    streamlit_context: Any = None,
):
    """Render the interactive tactical Dark Matter Folium map and metadata in Streamlit."""
    import streamlit as st

    ctx = streamlit_context or st

    ctx.markdown("### 📍 Tactical Geospatial Pinpoint (CartoDB Dark Matter)")
    ctx.caption("Physical coordinate resolution via Google Maps and Local places consensus.")

    if not candidate or getattr(candidate, "latitude", None) is None:
        ctx.warning("No geographic coordinates resolved for this target.")
        return

    m = create_folium_map(candidate, accuracy_radius_meters=accuracy_radius_meters)
    st_folium(m, width=None, height=420, returned_objects=[])

    # High-contrast metadata card below map
    safe_name = html.escape(str(getattr(candidate, "name", "N/A")))
    safe_addr = html.escape(str(getattr(candidate, "address", "N/A")))
    lat_val = f"{candidate.latitude:.5f}°N"
    lon_val = f"{candidate.longitude:.5f}°E"
    score_pct = int(getattr(candidate, "match_score", 0.0) * 100)
    source_url = getattr(candidate, "source_url", None)

    link_html = ""
    if source_url and (source_url.startswith("http://") or source_url.startswith("https://")):
        safe_source_url = html.escape(source_url, quote=True)
        link_html = f'<a href="{safe_source_url}" target="_blank" style="color: #60a5fa; text-decoration: none; font-weight: 600;">Open in Google Maps ↗</a>'

    meta_html = f"""
    <div style="background: #111622; border: 1px solid #1e293b; border-radius: 8px; padding: 12px 16px; margin-top: 8px; font-family: monospace;">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;">
            <div>
                <span style="color: #94a3b8; font-size: 11px; text-transform: uppercase;">RESOLVED LOCATION</span>
                <div style="color: #f1f5f9; font-size: 14px; font-weight: 700;">{safe_name}</div>
                <div style="color: #64748b; font-size: 12px;">{safe_addr}</div>
            </div>
            <div style="text-align: right;">
                <div style="color: #00f2fe; font-size: 13px; font-weight: 700;">{lat_val}, {lon_val}</div>
                <div style="color: #10b981; font-size: 11px;">Spatial Match Score: {score_pct}%</div>
                <div style="margin-top: 4px;">{link_html}</div>
            </div>
        </div>
    </div>
    """
    ctx.markdown(meta_html, unsafe_allow_html=True)
