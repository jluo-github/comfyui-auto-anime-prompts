"""
AnimePromptCombiner node for ComfyUI.

Combines characters from one file with styles from another file using nested loops.
Formula: Quality Tags + Style + Character + Action + Background + Camera Effects
"""

import random
from typing import Any

from ..core.constants import (
    ACTIONS,
    BACKGROUNDS,
    CAMERA_EFFECTS,
    DEFAULT_NEGATIVE,
    DEFAULT_SUFFIX,
    NEGATIVE_PRESETS,
    PRESETS,
)
from ..core.file_utils import (
    get_available_txt_files,
    get_prompt_file_path,
    parse_prompt_file,
)


class AutoPromptCombiner:
    """
    Combine characters with styles in nested loops.

    Formula: Quality Tags + Style + Character + Action + Background + Camera Effects

    For each character, iterate through all selected styles:
        for char in characters[start:start+count]:
            for style in styles[start:start+count]:
                prompt = quality + style + char + action + bg + camera

    Inputs:
        character_file: TXT file with character prompts
        style_file: TXT file with style prompts
        char_start_index: Starting index for characters
        style_start_index: Starting index for styles
        char_count: Number of characters to use
        style_count: Number of styles to use per character
        preset: Style preset for quality tags
        random_action/background/camera: Dynamic generation options

    Outputs:
        prompts: List of combined prompts (char_count × style_count)
        negative: Combined negative prompt
    """

    CATEGORY = "prompt/anime"
    FUNCTION = "combine_prompts"
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("prompts", "negative")
    OUTPUT_IS_LIST = (True, False)

    # Maximum prompts to prevent accidental massive batches
    MAX_TOTAL_PROMPTS = 100

    @classmethod
    def INPUT_TYPES(cls) -> dict[str, Any]:
        """Define input parameters for the node."""
        txt_files = get_available_txt_files()

        return {
            "required": {
                "character_file": (
                    txt_files,
                    {"default": txt_files[0] if txt_files else ""},
                ),
                "style_file": (
                    txt_files,
                    {
                        "default": (
                            "style_names_v1.txt"
                            if "style_names_v1.txt" in txt_files
                            else (
                                txt_files[1]
                                if len(txt_files) > 1
                                else txt_files[0]
                                if txt_files
                                else ""
                            )
                        )
                    },
                ),
                "char_start_index": (
                    "INT",
                    {"default": 0, "min": 0, "max": 99999, "step": 1},
                ),
                "style_start_index": (
                    "INT",
                    {"default": 0, "min": 0, "max": 99999, "step": 1},
                ),
                "char_count": (
                    "INT",
                    {"default": 1, "min": 1, "max": 100, "step": 1},
                ),
                "style_count": (
                    "INT",
                    {"default": 1, "min": 1, "max": 100, "step": 1},
                ),
                "preset": (
                    list(PRESETS.keys()),
                    {"default": "dynamic"},
                ),
                "random_action": ("BOOLEAN", {"default": True}),
                "random_background": ("BOOLEAN", {"default": True}),
                "random_camera": ("BOOLEAN", {"default": True}),
            },
            "optional": {
                "custom_positive": (
                    "STRING",
                    {
                        "default": "",
                        "multiline": True,
                        "placeholder": "Your POSITIVE prompt (appended to each)",
                    },
                ),
                "custom_negative": (
                    "STRING",
                    {
                        "default": "",
                        "multiline": True,
                        "placeholder": "Your NEGATIVE prompt (combined with preset)",
                    },
                ),
                "seed": (
                    "INT",
                    {
                        "default": 0,
                        "min": 0,
                        "max": 0xFFFFFFFFFFFFFFFF,
                        "display": "number",
                    },
                ),
            },
        }

    def combine_prompts(
        self,
        character_file: str,
        style_file: str,
        char_start_index: int,
        style_start_index: int,
        char_count: int,
        style_count: int,
        preset: str,
        random_action: bool,
        random_background: bool,
        random_camera: bool,
        custom_positive: str = "",
        custom_negative: str = "",
        seed: int = 0,
    ) -> tuple[list[str], str]:
        """
        Combine characters with styles using nested loops.

        Formula: Quality Tags + Style + Character + Action + Background + Camera + Custom

        Returns:
            Tuple of (list of prompts, negative prompt).
        """
        # Load character file
        char_path = get_prompt_file_path(character_file)
        try:
            characters = parse_prompt_file(char_path)
        except (FileNotFoundError, OSError) as e:
            return ([f"Error loading characters: {e}"], "")

        # Load style file
        style_path = get_prompt_file_path(style_file)
        try:
            styles = parse_prompt_file(style_path)
        except (FileNotFoundError, OSError) as e:
            return ([f"Error loading styles: {e}"], "")

        if not characters:
            return (["Error: No characters found"], "")
        if not styles:
            return (["Error: No styles found"], "")

        # Limit total prompts
        total_prompts = char_count * style_count
        if total_prompts > self.MAX_TOTAL_PROMPTS:
            return (
                [
                    f"Error: Total prompts ({total_prompts}) exceeds max ({self.MAX_TOTAL_PROMPTS})"
                ],
                "",
            )

        # Initialize random
        random.seed(seed)

        # Get preset values
        preset_suffix = PRESETS.get(preset, DEFAULT_SUFFIX)
        preset_negative = NEGATIVE_PRESETS.get(preset, DEFAULT_NEGATIVE)
        clean_preset = preset_suffix.lstrip(", ").strip() if preset_suffix else ""

        result: list[str] = []

        # Nested loop: for each character, iterate through styles
        for char_offset in range(char_count):
            char_idx = (char_start_index + char_offset) % len(characters)
            char = characters[char_idx]

            for style_offset in range(style_count):
                style_idx = (style_start_index + style_offset) % len(styles)
                style = styles[style_idx]

                # Build prompt: Quality + Style + Character + Action + Bg + Camera
                parts: list[str] = []

                # 1. Quality Tags (from preset)
                if clean_preset:
                    parts.append(clean_preset)

                # 2. Style tags (from style file)
                style_tags = style.tags.strip().rstrip(",")
                if style_tags:
                    parts.append(style_tags)

                # 3. Character tags (from character file)
                char_tags = char.tags.strip().rstrip(",")
                if char_tags:
                    parts.append(char_tags)

                # 4. Random Action
                if random_action:
                    parts.append(random.choice(ACTIONS))

                # 5. Random Background
                if random_background:
                    parts.append(random.choice(BACKGROUNDS))

                # 6. Random Camera
                if random_camera:
                    parts.append(random.choice(CAMERA_EFFECTS))

                # 7. Custom Positive
                if custom_positive.strip():
                    custom = custom_positive.strip().lstrip(",").strip()
                    if custom:
                        parts.append(custom)

                final_prompt = ", ".join(filter(None, parts))
                result.append(final_prompt)

        # Combine negatives
        if custom_negative.strip():
            if preset_negative:
                final_negative = f"{preset_negative}, {custom_negative.strip()}"
            else:
                final_negative = custom_negative.strip()
        else:
            final_negative = preset_negative

        return (result, final_negative)
