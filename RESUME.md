# SEGFAULT — RESUME / status

Where the project stands and what's left. Pick any "next" and we go.

## ✅ DONE (works right now)

- **Engine + clean structure** — pygame-ce, state machine, `python3 run.py` just works
- **Zero-asset pipeline** — every sprite + sound generated in code (no downloads)
- **Main menu** — New Game / Continue / Quit, animated code-rain bg, glitch title
- **Character select** — The Dev playable; Anime + Stark in, unlock-gated; stat bars
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

## 🔜 REMAINING (the resume list)

### Big stuff
1. **Chapters 2–5** — currently scaffolded + locked stubs. Each needs a level layout,
   a new enemy, lesson content, and a boss:
   - Ch2 TCP HANDSHAKE — enemy: Packet Sniffer (drains HP on contact)
   - Ch3 DNS LABYRINTH — enemy: DNS Spoofer (spawns fake clones of you)
   - Ch4 TRAINING DATA — enemy: Hallucination (random movement)
   - Ch5 PROMPT INJECTION — the LLM-powered final boss (full payoff)
2. **Weapon system** — right now weapons are baked into each hero. Original design wanted
   unlockable weapons (shotgun, sword, plasma…) + a weapon-select grid.

### Medium
3. **Options screen** — volume sliders / settings UI (volume is saved, just no UI yet)
4. **Tank enemy into Ch1 rotation** — it's coded but not spawned yet
5. **Background music** — only SFX right now
6. **Balance + test Anime & Stark** — only The Dev is thoroughly tuned

### Polish / nice-to-have
7. Screen shake + hit-stop on big hits
8. Persist the AI's "learned profile" across runs (so the boss remembers you next session)
9. Custom hand-drawn pixel art to replace procedural sprites (v2 — code already supports a swap)
10. More enemy variety / difficulty scaling per wave

## Suggested next step
**Chapter 2 (TCP Handshake)** — it reuses everything we built, so it's the fastest way to
make the game visibly *bigger*. Or the **weapon system** if you want combat variety first.
