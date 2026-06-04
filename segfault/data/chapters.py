"""Chapter definitions. Chapter 1 is fully playable; 2-5 are scaffolded
stubs so the structure (and unlock flow) is ready to grow into.

A `lesson` is {"title": str, "lines": [str, ...]} shown as a typewriter popup.
"""

from .. import constants as C

CHAPTERS = [
    {
        "id": 1,
        "name": "LOCALHOST",
        "subtitle": "Chapter 1 — your machine",
        "playable": True,
        "floor": (26, 31, 58),
        "floor_accent": (60, 90, 160),
        "wall": (46, 52, 92),
        "servers": 3,                 # corrupted servers to patch (objective)
        "max_enemies": 7,             # concurrent cap
        "spawn_interval": 2.2,        # seconds between spawns
        "spawn_types": ["null_pointer", "null_pointer", "spider"],
        "adaptive_boss": True,        # the learning enemy appears at the end
        "intro": {
            "title": "SEGFAULT",
            "lines": [
                "You pushed a hotfix to production at 2am.",
                "Something... went wrong. Reality threw an exception.",
                "Now you can SEE the bugs — and they can see you.",
                "",
                "CHAPTER 1: LOCALHOST",
                "Three of your servers are corrupted (red).",
                "Walk into each one and hold [E] to PATCH it.",
                "Kill the null-pointer bugs before they kill you.",
            ],
        },
        "lessons": {
            "first_patch": {
                "title": "WHAT IS A SEGFAULT?",
                "lines": [
                    "A segmentation fault happens when a program",
                    "touches memory it isn't allowed to touch.",
                    "",
                    "Classic cause: a NULL pointer — an address that",
                    "points to nothing. Dereference it and the OS",
                    "slaps you with SIGSEGV.",
                    "",
                    "You just 'patched' one. 2 servers left.",
                ],
            },
            "all_patched": {
                "title": "INCOMING: THE HEURISTIC",
                "lines": [
                    "All servers patched — but the corruption noticed you.",
                    "",
                    "A HEURISTIC has spawned. It doesn't just chase:",
                    "it watches how you fight and adapts. Dodge a lot?",
                    "It learns to wait you out. Spam ranged? It closes in.",
                    "",
                    "This is the offline 'AI' — pattern learning, no cloud.",
                    "Beat it to clear the chapter.",
                ],
            },
            "clear": {
                "title": "CHAPTER 1 CLEAR",
                "lines": [
                    "Localhost is stable again.",
                    "",
                    "But this was just your machine. The bug is",
                    "spreading up the stack — staging, prod, the cloud,",
                    "and finally... the Model.",
                    "",
                    "More chapters are coming. Nice debugging, dev.",
                ],
            },
        },
    },
    # ---------------------------------------------------------- stubs ----
    {"id": 2, "name": "TCP HANDSHAKE", "subtitle": "Chapter 2 — the network",
     "playable": False},
    {"id": 3, "name": "DNS LABYRINTH", "subtitle": "Chapter 3 — the web",
     "playable": False},
    {"id": 4, "name": "TRAINING DATA", "subtitle": "Chapter 4 — the AI lab",
     "playable": False},
    {"id": 5, "name": "PROMPT INJECTION", "subtitle": "Chapter 5 — the Model",
     "playable": False},
]

BY_ID = {c["id"]: c for c in CHAPTERS}


def get_chapter(cid):
    return BY_ID.get(cid)
