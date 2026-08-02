#!/usr/bin/env python3
"""
Generate GitHub contribution graph art: LFARSSI 💀
Creates backdated git commits to draw pixel art on the contribution graph.
"""

import os
import subprocess
from datetime import datetime, timedelta

# Git config
GIT_NAME = "lfarssi"
GIT_EMAIL = "medlfarssi10@gmail.com"

# Commits per lit pixel (ensures dark green)
COMMITS_PER_PIXEL = 5

# Today is 2026-08-02 (Sunday)
TODAY = datetime(2026, 8, 2)
# GitHub graph starts 52 weeks ago on a Sunday
GRAPH_START = TODAY - timedelta(weeks=52)  # 2025-08-03

# 5-row pixel font (rows map to Mon-Fri on the graph)
LETTERS = {
    'L': [
        [1, 0, 0],
        [1, 0, 0],
        [1, 0, 0],
        [1, 0, 0],
        [1, 1, 1],
    ],
    'F': [
        [1, 1, 1],
        [1, 0, 0],
        [1, 1, 0],
        [1, 0, 0],
        [1, 0, 0],
    ],
    'A': [
        [0, 1, 0],
        [1, 0, 1],
        [1, 1, 1],
        [1, 0, 1],
        [1, 0, 1],
    ],
    'R': [
        [1, 1, 0],
        [1, 0, 1],
        [1, 1, 0],
        [1, 0, 1],
        [1, 0, 1],
    ],
    'S': [
        [0, 1, 1],
        [1, 0, 0],
        [0, 1, 0],
        [0, 0, 1],
        [1, 1, 0],
    ],
    'I': [
        [1, 1, 1],
        [0, 1, 0],
        [0, 1, 0],
        [0, 1, 0],
        [1, 1, 1],
    ],
}

SKULL = [
    [0, 1, 1, 1, 1, 1, 0],
    [1, 1, 0, 1, 0, 1, 1],
    [1, 1, 1, 1, 1, 1, 1],
    [0, 1, 1, 1, 1, 1, 0],
    [0, 1, 0, 1, 0, 1, 0],
]


def build_grid():
    """Build the full 7x53 contribution grid."""
    grid = [[0] * 53 for _ in range(7)]

    # Place "LFARSSI" starting at column 8
    text = "LFARSSI"
    col = 8

    for char in text:
        letter = LETTERS[char]
        for row_idx, row_data in enumerate(letter):
            for col_idx, pixel in enumerate(row_data):
                if pixel:
                    grid[row_idx + 1][col + col_idx] = 1  # rows 1-5 = Mon-Fri
        col += len(letter[0]) + 1  # letter width + 1 gap

    # Place skull after text with 2-column gap
    col += 1
    for row_idx, row_data in enumerate(SKULL):
        for col_idx, pixel in enumerate(row_data):
            if pixel:
                grid[row_idx + 1][col + col_idx] = 1

    return grid


def date_for_cell(col, row):
    """Get the date for a specific grid cell (col=week, row=day_of_week)."""
    return GRAPH_START + timedelta(days=col * 7 + row)


def main():
    grid = build_grid()

    # Print preview
    print("\n🎨 Preview of contribution graph art:")
    print("=" * 56)
    days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
    for row in range(7):
        line = days[row] + " "
        for col in range(53):
            line += "█" if grid[row][col] else "░"
        print(line)
    print("=" * 56)

    total_pixels = sum(sum(r) for r in grid)
    total_commits = total_pixels * COMMITS_PER_PIXEL
    print(f"\nLit pixels: {total_pixels} | Commits per pixel: {COMMITS_PER_PIXEL}")
    print(f"Total commits to create: {total_commits}")

    response = input("\nProceed? (yes/no): ")
    if response.lower() != 'yes':
        print("Aborted.")
        return

    repo_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(repo_dir)

    # Wipe old git history and reinitialize
    print("\n🗑️  Reinitializing repository...")
    subprocess.run(["rm", "-rf", ".git"], check=True)
    subprocess.run(["git", "init", "-b", "main"], check=True)
    subprocess.run(["git", "config", "user.name", GIT_NAME], check=True)
    subprocess.run(["git", "config", "user.email", GIT_EMAIL], check=True)

    # Remove old files
    for f in ["daily_log.txt", "hourly_log.txt"]:
        if os.path.exists(f):
            os.remove(f)

    # Clear contributions file
    open("contributions.txt", "w").close()

    # Generate backdated commits
    print("⏳ Creating commits...")
    commit_count = 0

    for col in range(53):
        for row in range(7):
            if grid[row][col]:
                date = date_for_cell(col, row)
                if date > TODAY:
                    continue

                date_str = date.strftime("%Y-%m-%dT12:00:00")
                env = os.environ.copy()
                env["GIT_AUTHOR_DATE"] = date_str
                env["GIT_COMMITTER_DATE"] = date_str

                for i in range(COMMITS_PER_PIXEL):
                    commit_count += 1
                    with open("contributions.txt", "a") as f:
                        f.write(f"{commit_count}\n")

                    subprocess.run(["git", "add", "contributions.txt"],
                                   check=True, capture_output=True)
                    subprocess.run(
                        ["git", "commit", "-m", f"c{commit_count}"],
                        env=env, check=True, capture_output=True,
                    )

                if commit_count % 50 == 0:
                    print(f"  Progress: {commit_count}/{total_commits}")

    print(f"\n✅ Done! Created {commit_count} commits.")
    print(f"\nNext steps:")
    print(f"  git remote add origin https://github.com/lfarssi/github-bot.git")
    print(f"  git push -f origin main")
    print(f"\nThen check your GitHub profile! 🎨💀")


if __name__ == "__main__":
    main()
