import html
import logging
from typing import Any, Dict, List, Optional
from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger(__name__)

CATEGORY_COLORS = {
    "architecture": (52, 152, 219),     # Dodger Blue
    "signage": (231, 76, 60),           # Crimson Red
    "vegetation": (46, 204, 113),       # Emerald Green
    "landmark": (241, 196, 15),         # Sun Yellow
    "infrastructure": (155, 89, 182),   # Amethyst Purple
    "apparel": (56, 189, 248),          # Cyan
    "accessory": (244, 114, 182),       # Pink
    "footwear": (251, 146, 60),         # Orange
    "jewelry": (250, 204, 21),          # Gold
    "other": (149, 165, 166),           # Concrete Grey
}


def draw_bounding_boxes(
    image: Image.Image,
    clues: List[Any],
    box_width: int = 4,
) -> Image.Image:
    """Draw forensic bounding boxes and category labels onto a Pillow image copy.
    
    Coordinates are assumed normalized [ymin, xmin, ymax, xmax] in [0.0, 1.0].
    Supports both VisualClue models and itemized_dossier dictionaries.
    """
    annotated = image.copy().convert("RGB")
    draw = ImageDraw.Draw(annotated)
    w, h = annotated.size

    for clue in clues:
        bbox = clue.bounding_box if hasattr(clue, "bounding_box") else (clue.get("bounding_box") if isinstance(clue, dict) else None)
        if not bbox or len(bbox) != 4:
            continue

        if hasattr(clue, "category"):
            raw_cat = clue.category.value if hasattr(clue.category, "value") else str(clue.category)
        elif isinstance(clue, dict):
            raw_cat = clue.get("category") or clue.get("label") or "other"
        else:
            raw_cat = "other"

        cat_key = raw_cat.lower()
        color = CATEGORY_COLORS.get(cat_key, (56, 189, 248))

        ymin, xmin, ymax, xmax = bbox
        x1 = max(0, min(w - 1, int(xmin * w)))
        y1 = max(0, min(h - 1, int(ymin * h)))
        x2 = max(0, min(w - 1, int(xmax * w)))
        y2 = max(0, min(h - 1, int(ymax * h)))

        if x2 <= x1 or y2 <= y1:
            continue

        # Draw main bounding box
        draw.rectangle([x1, y1, x2, y2], outline=color, width=box_width)

        # Draw label header banner
        display_label = (
            getattr(clue, "label", None)
            or (clue.get("label") if isinstance(clue, dict) else None)
            or cat_key
        ).replace("_", " ").title()
        confidence = getattr(clue, "confidence", None) or (clue.get("confidence", 1.0) if isinstance(clue, dict) else 1.0)
        label_text = f"{display_label} ({int(confidence * 100)}%)"

        # Draw text background pill
        text_bbox = draw.textbbox((x1, max(0, y1 - 20)), label_text)
        draw.rectangle([text_bbox[0] - 2, text_bbox[1] - 2, text_bbox[2] + 4, text_bbox[3] + 2], fill=color)
        draw.text((x1, max(0, y1 - 20)), label_text, fill=(255, 255, 255))

    return annotated


def render_visual_evidence_board(
    image: Image.Image,
    visual_clues: List[Any],
    streamlit_context: Any = None,
):
    """Render the visual evidence board in Streamlit."""
    import streamlit as st

    ctx = streamlit_context or st

    ctx.markdown("### 🔍 Forensic Visual Evidence Board")
    ctx.caption("Multi-modal vision analysis: architectural motifs, signage, vegetation, and infrastructure clues.")

    # Render image with bounding box overlays
    annotated_img = draw_bounding_boxes(image, visual_clues)
    ctx.image(annotated_img, caption="Forensic Bounding Box Overlays", use_container_width=True)

    # Clue legend cards
    if visual_clues:
        cols = ctx.columns(min(len(visual_clues), 4))
        for idx, clue in enumerate(visual_clues):
            col = cols[idx % len(cols)]
            if hasattr(clue, "category"):
                raw_cat = clue.category.value if hasattr(clue.category, "value") else str(clue.category)
                desc = getattr(clue, "description", "") or ""
                conf = getattr(clue, "confidence", 0.0)
            elif isinstance(clue, dict):
                raw_cat = clue.get("category") or clue.get("label", "item")
                desc = clue.get("title") or clue.get("label", "").replace("_", " ").title()
                conf = clue.get("confidence", 0.9)
            else:
                raw_cat = "other"
                desc = str(clue)
                conf = 0.8

            safe_cat = html.escape(str(raw_cat).upper())
            safe_desc = html.escape(str(desc))

            with col:
                clue_html = (
                    f'<div style="background-color: #1a1e24; padding: 10px; border-radius: 8px; border-left: 4px solid #3498db; margin-bottom: 8px;">'
                    f'<span style="font-size: 11px; color: #8892b0; text-transform: uppercase;">{safe_cat}</span>'
                    f'<div style="font-size: 13px; font-weight: 600; color: #e6f1ff; margin-top: 4px;">{safe_desc}</div>'
                    f'<div style="font-size: 12px; color: #64ffda; margin-top: 4px;">Confidence: {int(conf * 100)}%</div>'
                    f'</div>'
                )
                col.markdown(clue_html, unsafe_allow_html=True)
    else:
        ctx.info("No visual forensic clues deconstructed.")
