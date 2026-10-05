import json
import operator
import pytest
from pydantic import ValidationError

from backend.app.agent.state import (
    OsintGraphState,
    create_initial_osint_state,
    merge_lists,
)
from backend.app.models.case import (
    CaseFile,
    Citation,
    ClueCategory,
    GeoCandidate,
    TimelineEvent,
    VisualClue,
)


def test_visual_clue_validation():
    """Verify field requirements and bounds on VisualClue."""
    clue = VisualClue(
        category=ClueCategory.ARCHITECTURE,
        description="Indo-Saracenic basalt arch with ornate minarets",
        bounding_box=[0.1, 0.2, 0.6, 0.7],
        confidence=0.95,
        suggested_query="Indo-Saracenic basalt arch Mumbai waterfront",
    )
    assert clue.category == ClueCategory.ARCHITECTURE
    assert clue.confidence == 0.95
    assert len(clue.bounding_box) == 4
    assert len(clue.clue_id) == 8

    # Confidence must be between 0.0 and 1.0
    with pytest.raises(ValidationError):
        VisualClue(
            category=ClueCategory.LANDMARK,
            description="Invalid confidence clue",
            confidence=1.5,
        )

    # Bounding box must have exactly 4 coordinates
    with pytest.raises(ValidationError):
        VisualClue(
            category=ClueCategory.LANDMARK,
            description="Malformed 3-coord box",
            bounding_box=[0.1, 0.2, 0.3],
            confidence=0.9,
        )

    # Bounding box coordinates must be normalized within [0.0, 1.0]
    with pytest.raises(ValidationError):
        VisualClue(
            category=ClueCategory.LANDMARK,
            description="Out of bounds coordinates",
            bounding_box=[0.1, 0.2, 1.5, 0.4],
            confidence=0.9,
        )


def test_geo_candidate_validation():
    """Verify coordinate requirements and score bounds on GeoCandidate."""
    candidate = GeoCandidate(
        name="Gateway of India",
        address="Apollo Bandar, Colaba, Mumbai",
        latitude=18.9220,
        longitude=72.8347,
        place_id="ChIJbU60Q_bQ5zsRz797rU461QQ",
        match_score=0.98,
        engine_source="google_maps",
        evidence_snippet="Historic arch facing Arabian Sea.",
    )
    assert candidate.name == "Gateway of India"
    assert candidate.latitude == 18.9220
    assert candidate.match_score == 0.98

    # Match score must be between 0.0 and 1.0
    with pytest.raises(ValidationError):
        GeoCandidate(
            name="Invalid Candidate",
            latitude=0.0,
            longitude=0.0,
            match_score=-0.1,
            engine_source="google_maps",
        )


def test_timeline_event_and_citation():
    """Verify TimelineEvent and Citation models."""
    event = TimelineEvent(
        date="1924-12-04",
        title="Gateway of India Opened",
        source="Historical Archive",
        snippet="Viceroy Lord Reading opened the basalt arch.",
        is_origin=True,
    )
    assert event.is_origin is True

    citation = Citation(
        title="Gateway of India Wikipedia",
        url="https://en.wikipedia.org/wiki/Gateway_of_India",
        engine="google_lens",
        snippet="Located in Colaba, Mumbai.",
    )
    assert citation.engine == "google_lens"


def test_case_file_serialization_roundtrip():
    """Verify CaseFile model serialization to/from JSON."""
    clue = VisualClue(
        category=ClueCategory.LANDMARK,
        description="Prominent waterfront basalt monument",
        confidence=0.92,
    )
    candidate = GeoCandidate(
        name="Gateway of India",
        latitude=18.9220,
        longitude=72.8347,
        match_score=0.95,
        engine_source="google_maps",
    )
    case_file = CaseFile(
        title="Waterfront Arch Mystery Solved",
        case_summary="## Forensic Verdict\nTarget pinpointed to Gateway of India, Mumbai.",
        confidence_score=0.96,
        resolved_location=candidate,
        visual_clues=[clue],
        refinement_hops=1,
        serp_queries_executed=3,
    )

    data = case_file.model_dump()
    assert data["confidence_score"] == 0.96
    assert data["resolved_location"]["name"] == "Gateway of India"
    assert len(data["visual_clues"]) == 1

    # Deserialization
    reconstructed = CaseFile.model_validate(data)
    assert reconstructed.title == case_file.title
    assert reconstructed.resolved_location.latitude == 18.9220


def test_create_initial_osint_state():
    """Verify state initialization helper factory."""
    state = create_initial_osint_state(
        image_path="test_image.jpg",
        image_url="https://example.com/test.jpg",
        context_hint="Mystery coastal landmark",
        max_budget=6,
        max_refinement_hops=2,
    )

    assert state["image_path"] == "test_image.jpg"
    assert state["image_url"] == "https://example.com/test.jpg"
    assert state["context_hint"] == "Mystery coastal landmark"
    assert state["budget_remaining"] == 6
    assert state["max_refinement_hops"] == 2
    assert state["refinement_hops"] == 0
    assert state["status"] == "initialized"
    assert state["visual_clues"] == []
    assert state["geo_candidates"] == []
    assert state["final_case_file"] is None


def test_merge_lists_reducer():
    """Verify custom merge_lists reducer deduplication."""
    match1 = {"title": "Gateway", "link": "https://example.com/1"}
    match2 = {"title": "Taj Palace", "link": "https://example.com/2"}
    match3 = {"title": "Colaba Port", "link": "https://example.com/3"}

    # Disjoint lists merge cleanly
    merged = merge_lists([match1], [match2])
    assert len(merged) == 2

    # Overlapping items are deduplicated
    merged_dup = merge_lists([match1, match2], [match2, match3])
    assert len(merged_dup) == 3
    assert merged_dup == [match1, match2, match3]

    # Empty inputs return new copies without shared reference
    assert merge_lists([], [match1]) == [match1]
    assert merge_lists([match1], []) == [match1]

    # Immutability check: mutating result must not mutate input list
    source_list = [{"title": "Original"}]
    merged_copy = merge_lists([], source_list)
    merged_copy.append({"title": "Mutated Item"})
    assert len(source_list) == 1
    assert "Mutated Item" not in [x.get("title") for x in source_list]


def test_simulated_state_reducer_accumulation():
    """Simulate LangGraph node state updates using operator.add and merge_lists."""
    clue1 = VisualClue(category=ClueCategory.ARCHITECTURE, description="Basalt arch", confidence=0.9)
    clue2 = VisualClue(category=ClueCategory.SIGNAGE, description="Devanagari lettering", confidence=0.8)

    # Node 1 produces clue1
    clues_step_1 = [clue1]

    # Node 2 produces clue2
    clues_step_2 = operator.add(clues_step_1, [clue2])
    assert len(clues_step_2) == 2
    assert clues_step_2[0].description == "Basalt arch"
    assert clues_step_2[1].description == "Devanagari lettering"
