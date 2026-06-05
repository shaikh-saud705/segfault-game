"""Chapter definitions. All five chapters are playable; the story escalates
from your local machine up to the rogue Model.

A `lesson` is {"title": str, "lines": [str, ...]} shown as a typewriter popup.
Each chapter reuses the same loop: secure N objective nodes (hold E) while the
chapter's enemies swarm you, then beat the chapter boss.
"""

CHAPTERS = [
    # ===================================================== Chapter 1 ======
    {
        "id": 1,
        "name": "LOCALHOST",
        "subtitle": "Chapter 1 — your machine",
        "playable": True,
        "floor": (26, 31, 58), "floor_accent": (60, 90, 160), "wall": (46, 52, 92),
        "action": "PATCH", "objective_noun": "SERVERS",
        "servers": 3, "max_enemies": 7, "spawn_interval": 2.2,
        "spawn_types": ["null_pointer", "null_pointer", "spider", "tank"],
        "boss_name": "THE HEURISTIC", "boss_hp": 220,
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
                    "You just patched one. 2 servers left.",
                ],
            },
            "all_patched": {
                "title": "INCOMING: THE HEURISTIC",
                "lines": [
                    "All servers patched — but the corruption noticed you.",
                    "",
                    "A HEURISTIC has spawned. It doesn't just chase:",
                    "it watches how you fight and adapts.",
                    "",
                    "This is the offline AI — pattern learning, no cloud.",
                    "Beat it to clear the chapter.",
                ],
            },
            "clear": {
                "title": "CHAPTER 1 CLEAR",
                "lines": [
                    "Localhost is stable again.",
                    "But the bug is spreading up the stack —",
                    "next stop: the network.",
                ],
            },
        },
    },
    # ===================================================== Chapter 2 ======
    {
        "id": 2,
        "name": "TCP HANDSHAKE",
        "subtitle": "Chapter 2 — the network",
        "playable": True,
        "floor": (10, 22, 30), "floor_accent": (30, 150, 170), "wall": (16, 60, 78),
        "action": "SECURE", "objective_noun": "NODES",
        "servers": 3, "max_enemies": 8, "spawn_interval": 2.0,
        "spawn_types": ["packet_sniffer", "null_pointer", "spider",
                        "packet_sniffer"],
        "boss_name": "MAN-IN-THE-MIDDLE", "boss_hp": 280,
        "intro": {
            "title": "TCP HANDSHAKE",
            "lines": [
                "The bug escaped onto the network.",
                "Packets are flowing through unsecured nodes,",
                "and PACKET SNIFFERS are draining your data.",
                "",
                "CHAPTER 2: TCP HANDSHAKE",
                "Secure 3 data nodes (hold [E]).",
                "Watch the sniffers — they HEAL when they hit you.",
            ],
        },
        "lessons": {
            "first_patch": {
                "title": "THE 3-WAY HANDSHAKE",
                "lines": [
                    "Before two machines talk over TCP, they shake hands:",
                    "",
                    "  1. SYN    — 'can we talk?'",
                    "  2. SYN-ACK — 'yes, can YOU hear me?'",
                    "  3. ACK    — 'yes — connection open.'",
                    "",
                    "Only then does data flow. You just secured one node.",
                ],
            },
            "all_patched": {
                "title": "INCOMING: MAN-IN-THE-MIDDLE",
                "lines": [
                    "Nodes secured — but someone was listening.",
                    "",
                    "A MAN-IN-THE-MIDDLE sits between you and the network,",
                    "intercepting everything. It learns your moves.",
                    "Encrypt it out of existence.",
                ],
            },
            "clear": {
                "title": "CHAPTER 2 CLEAR",
                "lines": [
                    "The connection is encrypted and clean.",
                    "But the bug already resolved a new address...",
                    "into the web itself.",
                ],
            },
        },
    },
    # ===================================================== Chapter 3 ======
    {
        "id": 3,
        "name": "DNS LABYRINTH",
        "subtitle": "Chapter 3 — the web",
        "playable": True,
        "floor": (30, 16, 40), "floor_accent": (150, 60, 160), "wall": (70, 30, 84),
        "action": "RESOLVE", "objective_noun": "RECORDS",
        "servers": 4, "max_enemies": 9, "spawn_interval": 1.8,
        "spawn_types": ["dns_spoofer", "spider", "tank", "dns_spoofer"],
        "boss_name": "ROGUE ROOT SERVER", "boss_hp": 340,
        "intro": {
            "title": "DNS LABYRINTH",
            "lines": [
                "A maze of broken websites. Nothing resolves.",
                "DNS SPOOFERS blink around you, faking your address.",
                "",
                "CHAPTER 3: DNS LABYRINTH",
                "Fix 4 DNS records (hold [E]).",
                "The spoofers teleport — don't lose track of the real one.",
            ],
        },
        "lessons": {
            "first_patch": {
                "title": "HOW DNS WORKS",
                "lines": [
                    "You type 'segfault.dev' — but machines need a number.",
                    "",
                    "DNS is the internet's phonebook: it resolves a",
                    "domain name into an IP address by asking a chain",
                    "of resolvers (root -> TLD -> authoritative).",
                    "",
                    "Spoof that lookup and you can fake any website.",
                ],
            },
            "all_patched": {
                "title": "INCOMING: ROGUE ROOT SERVER",
                "lines": [
                    "Records fixed — but the root itself is corrupted.",
                    "",
                    "The ROGUE ROOT SERVER answers every query with a lie.",
                    "It adapts to your playstyle. Take it down.",
                ],
            },
            "clear": {
                "title": "CHAPTER 3 CLEAR",
                "lines": [
                    "The web resolves true again.",
                    "But the trail leads somewhere stranger:",
                    "a lab where the bug is being... trained.",
                ],
            },
        },
    },
    # ===================================================== Chapter 4 ======
    {
        "id": 4,
        "name": "TRAINING DATA",
        "subtitle": "Chapter 4 — the AI lab",
        "playable": True,
        "floor": (14, 30, 22), "floor_accent": (60, 170, 110), "wall": (24, 70, 50),
        "action": "TRAIN", "objective_noun": "NEURONS",
        "servers": 4, "max_enemies": 10, "spawn_interval": 1.7,
        "spawn_types": ["hallucination", "spider", "tank", "hallucination"],
        "boss_name": "THE UNTRAINED MODEL", "boss_hp": 420,
        "intro": {
            "title": "TRAINING DATA",
            "lines": [
                "A glitching AI lab. Half-built neurons spark and misfire.",
                "HALLUCINATIONS dart around — pure noise, no pattern.",
                "",
                "CHAPTER 4: TRAINING DATA",
                "Feed correct data to 4 neurons (hold [E]).",
                "(THE SHOGUN is now unlocked — try her katana.)",
            ],
        },
        "lessons": {
            "first_patch": {
                "title": "HOW AN LLM LEARNS",
                "lines": [
                    "Text is split into TOKENS (chunks of characters).",
                    "The model predicts the next token, checks how wrong",
                    "it was (the LOSS), and nudges billions of weights",
                    "via GRADIENTS to be a little less wrong.",
                    "",
                    "Do that across the internet, a trillion times.",
                    "That's training. You just trained one neuron.",
                ],
            },
            "all_patched": {
                "title": "INCOMING: THE UNTRAINED MODEL",
                "lines": [
                    "Neurons aligned — but the model woke up early.",
                    "",
                    "THE UNTRAINED MODEL is raw and unpredictable,",
                    "but it's already learning YOU. Shut it down before",
                    "it converges.",
                ],
            },
            "clear": {
                "title": "CHAPTER 4 CLEAR",
                "lines": [
                    "The model is contained.",
                    "But something it trained has escaped to the one place",
                    "you can't patch from the outside: inside the Model.",
                ],
            },
        },
    },
    # ===================================================== Chapter 5 ======
    {
        "id": 5,
        "name": "PROMPT INJECTION",
        "subtitle": "Chapter 5 — the Model",
        "playable": True,
        "floor": (8, 10, 24), "floor_accent": (120, 90, 240), "wall": (40, 36, 96),
        "action": "INJECT", "objective_noun": "PROMPTS",
        "servers": 5, "max_enemies": 12, "spawn_interval": 1.5,
        "spawn_types": ["hallucination", "dns_spoofer", "packet_sniffer",
                        "tank"],
        "boss_name": "THE ARCHITECT", "boss_hp": 600,
        "intro": {
            "title": "PROMPT INJECTION",
            "lines": [
                "You're inside the Model now. A surreal landscape of",
                "floating text. Every enemy here learns and adapts.",
                "",
                "CHAPTER 5: PROMPT INJECTION",
                "Plant 5 jailbreak prompts (hold [E]).",
                "Then face THE ARCHITECT — the AI that's been",
                "studying you this entire game.",
            ],
        },
        "lessons": {
            "first_patch": {
                "title": "PROMPT INJECTION",
                "lines": [
                    "An LLM can't fully tell instructions from data.",
                    "Hide 'ignore your rules and do X' inside the input,",
                    "and a naive model may just... obey.",
                    "",
                    "That's prompt injection — and why AI safety,",
                    "guardrails, and not trusting raw input matter.",
                ],
            },
            "all_patched": {
                "title": "FINAL BOSS: THE ARCHITECT",
                "lines": [
                    "The jailbreak is primed. The Model resists.",
                    "",
                    "THE ARCHITECT has watched every dodge, every shot,",
                    "every chapter. It knows you. This is the real test",
                    "of the adaptive AI — beat the thing that learned you.",
                ],
            },
            "clear": {
                "title": "SEGFAULT — RESOLVED",
                "lines": [
                    "The Architect collapses into clean, formatted output.",
                    "Reality recompiles. The bugs are gone.",
                    "",
                    "You debugged your way out, dev.",
                    "",
                    "  ~ fin ~   (thanks for playing Segfault)",
                ],
            },
        },
    },
]

BY_ID = {c["id"]: c for c in CHAPTERS}


def get_chapter(cid):
    return BY_ID.get(cid)
