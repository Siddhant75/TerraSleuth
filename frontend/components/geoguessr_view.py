"""Geoguessr Mode Visual Component for TerraSleuth War Room.

Renders interactive 5,000-point competitive Geoguessr score, distance error metrics,
and the 4-phase progressive spatial radius tightening cards.
"""

import html
from typing import Optional
import streamlit as st
from backend.app.models.geoguessr import GeoguessrResult
from backend.app.services.geoguessr_service import GeoguessrService


def render_geoguessr_challenge_view(
    guess_lat: Optional[float],
    guess_lon: Optional[float],
    truth_lat: Optional[float],
    truth_lon: Optional[float],
    target_name: str = "Suspect Landmark",
) -> None:
    """Render interactive Geoguessr challenge scorecard and spatial tightening progression."""
    if guess_lat is None or guess_lon is None or truth_lat is None or truth_lon is None:
        st.info("⚠️ Ground truth or candidate coordinates missing. Select a target to run Geoguessr evaluation.")
        return

    result: GeoguessrResult = GeoguessrService.evaluate_challenge(
        guess_lat=guess_lat,
        guess_lon=guess_lon,
        truth_lat=truth_lat,
        truth_lon=truth_lon,
        target_name=target_name,
    )

    score_pct = int((result.score / result.max_score) * 100)
    score_color = "#10b981" if result.score >= 4900 else "#38bdf8" if result.score >= 4000 else "#f59e0b"

    st.markdown(
        f"""
        <div style="background: #0d121d; border: 1px solid rgba(0, 242, 254, 0.35); border-radius: 12px; padding: 18px; margin-bottom: 20px; box-shadow: 0 0 20px rgba(0, 242, 254, 0.15);">
            <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 12px; margin-bottom: 12px;">
                <div style="display: flex; align-items: center; gap: 10px;">
                    <span style="font-size: 28px;">🎯</span>
                    <div>
                        <span style="font-size: 16px; font-weight: 700; color: #f8fafc; letter-spacing: 0.5px;">AUTONOMOUS GEOGUESSR OSINT CHALLENGE</span><br>
                        <span style="font-size: 12px; color: #94a3b8; font-family: ui-monospace, monospace;">Target: {html.escape(target_name)}</span>
                    </div>
                </div>
                <div style="background: #111827; border: 1px solid {score_color}; border-radius: 8px; padding: 6px 14px; text-align: right;">
                    <span style="font-size: 11px; color: #94a3b8; font-family: ui-monospace, monospace;">OFFICIAL SCORE</span><br>
                    <span style="font-size: 20px; font-weight: 800; color: {score_color}; font-family: ui-monospace, monospace;">{result.score:,} / 5,000 PTS</span>
                </div>
            </div>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px; margin-bottom: 16px;">
                <div style="background: #141b2b; border: 1px solid #1e293b; border-radius: 8px; padding: 10px;">
                    <span style="font-size: 10px; color: #94a3b8; text-transform: uppercase;">Distance Error</span><br>
                    <span style="font-size: 16px; font-weight: 700; color: #38bdf8; font-family: ui-monospace, monospace;">{result.distance_meters:.1f} m</span>
                    <span style="font-size: 11px; color: #64748b;">({result.distance_km:.3f} km)</span>
                </div>
                <div style="background: #141b2b; border: 1px solid #1e293b; border-radius: 8px; padding: 10px;">
                    <span style="font-size: 10px; color: #94a3b8; text-transform: uppercase;">Accuracy Tier</span><br>
                    <span style="font-size: 14px; font-weight: 700; color: #10b981;">{html.escape(result.accuracy_tier)}</span>
                </div>
                <div style="background: #141b2b; border: 1px solid #1e293b; border-radius: 8px; padding: 10px;">
                    <span style="font-size: 10px; color: #94a3b8; text-transform: uppercase;">Geodesic Consensus</span><br>
                    <span style="font-size: 14px; font-weight: 700; color: #e2e8f0; font-family: ui-monospace, monospace;">{guess_lat:.5f}°N, {guess_lon:.5f}°E</span>
                </div>
            </div>
            <div style="font-size: 12px; color: #cbd5e1; background: rgba(15, 23, 42, 0.7); border-left: 3px solid #38bdf8; padding: 8px 12px; border-radius: 4px;">
                <b>Detective Verdict:</b> {html.escape(result.verdict)}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("#### 🔄 4-Phase Progressive Spatial Radius Tightening")
    st.caption("How TerraSleuth progressively constrains coordinate ambiguity from global biomes down to sub-50m pinpoint:")

    stage_cols = st.columns(4)
    for idx, stage in enumerate(result.tightening_stages):
        with stage_cols[idx]:
            radius_label = f"{stage.radius_km:.0f} km" if stage.radius_km >= 1.0 else f"{int(stage.radius_km * 1000)} m"
            st.markdown(
                f"""
                <div style="background: #0f172a; border: 1px solid #1e293b; border-top: 3px solid #38bdf8; border-radius: 8px; padding: 12px; height: 100%; display: flex; flex-direction: column; justify-content: space-between;">
                    <div>
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                            <span style="background: #1e293b; color: #38bdf8; font-size: 10px; font-weight: 700; padding: 2px 6px; border-radius: 4px; font-family: ui-monospace, monospace;">PHASE {stage.stage_num}</span>
                            <span style="color: #10b981; font-size: 11px; font-weight: 700; font-family: ui-monospace, monospace;">±{radius_label}</span>
                        </div>
                        <b style="font-size: 12px; color: #f1f5f9; display: block; margin-bottom: 4px;">{html.escape(stage.name)}</b>
                        <p style="font-size: 11px; color: #94a3b8; line-height: 1.4; margin-bottom: 8px;">{html.escape(stage.description)}</p>
                    </div>
                    <div style="background: #1e293b; border-radius: 4px; padding: 6px 8px; font-size: 10px; color: #38bdf8; font-family: ui-monospace, monospace;">
                        ✓ {html.escape(stage.clues_resolved)}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
