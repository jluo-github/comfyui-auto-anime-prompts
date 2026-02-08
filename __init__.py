"""
ComfyUI Custom Node: Anime Prompt Loader

Loads prompts from TXT files and adds aesthetic suffixes for
high-fidelity anime image generation.

Author: JL
License: MIT
"""

from .nodes import (
    AutoPromptBatch,
    AutoPromptCombiner,
    AutoPromptLoader,
    AutoPromptRedNote,
    PassportPrompt,
    PassportResize,
    PassportTile,
    SuffixEditor,
)

__version__ = "1.1.0"

# Node mappings for ComfyUI registration
NODE_CLASS_MAPPINGS: dict[str, type] = {
    "AutoPromptLoader": AutoPromptLoader,
    "AutoPromptBatch": AutoPromptBatch,
    "AutoPromptCombiner": AutoPromptCombiner,
    "AutoPromptRedNote": AutoPromptRedNote,
    "SuffixEditor": SuffixEditor,
    "PassportPrompt": PassportPrompt,
    "PassportResize": PassportResize,
    "PassportTile": PassportTile,
}

NODE_DISPLAY_NAME_MAPPINGS: dict[str, str] = {
    "AutoPromptLoader": "🎨 Auto Prompt Loader",
    "AutoPromptBatch": "🎨 Auto Prompt Batch",
    "AutoPromptCombiner": "🎨 Auto Prompt Combiner",
    "AutoPromptRedNote": "🎨 Auto Prompt RedNote",
    "SuffixEditor": "✨ Suffix Editor",
    "PassportPrompt": "📷 Passport Prompt",
    "PassportResize": "📷 Passport Resize",
    "PassportTile": "📷 Passport Tile (4x6)",
}

__all__ = [
    "NODE_CLASS_MAPPINGS",
    "NODE_DISPLAY_NAME_MAPPINGS",
    "__version__",
]
