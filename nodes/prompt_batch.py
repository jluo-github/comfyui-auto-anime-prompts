"""
AnimePromptBatch node for ComfyUI.

Outputs multiple prompts for batch image generation with dynamic actions, backgrounds, and camera effects.
Formula: Quality Tags + Character + Action + Background + Camera Effects
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


class AutoPromptBatch:
    """
    Output multiple prompts for batch image generation.

    Formula: Quality Tags + Character + Action + Background + Camera Effects

    TXT format: tags<TAB>character_name (one per line)

    Inputs:
        prompt_file: Select from available TXT files
        start_index: Starting index for batch
        batch_size: Number of prompts to output
        preset: Style preset for quality tags
        random_action: Add random actions to each prompt
        random_background: Add random backgrounds to each prompt
        random_camera: Add random camera effects to each prompt
        custom_positive: Your additional positive tags
        custom_negative: Your additional negative tags

    Outputs:
        prompts: List of prompt strings (for batch processing)
        negative: Combined negative prompt
    """

    CATEGORY = "prompt/anime"
    FUNCTION = "load_batch"
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("prompts", "negative")
    OUTPUT_IS_LIST = (True, False)

    @classmethod
    def INPUT_TYPES(cls) -> dict[str, Any]:
        """Define input parameters for the node."""
        txt_files = get_available_txt_files()

        return {
            "required": {
                "prompt_file": (
                    txt_files,
                    {"default": txt_files[0] if txt_files else ""},
                ),
                "start_index": (
                    "INT",
                    {"default": 0, "min": 0, "max": 99999, "step": 1},
                ),
                "batch_size": (
                    "INT",
                    {"default": 4, "min": 1, "max": 1000, "step": 1},
                ),
                "preset": (
                    list(PRESETS.keys()),
                    {"default": "standard"},
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

    def load_batch(
        self,
        prompt_file: str,
        start_index: int,
        batch_size: int,
        preset: str,
        random_action: bool,
        random_background: bool,
        random_camera: bool,
        custom_positive: str = "",
        custom_negative: str = "",
        seed: int = 0,
    ) -> tuple[list[str], str]:
        """
        Load a batch of prompts with dynamic generation.

        Formula: Quality Tags + Character + Action + Background + Camera + Custom

        Args:
            prompt_file: Name of the TXT file to load.
            start_index: Starting index for the batch.
            batch_size: Number of prompts to return.
            preset: Style preset for quality tags.
            random_action: Whether to add random actions.
            random_background: Whether to add random backgrounds.
            random_camera: Whether to add random camera effects.
            custom_positive: Your custom POSITIVE prompt.
            custom_negative: Your custom NEGATIVE prompt.
            seed: Random seed for reproducibility.

        Returns:
            Tuple containing (list of prompt strings, negative prompt).
        """
        file_path = get_prompt_file_path(prompt_file)

        try:
            prompts = parse_prompt_file(file_path)
        except FileNotFoundError:
            return ([f"Error: {prompt_file} not found"], "")
        except OSError as e:
            return ([f"Error: {e}"], "")

        if not prompts:
            return (["Error: No prompts found"], "")

        total = len(prompts)
        result: list[str] = []

        # Initialize random with seed
        random.seed(seed)

        # Get preset values
        preset_suffix = PRESETS.get(preset, DEFAULT_SUFFIX)
        preset_negative = NEGATIVE_PRESETS.get(preset, DEFAULT_NEGATIVE)

        # Clean preset suffix (remove leading comma)
        clean_preset = preset_suffix.lstrip(", ").strip() if preset_suffix else ""

        for i in range(batch_size):
            idx = (start_index + i) % total
            entry = prompts[idx]

            # Build prompt using formula:
            # Quality Tags + Character + Action + Background + Camera + Custom
            parts: list[str] = []

            # 1. Quality Tags
            if clean_preset:
                parts.append(clean_preset)

            # 2. Character tags
            character_tags = entry.tags.strip().rstrip(",")
            if character_tags:
                parts.append(character_tags)

            # 3. Random Action (different for each batch item)
            if random_action:
                action = random.choice(ACTIONS)
                parts.append(action)

            # 4. Random Background (different for each batch item)
            if random_background:
                background = random.choice(BACKGROUNDS)
                parts.append(background)

            # 5. Random Camera (different for each batch item)
            if random_camera:
                camera = random.choice(CAMERA_EFFECTS)
                parts.append(camera)

            # 6. Custom Positive
            if custom_positive.strip():
                custom = custom_positive.strip().lstrip(",").strip()
                if custom:
                    parts.append(custom)

            # Join all parts
            final_prompt = ", ".join(filter(None, parts))
            result.append(final_prompt)

        # Combine preset negative + custom_negative
        if custom_negative.strip():
            if preset_negative:
                final_negative = f"{preset_negative}, {custom_negative.strip()}"
            else:
                final_negative = custom_negative.strip()
        else:
            final_negative = preset_negative

        return (result, final_negative)
