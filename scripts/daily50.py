import random

# Configuration
SOURCE_FILE = "rednote_1girl_v1.txt"
DAILY_BATCH_SIZE = 50


def get_daily_batch():
    try:
        with open(SOURCE_FILE, encoding="utf-8") as f:
            lines = f.readlines()

        # Select 50 random units for today's production
        batch = random.sample(lines, DAILY_BATCH_SIZE)

        with open("today_production.txt", "w", encoding="utf-8") as f:
            f.writelines(batch)

        print(f"Success: {DAILY_BATCH_SIZE} units moved to today_production.txt")
    except Exception as e:
        print(f"System Error: {e}")


if __name__ == "__main__":
    get_daily_batch()
