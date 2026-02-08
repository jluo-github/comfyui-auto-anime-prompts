input_file = "rednote_1girl_v1.txt"
output_file = "v2.txt"

banned_keywords = [
    "blue hair",
    "blue dress",
    "mermaid",
    "sharp teeth",
    "blue jacket",
    "princess",
]

print(f"Filtering {input_file} to {output_file}...")

kept_lines = 0
total_lines = 0

try:
    with (
        open(input_file, encoding="utf-8") as f_in,
        open(output_file, "w", encoding="utf-8") as f_out,
    ):
        for line in f_in:
            total_lines += 1
            line_lower = line.lower()
            if not any(keyword in line_lower for keyword in banned_keywords):
                f_out.write(line)
                kept_lines += 1
            else:
                # Optional: print dropped lines for debugging
                # print(f"Dropped: {line.strip()}")
                pass

    print(f"Done. Processed {total_lines} lines, kept {kept_lines} lines.")

except FileNotFoundError:
    print(f"Error: {input_file} not found.")
except Exception as e:
    print(f"An error occurred: {e}")
