"""Playable heroes. `sprite` keys map into sprites.SpriteBank.heroes."""

CHARACTERS = [
    {
        "id": "dev",
        "name": "THE DEV",
        "role": "Junior Engineer",
        "sprite": "dev",
        "blurb": "Pushed a hotfix to prod. Now reality has bugs.",
        "hp": 100,
        "speed": 260,
        "melee_dmg": 25,
        "ranged_dmg": 15,
        "weapon": "Laptop / Pistol",
        "shoot_sound": "pistol",
        "unlock": None,                  # available from the start
    },
    {
        "id": "anime",
        "name": "THE ANIME",
        "role": "Glass Cannon",
        "sprite": "anime",
        "blurb": "Fast, fragile, all melee. Believes in the heart of the code.",
        "hp": 75,
        "speed": 340,
        "melee_dmg": 38,
        "ranged_dmg": 0,                 # no projectile
        "weapon": "Energy Blade",
        "shoot_sound": "plasma",
        "unlock": 2,                     # unlocks after clearing chapter 2
    },
    {
        "id": "shogun",
        "name": "THE SHOGUN",
        "role": "Kensei / Samurai",
        "sprite": "shogun",
        "blurb": "Purple-haired swordmaster. Katana up close, plasma slash at range.",
        "hp": 95,
        "speed": 320,
        "melee_dmg": 34,
        "ranged_dmg": 18,
        "weapon": "Plasma Katana",
        "shoot_sound": "plasma",
        "unlock": 4,                     # unlocks after clearing chapter 4
    },
]

BY_ID = {c["id"]: c for c in CHARACTERS}


def get_character(cid):
    return BY_ID.get(cid, CHARACTERS[0])


# Chapters 2-5 aren't built yet, so chapter-gating would make Anime/Shogun
# permanently unreachable. Until those chapters ship, all heroes are available.
# Flip this to False to re-enable the "unlock by clearing chapter N" gating.
UNLOCK_ALL = True


def is_unlocked(character, highest_chapter, unlocked_list):
    if UNLOCK_ALL:
        return True
    if character["id"] in unlocked_list:
        return True
    req = character["unlock"]
    return req is None or highest_chapter > req
