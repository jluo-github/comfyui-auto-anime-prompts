import os

import pandas as pd

# --- Configuration ---
INPUT_FILE = "pure_1girl_v1.csv"
OUTPUT_FILE = "system_lock_prompts.txt"

# Your specialized aesthetic "System-Lock" suffix
# Optimized for 7900XTX rendering and high-fidelity output
AESTHETIC_SUFFIX = (
    ", (violet and gold theme:1.3), (managed asset:1.2), (mechanical parts:1.1), "
    "system-lock, masterpiece, best quality, ultra-detailed, 8k, highres, "
    "sharp focus, cinematic lighting"
)


def generate_prompts():
    if not os.path.exists(INPUT_FILE):
        print(f"Error: {INPUT_FILE} not found in current directory.")
        return

    # Load data - skipping header as the file appears to be raw tag strings
    try:
        df = pd.read_csv(INPUT_FILE, header=None)

        # The first column contains the tags
        raw_tags = df[0].astype(str).tolist()

        processed_prompts = []
        for tags in raw_tags:
            # Clean and append suffix
            clean_tags = tags.strip().rstrip(",")
            full_prompt = clean_tags + AESTHETIC_SUFFIX
            processed_prompts.append(full_prompt)

        # Write to text file (one prompt per line for batch loaders)
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            for p in processed_prompts:
                f.write(p + "\n")

        print(
            f"Success: {len(processed_prompts)} prompts optimized and saved to {OUTPUT_FILE}."
        )

    except Exception as e:
        print(f"System Error during processing: {e}")


if __name__ == "__main__":
    generate_prompts()
