"""Unlockable ranged weapons. A character's *signature* weapon (their built-in
ranged_dmg + shoot_sound) is the default; equipping one of these overrides the
ranged attack. Damage is scaled by the character's ranged_dmg so heroes keep
their identity (Iron Man hits harder than Wall-E with the same gun).

Melee-only heroes (ranged_dmg == 0) can't use guns - they stay pure melee.

Weapons unlock by clearing chapters (same as heroes).
"""

# damage here is the BASE; effective = base * (char.ranged_dmg / 20)
WEAPONS = [
    {"id": "signature", "name": "SIGNATURE", "unlock": None,
     "desc": "Each hero's own built-in weapon."},
    {"id": "pistol", "name": "PISTOL", "unlock": None,
     "damage": 15, "cooldown": 0.42, "count": 1, "spread": 0, "speed": 560,
     "sound": "pistol", "desc": "Reliable semi-auto sidearm."},
    {"id": "smg", "name": "SMG", "unlock": 1,
     "damage": 9, "cooldown": 0.14, "count": 1, "spread": 9, "speed": 640,
     "sound": "pistol", "desc": "Rapid fire, low damage, a little spray."},
    {"id": "shotgun", "name": "SHOTGUN", "unlock": 2,
     "damage": 7, "cooldown": 0.72, "count": 5, "spread": 36, "speed": 520,
     "sound": "blaster", "desc": "Five pellets. Devastating up close."},
    {"id": "plasma", "name": "PLASMA RIFLE", "unlock": 3,
     "damage": 28, "cooldown": 0.55, "count": 1, "spread": 0, "speed": 720,
     "sound": "plasma", "desc": "Heavy high-damage bolt."},
    {"id": "pulse", "name": "PULSE CANNON", "unlock": 4,
     "damage": 14, "cooldown": 0.6, "count": 3, "spread": 16, "speed": 580,
     "sound": "repulsor", "desc": "Three-round burst spread."},
    {"id": "beam", "name": "DEBUGGER BEAM", "unlock": 5,
     "damage": 18, "cooldown": 0.28, "count": 1, "spread": 0, "speed": 860,
     "sound": "beep", "desc": "Fast, flat, surgical."},
]

BY_ID = {w["id"]: w for w in WEAPONS}


def get_weapon(wid):
    return BY_ID.get(wid)


def is_weapon_unlocked(weapon, highest_chapter):
    req = weapon.get("unlock")
    return req is None or highest_chapter > req
