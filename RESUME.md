# SEGFAULT — RESUME / status

Where the project stands and what's left. Pick any "next" and we go.

## ✅ DONE (works right now)

- **Engine + clean structure** — pygame-ce, state machine, `python3 run.py` just works
- **Zero-asset pipeline** — every sprite + sound generated in code (no downloads)
- **Pixel font everywhere** — whole UI uses an in-code pixel bitmap font
- **Logo / icon** — retro-computer artwork (`assets/title.png`) as the window icon
- **Main menu** — New Game / Continue / Quit, animated code-rain bg, glitch title
- **Character select** — 3 heroes, all sprites done, unlock-gated, stat bars:
  The Dev (start) · The Anime (Ch2) · The Shogun – anime samurai (Ch4)
- **Save system** — JSON in `~/.segfault` (kills, deaths, progress, volume, playtime)
- **Chapter 1: LOCALHOST** — fully playable start → finish
- **Combat feel** — WASD move, mouse aim, melee swing arc, ranged + projectile trails,
  dodge roll w/ i-frames, knockback, hit flash, particles
- **Objective loop** — patch 3 corrupted servers (hold E), survive the swarm
- **Enemies** — null-pointer bug + spider (zigzag AI) [tank + glitch also coded]
- **⭐ Adaptive AI boss (the Heuristic)** — offline pattern-learning + optional local
  Ollama `llama3.2` strategist w/ taunts. Both tested working.
- **Lessons** — typewriter dev-concept popups
- **Pause / Game Over / Victory** screens
- **HUD + minimap + camera** (deadzone follow)
- **F3 debug overlay** — FPS, frame time, entity counts, live AI state, real Ollama status
- **Backed up on GitHub** (private): github.com/shaikh-saud705/segfault-game

## ✅ DONE (polish + content)

- **Options screen** — master vol, music vol, music on/off; in main menu + pause; saved
- **Background music** — procedural synthwave loop (built in code, off-thread at startup)
- **All 3 heroes** unlocked + headless-playtested through the boss (Dev/Anime/Shogun)
- **Enemy variety** — Packet Sniffer (leech), DNS Spoofer (blink), Hallucination (erratic),
  tank — coded and wired into each chapter's roster
- **⭐ ALL 5 CHAPTERS PLAYABLE** start→finish, each with its own theme/colours, lessons
  (TCP handshake, DNS, how LLMs train, prompt injection), enemies, and a named boss:
  Heuristic → Man-in-the-Middle → Rogue Root Server → Untrained Model → The Architect
- **Chapter progression** — Victory screen → NEXT CHAPTER → character select → next chapter;
  final ending after Ch5. Verified by an automated full-game playthrough.
- **Per-character weapon sounds** — pistol (Dev), plasma (Shogun/Anime); repulsor / blaster /
  beep synthesised and ready for the incoming hero roster

## 🔜 REMAINING (the resume list)

### Big stuff
1. **Hero roster expansion** — Iron Man, Ultron, Big Hero (Baymax), Bumblebee, Wall-E as
   original pixel sprites, each tied to a chapter unlock, with their weapon + sound
   (repulsor/blaster/beep already made). NEXT UP.
2. **Weapon system** — weapons are baked into each hero; original design wanted unlockable
   weapons (shotgun, sword, plasma…) + a weapon-select grid.

### Polish / nice-to-have
3. Screen shake + hit-stop on big hits
4. Persist the AI's "learned profile" across runs (boss remembers you next session)
5. Custom hand-drawn pixel art to replace procedural sprites (code already supports the swap)
6. Re-enable chapter-gating for heroes once chapters 2–4 exist (flag `UNLOCK_ALL` in
   `data/characters.py`)

## Suggested next step
**Chapter 2 (TCP Handshake)** — reuses everything we built (incl. the Packet Sniffer enemy
that's already coded), so it's the fastest way to make the game visibly *bigger*.
