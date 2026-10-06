"""Unit tests for GeoguessrService (mathematical scoring, Haversine distance, and radius tightening).

Ensures 100% offline mathematical verification with 0 live SerpApi credits burned.
"""

import pytest
from backend.app.services.geoguessr_service import GeoguessrService


def test_haversine_distance_known_points():
    """Verify geodesic distance calculation between known landmarks."""
    # Gateway of India (18.9220, 72.8347) to Taj Mahal Palace Hotel (18.9217, 72.8333) ~ 150m
    dist_km = GeoguessrService.calculate_haversine_distance_km(
        18.9220, 72.8347, 18.9217, 72.8333
    )
    # Expected distance is between 100m and 200m (0.1 to 0.2 km)
    assert 0.10 <= dist_km <= 0.20

    # Identical coordinates should yield exactly 0.0 distance
    dist_zero = GeoguessrService.calculate_haversine_distance_km(
        40.7128, -74.0060, 40.7128, -74.0060
    )
    assert dist_zero == pytest.approx(0.0, abs=1e-6)

    # London (51.5074, -0.1278) to Paris (48.8566, 2.3522) ~ 343 km
    london_paris = GeoguessrService.calculate_haversine_distance_km(
        51.5074, -0.1278, 48.8566, 2.3522
    )
    assert 340.0 <= london_paris <= 350.0


def test_scoring_algorithm_curve():
    """Verify 5,000-point competitive Geoguessr scoring curve."""
    # <= 50m (0.05 km) must give perfect 5,000 points
    assert GeoguessrService.calculate_geoguessr_score(0.0) == 5000
    assert GeoguessrService.calculate_geoguessr_score(0.025) == 5000
    assert GeoguessrService.calculate_geoguessr_score(0.05) == 5000

    # 1 km should yield > 4,990 points
    score_1km = GeoguessrService.calculate_geoguessr_score(1.0)
    assert score_1km >= 4990

    # 100 km should yield ~ 4,675 points
    score_100km = GeoguessrService.calculate_geoguessr_score(100.0)
    assert 4650 <= score_100km <= 4700

    # 2,000 km should yield ~ 1,300 points
    score_2000km = GeoguessrService.calculate_geoguessr_score(2000.0)
    assert 1200 <= score_2000km <= 1400

    # 10,000 km should yield very low score (< 20 points)
    score_10000km = GeoguessrService.calculate_geoguessr_score(10000.0)
    assert 0 <= score_10000km <= 20


def test_tightening_stages_generation():
    """Verify 4 progressive spatial radius narrowing stages are constructed."""
    stages = GeoguessrService.generate_tightening_stages(0.035, context_name="Gateway of India")
    assert len(stages) == 4

    assert stages[0].stage_num == 1
    assert stages[0].radius_km == 2500.0
    assert "Continental" in stages[0].name

    assert stages[1].stage_num == 2
    assert stages[1].radius_km == 250.0
    assert "Regional" in stages[1].name

    assert stages[2].stage_num == 3
    assert stages[2].radius_km == 25.0
    assert "Metropolitan" in stages[2].name

    assert stages[3].stage_num == 4
    assert stages[3].radius_km == pytest.approx(0.035, abs=0.005)
    assert "Tactical" in stages[3].name


def test_evaluate_challenge_complete():
    """Verify complete Geoguessr challenge evaluation against ground truth."""
    # Simulate high-accuracy prediction for Gateway of India (error ~ 30 meters)
    res = GeoguessrService.evaluate_challenge(
        guess_lat=18.92200,
        guess_lon=72.83470,
        truth_lat=18.92198,
        truth_lon=72.83465,
        target_name="Gateway of India",
    )

    assert res.score == 5000
    assert res.distance_km < 0.05
    assert res.distance_meters < 50.0
    assert "Sub-50m Tactical Pinpoint" in res.accuracy_tier
    assert len(res.tightening_stages) == 4
    assert res.max_score == 5000
