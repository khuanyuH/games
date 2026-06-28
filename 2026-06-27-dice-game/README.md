# 🎲 Press Your Luck — Dice Game (MVP)

A tiny "push your luck" dice game you play against the computer. Single self-contained
`index.html` — no build step, no dependencies. Just open it in a browser.

## How to play

You and the computer each take **3 turns**, alternating (you go first).

On a turn:

1. **Roll** a six-sided die. The face value is added to your **turn sum**.
2. After each roll you choose to either:
   - **Bank** — add your turn sum to your game total and end the turn, or
   - **Roll again** to push your turn sum higher.
3. **The catch:** if you roll a number you've **already rolled this turn**, you **bust** —
   your turn sum drops to 0 and the turn passes to your opponent.

The set of "already rolled" numbers **resets at the start of each turn**.

After both players have taken 3 turns, the **highest game total wins** (ties are possible).

First move is decided by a **coin flip** each game (see "second-mover advantage" below).
There are two opponents, selectable in-game:

### Perfect (solved) — default

This game is a finite, perfect-information, zero-sum game, so it is **solvable exactly** by
backward induction. The agent plays the **provably optimal** move — it maximizes its
probability of *winning* (not its points), pushing harder when behind and banking
conservatively when ahead, calibrated to the exact score gap and turns remaining.

Under perfect play by both sides, the **second mover wins ≈ 56.9%** vs ≈ 39.5% (3.6% ties).
Acting second is a genuine advantage because that player always knows the opponent's banked
total and can calibrate final-turn risk perfectly — hence the coin flip for fairness.

The solver is in `solver.py` / `compare.py` and is ported to JavaScript inside `index.html`
(`vStart` / `vDec` / `optimalShouldBank`). Full analysis is in **`STRATEGY.md`**.

### Risk-aware (beatable)

A simpler heuristic for an easier game. After each roll it weighs its bust probability
(`k / 6`, where *k* = distinct numbers held) against the average points a safe roll would
add, and rolls only while expected gain beats expected loss, with catch-up/lead-protection
on the last turn. It beats a naive "always bank at 12" player ~70% of the time — competent
but very beatable.

## Run it

Open `index.html` in any modern browser. That's it.

## Files

- `index.html` — the entire game (markup, styling, logic, and the embedded optimal solver).
- `STRATEGY.md` — analysis: solvability, the optimal policy, second-mover advantage, and why
  self-play isn't needed.
- `solver.py` — backward-induction solver (optimal value, win/tie/loss, stopping frontier).
- `compare.py` — optimal-vs-greedy matchup table + Monte Carlo verification.
- `README.md` — this file.
