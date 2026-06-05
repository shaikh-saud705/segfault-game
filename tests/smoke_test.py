"""Headless smoke test: drive the game through menu -> select -> play -> boss
-> clear without a display, catching runtime errors. Not shipped."""
import os
import sys

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["SEGFAULT_NO_LLM"] = "1"   # keep smoke test offline/deterministic
# repo root is one level up from tests/
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame
from segfault.main import Game
from segfault.states.menu import MenuState
from segfault.states.character_select import CharacterSelectState
from segfault.states.playing import PlayingState


def press(game, key):
    ev = pygame.event.Event(pygame.KEYDOWN, key=key)
    if game.stack:
        game.stack[-1].handle_events([ev])


def step(game, n=1, dt=1 / 60):
    for _ in range(n):
        if game.stack:
            game.stack[-1].update(dt, [])
        game._draw()


g = Game()
assert isinstance(g.stack[-1], MenuState), "should boot to menu"
print("boot -> menu OK")

# New Game -> character select
press(g, pygame.K_RETURN)
step(g, 2)
assert isinstance(g.stack[-1], CharacterSelectState), "menu->charselect"
print("menu -> character select OK")

# pick The Dev
press(g, pygame.K_RETURN)
step(g, 2)
# now should be Playing with an intro lesson on top
top = g.stack[-1]
print("after select, top =", type(top).__name__, "stack depth", len(g.stack))
assert any(isinstance(s, PlayingState) for s in g.stack), "playing in stack"

# dismiss intro lesson (space twice: fast-forward then continue)
press(g, pygame.K_SPACE)
step(g, 2)
press(g, pygame.K_SPACE)
step(g, 2)
playing = next(s for s in g.stack if isinstance(s, PlayingState))
print("phase after intro:", playing.phase)

# force-patch all servers to drive the phase machine
for s in playing.level.servers:
    s.patched = True
step(g, 5)
# dismiss any lesson popups that appear (all_patched)
for _ in range(6):
    press(g, pygame.K_SPACE)
    step(g, 3)
print("phase after patching:", playing.phase, "boss?", playing.boss is not None)

# run some frames so enemies/boss move and AI ticks
step(g, 200)
print("enemies:", len(playing.enemies), "kills:", playing.kills,
      "player hp:", round(playing.player.hp, 1))

# kill the boss to trigger clear
if playing.boss:
    playing.boss.take_damage(99999, g.sound)
    step(g, 3)
    for _ in range(6):
        press(g, pygame.K_SPACE)
        step(g, 3)
print("final top:", type(g.stack[-1]).__name__)
print("SMOKE OK")
