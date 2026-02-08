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
    SuffixEditor,
)

__version__ = "1.0.0"

# Node mappings for ComfyUI registration
NODE_CLASS_MAPPINGS = {
    "AutoPromptLoader": AutoPromptLoader,
    "AutoPromptBatch": AutoPromptBatch,
    "AutoPromptCombiner": AutoPromptCombiner,
    "AutoPromptRedNote": AutoPromptRedNote,
    "SuffixEditor": SuffixEditor,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "AutoPromptLoader": "🎨 Auto Prompt Loader",
    "AutoPromptBatch": "🎨 Auto Prompt Batch",
    "AutoPromptCombiner": "🎨 Auto Prompt Combiner",
    "AutoPromptRedNote": "🎨 Auto Prompt RedNote",
    "SuffixEditor": "✨ Suffix Editor",
}

__all__ = [
    "NODE_CLASS_MAPPINGS",
    "NODE_DISPLAY_NAME_MAPPINGS",
    "__version__",
]
