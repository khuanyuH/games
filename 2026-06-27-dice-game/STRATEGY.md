# Is this game solved? How should a perfect player play?

Short answer: **yes, it is exactly solvable**, and the prototype now ships with the
provably optimal opponent. No machine learning or self-play is required. This note records
the reasoning and the numbers, all reproducible from the solver scripts.

## 1. What kind of game is this?

The game is a **finite, two-player, zero-sum, perfect-information stochastic game** with
alternating moves:

- **Finite** — each player takes exactly 3 turns; a turn can hold at most the 6 distinct
  die faces, so play always terminates.
- **Perfect information** — both totals, the turn sum, and which numbers have been rolled
  this turn are fully observable. Nothing is hidden.
- **Zero-sum** — one player's win is the other's loss (ties split).
- **Stochastic** — the die adds chance, but chance with *known* probabilities.

Every game in this class is **solvable exactly by backward induction** (dynamic
programming). There is no need to "gather data" to approximate a strategy — the optimal
policy can be computed directly. This game is not famous in the literature, but it is
trivially solved computationally.

## 2. The state space collapses to something tiny

The key reduction: within a turn, the **turn sum equals the sum of the distinct numbers
rolled**, because each success adds a new face's value and a repeat busts. So the
within-turn state is just the *subset* of faces seen — 2⁶ = 64 possibilities.

At the game level, nothing depends on the absolute scores, only their **difference**
`d = (first mover's total) − (second mover's total)`, because the payoff only compares the
two final totals. So the full decision state is:

| Variable | Meaning | Range |
|---|---|---|
| `t` | half-turn index in the fixed order A,B,A,B,A,B | 0–5 |
| `d` | score difference (first mover − second mover) | −63…63 |
| `mask` | set of faces already rolled this turn | 64 subsets |

That is ~20,000 reachable decision nodes — solved in **milliseconds**.

## 3. The exact solution

Defining payoff (win = 1, tie = 0.5, loss = 0) and solving by backward induction:

| Metric (both players perfect) | Value |
|---|---|
| First mover's value | **0.4126** |
| P(first mover wins) | **39.5%** |
| P(tie) | **3.6%** |
| P(second mover wins) | **56.9%** |

**There is a large second-mover advantage.** The player who acts second always knows the
opponent's banked total, and on the final turn can calibrate risk perfectly — pushing only
as far as needed to pass the opponent. This is why the prototype now decides the first move
by a **coin flip** each game, rather than always seating the human first.

An independent Monte Carlo simulation (300,000 games, both sides playing the solved policy)
reproduces these probabilities to within rounding: 0.395 / 0.036 / 0.569.

## 4. How the perfect player actually plays

It is useful to separate two layers.

### Layer A — the score-blind "maximize expected points" stopping rule

If you ignore the opponent and just maximize expected points banked in a turn, the optimal
stopping rule is:

| Distinct numbers held (`k`) | Bust chance next roll | Optimal action |
|---|---|---|
| 1 | 17% | **Always roll** |
| 2 | 33% | Roll if turn sum ≤ 6, otherwise bank |
| 3 | 50% | **Always bank** |
| 4 | 67% | Always bank |
| 5 | 83% | Always bank |
| 6 | 100% | Bank (any roll busts) |

This yields **≈ 6.19 expected points per turn**. Intuition: a single number held is cheap
insurance (only 1-in-6 busts), but once you hold three distinct numbers the 50% bust risk
almost always outweighs the upside.

### Layer B — the score-aware optimal policy (what the agent uses)

The *true* optimum maximizes **probability of winning, not points**. So it deviates from
Layer A based on the score gap and turns remaining:

- **When behind, push harder** — especially on the last turn, it keeps rolling until it
  passes the opponent or busts, even at negative expected-points.
- **When ahead, bank earlier** — it locks in a lead rather than chasing more points it
  doesn't need.
- **When a banked total already clinches the game, it stops immediately.**

This is the policy embedded as **"Perfect (solved)"** in the game.

## 5. How much does optimal play matter?

Comparing the solved policy against the score-blind greedy ("expected-points") policy
(A value = win + 0.5·tie, from the first mover's perspective):

| First mover | Second mover | First mover's value |
|---|---|---|
| Optimal | Optimal | 0.4126 |
| Optimal | Greedy | 0.5517 |
| Greedy | Optimal | 0.3795 |
| Greedy | Greedy | 0.5000 |

Reading this: switching from greedy to optimal is worth roughly **+5 points of win value as
the first mover and +12 as the second mover**, against a greedy opponent. Note that two
greedy players land at exactly 50/50 — the score-blind policy *throws away the entire
second-mover advantage*, because it never looks at the score. Capturing that edge is exactly
what the optimal policy buys.

## 6. So is self-play / "self-improvement" worth building?

**For this game, no — it would be strictly inferior to the exact solution.** Self-play
reinforcement learning can only *approximate* a policy that we can already compute *exactly*
in milliseconds. Building a learner here adds variance, training time, and bugs for no gain.

Self-play / data-gathering becomes the right tool only when one of these is true:

1. **The state space is too large to solve exactly** (not the case here — it's ~20k states).
2. **You want to *exploit* a specific imperfect opponent** rather than play minimax-optimal.
   A learner trained on a particular human's tendencies could beat that human by *more* than
   the game-theoretic optimum — at the cost of being exploitable itself. That is a different
   objective (maximize winnings vs. a known opponent) from "play perfectly."

If exploiting human-specific weaknesses is the real goal, then logging real games and
training an opponent model is justified. If the goal is simply "play perfectly," the solved
policy already does that, optimally and for free.

## 7. Reproducing the numbers

- `solver.py` — backward-induction solver; prints the optimal value, win/tie/loss
  probabilities, and the score-blind stopping frontier.
- `compare.py` — the matchup table above plus an independent Monte Carlo check.

Run with `python3 solver.py` and `python3 compare.py`. The same DP is ported to JavaScript
inside `index.html` (functions `vStart` / `vDec` / `optimalShouldBank`) and verified to
produce the identical first-mover value of 0.4126.
