"""
AnimePromptLoader node for ComfyUI.

Loads anime character prompts from TXT files with dynamic actions, backgrounds, and camera effects.
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
    PromptEntry,
    get_available_txt_files,
    get_prompt_file_path,
    parse_prompt_file,
)


class AutoPromptLoader:
    """
    Load anime character prompts with dynamic generation.

    Formula: Quality Tags + Character + Action + Background + Camera Effects

    TXT format: tags<TAB>character_name (one per line)

    Inputs:
        prompt_file: Select from available TXT files
        index: Prompt index for sequential mode
        mode: "sequential" or "random" selection
        preset: Style preset for quality tags
        random_action: Add a random action/pose
        random_background: Add a random background
        random_camera: Add random camera/lighting effects
        custom_positive: Your additional positive tags
        custom_negative: Your additional negative tags

    Outputs:
        prompt: The complete prompt string
        negative: Combined negative prompt
        character_name: Character name from file
        current_index: The selected prompt index
        total_prompts: Total number of prompts in file
    """

    CATEGORY = "prompt/anime"
    FUNCTION = "load_prompt"
    RETURN_TYPES = ("STRING", "STRING", "STRING", "INT", "INT")
    RETURN_NAMES = (
        "prompt",
        "negative",
        "character_name",
        "current_index",
        "total_prompts",
    )

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
                "index": (
                    "INT",
                    {
                        "default": 0,
                        "min": 0,
                        "max": 99999,
                        "step": 1,
                        "display": "number",
                    },
                ),
                "mode": (["sequential", "random"], {"default": "sequential"}),
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
                        "placeholder": "Your POSITIVE prompt (appended at end)",
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

    def load_prompt(
        self,
        prompt_file: str,
        index: int,
        mode: str,
        preset: str,
        random_action: bool,
        random_background: bool,
        random_camera: bool,
        custom_positive: str = "",
        custom_negative: str = "",
        seed: int = 0,
    ) -> tuple[str, str, str, int, int]:
        """
        Load a prompt with dynamic generation.

        Formula: Quality Tags + Character + Action + Background + Camera + Custom

        Args:
            prompt_file: Name of the TXT file to load.
            index: Index for sequential mode.
            mode: Selection mode ("sequential" or "random").
            preset: Style preset for quality tags.
            random_action: Whether to add a random action.
            random_background: Whether to add a random background.
            random_camera: Whether to add random camera effects.
            custom_positive: Your custom POSITIVE prompt.
            custom_negative: Your custom NEGATIVE prompt.
            seed: Random seed for reproducibility.

        Returns:
            Tuple of (prompt, negative, character_name, current_index, total_prompts).
        """
        file_path = get_prompt_file_path(prompt_file)

        try:
            prompts: list[PromptEntry] = parse_prompt_file(file_path)
        except FileNotFoundError:
            return (f"Error: {prompt_file} not found", "", "", 0, 0)
        except OSError as e:
            return (f"Error: {e}", "", "", 0, 0)

        if not prompts:
            return ("Error: No prompts found in file", "", "", 0, 0)

        total = len(prompts)

        # Initialize random with seed for reproducibility
        random.seed(seed)

        # Select prompt based on mode
        if mode == "random":
            selected_index = random.randint(0, total - 1)
        else:
            selected_index = index % total

        entry = prompts[selected_index]

        # Get preset values
        preset_suffix = PRESETS.get(preset, DEFAULT_SUFFIX)
        preset_negative = NEGATIVE_PRESETS.get(preset, DEFAULT_NEGATIVE)

        # Build the final prompt using the formula:
        # Quality Tags + Character + Action + Background + Camera + Custom
        parts: list[str] = []

        # 1. Quality Tags (from preset)
        if preset_suffix:
            # Remove leading comma and space from preset
            clean_preset = preset_suffix.lstrip(", ").strip()
            if clean_preset:
                parts.append(clean_preset)

        # 2. Character tags (from file)
        character_tags = entry.tags.strip().rstrip(",")
        if character_tags:
            parts.append(character_tags)

        # 3. Random Action
        if random_action:
            action = random.choice(ACTIONS)
            parts.append(action)

        # 4. Random Background
        if random_background:
            background = random.choice(BACKGROUNDS)
            parts.append(background)

        # 5. Random Camera Effects
        if random_camera:
            camera = random.choice(CAMERA_EFFECTS)
            parts.append(camera)

        # 6. Custom Positive
        if custom_positive.strip():
            custom = custom_positive.strip().lstrip(",").strip()
            if custom:
                parts.append(custom)

        # Join all parts with comma separator
        final_prompt = ", ".join(filter(None, parts))

        # Combine preset negative + custom_negative
        if custom_negative.strip():
            if preset_negative:
                final_negative = f"{preset_negative}, {custom_negative.strip()}"
            else:
                final_negative = custom_negative.strip()
        else:
            final_negative = preset_negative

        return (
            final_prompt,
            final_negative,
            entry.character_name,
            selected_index,
            total,
        )
