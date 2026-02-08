"""Random selection utilities for prompt generation."""

from __future__ import annotations

import random
from typing import Sequence, TypeVar

from .constants import ACTIONS, BACKGROUNDS, CAMERA_EFFECTS

T = TypeVar("T")

# Keywords that trigger safety shorts (exposed leg positions)
SAFETY_TRIGGER_KEYWORDS: tuple[str, ...] = ("sitting", "hugging", "lying")


def pick_random(items: Sequence[T], rng: random.Random | None = None) -> T:
    """
    Pick a random item from a sequence.

    Args:
        items: Sequence of items to choose from.
        rng: Optional Random instance for deterministic selection.

    Returns:
        A randomly selected item from the sequence.
    """
    if rng:
        return rng.choice(items)
    return random.choice(items)


def pick_action(rng: random.Random | None = None) -> str:
    """Pick a random action from ACTIONS."""
    return pick_random(ACTIONS, rng)


def pick_background(rng: random.Random | None = None) -> str:
    """Pick a random background from BACKGROUNDS."""
    return pick_random(BACKGROUNDS, rng)


def pick_camera(rng: random.Random | None = None) -> str:
    """Pick a random camera effect from CAMERA_EFFECTS."""
    return pick_random(CAMERA_EFFECTS, rng)


def needs_safety_shorts(action: str) -> bool:
    """
    Check if an action requires safety shorts.

    Some actions (sitting, lying, hugging) may expose legs and require
    safety shorts to be added to the prompt for RedNote compliance.

    Args:
        action: The action string to check.

    Returns:
        True if the action contains trigger keywords.
    """
    return any(keyword in action for keyword in SAFETY_TRIGGER_KEYWORDS)
