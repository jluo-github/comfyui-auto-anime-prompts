"""ComfyUI custom nodes for anime prompt loading."""

from .prompt_batch import AutoPromptBatch
from .prompt_combiner import AutoPromptCombiner
from .prompt_loader import AutoPromptLoader
from .prompt_rednote import AutoPromptRedNote
from .suffix_editor import SuffixEditor

# Passport photo nodes require torch/diffusers - only import if available
try:
    from .passport_photo import QwenPassportPhoto, QwenPassportPhotoUnload

    _PASSPORT_NODES_AVAILABLE = True
except ImportError:
    # torch/diffusers not installed (e.g., in test environment)
    QwenPassportPhoto = None  # type: ignore[misc, assignment]
    QwenPassportPhotoUnload = None  # type: ignore[misc, assignment]
    _PASSPORT_NODES_AVAILABLE = False

__all__ = [
    "AutoPromptLoader",
    "AutoPromptBatch",
    "AutoPromptCombiner",
    "AutoPromptRedNote",
    "SuffixEditor",
]

if _PASSPORT_NODES_AVAILABLE:
    __all__.extend(["QwenPassportPhoto", "QwenPassportPhotoUnload"])
