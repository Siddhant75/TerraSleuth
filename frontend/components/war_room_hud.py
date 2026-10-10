import html
from typing import Any, Dict, List, Optional
import streamlit as st


def sanitize_url(url: Optional[str]) -> str:
    """Sanitize URL for safe inclusion in href attributes, allowing only http, https, and mailto schemes."""
    if not url:
        return "#"
    clean = str(url).strip()
    if clean.lower().startswith(("http://", "https://", "mailto:")):
        return html.escape(clean)
    return "#"


def render_war_room_header():
    """Render the high-tech Forensic Command Deck Header matching the design blueprint."""
    st.markdown(
        """
        <div style="background: #0d121d; border: 1px solid rgba(0, 242, 254, 0.35); border-radius: 12px; padding: 20px 24px; margin-bottom: 20px; box-shadow: 0 0 25px rgba(0, 242, 254, 0.12); display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 16px;">
          <div style="display: flex; align-items: center; gap: 14px;">
            <span style="font-size: 32px; filter: drop-shadow(0 0 10px rgba(0, 242, 254, 0.5));">🕵️</span>
            <div>
              <div style="display: flex; align-items: center; gap: 10px; flex-wrap: wrap;">
                <h1 style="margin: 0; font-size: 22px; font-weight: 800; letter-spacing: 0.5px; background: linear-gradient(90deg, #38bdf8, #818cf8); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                  TERRASLEUTH // FORENSIC COMMAND DECK
                </h1>
                <span style="background: rgba(8, 51, 68, 0.8); color: #38bdf8; font-size: 11px; font-weight: 700; padding: 2px 10px; border-radius: 9999px; border: 1px solid rgba(14, 165, 233, 0.4); font-family: ui-monospace, monospace;">
                  AI AGENTS TRACK
                </span>
              </div>
              <p style="margin: 4px 0 0 0; color: #94a3b8; font-size: 13px;">
                Autonomous Multi-Modal Geospatial & Visual Intelligence Detective
              </p>
            </div>
          </div>
          <div style="display: flex; align-items: center; gap: 8px; background: rgba(6, 78, 59, 0.35); border: 1px solid rgba(16, 185, 129, 0.4); border-radius: 20px; padding: 6px 14px;">
            <span style="width: 8px; height: 8px; border-radius: 50%; background: #10b981; box-shadow: 0 0 8px #10b981; display: inline-block;"></span>
            <span style="font-size: 11px; font-weight: 700; font-family: ui-monospace, monospace; color: #34d399; letter-spacing: 0.5px;">
              SERPAPI ENGINES SYNCED
            </span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_anomaly_alert(anomalies: List[Dict[str, Any]]):
    """Render high-contrast, glowing fraud & disinformation alert banners."""
    if not anomalies:
        return

    for a in anomalies:
        a_type = html.escape(str(a.get("anomaly_type", "anomaly")).upper())
        a_title = html.escape(a.get("title", "Forensic Contradiction Detected"))
        a_desc = html.escape(a.get("description", ""))
        a_truth = html.escape(a.get("authoritative_truth", ""))
        a_claimed = html.escape(a.get("claimed_context", ""))
        evidence_url = sanitize_url(a.get("evidence_url"))

        evidence_btn = (
            f'<div style="margin-top: 10px;"><a href="{evidence_url}" target="_blank" style="display: inline-block; background: rgba(239, 68, 68, 0.25); border: 1px solid #ef4444; color: #fca5a5; font-size: 11px; font-weight: 700; padding: 4px 12px; border-radius: 4px; text-decoration: none; font-family: ui-monospace, monospace;">VERIFY SOURCE LINK ↗</a></div>'
            if evidence_url != "#"
            else ""
        )

        st.markdown(
            f"""
            <div style="background: rgba(69, 10, 10, 0.45); border: 1.5px solid #ef4444; border-radius: 10px; padding: 16px 20px; margin-bottom: 18px; box-shadow: 0 0 20px rgba(239, 68, 68, 0.25);">
              <div style="display: flex; align-items: center; justify-content: space-between; gap: 8px;">
                <span style="background: #ef4444; color: #fff; font-size: 10px; font-weight: 800; padding: 2px 8px; border-radius: 4px; font-family: ui-monospace, monospace; letter-spacing: 0.5px;">
                  {a_type}
                </span>
                <span style="color: #f87171; font-size: 11px; font-family: ui-monospace, monospace; font-weight: 700;">
                  HIGH CONFIDENCE FRAUD DETECTION
                </span>
              </div>
              <h3 style="margin: 8px 0 6px 0; color: #fee2e2; font-size: 17px; font-weight: 700;">
                {a_title}
              </h3>
              <p style="margin: 0 0 10px 0; color: #fca5a5; font-size: 13px; line-height: 1.5;">
                {a_desc}
              </p>
              <div style="background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(239, 68, 68, 0.3); border-radius: 6px; padding: 10px 14px; font-size: 12px;">
                {f'<div style="color: #cbd5e1; margin-bottom: 4px;"><b>Claimed Submission:</b> <span style="color: #f87171;">{a_claimed}</span></div>' if a_claimed else ''}
                <div style="color: #86efac;"><b>Authoritative Truth:</b> {a_truth}</div>
              </div>
              {evidence_btn}
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_mission_briefing():
    """Render an interactive Mission Briefing card section matching Tab 3 of the blueprint."""
    html_content = (
        '<div style="background: #0b0e17; border: 1px solid rgba(0, 242, 254, 0.25); border-radius: 12px; padding: 20px; margin-bottom: 24px; box-shadow: 0 0 20px rgba(0, 242, 254, 0.08);">'
        '<div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 14px;">'
        '<div style="display: flex; align-items: center; gap: 8px;">'
        '<span style="font-size: 18px;">🎯</span>'
        '<span style="font-size: 14px; font-weight: 700; color: #38bdf8; letter-spacing: 0.5px;">MISSION BRIEFING & INVESTIGATIVE SCENARIOS</span>'
        '</div>'
        '<span style="font-size: 11px; font-family: ui-monospace, monospace; color: #10b981; background: rgba(16, 185, 129, 0.15); padding: 2px 8px; border-radius: 4px; border: 1px solid rgba(16, 185, 129, 0.3);">'
        'ZERO CREDIT PRE-CACHED'
        '</span>'
        '</div>'
        '<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 14px;">'
        '<div style="background: #101522; border: 1px solid #1e293b; border-radius: 8px; padding: 14px;">'
        '<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">'
        '<span style="font-size: 10px; font-weight: 700; font-family: ui-monospace, monospace; color: #38bdf8; background: rgba(56, 189, 248, 0.1); padding: 2px 6px; border-radius: 3px;">LANDMARK GEOLOCATION</span>'
        '<span style="font-size: 16px;">🏛️</span>'
        '</div>'
        '<b style="color: #f1f5f9; font-size: 13px; display: block; margin-bottom: 4px;">Apollo Bunder & Gateway Arch</b>'
        '<p style="color: #94a3b8; font-size: 11px; margin: 0; line-height: 1.4;">'
        'Uncaptioned waterfront monument. Tests Indo-Saracenic basalt architectural deconstruction and sub-35m Google Maps pinpointing.'
        '</p>'
        '</div>'
        '<div style="background: #101522; border: 1px solid #1e293b; border-radius: 8px; padding: 14px;">'
        '<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">'
        '<span style="font-size: 10px; font-weight: 700; font-family: ui-monospace, monospace; color: #a78bfa; background: rgba(167, 139, 250, 0.1); padding: 2px 6px; border-radius: 3px;">ALPINE HERITAGE</span>'
        '<span style="font-size: 16px;">🏰</span>'
        '</div>'
        '<b style="color: #f1f5f9; font-size: 13px; display: block; margin-bottom: 4px;">Neuschwanstein Castle</b>'
        '<p style="color: #94a3b8; font-size: 11px; margin: 0; line-height: 1.4;">'
        'Alpine fortress hidden behind spires and conifers. Tests Romanesque Revival visual clues and Bavarian mountain triangulation.'
        '</p>'
        '</div>'
        '<div style="background: #101522; border: 1px solid rgba(239, 68, 68, 0.4); border-radius: 8px; padding: 14px;">'
        '<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">'
        '<span style="font-size: 10px; font-weight: 800; font-family: ui-monospace, monospace; color: #f87171; background: rgba(239, 68, 68, 0.15); padding: 2px 6px; border-radius: 3px;">FRAUD EXPOSER</span>'
        '<span style="font-size: 16px;">🚨</span>'
        '</div>'
        '<b style="color: #fee2e2; font-size: 13px; display: block; margin-bottom: 4px;">Vacation Rental Listing Fraud</b>'
        '<p style="color: #fca5a5; font-size: 11px; margin: 0; line-height: 1.4;">'
        'Claimed local beachfront rental unmasked by Google Lens visual twins as a copyrighted luxury resort in Oia, Santorini, Greece.'
        '</p>'
        '</div>'
        '</div>'
        '</div>'
    )
    st.markdown(html_content, unsafe_allow_html=True)


def render_osint_dorks(dorks: List[Dict[str, Any]]):
    """Render interactive clickable OSINT Google search dorks."""
    if not dorks:
        return

    st.markdown("#### 🕵️ Advanced OSINT Google Search Dorks")
    st.caption("Targeted queries formulated to extract public property records, municipal filings, and archived press.")

    for d in dorks:
        cat = html.escape(d.get("category", "OSINT Dork"))
        query = html.escape(d.get("query", ""))
        url = sanitize_url(d.get("search_url", "#"))
        exp = html.escape(d.get("explanation", ""))

        st.markdown(
            f"""
            <div style="background: #101522; border: 1px solid #1e293b; border-radius: 6px; padding: 12px 16px; margin-bottom: 10px;">
              <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="color: #fbbf24; font-size: 11px; font-weight: 700; text-transform: uppercase; font-family: ui-monospace, monospace;">{cat}</span>
                <a href="{url}" target="_blank" style="color: #38bdf8; font-size: 12px; font-weight: 700; text-decoration: none;">Execute on Google ↗</a>
              </div>
              <div style="margin: 6px 0; background: #07090e; padding: 6px 10px; border-radius: 4px; border: 1px solid #1e293b;">
                <code style="color: #38bdf8; font-size: 12px; font-family: ui-monospace, monospace;">{query}</code>
              </div>
              <p style="margin: 0; color: #94a3b8; font-size: 11px;">{exp}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
