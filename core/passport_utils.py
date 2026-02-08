"""
Passport photo utilities for Qwen Image Edit integration.

Handles model loading, image resizing, and passport photo validation.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import torch
from PIL import Image

if TYPE_CHECKING:
    from diffusers import QwenImageEditPlusPipeline

logger = logging.getLogger(__name__)

# USA Passport Photo Specifications
# Standard: 2x2 inches, head height 1-1.375 inches (50-69% of image)
PASSPORT_SIZES: dict[str, tuple[int, int]] = {
    "2x2_inch_600dpi": (600, 600),  # CVS/Walgreens print quality
    "2x2_inch_300dpi": (300, 300),  # Standard print
    "digital_only": (800, 800),  # High-res square for digital use
}

DEFAULT_PASSPORT_PROMPT = (
    "Make a professional USA passport photo: pure white background, "
    "center the face and shoulders perfectly, neutral expression with "
    "both eyes open and mouth closed, even studio lighting with no shadows, "
    "high resolution, formal portrait style, head occupies 50-69% of image height"
)

# Singleton pipeline cache
_pipeline_cache: QwenImageEditPlusPipeline | None = None


def get_qwen_pipeline(
    device: str = "cuda",
    dtype: torch.dtype = torch.bfloat16,
) -> QwenImageEditPlusPipeline:
    """
    Load or retrieve cached Qwen Image Edit pipeline.

    Uses singleton pattern to avoid reloading the large model.

    Args:
        device: Target device ("cuda", "cpu", etc.)
        dtype: Model dtype (default: bfloat16 for memory efficiency)

    Returns:
        Loaded QwenImageEditPlusPipeline ready for inference.

    Raises:
        ImportError: If diffusers is not installed or outdated.
    """
    global _pipeline_cache

    if _pipeline_cache is not None:
        logger.info("Using cached Qwen pipeline")
        return _pipeline_cache

    try:
        from diffusers import QwenImageEditPlusPipeline
    except ImportError as e:
        raise ImportError(
            "QwenImageEditPlusPipeline not found. Install latest diffusers:\n"
            "pip install git+https://github.com/huggingface/diffusers"
        ) from e

    logger.info("Loading Qwen-Image-Edit-2511 pipeline...")
    pipeline = QwenImageEditPlusPipeline.from_pretrained(
        "Qwen/Qwen-Image-Edit-2511",
        torch_dtype=dtype,
    )
    pipeline.to(device)
    pipeline.set_progress_bar_config(disable=None)

    _pipeline_cache = pipeline
    logger.info("Pipeline loaded successfully")
    return pipeline


def unload_qwen_pipeline() -> bool:
    """
    Unload the cached pipeline to free memory.

    Returns:
        True if pipeline was unloaded, False if no pipeline was cached.
    """
    global _pipeline_cache

    if _pipeline_cache is not None:
        del _pipeline_cache
        _pipeline_cache = None
        torch.cuda.empty_cache()
        logger.info("Pipeline unloaded and CUDA cache cleared")
        return True
    return False


def resize_to_passport(
    image: Image.Image,
    size_key: str = "2x2_inch_600dpi",
) -> Image.Image:
    """
    Resize image to passport photo dimensions.

    Args:
        image: PIL Image to resize
        size_key: Key from PASSPORT_SIZES dict

    Returns:
        Resized PIL Image with passport dimensions.

    Raises:
        ValueError: If size_key is not valid.
    """
    if size_key not in PASSPORT_SIZES:
        valid_keys = ", ".join(PASSPORT_SIZES.keys())
        raise ValueError(f"Invalid size_key '{size_key}'. Valid options: {valid_keys}")

    target_size = PASSPORT_SIZES[size_key]

    # Use high-quality Lanczos resampling
    resized = image.resize(target_size, Image.Resampling.LANCZOS)

    return resized


def validate_passport_dimensions(image: Image.Image) -> dict[str, bool | str]:
    """
    Validate if image meets USA passport photo requirements.

    Args:
        image: PIL Image to validate

    Returns:
        Dictionary with validation results:
        - is_square: Whether image is square
        - meets_min_size: Whether image meets minimum 300px
        - meets_print_size: Whether image meets 600px for CVS print
        - recommendation: String with suggested action
    """
    width, height = image.size

    is_square = width == height
    meets_min_size = min(width, height) >= 300
    meets_print_size = min(width, height) >= 600

    if meets_print_size and is_square:
        recommendation = "Ready for CVS/Walgreens printing"
    elif meets_min_size and is_square:
        recommendation = "Suitable for digital use, may be low quality for print"
    elif is_square:
        recommendation = "Image too small, may appear pixelated when printed"
    else:
        recommendation = "Image is not square, needs cropping"

    return {
        "is_square": is_square,
        "meets_min_size": meets_min_size,
        "meets_print_size": meets_print_size,
        "recommendation": recommendation,
        "dimensions": f"{width}x{height}",
    }


def pil_to_tensor(image: Image.Image) -> torch.Tensor:
    """
    Convert PIL Image to ComfyUI-compatible tensor.

    ComfyUI expects: (batch, height, width, channels) in float32 [0, 1]

    Args:
        image: PIL Image in RGB mode

    Returns:
        Tensor with shape (1, H, W, 3) in float32
    """
    import numpy as np

    if image.mode != "RGB":
        image = image.convert("RGB")

    # Convert to numpy array and normalize to [0, 1]
    arr = np.array(image).astype(np.float32) / 255.0

    # Add batch dimension: (H, W, C) -> (1, H, W, C)
    tensor = torch.from_numpy(arr).unsqueeze(0)

    return tensor


def tensor_to_pil(tensor: torch.Tensor) -> Image.Image:
    """
    Convert ComfyUI tensor to PIL Image.

    Args:
        tensor: Tensor with shape (batch, H, W, C) or (H, W, C)

    Returns:
        PIL Image in RGB mode
    """
    import numpy as np

    # Handle batch dimension
    if tensor.dim() == 4:
        tensor = tensor[0]  # Take first image from batch

    # Convert to numpy and scale to [0, 255]
    arr = tensor.cpu().numpy()
    arr = (arr * 255).clip(0, 255).astype(np.uint8)

    return Image.fromarray(arr, mode="RGB")
