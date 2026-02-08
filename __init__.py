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

# Conditional import for passport nodes (requires torch/diffusers)
from .nodes import _PASSPORT_NODES_AVAILABLE

if _PASSPORT_NODES_AVAILABLE:
    from .nodes import QwenPassportPhoto, QwenPassportPhotoUnload

__version__ = "1.0.0"

# Node mappings for ComfyUI registration
NODE_CLASS_MAPPINGS: dict[str, type] = {
    "AutoPromptLoader": AutoPromptLoader,
    "AutoPromptBatch": AutoPromptBatch,
    "AutoPromptCombiner": AutoPromptCombiner,
    "AutoPromptRedNote": AutoPromptRedNote,
    "SuffixEditor": SuffixEditor,
}

NODE_DISPLAY_NAME_MAPPINGS: dict[str, str] = {
    "AutoPromptLoader": "🎨 Auto Prompt Loader",
    "AutoPromptBatch": "🎨 Auto Prompt Batch",
    "AutoPromptCombiner": "🎨 Auto Prompt Combiner",
    "AutoPromptRedNote": "🎨 Auto Prompt RedNote",
    "SuffixEditor": "✨ Suffix Editor",
}

# Register passport nodes if available
if _PASSPORT_NODES_AVAILABLE:
    NODE_CLASS_MAPPINGS["QwenPassportPhoto"] = QwenPassportPhoto
    NODE_CLASS_MAPPINGS["QwenPassportPhotoUnload"] = QwenPassportPhotoUnload
    NODE_DISPLAY_NAME_MAPPINGS["QwenPassportPhoto"] = "📷 Qwen Passport Photo"
    NODE_DISPLAY_NAME_MAPPINGS["QwenPassportPhotoUnload"] = "📷 Qwen Passport Unload"

__all__ = [
    "NODE_CLASS_MAPPINGS",
    "NODE_DISPLAY_NAME_MAPPINGS",
    "__version__",
]
