import datetime
import html
from typing import List, Optional
import streamlit as st


def format_terminal_log_entry(
    step_name: str,
    deduction: str,
    timestamp: Optional[str] = None,
) -> str:
    """Format an atomic agent reasoning event for the monospace cyber terminal."""
    if not timestamp:
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    clean_step = step_name.upper().strip()
    return f"[{timestamp}] [{clean_step}] {deduction.strip()}"


def generate_swarm_terminal_html(
    log_entries: List[str],
    max_height_px: int = 240,
) -> str:
    """Generate high-contrast obsidian cyber terminal HTML with auto-scroll and glow."""
    if not log_entries:
        safe_logs = '<span style="color: #64748b;">[STANDBY] Swarm telemetry initialized. Awaiting investigative dispatch...</span>'
    else:
        escaped_lines = []
        for line in log_entries:
            safe_line = html.escape(str(line))
            # Highlight step names in cyan/emerald
            if "[SCENE_DECONSTRUCTOR]" in safe_line:
                safe_line = safe_line.replace("[SCENE_DECONSTRUCTOR]", "<span style='color: #38bdf8; font-weight: 700;'>[SCENE_DECONSTRUCTOR]</span>")
            elif "[LENS_HUNTER]" in safe_line:
                safe_line = safe_line.replace("[LENS_HUNTER]", "<span style='color: #a78bfa; font-weight: 700;'>[LENS_HUNTER]</span>")
            elif "[GEO_TRIANGULATOR]" in safe_line:
                safe_line = safe_line.replace("[GEO_TRIANGULATOR]", "<span style='color: #34d399; font-weight: 700;'>[GEO_TRIANGULATOR]</span>")
            elif "[CHRONO_AUDITOR]" in safe_line:
                safe_line = safe_line.replace("[CHRONO_AUDITOR]", "<span style='color: #fbbf24; font-weight: 700;'>[CHRONO_AUDITOR]</span>")
            elif "[CASE_SYNTHESIZER]" in safe_line:
                safe_line = safe_line.replace("[CASE_SYNTHESIZER]", "<span style='color: #f43f5e; font-weight: 700;'>[CASE_SYNTHESIZER]</span>")
            escaped_lines.append(f"<div style='margin-bottom: 4px; line-height: 1.45;'>{safe_line}</div>")
        safe_logs = "".join(escaped_lines)

    return f"""
    <div class="terminal-container" style="
        background-color: #090d16;
        border: 1px solid #1e293b;
        border-radius: 6px;
        padding: 12px 14px;
        font-family: 'JetBrains Mono', 'Fira Code', 'Courier New', monospace;
        font-size: 11.5px;
        color: #94a3b8;
        max-height: {max_height_px}px;
        overflow-y: auto;
        box-shadow: inset 0 2px 8px rgba(0, 0, 0, 0.6);
        margin-bottom: 12px;
    ">
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px; border-bottom: 1px solid #1e293b; padding-bottom: 6px;">
            <div style="display: flex; align-items: center; gap: 6px;">
                <span style="display: inline-block; width: 8px; height: 8px; border-radius: 50%; background-color: #10b981; box-shadow: 0 0 6px #10b981;"></span>
                <span style="font-weight: 700; color: #e2e8f0; font-size: 11px; letter-spacing: 0.5px;">LIVE SWARM TELEMETRY RADAR</span>
            </div>
            <span style="font-size: 10px; color: #64748b; font-family: monospace;">SERPAPI + LANGGRAPH v0.4</span>
        </div>
        <div class="terminal-body" style="word-break: break-word;">
            {safe_logs}
        </div>
    </div>
    """


def render_swarm_telemetry_terminal(
    log_entries: List[str],
    max_height_px: int = 240,
) -> None:
    """Render the monospace cyber terminal inside Streamlit."""
    html_markup = generate_swarm_terminal_html(log_entries, max_height_px=max_height_px)
    st.markdown(html_markup, unsafe_allow_html=True)
