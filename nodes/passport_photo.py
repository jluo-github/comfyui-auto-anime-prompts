"""
QwenPassportPhoto node for ComfyUI.

Uses Qwen-Image-Edit-2511 to transform selfies into USA passport-compliant photos.
"""

from __future__ import annotations

from typing import Any

import torch

from ..core.passport_utils import (
    DEFAULT_PASSPORT_PROMPT,
    PASSPORT_SIZES,
    get_qwen_pipeline,
    pil_to_tensor,
    resize_to_passport,
    tensor_to_pil,
    unload_qwen_pipeline,
    validate_passport_dimensions,
)


class QwenPassportPhoto:
    """
    Transform selfies into USA passport-compliant photos using Qwen-Image-Edit-2511.

    This node uses AI to:
    - Replace background with pure white
    - Center face and shoulders properly
    - Adjust lighting for even, shadow-free appearance
    - Resize to standard passport dimensions (2x2 inches)

    USA Passport Requirements:
    - 2x2 inches (51x51 mm)
    - White background
    - Head size: 1 to 1-3/8 inches (25-35mm)
    - Neutral expression, eyes open, mouth closed

    Inputs:
        image: Your selfie or portrait photo
        prompt: Edit instructions (uses optimized default)
        output_size: Target dimensions for printing
        num_inference_steps: More steps = better quality, slower
        true_cfg_scale: Prompt adherence strength
        seed: For reproducible results

    Outputs:
        IMAGE: Passport-ready photo
        info: Dimensions and compliance notes
    """

    CATEGORY = "image/passport"
    FUNCTION = "generate_passport_photo"
    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("image", "info")

    @classmethod
    def INPUT_TYPES(cls) -> dict[str, Any]:
        """Define input parameters for the node."""
        return {
            "required": {
                "image": ("IMAGE",),
                "prompt": (
                    "STRING",
                    {
                        "default": DEFAULT_PASSPORT_PROMPT,
                        "multiline": True,
                    },
                ),
                "output_size": (
                    list(PASSPORT_SIZES.keys()),
                    {"default": "2x2_inch_600dpi"},
                ),
                "num_inference_steps": (
                    "INT",
                    {
                        "default": 40,
                        "min": 20,
                        "max": 80,
                        "step": 5,
                    },
                ),
                "true_cfg_scale": (
                    "FLOAT",
                    {
                        "default": 4.0,
                        "min": 1.0,
                        "max": 10.0,
                        "step": 0.5,
                    },
                ),
                "seed": (
                    "INT",
                    {
                        "default": 0,
                        "min": 0,
                        "max": 0xFFFFFFFFFFFFFFFF,
                    },
                ),
            },
        }

    def generate_passport_photo(
        self,
        image: torch.Tensor,
        prompt: str,
        output_size: str,
        num_inference_steps: int,
        true_cfg_scale: float,
        seed: int,
    ) -> tuple[torch.Tensor, str]:
        """
        Generate a passport photo from input image.

        Args:
            image: Input image tensor (batch, H, W, C)
            prompt: Edit instructions for the model
            output_size: Target size key from PASSPORT_SIZES
            num_inference_steps: Diffusion steps
            true_cfg_scale: CFG scale for prompt adherence
            seed: Random seed for reproducibility

        Returns:
            Tuple of (output_image_tensor, info_string)
        """
        # Convert ComfyUI tensor to PIL
        pil_image = tensor_to_pil(image)

        # Load or get cached pipeline
        pipeline = get_qwen_pipeline()

        # Prepare inputs
        inputs = {
            "image": [pil_image],
            "prompt": prompt,
            "generator": torch.manual_seed(seed),
            "true_cfg_scale": true_cfg_scale,
            "negative_prompt": " ",
            "num_inference_steps": num_inference_steps,
            "guidance_scale": 1.0,
            "num_images_per_prompt": 1,
        }

        # Run inference
        with torch.inference_mode():
            output = pipeline(**inputs)

        result_pil = output.images[0]

        # Resize to passport dimensions
        resized = resize_to_passport(result_pil, output_size)

        # Validate final output
        validation = validate_passport_dimensions(resized)

        # Build info string
        target_dims = PASSPORT_SIZES[output_size]
        info = (
            f"Output: {validation['dimensions']}\n"
            f"Target: {target_dims[0]}x{target_dims[1]}px ({output_size})\n"
            f"Status: {validation['recommendation']}\n"
            f"Steps: {num_inference_steps}, CFG: {true_cfg_scale}, Seed: {seed}"
        )

        # Convert back to ComfyUI tensor
        result_tensor = pil_to_tensor(resized)

        return (result_tensor, info)


class QwenPassportPhotoUnload:
    """
    Unload Qwen-Image-Edit-2511 model from memory.

    Use this node to free GPU memory when you're done generating passport photos.
    Connect to any workflow to trigger unloading.

    Outputs:
        status: Message confirming unload status
    """

    CATEGORY = "image/passport"
    FUNCTION = "unload_model"
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("status",)

    @classmethod
    def INPUT_TYPES(cls) -> dict[str, Any]:
        """Define input parameters for the node."""
        return {
            "required": {
                "trigger": ("*", {}),  # Accept any input to trigger
            },
        }

    def unload_model(self, trigger: Any) -> tuple[str]:
        """
        Unload the Qwen pipeline from memory.

        Args:
            trigger: Any input to trigger the unload

        Returns:
            Tuple with status message
        """
        was_unloaded = unload_qwen_pipeline()

        if was_unloaded:
            return ("Qwen-Image-Edit-2511 unloaded. GPU memory freed.",)
        return ("No model was loaded.",)
