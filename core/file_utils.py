"""File utilities for parsing prompt files."""

import os
from typing import NamedTuple

from .constants import PROMPT_DIR


class PromptEntry(NamedTuple):
    """A single prompt entry with tags and optional character name."""

    tags: str
    character_name: str


def get_available_txt_files() -> list[str]:
    """
    Get list of available TXT files in the prompt directory.

    Returns:
        List of TXT filenames. Returns ["No TXT files found"] if none exist.
    """
    try:
        txt_files = [f for f in os.listdir(PROMPT_DIR) if f.endswith(".txt")]
        return txt_files if txt_files else ["No TXT files found"]
    except OSError:
        return ["No TXT files found"]


def parse_prompt_file(file_path: str) -> list[PromptEntry]:
    """
    Parse a TXT prompt file into a list of PromptEntry objects.

    TXT format: tags<TAB>character_name (one per line)
    Lines without tabs are treated as tags-only entries.

    Args:
        file_path: Absolute path to the TXT file.

    Returns:
        List of PromptEntry tuples containing (tags, character_name).

    Raises:
        FileNotFoundError: If the file doesn't exist.
        IOError: If the file can't be read.
    """
    prompts: list[PromptEntry] = []

    with open(file_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            if "\t" in line:
                parts = line.split("\t", 1)
                tags = parts[0].strip()
                char_name = parts[1].strip() if len(parts) > 1 else ""
            else:
                tags = line
                char_name = ""

            prompts.append(PromptEntry(tags=tags, character_name=char_name))

    return prompts


def apply_suffix(tags: str, suffix: str, force_comma: bool = True) -> str:
    """
    Apply an aesthetic suffix to tags.

    Args:
        tags: The base tags string.
        suffix: The suffix to append.
        force_comma: If True, ensures suffix starts with a comma separator.

    Returns:
        Combined prompt string with suffix applied.
    """
    clean_tags = tags.strip().rstrip(",")

    if not suffix:
        return clean_tags

    suffix = suffix.strip()
    if force_comma and not suffix.startswith(","):
        suffix = ", " + suffix

    return clean_tags + suffix


def get_prompt_file_path(filename: str) -> str:
    """
    Get the full path to a prompt file.

    Args:
        filename: The prompt file name.

    Returns:
        Absolute path to the file.
    """
    return os.path.join(PROMPT_DIR, filename)
