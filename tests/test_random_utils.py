"""Unit tests for random selection utilities."""

import random

import pytest

# Imports handled by conftest.py

# Now import from core directly (not the root package)
from core.constants import ACTIONS, BACKGROUNDS, CAMERA_EFFECTS
from core.random_utils import (
    SAFETY_TRIGGER_KEYWORDS,
    needs_safety_shorts,
    pick_action,
    pick_background,
    pick_camera,
    pick_random,
)


class TestPickRandom:
    """Tests for the pick_random function."""

    def test_returns_item_from_list(self):
        """Test that returned item is from the provided list."""
        items = ["a", "b", "c"]
        result = pick_random(items, random.Random(42))
        assert result in items

    def test_deterministic_with_seed(self):
        """Test that same seed produces same result."""
        items = ["a", "b", "c"]
        result1 = pick_random(items, random.Random(42))
        result2 = pick_random(items, random.Random(42))
        assert result1 == result2

    def test_works_without_rng(self):
        """Test that function works without RNG instance (uses global)."""
        items = ["a", "b", "c"]
        result = pick_random(items)
        assert result in items


class TestPickActionBackgroundCamera:
    """Tests for specialized pick functions."""

    def test_pick_action_returns_action_from_list(self):
        """Test pick_action returns a valid action."""
        result = pick_action(random.Random(42))
        assert result in ACTIONS

    def test_pick_background_returns_background_from_list(self):
        """Test pick_background returns a valid background."""
        result = pick_background(random.Random(42))
        assert result in BACKGROUNDS

    def test_pick_camera_returns_camera_from_list(self):
        """Test pick_camera returns a valid camera effect."""
        result = pick_camera(random.Random(42))
        assert result in CAMERA_EFFECTS

    def test_deterministic_across_functions(self):
        """Test that seeded picks are deterministic across calls."""
        rng1 = random.Random(42)
        rng2 = random.Random(42)

        action1 = pick_action(rng1)
        bg1 = pick_background(rng1)
        cam1 = pick_camera(rng1)

        action2 = pick_action(rng2)
        bg2 = pick_background(rng2)
        cam2 = pick_camera(rng2)

        assert action1 == action2
        assert bg1 == bg2
        assert cam1 == cam2


class TestNeedsSafetyShorts:
    """Tests for the needs_safety_shorts function."""

    @pytest.mark.parametrize(
        "action",
        [
            "sitting on floor, hugging knees",
            "lying down, looking at sky",
            "hugging plushie, soft expression",
            "sitting at table, small cake",
        ],
    )
    def test_triggers_on_keywords(self, action: str):
        """Test that function returns True for actions with trigger keywords."""
        assert needs_safety_shorts(action) is True

    @pytest.mark.parametrize(
        "action",
        [
            "peace sign, winking",
            "running, dynamic pose",
            "reading book, focused",
            "jumping, mid-air",
        ],
    )
    def test_no_trigger_on_safe_actions(self, action: str):
        """Test that function returns False for safe actions."""
        assert needs_safety_shorts(action) is False

    def test_safety_keywords_constant(self):
        """Test that safety keywords constant has expected values."""
        assert "sitting" in SAFETY_TRIGGER_KEYWORDS
        assert "hugging" in SAFETY_TRIGGER_KEYWORDS
        assert "lying" in SAFETY_TRIGGER_KEYWORDS
