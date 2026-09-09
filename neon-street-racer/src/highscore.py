"""
highscore.py
Loads and saves the local high score as JSON in the user-writable
data/ directory. Fails gracefully (falls back to 0 / in-memory only)
if the file is missing, corrupted, or the directory is not writable.
"""

import json
import os

from src import settings


def load_high_score():
    try:
        if os.path.exists(settings.HIGHSCORE_FILE):
            with open(settings.HIGHSCORE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return float(data.get("high_score", 0))
    except (json.JSONDecodeError, ValueError, OSError):
        pass
    return 0.0


def save_high_score(value):
    try:
        os.makedirs(settings.DATA_DIR, exist_ok=True)
        with open(settings.HIGHSCORE_FILE, "w", encoding="utf-8") as f:
            json.dump({"high_score": value}, f)
        return True
    except OSError:
        return False
