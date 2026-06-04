"""All tunable game constants live here. No magic numbers scattered in logic."""

import os

# ---------------------------------------------------------------- Display ----
WINDOW_WIDTH = 960
WINDOW_HEIGHT = 600
TARGET_FPS = 60
TITLE = "Segfault"

# ------------------------------------------------------------------ World ----
# Source art is 16x16, scaled up at runtime for that chunky pixel look.
TILE_SRC = 16
TILE_SCALE = 3
TILE_SIZE = TILE_SRC * TILE_SCALE          # 48px tiles in-world

WORLD_W_TILES = 40
WORLD_H_TILES = 30
WORLD_WIDTH = WORLD_W_TILES * TILE_SIZE
WORLD_HEIGHT = WORLD_H_TILES * TILE_SIZE

# ----------------------------------------------------------------- Camera ----
CAMERA_DEADZONE_W = 220
CAMERA_DEADZONE_H = 160
CAMERA_LERP = 0.12                          # smoothing factor (0..1)

# ----------------------------------------------------------------- Player ----
PLAYER_W = 30
PLAYER_H = 42
IFRAME_DURATION = 0.8                       # invulnerability after a hit (s)
WALK_BOB_AMP = 3
WALK_BOB_SPEED = 14
DODGE_SPEED = 620
DODGE_DURATION = 0.18
DODGE_COOLDOWN = 0.7

# Weapons (base; per-character multipliers in data/characters.py)
MELEE_COOLDOWN = 0.35
MELEE_RANGE = 64
MELEE_ARC = 90                              # degrees of the swing cone
MELEE_KNOCKBACK = 340

RANGED_COOLDOWN = 0.45
RANGED_LIFETIME = 1.1
RANGED_SPEED = 560
PROJECTILE_R = 6

# ---------------------------------------------------------------- Enemies ----
ENEMY_CONTACT_COOLDOWN = 0.6                # how often an enemy can touch-damage

# --------------------------------------------------------------- Spawning ----
WAVE_SPAWN_PADDING = TILE_SIZE * 2

# ------------------------------------------------------------------ Colors ----
BLACK       = (8, 8, 12)
WHITE       = (240, 240, 245)
GREY        = (120, 124, 140)
DARK        = (22, 24, 34)
DARKER      = (14, 15, 22)
RED         = (235, 64, 72)
GREEN       = (70, 220, 120)
BLUE        = (70, 130, 240)
CYAN        = (60, 220, 230)
YELLOW      = (245, 210, 70)
PURPLE      = (150, 90, 245)
ORANGE      = (245, 150, 60)
PINK        = (245, 90, 200)
UI_PANEL    = (18, 20, 30)
UI_BORDER   = (60, 70, 110)
HP_BACK     = (50, 16, 22)
HP_FRONT    = (235, 64, 72)

# ----------------------------------------------------------------- Layers ----
DEPTH_FLOOR = 0
DEPTH_WALL = 1

# ----------------------------------------------------------------- Saving ----
# SEGFAULT_SAVE_DIR lets tests (and portable installs) redirect the save.
SAVE_DIR = os.environ.get("SEGFAULT_SAVE_DIR",
                          os.path.expanduser("~/.segfault"))
SAVE_FILE = os.path.join(SAVE_DIR, "save.json")

# -------------------------------------------------------------------- Font ----
# Bundled-by-default pygame font; None => pygame default monospace.
FONT_NAME = None
