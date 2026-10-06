"""Geoguessr Scoring and Spatial Radius Tightening Service.

Implements geodesic distance error calculation (Haversine formula),
standard 5,000-point competitive Geoguessr scoring curve,
and progressive 4-phase spatial radius narrowing.
"""

import math
from typing import List, Tuple
from backend.app.models.geoguessr import GeoguessrResult, TighteningStage


class GeoguessrService:
    """Evaluates spatial triangulation against ground truth for Geoguessr challenges."""

    EARTH_RADIUS_KM: float = 6371.0088

    @classmethod
    def calculate_haversine_distance_km(
        cls,
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float,
    ) -> float:
        """Calculate the geodesic distance between two points on Earth using Haversine formula."""
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)

        a = (
            math.sin(delta_phi / 2.0) ** 2
            + math.cos(phi1) * math.cos(phi2) * (math.sin(delta_lambda / 2.0) ** 2)
        )
        c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
        return cls.EARTH_RADIUS_KM * c

    @classmethod
    def calculate_geoguessr_score(cls, distance_km: float) -> int:
        """Calculate the 5,000-point Geoguessr competitive score.

        Uses standard exponential decay where:
        - <= 50 meters (0.05 km) yields a perfect 5,000 points.
        - <= 1 km yields > 4,995 points.
        - 100 km yields ~ 4,675 points.
        - >= 10,000 km yields < 10 points.
        """
        if distance_km <= 0.05:
            return 5000

        # Scale factor tuned for global Geoguessr distribution
        decay_factor = 1492.7
        score = int(5000.0 * math.exp(-distance_km / decay_factor))
        return max(0, min(5000, score))

    @classmethod
    def determine_accuracy_tier(cls, distance_km: float) -> Tuple[str, str]:
        """Return human-readable accuracy tier and forensic detective verdict."""
        if distance_km <= 0.05:
            return (
                "🎯 Sub-50m Tactical Pinpoint",
                "Legendary Champion: AI resolved exact physical ground truth within sub-50m walking radius.",
            )
        elif distance_km <= 1.0:
            return (
                "🏙️ Street / Neighborhood Lock",
                "Master Detective: AI identified the exact immediate neighborhood / city street.",
            )
        elif distance_km <= 25.0:
            return (
                "📍 Metro Area Consensus",
                "Senior Analyst: AI pinpointed the metropolitan urban cluster.",
            )
        elif distance_km <= 250.0:
            return (
                "🗺️ Regional District Corridor",
                "Investigator: AI resolved the state / province / administrative region.",
            )
        elif distance_km <= 2500.0:
            return (
                "🌍 Country / Sub-Continent",
                "Scout: AI narrowed coordinates to national borders.",
            )
        else:
            return (
                "🌐 Global Hemisphere",
                "Initial Lead: Spatial coordinates require further disambiguation hops.",
            )

    @classmethod
    def generate_tightening_stages(
        cls,
        final_distance_km: float,
        context_name: str = "Target Landmark",
    ) -> List[TighteningStage]:
        """Generate the 4-phase progressive spatial radius narrowing progression."""
        tactical_radius = max(0.035, round(final_distance_km, 3))
        return [
            TighteningStage(
                stage_num=1,
                name="Continental / Biome Reconnaissance",
                radius_km=2500.0,
                description="Scene Deconstructor scans architectural motifs, solar elevation, native vegetation, and terrain.",
                clues_resolved="Architectural style & regional climate motifs cataloged.",
            ),
            TighteningStage(
                stage_num=2,
                name="Regional & Cultural Corroboration",
                radius_km=250.0,
                description="SerpApi OCR & script recognition narrows administrative state, language dialect, and infrastructure.",
                clues_resolved="Signage script, utility pole construction & language markers isolated.",
            ),
            TighteningStage(
                stage_num=3,
                name="Metropolitan Entity Disambiguation",
                radius_km=25.0,
                description="SerpApi Google Lens queries reverse visual twins, linking suspect imagery to named entities.",
                clues_resolved=f"Authoritative visual twins identified matching '{context_name}'.",
            ),
            TighteningStage(
                stage_num=4,
                name="Tactical Ground Truth Pinpoint",
                radius_km=tactical_radius,
                description="SerpApi Google Maps / Local places resolves physical street address, WGS84 coordinates, and consensus pin.",
                clues_resolved=f"WGS84 centroid verified with ±{int(tactical_radius * 1000)}m spatial consensus.",
            ),
        ]

    @classmethod
    def evaluate_challenge(
        cls,
        guess_lat: float,
        guess_lon: float,
        truth_lat: float,
        truth_lon: float,
        target_name: str = "Suspect Landmark",
    ) -> GeoguessrResult:
        """Run complete Geoguessr evaluation comparing resolved coordinates against ground truth."""
        dist_km = cls.calculate_haversine_distance_km(guess_lat, guess_lon, truth_lat, truth_lon)
        dist_m = dist_km * 1000.0
        score = cls.calculate_geoguessr_score(dist_km)
        tier, verdict = cls.determine_accuracy_tier(dist_km)
        stages = cls.generate_tightening_stages(dist_km, context_name=target_name)

        return GeoguessrResult(
            distance_km=round(dist_km, 4),
            distance_meters=round(dist_m, 1),
            score=score,
            max_score=5000,
            accuracy_tier=tier,
            verdict=verdict,
            tightening_stages=stages,
        )
