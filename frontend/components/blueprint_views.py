"""Interactive Showcase Views for TerraSleuth War Room 2.0.

Renders:
1. Screenshot Audit & Critique (4 visual flaw cards with red/amber badges and fixes).
2. SerpApi Features & Add-ons (High-impact feature cards + SerpApi Multi-Engine Coverage Matrix).
3. Implementation Roadmap (Sprint milestones and architecture tracking).
"""

import streamlit as st


def render_screenshot_critique_view() -> None:
    """Render Tab 1: Screenshot Audit & Critique."""
    card1 = (
        '<div style="background: #0e1422; border: 1px solid rgba(239, 68, 68, 0.25); border-radius: 10px; padding: 16px;">'
        '<div style="display: flex; align-items: center; gap: 8px; color: #f87171; font-size: 13px; font-weight: 700; margin-bottom: 8px;">'
        '<span>⚠️</span><span>Synthetic Geometric Diagrams vs Authentic Photography</span></div>'
        '<p style="color: #cbd5e1; font-size: 12px; line-height: 1.5; margin-bottom: 10px;">'
        'Baseline test cases used synthetic tan/brown geometric blocks (<code style="color: #fbbf24;">target.jpg</code>). While computationally valid, it looked like an engineer\'s wireframe unit test, breaking forensic credibility for judges.</p>'
        '<div style="background: rgba(127, 29, 29, 0.3); border: 1px solid rgba(239, 68, 68, 0.3); border-radius: 6px; padding: 8px 10px; font-size: 11px; color: #fecaca;">'
        '<b>War Room 2.0 Fix:</b> Embedded high-resolution photographic library (Apollo Bunder maritime arch, Bavarian alpine fortress, Santorini luxury rental) with verified metadata.</div>'
        '</div>'
    )

    card2 = (
        '<div style="background: #0e1422; border: 1px solid rgba(239, 68, 68, 0.25); border-radius: 10px; padding: 16px;">'
        '<div style="display: flex; align-items: center; gap: 8px; color: #f87171; font-size: 13px; font-weight: 700; margin-bottom: 8px;">'
        '<span>⚠️</span><span>Metric Truncation (<code style="color: #fbbf24;">Gatewa...</code>, <code style="color: #fbbf24;">18.9220...</code>)</span></div>'
        '<p style="color: #cbd5e1; font-size: 12px; line-height: 1.5; margin-bottom: 10px;">'
        'Standard Streamlit <code style="color: #fbbf24;">st.metric</code> cards truncated essential coordinate strings and landmark titles with ellipses on multi-column layouts, hiding crucial geospatial intelligence.</p>'
        '<div style="background: rgba(127, 29, 29, 0.3); border: 1px solid rgba(239, 68, 68, 0.3); border-radius: 6px; padding: 8px 10px; font-size: 11px; color: #fecaca;">'
        '<b>War Room 2.0 Fix:</b> Custom flexbox telemetry ribbon with auto-wrapping, monospace font, zero-truncation WGS84 precision, and zero-quota status indicators.</div>'
        '</div>'
    )

    card3 = (
        '<div style="background: #0e1422; border: 1px solid rgba(245, 158, 11, 0.25); border-radius: 10px; padding: 16px;">'
        '<div style="display: flex; align-items: center; gap: 8px; color: #fbbf24; font-size: 13px; font-weight: 700; margin-bottom: 8px;">'
        '<span>⚠️</span><span>Fragmented Tab Layouts Hiding Visual Evidence</span></div>'
        '<p style="color: #cbd5e1; font-size: 12px; line-height: 1.5; margin-bottom: 10px;">'
        'When switching between "Geospatial Pinpoint" and "Visual Evidence", investigators lost sight of the target image. An investigator needs a unified, synchronized split-screen view.</p>'
        '<div style="background: rgba(120, 53, 15, 0.3); border: 1px solid rgba(245, 158, 11, 0.3); border-radius: 6px; padding: 8px 10px; font-size: 11px; color: #fef3c7;">'
        '<b>War Room 2.0 Fix:</b> Unified 45/55 Split-Screen Command Deck: Left 45% = Visual Forensic Inspector & Visual Twin Comparator; Right 55% = Satellite Recon Map & Intelligence Feed.</div>'
        '</div>'
    )

    card4 = (
        '<div style="background: #0e1422; border: 1px solid rgba(245, 158, 11, 0.25); border-radius: 10px; padding: 16px;">'
        '<div style="display: flex; align-items: center; gap: 8px; color: #fbbf24; font-size: 13px; font-weight: 700; margin-bottom: 8px;">'
        '<span>⚠️</span><span>Static Progress Alerts vs Autonomous Agent Swarm</span></div>'
        '<p style="color: #cbd5e1; font-size: 12px; line-height: 1.5; margin-bottom: 10px;">'
        'Agent progression appeared as plain stacked green boxes (<code style="color: #34d399;">Scene Deconstructor — complete</code>). It lacked the dynamic feel of an autonomous multi-agent swarm coordinating live searches.</p>'
        '<div style="background: rgba(120, 53, 15, 0.3); border: 1px solid rgba(245, 158, 11, 0.3); border-radius: 6px; padding: 8px 10px; font-size: 11px; color: #fef3c7;">'
        '<b>War Room 2.0 Fix:</b> Live Cyber Swarm Radar with active node indicators, deduction logs, and an obsidian monospace telemetry terminal (<code style="color: #38bdf8;">#090d16</code>).</div>'
        '</div>'
    )

    full_html = (
        '<div style="background: #0d121d; border: 1px solid rgba(0, 242, 254, 0.25); border-radius: 12px; padding: 20px; margin-bottom: 20px;">'
        '<div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px; flex-wrap: wrap; gap: 10px;">'
        '<div><h3 style="color: #38bdf8; margin: 0; font-size: 18px; font-weight: 700;">1. Playwright Visual Audit & Forensic UI Critique</h3>'
        '<p style="color: #94a3b8; margin: 4px 0 0 0; font-size: 12px;">Comparative analysis of baseline prototype visual flaws vs War Room 2.0 engineered fixes.</p></div>'
        '<span style="background: rgba(239, 68, 68, 0.15); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.4); font-size: 11px; font-weight: 700; padding: 4px 10px; border-radius: 20px; font-family: ui-monospace, monospace;">4 CRITICAL FLAWS RESOLVED</span>'
        '</div>'
        '<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(420px, 1fr)); gap: 16px;">'
        f'{card1}{card2}{card3}{card4}'
        '</div></div>'
    )
    st.markdown(full_html, unsafe_allow_html=True)


