"""JSON save/load in ~/.segfault/save.json. Forgiving: missing keys are
backfilled from defaults, corrupt files fall back cleanly."""

import json
import os

from .constants import SAVE_DIR, SAVE_FILE

DEFAULTS = {
    "current_chapter": 1,
    "highest_chapter": 1,
    "unlocked_characters": ["dev"],
    "total_kills": 0,
    "deaths": 0,
    "playtime": 0.0,
    "master_volume": 0.5,
    "seen_intro": False,
}


def load_save():
    data = dict(DEFAULTS)
    try:
        if os.path.exists(SAVE_FILE):
            with open(SAVE_FILE, "r") as f:
                loaded = json.load(f)
            if isinstance(loaded, dict):
                data.update({k: loaded.get(k, v) for k, v in DEFAULTS.items()})
    except Exception as exc:
        print(f"[save] could not load ({exc}); using defaults")
    return data


def write_save(data):
    try:
        os.makedirs(SAVE_DIR, exist_ok=True)
        with open(SAVE_FILE, "w") as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as exc:
        print(f"[save] could not write ({exc})")
        return False
