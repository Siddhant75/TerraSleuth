import pytest
from frontend.components.swarm_telemetry_terminal import generate_swarm_terminal_html

def test_swarm_terminal_renders_role_badges():
    logs = [
        "[HUNTER] Proposing Gateway of India based on basalt arch matches.",
        "[SKEPTIC] Auditing flora and municipal records... No contradiction.",
        "[ARBITER] Audit certified with 96% confidence score.",
    ]
    html = generate_swarm_terminal_html(logs)
    assert "HUNTER" in html
    assert "SKEPTIC" in html
    assert "ARBITER" in html
    assert "#00f2fe" in html  # Hunter cyan glow
    assert "#ef4444" in html  # Skeptic red glow
    assert "#10b981" in html  # Arbiter emerald glow
