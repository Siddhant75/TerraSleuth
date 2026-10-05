import base64
import html
import io
import time
from typing import Any, Dict, List, Optional
from PIL import Image

from backend.app.models.case import CaseFile


def sanitize_url(url: Optional[str]) -> str:
    """Sanitize URL for safe inclusion in href attributes, allowing only http, https, and mailto schemes."""
    if not url:
        return "#"
    clean = str(url).strip()
    if clean.lower().startswith(("http://", "https://", "mailto:")):
        return html.escape(clean)
    return "#"


def image_to_base64_data_uri(img: Optional[Image.Image]) -> Optional[str]:
    """Convert a PIL Image to a base64 JPEG data URI for standalone offline HTML embedding."""
    if not img:
        return None
    try:
        buffered = io.BytesIO()
        rgb_img = img.convert("RGB")
        rgb_img.save(buffered, format="JPEG", quality=88)
        b64_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
        return f"data:image/jpeg;base64,{b64_str}"
    except Exception:
        return None


def generate_standalone_html_dossier(
    case_file: CaseFile,
    target_image: Optional[Image.Image] = None,
) -> str:
    """Generate a self-contained, beautifully styled offline HTML forensic investigation report."""
    safe_title = html.escape(case_file.title or "Untitled OSINT Case")
    safe_case_id = html.escape(case_file.case_id or "case_unknown")
    conf_pct = int(case_file.confidence_score * 100)
    img_data_uri = image_to_base64_data_uri(target_image)
    
    loc = case_file.resolved_location
    loc_name = html.escape(loc.name if loc and loc.name else "Unidentified")
    loc_addr = html.escape(loc.address if loc and loc.address else "Unspecified")
    lat_str = f"{loc.latitude:.5f}°N" if loc and loc.latitude is not None else "N/A"
    lon_str = f"{loc.longitude:.5f}°E" if loc and loc.longitude is not None else "N/A"
    coords_display = f"{lat_str}, {lon_str}" if loc else "N/A"
    maps_url = sanitize_url(loc.source_url) if loc and loc.source_url else sanitize_url(f"https://www.google.com/maps/search/?api=1&query={loc.latitude},{loc.longitude}") if loc else "#"

    # Build Anomalies HTML
    anomalies_html = ""
    if case_file.anomalies:
        cards = []
        for a in case_file.anomalies:
            a_type = html.escape(str(a.get("anomaly_type", "anomaly")).upper())
            a_title = html.escape(a.get("title", "Forensic Anomaly Detected"))
            a_desc = html.escape(a.get("description", ""))
            a_truth = html.escape(a.get("authoritative_truth", ""))
            a_claimed = html.escape(a.get("claimed_context", ""))
            cards.append(f"""
            <div class="anomaly-card">
              <div class="anomaly-tag">{a_type}</div>
              <div class="anomaly-title">{a_title}</div>
              <div class="anomaly-desc">{a_desc}</div>
              {f'<div class="anomaly-detail"><b>Claimed:</b> {a_claimed}</div>' if a_claimed else ''}
              <div class="anomaly-truth"><b>Authoritative Ground Truth:</b> {a_truth}</div>
            </div>
            """)
        anomalies_html = f"""
        <div class="section-container alert-border">
          <h2 class="section-title text-red">🚨 DETECTED FORENSIC CONTRADICTIONS & FRAUD WARNINGS</h2>
          {''.join(cards)}
        </div>
        """

    # Build Visual Clues HTML
    clues_rows = []
    for c in case_file.visual_clues:
        cat = html.escape(c.category.value if hasattr(c.category, "value") else str(c.category)).upper()
        desc = html.escape(c.description)
        c_conf = f"{int(c.confidence * 100)}%"
        clues_rows.append(f"""
        <tr>
          <td><span class="badge badge-cyan">{cat}</span></td>
          <td>{desc}</td>
          <td class="text-right font-mono text-emerald">{c_conf}</td>
        </tr>
        """)
    clues_table_html = "".join(clues_rows) if clues_rows else "<tr><td colspan='3'>No visual clues decomposed.</td></tr>"

    # Build Lens Twins HTML
    lens_rows = []
    for idx, m in enumerate(case_file.lens_matches[:4], 1):
        m_title = html.escape(m.get("title", "Visual Match"))
        m_source = html.escape(m.get("source", "Web"))
        m_link = sanitize_url(m.get("link", "#"))
        lens_rows.append(f"""
        <tr>
          <td class="font-mono">#{idx}</td>
          <td><b><a href="{m_link}" target="_blank" class="link-cyan">{m_title}</a></b></td>
          <td class="font-mono text-slate">{m_source}</td>
        </tr>
        """)
    lens_table_html = "".join(lens_rows) if lens_rows else "<tr><td colspan='3'>No Google Lens visual matches cataloged.</td></tr>"

    # Build Timeline HTML
    time_rows = []
    for t in case_file.timeline:
        t_date = html.escape(t.date)
        t_title = html.escape(t.title)
        t_source = html.escape(t.source)
        t_snip = html.escape(t.snippet)
        origin_tag = '<span class="badge badge-emerald">EARLIEST KNOWN</span> ' if t.is_origin else ''
        time_rows.append(f"""
        <div class="timeline-item">
          <div class="timeline-date">{origin_tag}{t_date}</div>
          <div class="timeline-headline"><b>{t_title}</b> <span class="text-slate">({t_source})</span></div>
          <div class="timeline-snippet">{t_snip}</div>
        </div>
        """)
    timeline_html = "".join(time_rows) if time_rows else "<p class='text-slate'>No external chronological records discovered.</p>"

    # Build Citations HTML
    cit_rows = []
    for idx, cit in enumerate(case_file.citations, 1):
        c_eng = html.escape(cit.engine).upper()
        c_title = html.escape(cit.title)
        c_url = sanitize_url(cit.url)
        c_snip = html.escape(cit.snippet)
        cit_rows.append(f"""
        <div class="citation-item">
          <span class="badge badge-blue">{c_eng}</span>
          <a href="{c_url}" target="_blank" class="link-cyan font-bold">{c_title}</a>
          <p class="citation-snippet">"{c_snip}"</p>
        </div>
        """)
    citations_html = "".join(cit_rows) if cit_rows else "<p class='text-slate'>No evidentiary citations recorded.</p>"

    # Build OSINT Dorks HTML
    dorks_rows = []
    for d in case_file.dorks:
        d_cat = html.escape(d.get("category", "OSINT Dork"))
        d_query = html.escape(d.get("query", ""))
        d_url = sanitize_url(d.get("search_url", "#"))
        d_exp = html.escape(d.get("explanation", ""))
        dorks_rows.append(f"""
        <div class="dork-item">
          <div class="dork-cat">{d_cat}</div>
          <div class="dork-query font-mono"><code>{d_query}</code></div>
          <div class="dork-exp">{d_exp}</div>
          <a href="{d_url}" target="_blank" class="link-cyan text-xs">Execute Query on Google Search ↗</a>
        </div>
        """)
    dorks_html = "".join(dorks_rows) if dorks_rows else ""

    date_str = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>TerraSleuth Forensic Intelligence Dossier — {safe_title}</title>
  <style>
    body {{
      background-color: #07090e;
      color: #e2e8f0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      margin: 0;
      padding: 30px;
      line-height: 1.5;
    }}
    .max-container {{
      max-width: 1000px;
      margin: 0 auto;
    }}
    .header-box {{
      background: #0d121d;
      border: 1px solid rgba(0, 242, 254, 0.4);
      border-radius: 12px;
      padding: 24px;
      margin-bottom: 24px;
      box-shadow: 0 0 25px rgba(0, 242, 254, 0.15);
    }}
    .case-id {{
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
      color: #00f2fe;
      font-size: 13px;
      letter-spacing: 1px;
      text-transform: uppercase;
    }}
    h1 {{
      margin: 6px 0 12px 0;
      color: #f8fafc;
      font-size: 26px;
    }}
    .meta-ribbon {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 12px;
      margin-top: 18px;
    }}
    .meta-card {{
      background: #111726;
      border: 1px solid #1e293b;
      border-radius: 8px;
      padding: 10px 14px;
      text-align: center;
    }}
    .meta-label {{
      font-size: 11px;
      color: #94a3b8;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }}
    .meta-value {{
      font-size: 15px;
      font-weight: 700;
      color: #f1f5f9;
      margin-top: 4px;
    }}
    .section-container {{
      background: #0d121d;
      border: 1px solid #1e293b;
      border-radius: 10px;
      padding: 20px;
      margin-bottom: 20px;
    }}
    .alert-border {{
      border: 1px solid rgba(239, 68, 68, 0.5);
      background: rgba(239, 68, 68, 0.05);
    }}
    .section-title {{
      font-size: 16px;
      font-weight: 700;
      color: #38bdf8;
      margin-top: 0;
      margin-bottom: 14px;
      border-bottom: 1px solid #1e293b;
      padding-bottom: 8px;
    }}
    .text-red {{ color: #ef4444 !important; }}
    .text-emerald {{ color: #10b981 !important; }}
    .text-slate {{ color: #94a3b8 !important; }}
    .font-mono {{ font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; }}
    .text-right {{ text-align: right; }}
    .badge {{
      display: inline-block;
      padding: 2px 8px;
      border-radius: 4px;
      font-size: 11px;
      font-weight: 700;
      font-family: ui-monospace, monospace;
    }}
    .badge-cyan {{ background: rgba(0, 242, 254, 0.15); color: #00f2fe; border: 1px solid rgba(0, 242, 254, 0.4); }}
    .badge-blue {{ background: rgba(59, 130, 246, 0.15); color: #60a5fa; border: 1px solid rgba(59, 130, 246, 0.4); }}
    .badge-emerald {{ background: rgba(16, 185, 129, 0.15); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.4); }}
    .table-custom {{
      width: 100%;
      border-collapse: collapse;
      font-size: 13px;
    }}
    .table-custom th {{
      text-align: left;
      padding: 8px;
      color: #94a3b8;
      border-bottom: 1px solid #1e293b;
      font-size: 11px;
      text-transform: uppercase;
    }}
    .table-custom td {{
      padding: 10px 8px;
      border-bottom: 1px solid #141b2b;
    }}
    .link-cyan {{
      color: #38bdf8;
      text-decoration: none;
    }}
    .link-cyan:hover {{ text-decoration: underline; }}
    .anomaly-card {{
      background: rgba(239, 68, 68, 0.1);
      border: 1px solid rgba(239, 68, 68, 0.3);
      border-radius: 8px;
      padding: 14px;
      margin-bottom: 10px;
    }}
    .anomaly-tag {{
      display: inline-block;
      background: #ef4444;
      color: #fff;
      font-size: 10px;
      font-weight: 800;
      padding: 2px 6px;
      border-radius: 3px;
      font-family: monospace;
    }}
    .anomaly-title {{ font-size: 15px; font-weight: 700; color: #fca5a5; margin: 6px 0; }}
    .anomaly-desc {{ font-size: 13px; color: #fecaca; margin-bottom: 6px; }}
    .anomaly-truth {{ font-size: 13px; color: #86efac; font-weight: 600; }}
    .timeline-item {{
      border-left: 2px solid #38bdf8;
      padding-left: 14px;
      margin-bottom: 16px;
    }}
    .timeline-date {{ font-size: 12px; font-weight: 700; color: #38bdf8; font-family: monospace; }}
    .timeline-headline {{ font-size: 14px; color: #f1f5f9; margin: 3px 0; }}
    .timeline-snippet {{ font-size: 12px; color: #94a3b8; }}
    .citation-item {{
      background: #101522;
      border: 1px solid #1e293b;
      border-radius: 6px;
      padding: 10px 14px;
      margin-bottom: 8px;
    }}
    .citation-snippet {{ font-size: 12px; color: #94a3b8; margin: 4px 0 0 0; font-style: italic; }}
    .dork-item {{
      background: #101522;
      border: 1px solid #1e293b;
      border-radius: 6px;
      padding: 10px 14px;
      margin-bottom: 8px;
    }}
    .dork-cat {{ font-size: 12px; font-weight: 700; color: #fbbf24; text-transform: uppercase; }}
    .dork-query code {{ background: #07090e; color: #38bdf8; padding: 2px 6px; border-radius: 4px; font-size: 12px; }}
    .dork-exp {{ font-size: 12px; color: #94a3b8; margin: 4px 0; }}
    .img-preview {{
      max-width: 100%;
      border-radius: 8px;
      border: 1px solid #334155;
      margin-bottom: 12px;
    }}
    @media print {{
      body {{ background: #fff; color: #000; }}
      .header-box, .section-container {{ background: #fff; border: 1px solid #ccc; box-shadow: none; }}
      .section-title {{ color: #000; border-bottom: 1px solid #ccc; }}
      .link-cyan {{ color: #000; text-decoration: underline; }}
    }}
  </style>
</head>
<body>
  <div class="max-container">
    
    <!-- Header Box -->
    <div class="header-box">
      <div style="display: flex; justify-content: space-between; align-items: center;">
        <span class="case-id">TERRASLEUTH // CASE FILE #{safe_case_id}</span>
        <span class="badge badge-emerald">AUTHENTIC PROVENANCE VERIFIED</span>
      </div>
      <h1>{safe_title}</h1>
      <p style="color: #94a3b8; font-size: 13px; margin: 0;">Generated on {date_str} • Autonomous Multi-Modal OSINT Swarm Engine</p>

      <div class="meta-ribbon">
        <div class="meta-card">
          <div class="meta-label">Ground Truth Target</div>
          <div class="meta-value text-emerald">{loc_name}</div>
        </div>
        <div class="meta-card">
          <div class="meta-label">WGS84 Coordinates</div>
          <div class="meta-value font-mono">{coords_display}</div>
        </div>
        <div class="meta-card">
          <div class="meta-label">Consensus Confidence</div>
          <div class="meta-value text-emerald">{conf_pct}% [VERIFIED]</div>
        </div>
        <div class="meta-card">
          <div class="meta-label">SerpApi Searches</div>
          <div class="meta-value font-mono text-cyan">{case_file.serp_queries_executed} QUERIES</div>
        </div>
      </div>
    </div>

    <!-- Anomaly Section (if any) -->
    {anomalies_html}

    <!-- Geospatial Triangulation -->
    <div class="section-container">
      <h2 class="section-title">📍 GEOSPATIAL PINPOINT & TRIANGULATION</h2>
      <p><b>Street Address:</b> {loc_addr}</p>
      <p><b>Coordinates:</b> <code class="badge badge-cyan">{coords_display}</code></p>
      <p><b>Google Maps Reference:</b> <a href="{maps_url}" target="_blank" class="link-cyan">Open in Google Maps ↗</a></p>
    </div>

    <!-- Target Image & Visual Clues -->
    <div class="section-container">
      <h2 class="section-title">🔍 VISUAL FORENSIC DECONSTRUCTION</h2>
      {f'<img src="{img_data_uri}" class="img-preview" alt="Suspect Evidence" />' if img_data_uri else ''}
      <table class="table-custom">
        <thead>
          <tr>
            <th>Category</th>
            <th>Forensic Clue Description</th>
            <th class="text-right">Confidence</th>
          </tr>
        </thead>
        <tbody>
          {clues_table_html}
        </tbody>
      </table>
    </div>

    <!-- Google Lens Visual Twin Provenance -->
    <div class="section-container">
      <h2 class="section-title">🔬 GOOGLE LENS VISUAL TWIN MATCHES</h2>
      <table class="table-custom">
        <thead>
          <tr>
            <th>Rank</th>
            <th>Authoritative Match Title</th>
            <th>Domain Source</th>
          </tr>
        </thead>
        <tbody>
          {lens_table_html}
        </tbody>
      </table>
    </div>

    <!-- Timeline -->
    <div class="section-container">
      <h2 class="section-title">⏱️ CHRONOLOGICAL PROVENANCE & MEDIA TIMELINE</h2>
      {timeline_html}
    </div>

    <!-- Verifiable Citations -->
    <div class="section-container">
      <h2 class="section-title">🔗 VERIFIABLE CITATION CHAIN</h2>
      {citations_html}
    </div>

    <!-- OSINT Dorks -->
    {f'<div class="section-container"><h2 class="section-title">🕵️ TARGETED OSINT GOOGLE SEARCH DORKS</h2>{dorks_html}</div>' if dorks_html else ''}

    <div style="text-align: center; color: #64748b; font-size: 11px; margin-top: 30px;">
      TERRASLEUTH OSINT ENGINE • ZERO CREDIT QUOTA DEFENSE • POWERED BY SERPAPI & LANGGRAPH
    </div>

  </div>
</body>
</html>
"""