def render_serpapi_features_view() -> None:
    """Render Tab 2: SerpApi Features & Add-ons."""
    feat1 = (
        '<div style="background: #0e1422; border: 1px solid rgba(0, 242, 254, 0.3); border-radius: 10px; padding: 16px; display: flex; flex-direction: column; justify-content: space-between;">'
        '<div><div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">'
        '<span style="background: rgba(30, 58, 138, 0.6); color: #93c5fd; font-size: 10px; font-weight: 700; padding: 3px 8px; border-radius: 4px; font-family: ui-monospace, monospace;">LENS + MAPS</span>'
        '<span style="font-size: 20px;">⚖️</span></div>'
        '<h4 style="color: #38bdf8; margin: 0 0 6px 0; font-size: 14px; font-weight: 700;">Vacation Rental Listing Fraud Exposer</h4>'
        '<p style="color: #94a3b8; font-size: 12px; line-height: 1.45; margin: 0 0 10px 0;">'
        'Compares marketplace / rental listing photos against Google Lens visual twins to uncover stolen luxury hotel photos fraudulently advertised as local properties.</p></div>'
        '<div style="color: #34d399; font-size: 11px; font-family: ui-monospace, monospace; border-top: 1px solid #1e293b; padding-top: 8px;">Engines: google_lens + google_maps</div></div>'
    )

    feat2 = (
        '<div style="background: #0e1422; border: 1px solid rgba(0, 242, 254, 0.3); border-radius: 10px; padding: 16px; display: flex; flex-direction: column; justify-content: space-between;">'
        '<div><div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">'
        '<span style="background: rgba(88, 28, 135, 0.6); color: #d8b4fe; font-size: 10px; font-weight: 700; padding: 3px 8px; border-radius: 4px; font-family: ui-monospace, monospace;">NEWS + SEARCH</span>'
        '<span style="font-size: 20px;">📰</span></div>'
        '<h4 style="color: #38bdf8; margin: 0 0 6px 0; font-size: 14px; font-weight: 700;">Bellingcat Viral Media Temporal Debunker</h4>'
        '<p style="color: #94a3b8; font-size: 12px; line-height: 1.45; margin: 0 0 10px 0;">'
        'Audits claimed publication dates against the earliest indexed Google News and Search archives to detect pre-dated recycled conflict/disaster media.</p></div>'
        '<div style="color: #34d399; font-size: 11px; font-family: ui-monospace, monospace; border-top: 1px solid #1e293b; padding-top: 8px;">Engines: google_news + google (search)</div></div>'
    )

    feat3 = (
        '<div style="background: #0e1422; border: 1px solid rgba(0, 242, 254, 0.3); border-radius: 10px; padding: 16px; display: flex; flex-direction: column; justify-content: space-between;">'
        '<div><div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">'
        '<span style="background: rgba(120, 53, 15, 0.6); color: #fde68a; font-size: 10px; font-weight: 700; padding: 3px 8px; border-radius: 4px; font-family: ui-monospace, monospace;">MAPS + LENS</span>'
        '<span style="font-size: 20px;">🎯</span></div>'
        '<h4 style="color: #38bdf8; margin: 0 0 6px 0; font-size: 14px; font-weight: 700;">Autonomous Geoguessr Mode (5,000 Pts)</h4>'
        '<p style="color: #94a3b8; font-size: 12px; line-height: 1.45; margin: 0 0 10px 0;">'
        'Evaluates spatial triangulation against physical ground truth with exponential distance decay scoring and 4-phase progressive radius narrowing down to sub-50m.</p></div>'
        '<div style="color: #34d399; font-size: 11px; font-family: ui-monospace, monospace; border-top: 1px solid #1e293b; padding-top: 8px;">Engines: google_maps + google_lens</div></div>'
    )

    table_html = (
        '<div style="background: #0b0e17; border: 1px solid #1e293b; border-radius: 8px; padding: 14px; overflow-x: auto;">'
        '<h4 style="color: #f8fafc; font-size: 13px; font-weight: 700; margin: 0 0 10px 0;">SerpApi Engine Utilization Matrix</h4>'
        '<table style="width: 100%; border-collapse: collapse; font-size: 12px; text-align: left;">'
        '<thead><tr style="border-bottom: 1px solid #1e293b; color: #94a3b8; font-family: ui-monospace, monospace;">'
        '<th style="padding: 8px 12px;">Engine</th><th style="padding: 8px 12px;">TerraSleuth Role</th><th style="padding: 8px 12px;">OSINT Extraction Capability</th><th style="padding: 8px 12px;">Quota Defense Strategy</th></tr></thead>'
        '<tbody style="color: #cbd5e1;">'
        '<tr style="border-bottom: 1px solid rgba(30, 41, 59, 0.5);"><td style="padding: 8px 12px; font-family: ui-monospace, monospace; color: #38bdf8;">google_lens</td><td style="padding: 8px 12px;">Visual Provenance Hunter</td><td style="padding: 8px 12px;">Reverse image visual twins, Knowledge Graph, OCR script & entity links</td><td style="padding: 8px 12px; color: #34d399; font-family: ui-monospace, monospace;">1 call / target (SQLite cached)</td></tr>'
        '<tr style="border-bottom: 1px solid rgba(30, 41, 59, 0.5);"><td style="padding: 8px 12px; font-family: ui-monospace, monospace; color: #38bdf8;">google_maps</td><td style="padding: 8px 12px;">Spatial Triangulator</td><td style="padding: 8px 12px;">Resolves WGS84 coordinates, place IDs, addresses, rating consensus</td><td style="padding: 8px 12px; color: #34d399; font-family: ui-monospace, monospace;">1–2 calls / target (circuit breaker)</td></tr>'
        '<tr style="border-bottom: 1px solid rgba(30, 41, 59, 0.5);"><td style="padding: 8px 12px; font-family: ui-monospace, monospace; color: #38bdf8;">google_news</td><td style="padding: 8px 12px;">Chrono Auditor</td><td style="padding: 8px 12px;">Earliest indexed appearance, temporal milestones, disinformation debunking</td><td style="padding: 8px 12px; color: #34d399; font-family: ui-monospace, monospace;">1 call / target (SQLite cached)</td></tr>'
        '<tr><td style="padding: 8px 12px; font-family: ui-monospace, monospace; color: #38bdf8;">google (search)</td><td style="padding: 8px 12px;">Advanced Dorker</td><td style="padding: 8px 12px;">Targeted queries (<code>site:</code>, <code>filetype:pdf</code>, <code>before:</code>, municipal filings)</td><td style="padding: 8px 12px; color: #34d399; font-family: ui-monospace, monospace;">Optional disambiguation hop</td></tr>'
        '</tbody></table></div>'
    )

    full_html = (
        '<div style="background: #0d121d; border: 1px solid rgba(0, 242, 254, 0.25); border-radius: 12px; padding: 20px; margin-bottom: 20px;">'
        '<div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px; flex-wrap: wrap; gap: 10px;">'
        '<div><h3 style="color: #38bdf8; margin: 0; font-size: 18px; font-weight: 700;">2. SerpApi Multi-Engine Portfolio & High-Impact Feature Pack</h3>'
        '<p style="color: #94a3b8; margin: 4px 0 0 0; font-size: 12px;">Deep technical integration across Google Lens, Maps/Local, News, and Search Dorking.</p></div>'
        '<span style="background: rgba(16, 185, 129, 0.15); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.4); font-size: 11px; font-weight: 700; padding: 4px 10px; border-radius: 20px; font-family: ui-monospace, monospace;">4 ENGINES ORCHESTRATED</span></div>'
        f'<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 14px; margin-bottom: 20px;">{feat1}{feat2}{feat3}</div>'
        f'{table_html}</div>'
    )
    st.markdown(full_html, unsafe_allow_html=True)


