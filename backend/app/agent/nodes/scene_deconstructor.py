import logging
import os
from typing import Any, Dict

from backend.app.agent.state import OsintGraphState
from backend.app.services.vision_service import VisionService

logger = logging.getLogger(__name__)


def scene_deconstructor_node(state: OsintGraphState) -> Dict[str, Any]:
    """LangGraph node: Deconstructs the mystery image into categorized visual forensic clues.
    
    Extracts architectural style, script/signage, flora/climate, and landmark observations
    to seed downstream Google Lens provenance searches and Google Maps spatial triangulation.
    """
    image_path = state.get("image_path")
    image_url = state.get("image_url")
    context_hint = state.get("context_hint")

    logger.info("Executing scene_deconstructor_node for target: path=%s, url=%s", image_path, image_url)

    # Validate image input availability
    if not image_path and not image_url:
        logger.error("scene_deconstructor_node failed: neither image_path nor image_url provided")
        return {
            "status": "error",
            "error": "Investigation failed: Neither image_path nor image_url was provided.",
        }

    # If image_path is specified as a local file, ensure it exists unless URL is also provided
    if image_path and not os.path.exists(image_path) and not image_url:
        logger.error("scene_deconstructor_node failed: local image file not found: %s", image_path)
        return {
            "status": "error",
            "error": f"Investigation failed: Local image file not found: {image_path}",
        }

    try:
        service = VisionService()
        clues = service.deconstruct_scene(
            image_path=image_path,
            image_url=image_url,
            context_hint=context_hint,
        )
        logger.info("scene_deconstructor_node extracted %d forensic clues", len(clues))
        return {
            "visual_clues": clues,
            "status": "deconstructed",
            "error": None,
        }
    except Exception as exc:
        logger.exception("Unexpected error in scene_deconstructor_node: %s", exc)
        return {
            "status": "error",
            "error": f"Scene deconstruction error: {str(exc)}",
        }
