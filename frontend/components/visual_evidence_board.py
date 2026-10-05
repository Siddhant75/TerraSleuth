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
    "other": (149, 165, 166),           # Concrete Grey
}


def draw_bounding_boxes(
    image: Image.Image,
    clues: List[Any],
    box_width: int = 4,
) -> Image.Image:
    """Draw forensic bounding boxes and category labels onto a Pillow image copy.
    
    Coordinates are assumed normalized [ymin, xmin, ymax, xmax] in [0.0, 1.0].
    """
    annotated = image.copy().convert("RGB")
    draw = ImageDraw.Draw(annotated)
    w, h = annotated.size

    for clue in clues:
        bbox = clue.bounding_box if hasattr(clue, "bounding_box") else clue.get("bounding_box")
        if not bbox or len(bbox) != 4:
            continue

        raw_cat = clue.category.value if hasattr(getattr(clue, "category", None), "value") else str(getattr(clue, "category", "other"))
        cat_key = raw_cat.lower()
        color = CATEGORY_COLORS.get(cat_key, (241, 196, 15))

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
        confidence = getattr(clue, "confidence", 1.0)
        label_text = f"{cat_key.upper()} ({int(confidence * 100)}%)"

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
            raw_cat = clue.category.value if hasattr(getattr(clue, "category", None), "value") else str(getattr(clue, "category", "other"))
            desc = getattr(clue, "description", "") or ""
            conf = getattr(clue, "confidence", 0.0)

            safe_cat = html.escape(str(raw_cat))
            safe_desc = html.escape(str(desc))

            with col:
                st.markdown(
                    f"""
                    <div style="background-color: #1a1e24; padding: 10px; border-radius: 8px; border-left: 4px solid #3498db; margin-bottom: 8px;">
                        <span style="font-size: 11px; color: #8892b0; text-transform: uppercase;">{safe_cat}</span>
                        <div style="font-size: 13px; font-weight: 600; color: #e6f1ff; margin-top: 4px;">{safe_desc}</div>
                        <div style="font-size: 12px; color: #64ffda; margin-top: 4px;">Confidence: {int(conf * 100)}%</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
    else:
        ctx.info("No visual forensic clues deconstructed.")