def render_implementation_roadmap_view() -> None:
    """Render Tab 4: Implementation Roadmap."""
    sprints = [
        ("Sprint 1 — Foundation & SerpApi Multi-Engine Service", "v0.1.0 CERTIFIED", "#10b981", "#34d399", "SerpApi clients (Lens, Maps, News, Search), SQLite WAL caching layer, budget defense manager."),
        ("Sprint 2 — LangGraph Multi-Agent OSINT Swarm", "v0.2.0 CERTIFIED", "#10b981", "#34d399", "Scene Deconstructor, Lens Hunter, Geo Triangulator, Chrono Auditor, Case Synthesizer, conditional router."),
        ("Sprint 3 — Interactive Visual OSINT Dashboard", "v0.3.0 CERTIFIED", "#10b981", "#34d399", "Bounding box overlays, Leaflet/Folium map pinpoint, timeline, citation ledger, golden demo walk-through."),
        ("Sprint 4 — Tactical Command Deck & High-Res Target Library", "v0.4.0 CERTIFIED", "#10b981", "#34d399", "45/55 Split-Screen Command Deck, authentic photography, visual twin matcher, satellite recon, cyber radar."),
        ("Sprint 5 — War Room 2.0 HUD, Fraud Engine & Standalone Dossier", "v0.5.0 CERTIFIED", "#10b981", "#34d399", "Rental fraud exposer, Bellingcat temporal debunker, standalone offline HTML dossier exporter, Docker container."),
        ("Sprint 6 — UI/UX High-Fidelity War Room Alignment & Autonomous Geoguessr Mode", "v0.6.0 CERTIFIED", "#38bdf8", "#38bdf8", "Top-level 4-tab blueprint navigation, glowing neon container, side-by-side twin always-visible integration, Autonomous Geoguessr Mode (5,000 pts), SDD git pre-commit hook."),
    ]

    sprint_cards = "".join(
        f'<div style="background: #0e1422; border-left: 4px solid {border_col}; border-radius: 8px; padding: 12px 16px; margin-bottom: 10px;">'
        f'<div style="display: flex; justify-content: space-between; align-items: center;">'
        f'<b style="color: #f8fafc; font-size: 13px;">{title}</b>'
        f'<span style="color: {tag_col}; font-size: 11px; font-weight: 700; font-family: ui-monospace, monospace;">{tag}</span></div>'
        f'<p style="color: #94a3b8; font-size: 12px; margin: 4px 0 0 0;">{desc}</p></div>'
        for title, tag, border_col, tag_col, desc in sprints
    )

    full_html = (
        '<div style="background: #0d121d; border: 1px solid rgba(0, 242, 254, 0.25); border-radius: 12px; padding: 20px; margin-bottom: 20px;">'
        '<div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px; flex-wrap: wrap; gap: 10px;">'
        '<div><h3 style="color: #38bdf8; margin: 0; font-size: 18px; font-weight: 700;">4. Subagent-Driven Execution Roadmap & Milestones</h3>'
        '<p style="color: #94a3b8; margin: 4px 0 0 0; font-size: 12px;">Living milestone certification tracking from Sprint 1 through Sprint 6.</p></div>'
        '<span style="background: rgba(56, 189, 248, 0.15); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.4); font-size: 11px; font-weight: 700; padding: 4px 10px; border-radius: 20px; font-family: ui-monospace, monospace;">ACTIVE: RELEASE v0.6</span></div>'
        f'<div style="display: flex; flex-direction: column;">{sprint_cards}</div></div>'
    )
    st.markdown(full_html, unsafe_allow_html=True)
