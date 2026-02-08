"""
AnimePromptRedNote node for ComfyUI - FLUX/QWEN COMPATIBLE.
- Added 'target_model' switch.
- Added 'clean_tag' to strip weights (:1.2) and underscores.
- Fixes 'Tag Soup' for Flux generations.
"""

import random
import re
from typing import Any

from ..core.constants import (
    ACTIONS,
    BACKGROUNDS,
    CAMERA_EFFECTS,
    FLUX_CONNECTORS,
    FLUX_PREFIX,
    FLUX_STYLE_PREFIX,
    NEGATIVE_PRESETS,
    PRESETS,
    QUALITY_TAGS,
)
from ..core.file_utils import (
    get_available_txt_files,
    get_prompt_file_path,
    parse_prompt_file,
)
from ..core.rednote_utils import (
    REDNOTE_CHARACTER,
    REDNOTE_NEG_BASE,
    REDNOTE_NEG_SAFETY,
    REDNOTE_SAFETY_SHORTS,
    REDNOTE_STYLE,
    get_mood_prompt,
)


class AutoPromptRedNote:
    CATEGORY = "prompt/anime"
    FUNCTION = "generate_rednote"
    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("prompt", "negative", "character_name", "mood_tags")
    OUTPUT_IS_LIST = (True, False, True, True)

    @classmethod
    def INPUT_TYPES(cls) -> dict[str, Any]:
        txt_files = get_available_txt_files()
        default_style = (
            "style_names_v1.txt"
            if "style_names_v1.txt" in txt_files
            else (txt_files[0] if txt_files else "")
        )
        preset_list = ["RedNote"] + list(PRESETS.keys())

        return {
            "required": {
                "prompt_file": (
                    txt_files,
                    {"default": txt_files[0] if txt_files else ""},
                ),
                "style_file": (txt_files, {"default": default_style}),
                # --- NEW SWITCH ---
                "target_model": (
                    ["Illustrious (Tags)", "Flux/Qwen (Natural)"],
                    {"default": "Illustrious (Tags)"},
                ),
                "start_index": (
                    "INT",
                    {"default": 0, "min": 0, "max": 99999, "step": 1},
                ),
                "batch_size": ("INT", {"default": 1, "min": 1, "max": 1000, "step": 1}),
                "preset": (preset_list, {"default": "RedNote"}),
                "mode": (["sequential", "random"], {"default": "sequential"}),
                "mood_level": (
                    "FLOAT",
                    {
                        "default": 0.5,
                        "min": 0.0,
                        "max": 1.0,
                        "step": 0.1,
                        "display": "slider",
                    },
                ),
                "enable_style_lock": (
                    "BOOLEAN",
                    {"default": False},
                ),
                "random_action": ("BOOLEAN", {"default": True}),
                "random_background": ("BOOLEAN", {"default": True}),
                "random_camera": ("BOOLEAN", {"default": True}),
            },
            "optional": {
                "custom_positive": ("STRING", {"default": "", "multiline": True}),
                "custom_negative": ("STRING", {"default": "", "multiline": True}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xFFFFFFFFFFFFFFFF}),
            },
        }

    def clean_tag(self, text: str) -> str:
        """
        Aggressive cleaner for Flux/Natural Language.
        Removes: weights (:1.3), parens, '1girl', 'lora triggers', and fixes commas.
        """
        if not text:
            return ""

        # 1. Remove weights (e.g., :1.3, :0.5, :1)
        text = re.sub(r":\d+(\.\d+)?", "", text)

        # 2. Remove parenthesis completely
        text = text.replace("(", "").replace(")", "").replace("{", "").replace("}", "")

        # 3. Replace underscores with spaces
        text = text.replace("_", " ")

        # 4. Remove Booru-isms that sound robotic in sentences
        # Remove '1girl' (we already say 'A girl with...')
        text = re.sub(r"\b1girl\b", "", text, flags=re.IGNORECASE)
        # Remove 'lora triggers:' junk text (Case insensitive)
        text = re.sub(r"(?i)lora triggers?:?", "", text)

        # 5. Fix Comma Spacing (tag1,tag2 -> tag1, tag2)
        text = re.sub(r",\s*", ", ", text)

        # 6. Cleanup double spaces or trailing punctuation
        text = re.sub(r"\s+", " ", text).strip()
        text = text.strip(", ")  # Remove trailing commas

        return text

    def generate_rednote(
        self,
        prompt_file: str,
        style_file: str,
        target_model: str,
        start_index: int,
        batch_size: int,
        preset: str,
        mode: str,
        mood_level: float,
        enable_style_lock: bool,
        random_action: bool,
        random_background: bool,
        random_camera: bool,
        custom_positive: str = "",
        custom_negative: str = "",
        seed: int = 0,
    ) -> tuple[list[str], str, list[str], list[str]]:
        try:
            char_prompts = parse_prompt_file(get_prompt_file_path(prompt_file))
            style_prompts = parse_prompt_file(get_prompt_file_path(style_file))
        except Exception:
            return (["Error loading files"], "", ["Error"], ["Error"])

        if not char_prompts:
            return (["Error: No prompts"], "", ["Error"], ["Error"])

        # Setup
        target_list = char_prompts
        total_chars = len(target_list)
        total_styles = len(style_prompts) if style_prompts else 0
        prompts_out = []
        character_names_out = []
        mood_tags_out = []

        # Detect Model Mode
        is_flux = target_model == "Flux/Qwen (Natural)"

        random.seed(seed)

        for i in range(batch_size):
            current_index = start_index + i

            # Select Character
            if mode == "random":
                char_idx = random.randint(0, total_chars - 1)
            else:
                char_idx = current_index % total_chars
            entry = target_list[char_idx]

            # Select Style
            style_tag = ""
            if style_prompts:
                if enable_style_lock:
                    style_idx = current_index % total_styles
                else:
                    style_idx = random.randint(0, total_styles - 1)
                style_tag = style_prompts[style_idx].tags.strip().rstrip(",")

            # --- BRANCHING LOGIC ---

            if is_flux:
                # === FLUX / NATURAL LANGUAGE MODE ===

                # 1. Subject Sentence
                # Clean the character tags (remove :1.2, underscores)
                clean_char_tags = self.clean_tag(entry.tags)
                clean_char_name = self.clean_tag(entry.character_name)

                # "A high-quality anime illustration of [Name], a girl with [Tags]."
                prompt_text = (
                    f"{FLUX_PREFIX} {clean_char_name}, a girl with {clean_char_tags}."
                )

                # 2. Action Sentence
                if random_action:
                    act = random.choice(ACTIONS)
                    clean_act = self.clean_tag(act)
                    prompt_text += f" {FLUX_CONNECTORS['action']} {clean_act}."

                # 3. Background Sentence
                if random_background:
                    bg = random.choice(BACKGROUNDS)
                    clean_bg = self.clean_tag(bg)
                    prompt_text += f" {FLUX_CONNECTORS['background']} {clean_bg}."

                # 4. Mood/Expression Sentence
                mood_tags = get_mood_prompt(mood_level)
                if mood_tags:
                    clean_mood = self.clean_tag(mood_tags)
                    prompt_text += f" {FLUX_CONNECTORS['mood']} {clean_mood}."

                # 5. Style/Camera Sentence
                if style_tag or random_camera:
                    cam = random.choice(CAMERA_EFFECTS) if random_camera else ""
                    clean_style = self.clean_tag(style_tag)
                    clean_cam = self.clean_tag(cam)

                    if clean_style:
                        prompt_text += f" {FLUX_STYLE_PREFIX} {clean_style}."
                    if clean_cam:
                        prompt_text += f" {clean_cam}."

                if custom_positive:
                    # Clean the custom prompt too!
                    clean_custom = self.clean_tag(custom_positive)
                    prompt_text += f" {clean_custom}."

                prompts_out.append(prompt_text)

            else:
                # === ILLUSTRIOUS / TAG MODE (Your original logic) ===
                parts = []

                # Layer 1: Quality
                if preset == "RedNote":
                    parts.append(QUALITY_TAGS)
                    parts.append(REDNOTE_STYLE.lstrip(", ").strip())
                else:
                    preset_tags = PRESETS.get(preset, "")
                    if preset_tags:
                        parts.append(preset_tags)

                # Layer 2: Artist Style
                if style_tag:
                    parts.append(style_tag)

                # Layer 3: Character
                parts.append(entry.tags.strip().rstrip(","))

                # Layer 4: Action & Safety
                if random_action:
                    selected_action = random.choice(ACTIONS)
                    parts.append(selected_action)
                    if any(
                        x in selected_action for x in ["sitting", "hugging", "lying"]
                    ):
                        parts.append(REDNOTE_SAFETY_SHORTS)

                if random_background:
                    parts.append(random.choice(BACKGROUNDS))
                if random_camera:
                    parts.append(random.choice(CAMERA_EFFECTS))

                # Layer 5: Mood
                mood_tags = get_mood_prompt(mood_level)
                parts.append(mood_tags)

                # Layer 6: RedNote Enforcers
                if preset == "RedNote":
                    parts.append(REDNOTE_CHARACTER.lstrip(", ").strip())

                if custom_positive:
                    parts.append(custom_positive)

                final_prompt = ", ".join(filter(None, parts))
                prompts_out.append(final_prompt)

            character_names_out.append(entry.character_name)
            mood_tags_out.append(mood_tags)

        # 4. Construct Negative Prompt
        if is_flux:
            final_negative = ""  # Flux works best with empty negative
        else:
            negative_parts = []
            if preset == "RedNote":
                negative_parts.append(REDNOTE_NEG_BASE)
                negative_parts.append(REDNOTE_NEG_SAFETY)
            else:
                preset_neg = NEGATIVE_PRESETS.get(preset, "")
                if preset_neg:
                    negative_parts.append(preset_neg)
                else:
                    negative_parts.append(REDNOTE_NEG_BASE)

            if custom_negative.strip():
                negative_parts.append(custom_negative.strip())

            final_negative = ", ".join(filter(None, negative_parts))

        return (prompts_out, final_negative, character_names_out, mood_tags_out)
