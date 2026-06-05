"""Playable heroes. `sprite` keys map into sprites.SpriteBank.heroes.

Each hero has a weapon (gun sound), an `unlock` chapter (you unlock them by
clearing chapters), and an `ability` (special move on the Q key):
  hotfix    - heal a chunk of HP
  nova      - AoE burst that damages + knocks back nearby enemies
  barrage   - fire a fan of projectiles
  shield    - brief invulnerability
  overdrive - temporary speed + fire-rate boost
"""

CHARACTERS = [
    {
        "id": "dev", "name": "THE DEV", "role": "Junior Engineer",
        "sprite": "dev",
        "blurb": "Pushed a hotfix to prod. Now reality has bugs.",
        "hp": 100, "speed": 260, "melee_dmg": 25, "ranged_dmg": 15,
        "weapon": "Laptop / Pistol", "shoot_sound": "pistol",
        "ability": {"type": "hotfix", "name": "HOTFIX", "cd": 10},
        "unlock": None,                       # available from the start
    },
    {
        "id": "anime", "name": "THE ANIME", "role": "Glass Cannon",
        "sprite": "anime",
        "blurb": "Fast, fragile, all melee. Believes in the heart of the code.",
        "hp": 80, "speed": 340, "melee_dmg": 38, "ranged_dmg": 0,
        "weapon": "Energy Blade", "shoot_sound": "plasma",
        "ability": {"type": "nova", "name": "OMNI-SLASH", "cd": 9},
        "unlock": 1,                          # clear Chapter 1
    },
    {
        "id": "shogun", "name": "THE SHOGUN", "role": "Kensei / Samurai",
        "sprite": "shogun",
        "blurb": "Purple-haired swordmaster. Katana up close, plasma at range.",
        "hp": 95, "speed": 320, "melee_dmg": 34, "ranged_dmg": 18,
        "weapon": "Plasma Katana", "shoot_sound": "plasma",
        "ability": {"type": "nova", "name": "MUSOU", "cd": 9},
        "unlock": 2,                          # clear Chapter 2
    },
    {
        "id": "ironman", "name": "IRON MAN", "role": "Armored Avenger",
        "sprite": "ironman",
        "blurb": "Powered armour, glowing reactor, repulsors that wreck.",
        "hp": 150, "speed": 230, "melee_dmg": 20, "ranged_dmg": 30,
        "weapon": "Repulsor", "shoot_sound": "repulsor",
        "ability": {"type": "barrage", "name": "REPULSOR VOLLEY", "cd": 8},
        "unlock": 3,                          # clear Chapter 3
    },
    {
        "id": "ultron", "name": "ULTRON", "role": "Rogue AI",
        "sprite": "ultron",
        "blurb": "A machine that decided humanity was the bug.",
        "hp": 130, "speed": 250, "melee_dmg": 22, "ranged_dmg": 26,
        "weapon": "Energy Bolts", "shoot_sound": "blaster",
        "ability": {"type": "barrage", "name": "DRONE SWARM", "cd": 8},
        "unlock": 3,                          # clear Chapter 3
    },
    {
        "id": "baymax", "name": "BAYMAX", "role": "Guardian",
        "sprite": "baymax",
        "blurb": "Your personal healthcare tank. Soft outside, rocket fists.",
        "hp": 210, "speed": 200, "melee_dmg": 28, "ranged_dmg": 0,
        "weapon": "Rocket Fist", "shoot_sound": "blaster",
        "ability": {"type": "shield", "name": "GUARDIAN SHIELD", "cd": 12},
        "unlock": 4,                          # clear Chapter 4
    },
    {
        "id": "bumblebee", "name": "BUMBLEBEE", "role": "Scout",
        "sprite": "bumblebee",
        "blurb": "Fast yellow Autobot. Arm cannon and a need for speed.",
        "hp": 120, "speed": 320, "melee_dmg": 24, "ranged_dmg": 22,
        "weapon": "Arm Cannon", "shoot_sound": "blaster",
        "ability": {"type": "overdrive", "name": "OVERDRIVE", "cd": 12},
        "unlock": 4,                          # clear Chapter 4
    },
    {
        "id": "walle", "name": "WALL-E", "role": "Cleanup Unit",
        "sprite": "walle",
        "blurb": "Little trash compactor with a laser and a big heart.",
        "hp": 130, "speed": 230, "melee_dmg": 20, "ranged_dmg": 16,
        "weapon": "Cleanup Laser", "shoot_sound": "beep",
        "ability": {"type": "nova", "name": "COMPACTOR", "cd": 9},
        "unlock": 5,                          # clear Chapter 5
    },
]

BY_ID = {c["id"]: c for c in CHARACTERS}

# Heroes unlock by clearing chapters (set True to make all available, e.g. for
# testing). Chapter-wise progression is the intended experience.
UNLOCK_ALL = False


def get_character(cid):
    return BY_ID.get(cid, CHARACTERS[0])


def is_unlocked(character, highest_chapter, unlocked_list):
    if UNLOCK_ALL:
        return True
    if character["id"] in unlocked_list:
        return True
    req = character["unlock"]
    return req is None or highest_chapter > req
