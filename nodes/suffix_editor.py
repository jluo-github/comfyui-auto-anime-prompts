"""
SuffixEditor node for ComfyUI.

Utility node to create and preview aesthetic suffixes with presets.
Outputs both positive and negative prompt suffixes.
"""

from typing import Any

from ..core.constants import DEFAULT_NEGATIVE, NEGATIVE_PRESETS, PRESETS

# Safe fallback preset key
_DEFAULT_PRESET_KEY = "standard"


class SuffixEditor:
    """Create and preview aesthetic suffixes with style presets."""

    CATEGORY = "prompt/anime"
    FUNCTION = "get_suffix"
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("suffix", "negative")

    @classmethod
    def INPUT_TYPES(cls) -> dict[str, Any]:
        """Define input parameters for the node."""
        return {
            "required": {
                "preset": (list(PRESETS.keys()), {"default": "standard"}),
                "use_custom": ("BOOLEAN", {"default": False}),
            },
            "optional": {
                "custom_suffix": (
                    "STRING",
                    {
                        "default": "",
                        "multiline": True,
                        "placeholder": "Custom positive suffix",
                    },
                ),
                "custom_negative": (
                    "STRING",
                    {
                        "default": "",
                        "multiline": True,
                        "placeholder": "Custom negative prompt",
                    },
                ),
            },
        }

    def get_suffix(
        self,
        preset: str,
        use_custom: bool,
        custom_suffix: str = "",
        custom_negative: str = "",
    ) -> tuple[str, str]:
        """
        Return the selected preset or custom suffix and negative prompt.

        Args:
            preset: Name of the preset to use.
            use_custom: If True, use custom values instead of preset.
            custom_suffix: Custom positive suffix string.
            custom_negative: Custom negative prompt string.

        Returns:
            Tuple containing (positive_suffix, negative_prompt).
        """
        if use_custom:
            suffix = custom_suffix.strip() or PRESETS.get(
                preset, PRESETS.get(_DEFAULT_PRESET_KEY, "")
            )
            negative = custom_negative.strip() or DEFAULT_NEGATIVE
            return (suffix, negative)

        # Use preset values with safe fallback for legacy workflows
        positive = PRESETS.get(preset, PRESETS.get(_DEFAULT_PRESET_KEY, ""))
        negative = NEGATIVE_PRESETS.get(preset, DEFAULT_NEGATIVE)

        return (positive, negative)
