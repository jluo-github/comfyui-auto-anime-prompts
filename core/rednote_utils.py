"""
RedNote (XiaoHongShu) Aesthetic Utilities - ARCHITECT PURE COMBINER MATCH.
"""

from typing import Final

# --- 1. CLEAN NEGATIVE PROMPT ---
# Base Quality Negatives (Can be swapped if preset has own negatives)
REDNOTE_NEG_BASE: Final[str] = (
    "worst quality, low quality, normal quality, lowres, anatomical nonsense, conjoined, bad ai-generated, plastic hair, plastic skin, "
    "artistic error, bad anatomy, bad hands, missing fingers, extra digit, fewer digits, "
    "cropped, jpeg artifacts, signature, watermark, username, blurry, artist name, "
    "text, error, 3d, realistic, photo, real life, bad proportions, muscle, muscular"
)

# Safety/NSFW Negatives (ALWAYS APPLIED)
REDNOTE_NEG_SAFETY: Final[str] = (
    "(large breasts:1.5), (big breasts:1.5), (cleavage:1.4), nsfw, nude, "
    "(nipples:1.5), (visible nipples:1.4), (areola:1.5), "
    "(see-through:1.4), (transparent:1.4), (child:1.4), (loli:1.4), "
    "(rating_explicit:1.3), (rating_questionable:1.3), "
    "(mascara:1.5), (bandaid:1.5), (bandage:1.5), (messy makeup:1.3)"
)

# Combined for backward compatibility
REDNOTE_NEGATIVE_SUFFIX: Final[str] = REDNOTE_NEG_BASE + ", " + REDNOTE_NEG_SAFETY

# --- 2. POSITIVE SUFFIX (Pure & Safe) ---
# NO STYLE WORDS. Just Body + Clothes + Safety.
# This allows the "Dynamic Engine" from the Node to control the art style 100%.

# Distinct Style Tags (Can be swapped out)
REDNOTE_STYLE: Final[str] = (
    ", dreamy atmosphere, ethereal, delicate, 4k, high resolution, ultra-detailed, scenery"
)

# Character/Safety Tags (Always kept)
REDNOTE_CHARACTER: Final[str] = (
    "(solo:1.5), (perfect cute face:1.4), (beautiful detailed eyes:1.3), (sparkling eyes:1.3), "
    "(flat chest:1.2), (small breasts:1.2), (mature:1.2), (skinny:1.3), "
    "messy hair, big fluffy hair, big fluffy curls, large ribbons, fluffy volume, "
    "rating_safe"
)

# Combined for backward compatibility
REDNOTE_POSITIVE_SUFFIX: Final[str] = REDNOTE_STYLE + REDNOTE_CHARACTER

# Safety Shorts for Action Logic
REDNOTE_SAFETY_SHORTS: Final[str] = "(pretty white lace safety shorts:1.3)"


# --- 3. MOOD PROMPTS ---
def get_mood_prompt(level: float) -> str:
    if level < 0.2:
        return "(slight smile:1.2), (gentle expression:1.1), (obedient:1.1), demure"
    elif level < 0.4:
        return "(expressionless:1.3), (neutral face:1.2), (serious:1.2), (looking down:1.1)"
    elif level < 0.6:
        return "(stoned face:1.3), (hollow gaze:1.1), (dissociation:1.1)"
    elif level < 0.8:
        return "(annoyed expression:1.3), (glaring:1.2), (displeased:1.2)"
    else:
        return "(stubborn:1.5), (pouting:1.4), (grumpy:1.4), (angry:1.2), (looking away:1.1)"


# --- 4. COMPATIBILITY STUBS ---
def get_random_palette() -> dict[str, str]:
    return {"bg": "", "clothes": ""}


def get_weighted_color_tag(tag: str) -> str:
    return tag


def apply_rednote_style(positive: str, negative: str) -> tuple[str, str]:
    return positive + REDNOTE_POSITIVE_SUFFIX, negative + ", " + REDNOTE_NEGATIVE_SUFFIX


def filter_characters(*args, **kwargs):
    return []


AESTHETIC_KEYWORDS = []
EXCLUDE_KEYWORDS = []

if __name__ == "__main__":
    pass
