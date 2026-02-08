"""Unit tests for core file utilities."""

import os

# We need to set up the path before importing
import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.file_utils import PromptEntry, apply_suffix, parse_prompt_file


class TestApplySuffix:
    """Tests for the apply_suffix function."""

    def test_basic_suffix(self):
        """Test basic suffix application."""
        result = apply_suffix("tag1, tag2", ", suffix")
        assert result == "tag1, tag2, suffix"

    def test_adds_comma_when_missing(self):
        """Test that comma is added when suffix doesn't start with one."""
        result = apply_suffix("tag1, tag2", "suffix")
        assert result == "tag1, tag2, suffix"

    def test_strips_trailing_comma_from_tags(self):
        """Test that trailing commas are removed from tags."""
        result = apply_suffix("tag1, tag2,", ", suffix")
        assert result == "tag1, tag2, suffix"

    def test_empty_suffix(self):
        """Test with empty suffix."""
        result = apply_suffix("tag1, tag2", "")
        assert result == "tag1, tag2"

    def test_whitespace_handling(self):
        """Test whitespace is properly stripped."""
        result = apply_suffix("  tag1, tag2  ", "  , suffix  ")
        assert result == "tag1, tag2, suffix"


class TestParsePromptFile:
    """Tests for the parse_prompt_file function."""

    def test_parse_with_tab(self):
        """Test parsing lines with tab separator."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False, encoding="utf-8"
        ) as f:
            f.write("tag1, tag2\tCharacter Name\n")
            f.write("tag3, tag4\tAnother Character\n")
            temp_path = f.name

        try:
            prompts = parse_prompt_file(temp_path)
            assert len(prompts) == 2
            assert prompts[0] == PromptEntry(
                tags="tag1, tag2", character_name="Character Name"
            )
            assert prompts[1] == PromptEntry(
                tags="tag3, tag4", character_name="Another Character"
            )
        finally:
            os.unlink(temp_path)

    def test_parse_without_tab(self):
        """Test parsing lines without tab separator."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False, encoding="utf-8"
        ) as f:
            f.write("tag1, tag2, tag3\n")
            temp_path = f.name

        try:
            prompts = parse_prompt_file(temp_path)
            assert len(prompts) == 1
            assert prompts[0] == PromptEntry(tags="tag1, tag2, tag3", character_name="")
        finally:
            os.unlink(temp_path)

    def test_skip_empty_lines(self):
        """Test that empty lines are skipped."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False, encoding="utf-8"
        ) as f:
            f.write("tag1\n")
            f.write("\n")
            f.write("   \n")
            f.write("tag2\n")
            temp_path = f.name

        try:
            prompts = parse_prompt_file(temp_path)
            assert len(prompts) == 2
        finally:
            os.unlink(temp_path)

    def test_file_not_found(self):
        """Test FileNotFoundError is raised for missing files."""
        with pytest.raises(FileNotFoundError):
            parse_prompt_file("/nonexistent/file.txt")
