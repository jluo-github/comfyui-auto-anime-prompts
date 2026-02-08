"""
Passport photo nodes for ComfyUI (GGUF/Native workflow compatible).

These nodes work with any ComfyUI image workflow - no special dependencies.
Designed for use with Qwen-Image-Edit-2511 GGUF workflow.
"""

from __future__ import annotations

from typing import Any

from PIL import Image
import numpy as np
import torch


# USA Passport Photo Specifications
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


class PassportPrompt:
    """
    Generate optimized prompts for USA passport photo editing.

    Use with Qwen-Image-Edit-2511 or similar image editing models.
    Connect the output to your CLIP Text Encode (Positive Prompt) node.

    Outputs:
        prompt: Optimized passport photo generation prompt
        negative: Minimal negative prompt (empty for Qwen)
    """

    CATEGORY = "prompt/passport"
    FUNCTION = "get_prompt"
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("prompt", "negative")

    @classmethod
    def INPUT_TYPES(cls) -> dict[str, Any]:
        """Define input parameters for the node."""
        return {
            "required": {
                "use_default_prompt": ("BOOLEAN", {"default": True}),
            },
            "optional": {
                "custom_prompt": (
                    "STRING",
                    {
                        "default": "",
                        "multiline": True,
                        "placeholder": "Custom prompt (leave empty to use default)",
                    },
                ),
                "append_to_default": (
                    "STRING",
                    {
                        "default": "",
                        "multiline": True,
                        "placeholder": "Additional tags to append to default prompt",
                    },
                ),
            },
        }

    def get_prompt(
        self,
        use_default_prompt: bool,
        custom_prompt: str = "",
        append_to_default: str = "",
    ) -> tuple[str, str]:
        """
        Generate passport photo prompt.

        Args:
            use_default_prompt: Use the optimized default passport prompt
            custom_prompt: Full custom prompt (overrides default if provided)
            append_to_default: Additional tags to append to default prompt

        Returns:
            Tuple of (positive_prompt, negative_prompt)
        """
        if not use_default_prompt and custom_prompt.strip():
            prompt = custom_prompt.strip()
        else:
            prompt = DEFAULT_PASSPORT_PROMPT
            if append_to_default.strip():
                prompt = f"{prompt}, {append_to_default.strip()}"

        # Qwen models work best with empty/minimal negative
        negative = ""

        return (prompt, negative)


class PassportResize:
    """
    Resize images to USA passport photo dimensions.

    Standard CVS/Walgreens print size: 600x600 pixels (2x2 inches at 300 DPI)

    Inputs:
        image: Any image to resize
        output_size: Target passport dimensions

    Outputs:
        IMAGE: Square passport photo at target resolution
        info: Size information for reference
    """

    CATEGORY = "image/passport"
    FUNCTION = "resize_to_passport"
    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("image", "info")

    @classmethod
    def INPUT_TYPES(cls) -> dict[str, Any]:
        """Define input parameters for the node."""
        return {
            "required": {
                "image": ("IMAGE",),
                "output_size": (
                    list(PASSPORT_SIZES.keys()),
                    {"default": "2x2_inch_600dpi"},
                ),
                "crop_mode": (
                    ["center", "top", "none"],
                    {"default": "center"},
                ),
            },
        }

    def resize_to_passport(
        self,
        image: torch.Tensor,
        output_size: str,
        crop_mode: str,
    ) -> tuple[torch.Tensor, str]:
        """
        Resize image to passport dimensions.

        Args:
            image: Input image tensor (B, H, W, C)
            output_size: Target size key
            crop_mode: How to crop non-square images

        Returns:
            Tuple of (resized_image, info_string)
        """
        target_size = PASSPORT_SIZES[output_size]
        target_w, target_h = target_size

        # Convert tensor to PIL for processing
        # ComfyUI format: (B, H, W, C) float32 [0, 1]
        img_np = image[0].cpu().numpy()
        img_np = (img_np * 255).clip(0, 255).astype(np.uint8)
        pil_img = Image.fromarray(img_np, mode="RGB")

        orig_w, orig_h = pil_img.size

        # Crop to square if needed
        if crop_mode != "none" and orig_w != orig_h:
            min_dim = min(orig_w, orig_h)
            if crop_mode == "center":
                left = (orig_w - min_dim) // 2
                top = (orig_h - min_dim) // 2
            else:  # top - keep face at top
                left = (orig_w - min_dim) // 2
                top = 0
            pil_img = pil_img.crop((left, top, left + min_dim, top + min_dim))

        # Resize to target
        resized = pil_img.resize(target_size, Image.Resampling.LANCZOS)

        # Convert back to tensor
        result_np = np.array(resized).astype(np.float32) / 255.0
        result_tensor = torch.from_numpy(result_np).unsqueeze(0)

        # Build info
        info = (
            f"Input: {orig_w}x{orig_h}\n"
            f"Output: {target_w}x{target_h} ({output_size})\n"
            f"Crop: {crop_mode}\n"
            f"Ready for CVS/Walgreens printing"
        )

        return (result_tensor, info)


class PassportTile:
    """
    Tile 4 passport photos onto a 4x6 inch print sheet.

    Creates a standard CVS/Walgreens 4x6 print with 4 passport photos.
    Output: 1800x1200 pixels (4x6 inches at 300 DPI)

    Inputs:
        image: Single 600x600 passport photo

    Outputs:
        IMAGE: 4x6 sheet with 4 tiled photos
    """

    CATEGORY = "image/passport"
    FUNCTION = "tile_passport"
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("tiled_image",)

    @classmethod
    def INPUT_TYPES(cls) -> dict[str, Any]:
        """Define input parameters for the node."""
        return {
            "required": {
                "image": ("IMAGE",),
            },
        }

    def tile_passport(self, image: torch.Tensor) -> tuple[torch.Tensor]:
        """
        Tile passport photo onto 4x6 print sheet.

        Args:
            image: 600x600 passport photo tensor

        Returns:
            1800x1200 tiled image (4x6 at 300 DPI)
        """
        # Convert to PIL
        img_np = image[0].cpu().numpy()
        img_np = (img_np * 255).clip(0, 255).astype(np.uint8)
        passport = Image.fromarray(img_np, mode="RGB")

        # Resize to exactly 600x600 if needed
        if passport.size != (600, 600):
            passport = passport.resize((600, 600), Image.Resampling.LANCZOS)

        # Create 4x6 canvas (1800x1200 at 300 DPI)
        # Layout: 2 columns x 2 rows of 600x600, centered
        canvas = Image.new("RGB", (1800, 1200), color=(255, 255, 255))

        # Calculate positions (centered with some margin)
        # 2 photos horizontally: 600*2 = 1200, margin = (1800-1200)/2 = 300
        # 2 photos vertically: 600*2 = 1200, no vertical margin needed
        margin_x = 300
        positions = [
            (margin_x, 0),  # Top left
            (margin_x + 600, 0),  # Top right
            (margin_x, 600),  # Bottom left
            (margin_x + 600, 600),  # Bottom right
        ]

        for pos in positions:
            canvas.paste(passport, pos)

        # Convert back to tensor
        result_np = np.array(canvas).astype(np.float32) / 255.0
        result_tensor = torch.from_numpy(result_np).unsqueeze(0)

        return (result_tensor,)
