import html
import logging
from typing import Any, Dict, Optional
import folium
from streamlit_folium import st_folium

logger = logging.getLogger(__name__)


def create_folium_map(
    candidate: Any,
    accuracy_radius_meters: int = 150,
) -> folium.Map:
    """Create a dark, high-contrast Folium map centered on the resolved GeoCandidate."""
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
        tiles="OpenStreetMap",
        control_scale=True,
    )

    if getattr(candidate, "latitude", None) is not None:
        # Add primary target pin
        popup_html = f"""
        <div style="font-family: Arial, sans-serif; min-width: 180px;">
            <b style="color: #c0392b;">🎯 {safe_name}</b><br>
            <span style="font-size: 12px; color: #555;">{safe_address}</span><br>
            <hr style="margin: 4px 0;">
            <span style="font-size: 11px;"><b>Lat, Lon:</b> {lat:.5f}, {lon:.5f}</span>
        </div>
        """
        folium.Marker(
            location=[lat, lon],
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=f"{safe_name} ({lat:.4f}, {lon:.4f})",
            icon=folium.Icon(color="red", icon="crosshairs", prefix="fa"),
        ).add_to(m)

        # Add consensus accuracy radius
        folium.Circle(
            location=[lat, lon],
            radius=accuracy_radius_meters,
            color="#e74c3c",
            weight=2,
            fill=True,
            fill_color="#e74c3c",
            fill_opacity=0.15,
            tooltip="Spatial Consensus Radius",
        ).add_to(m)

    return m


def render_geo_map(
    candidate: Optional[Any],
    accuracy_radius_meters: int = 150,
    streamlit_context: Any = None,
):
    """Render the interactive Folium map and geospatial metadata in Streamlit."""
    import streamlit as st

    ctx = streamlit_context or st

    ctx.markdown("### 🗺️ Triangulated Geospatial Pinpoint")
    ctx.caption("Physical coordinate resolution via Google Maps and Local places consensus.")

    if not candidate or getattr(candidate, "latitude", None) is None:
        ctx.warning("No geographic coordinates resolved for this target.")
        return

    m = create_folium_map(candidate, accuracy_radius_meters=accuracy_radius_meters)
    st_folium(m, width=None, height=450, returned_objects=[])

    # Metadata badges below map
    col1, col2, col3, col4 = ctx.columns(4)
    with col1:
        st.metric("Resolved Landmark", getattr(candidate, "name", "N/A"))
    with col2:
        st.metric("Latitude", f"{candidate.latitude:.5f}°")
    with col3:
        st.metric("Longitude", f"{candidate.longitude:.5f}°")
    with col4:
        match_score = getattr(candidate, "match_score", 0.0)
        st.metric("Match Score", f"{int(match_score * 100)}%")

    source_url = getattr(candidate, "source_url", None)
    if source_url and (source_url.startswith("http://") or source_url.startswith("https://")):
        safe_source_url = html.escape(source_url, quote=True)
        ctx.markdown(f"📍 [Open Pinpoint in Google Maps]({safe_source_url})")
