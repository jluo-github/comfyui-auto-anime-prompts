"""ComfyUI custom nodes for anime prompt loading."""

from .passport_photo import PassportPrompt, PassportResize, PassportTile
from .prompt_batch import AutoPromptBatch
from .prompt_combiner import AutoPromptCombiner
from .prompt_loader import AutoPromptLoader
from .prompt_rednote import AutoPromptRedNote
from .suffix_editor import SuffixEditor

__all__ = [
    "AutoPromptLoader",
    "AutoPromptBatch",
    "AutoPromptCombiner",
    "AutoPromptRedNote",
    "SuffixEditor",
    "PassportPrompt",
    "PassportResize",
    "PassportTile",
]
