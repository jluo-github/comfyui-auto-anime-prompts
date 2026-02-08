input_file = "v2.txt"
output_file = "v3.txt"

banned_keywords = ["blue hair", "blue skirt"]

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


# *********************************
#
# keywords_to_keep = [
#     "1girl",
#     "pink",
#     "purple",
#     "white",
#     "sad",
#     "broken",
#     "pretty",
#     "cute",
#     "hair",
# ]
# keywords_to_purge = [
#     "machine",
#     "robot",
#     "cyborg",
#     "mechanical",
#     "wings",
#     "demon",
#     "magic",
#     "witch",
#     "wizard",
#     "hat",
#     "cap",
#     "armor",
#     "bandaid",
#     "bandage",
#     "mascara",
#     "blue hair",
#     "blue skirt",
#     "princess", "large breasts", "cleavage", "red hair", "red skirt", "black hair", "tail", "pointy ears", "animal", "army", "weapon", "sword", "uniform", "gun", "robot", "orange", "red", "devil", "angel", "wings", "horns", "pokemon", "no humans", "scar", "muscular", "topless", "male", "1boy", "glasses", "gloves", "armband", "detached sleeves", "detached collar", "fin", "feather", horns", "antler", "mouse", "halo", "antenna", "antennae", "leaf", "magician", "sprout", "ghost", "devil"
# # ]

# with open("v2.txt", "r", encoding="utf-8") as f:
#     lines = f.readlines()

# rednote_pure_units = []
# for line in lines:
#     tags = line.lower()
#     if any(k in tags for k in keywords_to_keep) and not any(
#         p in tags for p in keywords_to_purge
#     ):
#         rednote_pure_units.append(line)

# with open("rednote_pure_units.txt", "w", encoding="utf-8") as f:
#     f.writelines(rednote_pure_units)

# print(f"number of pure units: {len(rednote_pure_units)}")
