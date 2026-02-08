"""Pytest configuration for ComfyUI custom node tests.

This conftest handles the import path setup needed because the root package
uses relative imports designed for ComfyUI's plugin loading system.
"""

import sys
from pathlib import Path

# Add project root to path so 'core' module can be imported directly
# without triggering the root __init__.py (which has ComfyUI-specific relative imports)
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
