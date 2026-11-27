# Re-score of weeks 10-12: did the Nov 10 WR/RB shape cause the under losses?

Written Nov 27, 2026. Step 1 of the recent-weeks diagnosis.

## Short answer

- **Partly, yes.** On weeks 10-11 the new shape is worse on unders than the pre-Nov 10 model at every trust level with a real number of bets.
  - Positive-edge unders lost 31.8 units against 25.8 for the old model at 30% trust, 32.9 against 20.7 at 60%, and 39.9 against 31.8 at 100% ($1 flat bets).
  - So the shape change accounts for roughly 6 to 12 units of the under losses. The rest would have been lost under the old model too.
- **Where it comes from:** the new shape's extra lean to the under on low-volume players (WR3+ and RB2+). On these lines the market itself was close to right, so the extra lean was too much:

  | | Weeks 10-11: new / old / actual under rate | Weeks 5-9: new / old / actual |
  |---|---|---|
  | WR3+ | 55.8 / 51.4 / 42.6 | 54.9 / 50.6 / 50.6 |
  | RB2+ | 57.5 / 47.5 / 48.7 | 59.1 / 51.5 / 51.2 |

  It shows in weeks 5-9 too, so it is a lasting bias, not a two-week accident.
- **The new shape is still the better model overall.**
  - It beats the old model on Brier in every WR/RB group in both periods. The one exception is RB2+ receiving yards.
  - It leaves more money than the old one in weeks 5-9 (re-scored) at every trust level.
  - Both trail the market on Brier everywhere, as before.
- **Week 12 so far (4 games graded from nflverse, see below) went the other way.** Unders hit (WR3+ 60%, RB2+ 54%), and the new model did slightly better than the old there. With week 12 included, weeks 10-12 still show the new shape worse on unders: positive-edge unders lost 35.9 vs 30.1 units at 30% trust, 25.6 vs 15.2 at 60%, and 31.4 vs 22.7 at 100%.
- **Recommendation (per the decision rule: shrink, do not revert):**
  1. **Halve the zero-production term for RB2+ receiving yards** (`SHAPE.RB.player_reception_yds.z[2]` 1.545 → 0.7725). It does not touch RB1.
     - It improves RB2+ receiving-yards Brier in weeks 5-9 and weeks 10-12 (0.2705 vs 0.2815) and brings its under lean close to the market.
     - It improved return at every trust level in weeks 5-9 and weeks 10-11. With week 12 added, the return effect is small and mixed: +6.3 units at 30%, -1.2 at 60%, -1.2 at 100%, on WR/RB lines in weeks 10-12.
     - Week 12 alone has only 8 RB2+ receiving-yards lines, and it went slightly against the change there.
  2. **Keep the RB2+ rushing shape.** Reverting RB2+ to the old model was worse in weeks 5-9 at every trust level and no better in weeks 10-11. The rushing shape is a large Brier gain in every period (weeks 10-12: 0.2578 vs 0.3086; weeks 5-9: 0.2569 vs 0.2844).
  3. **Do not cut the WR3+ zero-production term yet.** A 25% cut is the best variant on weeks 10-12 (Brier 0.2687, and the smallest losses at every trust level) but cost return in weeks 5-9. A 50% cut fixed the level but worsened weeks 5-9 Brier and return at 60-100% trust. Re-check once all of week 12 is graded.
  4. **Leave the Nov 26 fringe-under rule in for now, but treat its evidence as weak.** It was built from these same week 10-11 losses, so weeks 10-11 are in-sample for it. It helps a lot at 30% trust, and nothing at 60% or 100% (it removes the better fringe unders there). In weeks 5-9 it is mixed: +4.6 units at 30%, -5.6 at 60%, +4.1 at 100%. Halving the RB2+ receiving term overlaps with it.
- Nothing has been published to the app. The change in item 1 needs your go-ahead.

## What was compared

- **NEW** = the current published app (artifact version 1795758316-836b): WR shape, WR1/2 × 1.07, and RB shape. It also has the Nov 26 fringe rule, which is only on the board's blending step (`index.html` line ~1411): the model's weight is halved for unders on WR3+/RB2+ lines of 2.5 catches or 20.5 yards or less.
- **OLD** = the same page with the 6 RB edits undone (`out/edits_rb.json` swapped) and then `out/edits_revert.json` applied. All 14 edits matched exactly once.
  - The repo's `index.html` is stale: it was last updated Nov 17 and has no fringe rule. So the published page was used, not the repo copy.
- **Inputs:** every saved pre-kickoff line in `data.json` `log` for games graded in `results`, WR/RB/TE/QB catches, receiving yards and rushing yards. Both models get the same saved projection (field 8), so only the step from projection to chance differs.
  - The old model's yardage spread and its small-line fallback (line under 5 or projection under 15) were rebuilt from each player's `stats.json` game log, cut off before that game.
- **Shape group (WR1/2, WR3+, RB1, RB2+)** was read off the chance the app actually saved: for each player-game, whichever group reproduces it. This uses the depth chart as it stood at save time, not today's.
- **Checks:**
  - The rebuilt NEW chances match the saved week 10-11 chances: median error 0.0002 on yards, 0.005 on catches (the saved projection is rounded to 0.1).
  - The rebuilt OLD chances match the saved weeks 5-9 chances to a median of 0.005-0.008 on smooth lines. They are looser (about 0.04) on small yardage lines that use the game log, because `stats.json` keeps only the last 10 games. Those are 140 of 1,520 week 10-11 WR/RB rows. Dropping them changes no conclusion (sensitivity run kept in the scripts).
  - The grader reproduces the app's own `backtest()` on the saved chances: 813 vs 809 bets, -64.1 vs -63.6 units at 10% trust. The gap is a few name matches.
- **Counting:**
  - Brier uses one row per player-line (event, player, market, line), over side, with the market as the mean no-vig chance across books.
  - ROI uses one pick per player and prop, as in the app's Backtest: the best-EV side across books and lines, $1 at the saved book price.
  - So a leg that sits on several slips is counted once.
- **Weeks:** weeks 10 and 11 = 27 games (Nov 12-23), all out of sample for the Nov 10 change.
  - **Week 12: 4 of 16 games graded.** No week 12 results were saved in `data.json` yet, so box scores for the games finished by Nov 27 (GB@LA, CHI@DET, PHI@DAL, KC@BUF) were taken from nflverse (`stats_player_week_2026.csv` from the nflverse-data `stats_player` release). They were added only to a scratch copy of `data.json`, not to the repo.
  - nflverse agrees exactly with the saved results on weeks 10-11: 620 of 620 player rows have the same rushing yards, catches and receiving yards.
  - The rest of week 12 (Black Friday through MNF) still needs grading.
  - Weeks 5-9 are shown only as context. They were used to check the Nov 10 changes (the WR1/2 level was tuned on them), so they are not a clean test.

## Weeks 10-11 results (all props in the three markets, WR/RB/TE/QB)

**Positive-edge picks (what the Backtest calls "Any positive edge")**, W-L and ROI

| Trust | Model | All | Overs | Unders | WR1/2 U | WR3+ U | RB1 U | RB2+ U | WR1/2 O | WR3+ O | RB1 O | RB2+ O |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 10% | old | 13-17, -13% | 7-9, -12% | 6-8, -14% | 3-0, +103% | 0-3, -100% | 2-0, +99% | 0-3, -100% | 1-1, +4% | 1-4, -62% | 2-1, +47% | 3-3, -6% |
| 10% | new | 6-7, -4% | 1-1, +26% | 5-6, -10% | 2-0, +98% | 0-2, -100% | 2-0, +99% | 0-2, -100% | 0-1, -100% | – | 1-0, +152% | – |
| 10% | new+fringe | 6-5, +13% | 1-1, +26% | 5-4, +11% | 2-0, +98% | – | 2-0, +99% | 0-2, -100% | 0-1, -100% | – | 1-0, +152% | – |
| 30% | old | 163-181, -11% | 67-71, -8% | 96-110, -13% | 28-36, -19% | 9-20, -44% | 22-21, -2% | 8-13, -28% | 11-11, -3% | 16-15, -2% | 12-12, -4% | 13-18, -21% |
| 30% | new | 121-148, -14% | 33-37, -9% | 88-111, -16% | 19-22, -13% | 7-25, -61% | 20-23, -10% | 13-21, -25% | 10-9, +3% | 4-5, -9% | 4-5, -12% | 0-3, -100% |
| 30% | new+fringe | 116-123, -8% | 33-37, -9% | 83-86, -7% | 19-22, -13% | 6-10, -30% | 20-23, -10% | 9-11, -15% | 10-9, +3% | 4-5, -9% | 4-5, -12% | 0-3, -100% |
| 60% | old | 267-289, -10% | 97-121, -15% | 170-168, -6% | 57-57, -6% | 16-29, -37% | 33-32, -4% | 14-19, -20% | 16-24, -22% | 19-20, -8% | 14-24, -30% | 23-27, -13% |
| 60% | new | 241-266, -10% | 58-72, -14% | 183-194, -9% | 43-43, -6% | 18-40, -44% | 37-37, -6% | 35-43, -13% | 16-18, -5% | 9-12, -18% | 8-10, -13% | 0-6, -100% |
| 60% | new+fringe | 223-249, -10% | 58-72, -14% | 165-177, -9% | 43-43, -6% | 10-32, -57% | 37-37, -6% | 25-34, -18% | 16-18, -5% | 9-12, -18% | 8-10, -13% | 0-6, -100% |
| 100% | old | 326-346, -9% | 128-144, -11% | 198-202, -8% | 65-63, -5% | 21-37, -36% | 40-40, -6% | 15-25, -29% | 20-28, -19% | 30-22, +7% | 17-25, -22% | 28-32, -11% |
| 100% | new | 303-345, -12% | 78-107, -20% | 225-238, -9% | 52-56, -10% | 29-47, -28% | 43-46, -9% | 44-52, -12% | 21-28, -15% | 11-14, -17% | 12-21, -30% | 1-7, -71% |
| 100% | new+fringe | 288-331, -12% | 78-107, -20% | 210-224, -9% | 52-56, -10% | 17-40, -46% | 43-46, -9% | 41-45, -8% | 21-28, -15% | 11-14, -17% | 12-21, -30% | 1-7, -71% |

**Every pick, no filter**, W-L and ROI

| Trust | Model | All | Overs | Unders | WR1/2 U | WR3+ U | RB1 U | RB2+ U | WR1/2 O | WR3+ O | RB1 O | RB2+ O |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 10% | old | 400-413, -8% | 164-182, -11% | 236-231, -6% | 73-67, -3% | 26-41, -32% | 48-50, -8% | 20-29, -21% | 25-36, -20% | 35-30, +1% | 23-31, -18% | 30-36, -15% |
| 10% | new | 402-411, -7% | 123-139, -11% | 279-272, -6% | 72-62, -0% | 40-56, -24% | 51-54, -9% | 47-56, -12% | 30-37, -13% | 20-16, +5% | 19-28, -22% | 3-9, -54% |
| 10% | new+fringe | 402-411, -7% | 123-139, -11% | 279-272, -6% | 72-62, -0% | 40-56, -24% | 51-54, -9% | 47-56, -12% | 30-37, -13% | 20-16, +5% | 19-28, -22% | 3-9, -54% |
| 30% | old | 400-413, -8% | 165-184, -10% | 235-229, -6% | 73-67, -3% | 25-41, -33% | 48-49, -8% | 20-28, -19% | 25-36, -20% | 35-31, +0% | 23-32, -20% | 31-36, -12% |
| 30% | new | 401-412, -7% | 123-139, -11% | 278-273, -6% | 72-62, +0% | 39-57, -24% | 51-54, -9% | 47-56, -12% | 30-37, -11% | 20-16, +5% | 19-28, -22% | 3-9, -54% |
| 30% | new+fringe | 401-412, -7% | 123-139, -11% | 278-273, -6% | 72-62, +0% | 39-57, -24% | 51-54, -9% | 47-56, -12% | 30-37, -11% | 20-16, +5% | 19-28, -22% | 3-9, -54% |
| 60% | old | 398-415, -8% | 164-185, -11% | 234-230, -7% | 73-67, -3% | 25-41, -33% | 48-49, -8% | 19-28, -24% | 25-36, -20% | 35-31, +0% | 23-32, -19% | 31-37, -13% |
| 60% | new | 400-413, -7% | 122-139, -11% | 278-274, -6% | 72-62, +0% | 39-57, -23% | 51-54, -9% | 47-56, -12% | 30-37, -11% | 20-16, +5% | 19-28, -22% | 3-9, -53% |
| 60% | new+fringe | 400-413, -7% | 122-139, -11% | 278-274, -6% | 72-62, +0% | 39-57, -24% | 51-54, -9% | 47-56, -12% | 30-37, -11% | 20-16, +5% | 19-28, -22% | 3-9, -53% |
| 100% | old | 399-414, -8% | 165-185, -11% | 234-229, -6% | 73-67, -3% | 25-41, -33% | 48-48, -7% | 19-28, -24% | 25-36, -20% | 35-31, +0% | 24-32, -17% | 31-37, -13% |
| 100% | new | 398-415, -8% | 121-140, -12% | 277-275, -6% | 71-63, -1% | 39-57, -23% | 51-54, -9% | 47-56, -12% | 29-38, -14% | 20-16, +5% | 19-28, -22% | 3-9, -53% |
| 100% | new+fringe | 398-415, -8% | 121-140, -12% | 277-275, -6% | 71-63, -1% | 39-57, -23% | 51-54, -9% | 47-56, -12% | 29-38, -14% | 20-16, +5% | 19-28, -22% | 3-9, -53% |

**Brier score, one row per player-line (over side), lower is better**

| Group | Lines | Over rate | Market | Old | New | Under chance: actual / market / old / new |
|---|---|---|---|---|---|---|
| All WR/RB/TE/QB | 828 | 0.483 | 0.2477 | 0.2739 | 0.2666 | 0.517 / 0.505 / 0.525 / 0.545 |
| WR1/2 | 205 | 0.454 | 0.2503 | 0.2745 | 0.2634 | 0.546 / 0.510 / 0.561 / 0.540 |
| WR3+ | 136 | 0.574 | 0.2463 | 0.2932 | 0.2836 | 0.426 / 0.509 / 0.514 / 0.558 |
| RB1 | 156 | 0.474 | 0.2485 | 0.2697 | 0.2663 | 0.526 / 0.504 / 0.530 / 0.551 |
| RB2+ | 115 | 0.513 | 0.2542 | 0.3039 | 0.2868 | 0.487 / 0.498 / 0.475 / 0.575 |
| TE | 170 | 0.424 | 0.2398 | 0.2510 | 0.2510 | 0.576 / 0.499 / 0.523 / 0.523 |
| QB | 46 | 0.522 | 0.2513 | 0.2386 | 0.2386 | 0.478 / 0.504 / 0.514 / 0.514 |
| fringe lines (WR3+/RB2+, <=2.5 rec / <=20.5 yds) | 161 | 0.547 | 0.2493 | 0.2973 | 0.2865 | 0.453 / 0.506 / 0.498 / 0.552 |
| WR1/2 player_receptions | 103 | 0.427 | 0.2509 | 0.2696 | 0.2657 | 0.573 / 0.520 / 0.578 / 0.548 |
| WR1/2 player_reception_yds | 99 | 0.475 | 0.2500 | 0.2830 | 0.2640 | 0.525 / 0.500 / 0.545 / 0.533 |
| WR3+ player_receptions | 71 | 0.535 | 0.2427 | 0.2843 | 0.2821 | 0.465 / 0.517 / 0.528 / 0.558 |
| WR3+ player_reception_yds | 65 | 0.615 | 0.2502 | 0.3030 | 0.2852 | 0.385 / 0.501 / 0.499 / 0.558 |
| RB1 player_receptions | 54 | 0.519 | 0.2459 | 0.2755 | 0.2750 | 0.481 / 0.513 / 0.556 / 0.580 |
| RB1 player_reception_yds | 51 | 0.431 | 0.2497 | 0.2582 | 0.2568 | 0.569 / 0.500 / 0.504 / 0.539 |
| RB1 player_rush_yds | 51 | 0.471 | 0.2500 | 0.2752 | 0.2666 | 0.529 / 0.500 / 0.530 / 0.533 |
| RB2+ player_receptions | 31 | 0.516 | 0.2655 | 0.3467 | 0.3307 | 0.484 / 0.491 / 0.499 / 0.536 |
| RB2+ player_reception_yds | 31 | 0.613 | 0.2500 | 0.2765 | 0.2886 | 0.387 / 0.502 / 0.483 / 0.594 |
| RB2+ player_rush_yds | 53 | 0.453 | 0.2500 | 0.2948 | 0.2601 | 0.547 / 0.500 / 0.457 / 0.587 |

## Variants (WR/RB lines only)

Under lean is the mean model under chance; lower Brier is better; profit is positive-edge picks in units.

| Period | Set | Actual under | Market | Old | New | Halve RB2+ rec-yds zero term | ...plus WR3+ term −25% | Halve all zero terms |
|---|---|---|---|---|---|---|---|---|
| Wk 10-11 | WR3+ under / Brier | 0.426 | 0.509 / 0.2463 | 0.514 / 0.2932 | 0.558 / 0.2836 | 0.558 / 0.2836 | 0.537 / 0.2818 | 0.525 / 0.2834 |
| Wk 10-11 | RB2+ under / Brier | 0.487 | 0.498 / 0.2542 | 0.475 / 0.3039 | 0.575 / 0.2868 | 0.557 / 0.2819 | 0.557 / 0.2819 | 0.501 / 0.2901 |
| Wk 10-11 | RB2+ rec yds | 0.387 | 0.502 / 0.2500 | 0.483 / 0.2765 | 0.594 / 0.2886 | 0.525 / 0.2702 | 0.525 / 0.2702 | 0.525 / 0.2702 |
| Wk 10-11 | All WR/RB Brier | | 0.2497 | 0.2830 | 0.2730 | 0.2721 | 0.2717 | 0.2736 |
| Wk 10-11 | Profit at 30 / 60 / 100% | | | -40.3 / -63.0 / -65.3 | -41.9 / -59.4 / -79.4 | -34.7 / -58.8 / -78.8 | -31.2 / -52.1 / -72.1 | -33.9 / -54.2 / -75.0 |
| Wk 5-9 | WR3+ under / Brier | 0.506 | 0.505 / 0.2473 | 0.506 / 0.2607 | 0.549 / 0.2534 | 0.549 / 0.2534 | 0.526 / 0.2541 | 0.513 / 0.2565 |
| Wk 5-9 | RB2+ under / Brier | 0.512 | 0.502 / 0.2486 | 0.515 / 0.2711 | 0.591 / 0.2591 | 0.573 / 0.2553 | 0.573 / 0.2553 | 0.525 / 0.2626 |
| Wk 5-9 | RB2+ rec yds | 0.475 | 0.501 / 0.2502 | 0.515 / 0.2590 | 0.613 / 0.2642 | 0.554 / 0.2512 | 0.554 / 0.2512 | 0.554 / 0.2512 |
| Wk 5-9 | All WR/RB Brier | | 0.2477 | 0.2643 | 0.2551 | 0.2543 | 0.2545 | 0.2568 |
| Wk 5-9 | Profit at 30 / 60 / 100% | | | -23.3 / -38.0 / -39.1 | +6.3 / +13.5 / +3.5 | +11.8 / +19.1 / +9.9 | +9.3 / +15.6 / +2.3 | +11.4 / -15.8 / -30.5 |

- With the fringe rule on top of NEW, profit is -21.9 / -58.1 / -79.8 in weeks 10-11 and +10.9 / +7.9 / +7.6 in weeks 5-9.
- The gap between the new and old models' under lean is solid in both periods (95% range by game, bootstrap):
  - weeks 10-11: WR3+ +0.044 [0.029, 0.058], RB2+ +0.101 [0.080, 0.122];
  - weeks 5-9: WR3+ +0.043 [0.033, 0.055], RB2+ +0.075 [0.063, 0.088].
- At 10% trust there are only 10 to 30 positive-edge picks per model, too few to read.
- Blended Brier (the chance actually bet, trust × model + rest × market) is never better than the market alone in weeks 10-11 at any trust level. In weeks 5-9 it is level with or a hair better than the market up to 30% trust.

## Caveats

- Two weeks is small: 136 WR3+ lines and 115 RB2+ lines. WR3+ overs hit 57% in weeks 10-11, and the market missed that too (it had them at 49%). Part of the under loss is that, not the model.
- Weeks 5-9 groups: 696 of 5,332 rows had no rescore match. Those took today's depth chart, which may differ from the one at the time.
- The rest of week 12 should be added once it is played. Use nflverse for box scores, not ESPN: download a fresh `stats_player_week_2026.csv`, run `add_nflverse_results.py`, then re-run the steps below with weeks `10,11,12`.
- The four earlier docs this builds on (`recent-weeks-diagnosis-nov-2026.md`, `change-log-fringe-under-trust-nov-26.md`, `wr-receiving-shape-and-opponent-test.md`, `rb-te-shape-test.md`) were not in the repo, its history, the tools zip or Google Drive. So this doc goes by the code, the edit files and the app's own comments.

## Week 12 so far (4 games, from nflverse) and weeks 10-12 combined

Under lean / Brier on WR/RB lines, and positive-edge profit in units at 30 / 60 / 100% trust (WR/RB lines only).

| Period | Set | Lines | Actual under | Market | Old | New | Halve RB2+ rec-yds term | ...plus WR3+ −25% | Halve all |
|---|---|---|---|---|---|---|---|---|---|
| Wk 12 | WR3+ | 20 | 0.600 | 0.509 / 0.2468 | 0.515 / 0.2097 | 0.551 / 0.2148 | 0.551 / 0.2148 | 0.529 / 0.2159 | 0.518 / 0.2162 |
| Wk 12 | RB2+ | 28 | 0.536 | 0.497 / 0.2331 | 0.473 / 0.3232 | 0.576 / 0.2521 | 0.556 / 0.2572 | 0.556 / 0.2572 | 0.485 / 0.2798 |
| Wk 12 | All WR/RB | 102 | 0.549 | 0.505 / 0.2399 | 0.520 / 0.2614 | 0.550 / 0.2490 | 0.544 / 0.2504 | 0.540 / 0.2506 | 0.518 / 0.2569 |
| Wk 12 | Profit | | | | -8.6 / -0.2 / +0.8 | -8.1 / +2.4 / +2.9 | -9.0 / +0.6 / +1.1 | -8.1 / -2.0 / +0.4 | -10.2 / -3.3 / -2.6 |
| Wk 10-12 | WR3+ | 156 | 0.449 | 0.509 / 0.2464 | 0.514 / 0.2825 | 0.557 / 0.2748 | 0.557 / 0.2748 | 0.536 / 0.2734 | 0.524 / 0.2748 |
| Wk 10-12 | RB2+ | 143 | 0.497 | 0.498 / 0.2501 | 0.475 / 0.3077 | 0.576 / 0.2800 | 0.557 / 0.2770 | 0.557 / 0.2770 | 0.498 / 0.2881 |
| Wk 10-12 | RB2+ rec yds | 39 | 0.436 | 0.501 / 0.2512 | 0.479 / 0.2885 | 0.596 / 0.2815 | 0.526 / 0.2705 | 0.526 / 0.2705 | 0.526 / 0.2705 |
| Wk 10-12 | All WR/RB | 714 | 0.510 | 0.506 / 0.2483 | 0.526 / 0.2799 | 0.553 / 0.2696 | 0.549 / 0.2690 | 0.545 / 0.2687 | 0.530 / 0.2712 |
| Wk 10-12 | Profit | | | | -48.9 / -63.2 / -64.5 | -50.0 / -57.0 / -76.5 | -43.7 / -58.2 / -77.7 | -39.2 / -54.1 / -71.7 | -44.0 / -57.5 / -77.6 |

- **All props (WR/RB/TE/QB), positive-edge unders, weeks 10-12, units at 30 / 60 / 100% trust:**
  - old: -30.1 / -15.2 / -22.7
  - new: -35.9 / -25.6 / -31.4
  - new + fringe rule: -15.4 / -29.4 / -33.6
- **Week 12 alone, all props:** new +1.4 vs old -1.2 at 60% trust, and new +5.1 vs old +3.1 at 100%.
- The fringe rule still helps only at 30% trust.

## How to re-run (scripts in `claude/rescore_w10_12/`)

```
python3 -I add_nflverse_results.py <repo> stats_player_week_2026.csv 12 <scratch repo dir>   # adds nflverse box scores for games missing from results; use <scratch repo dir> as <repo> below
python3 -I build_old.py index.new.html <wr_model_tools dir> index.old.html   # index.new.html = published page (Artifact read)
python3 -I collect.py <repo> 10,11 jobs_new.json ; python3 -I collect.py <repo> 5,6,7,8,9 jobs_old.json
node eval.js index.old.html index.new.html jobs_new.json ev_new.json          # same for jobs_old -> ev_old
python3 -I validate.py                                                          # rebuilt vs saved chances
python3 -I grade.py jobs_new.json ev_new.json g_w1011.json [--no-thin] ; python3 -I report.py g_w1011.json
node variants.js jobs_new.json var_new.json                                     # same for jobs_old -> var_old
python3 -I compare.py <repo> jobs_new.json ev_new.json var_new.json saved c_w1011.json
python3 -I compare.py <repo> jobs_old.json ev_old.json var_old.json rescore c_w59.json
```

`eval.js` and `variants.js` write `pm_*.js` next to themselves, so run them from a working copy.

## Profit levers, checked with the app's own backtest (added Nov 27)

- **Method:**
  - Each proposed change was applied to the saved lines, and the published app's `PM.backtest()` was run on them: all player props, best-EV side per player-prop.
  - Results are shown at sportsbook prices and at pick'em break-evens of 54.25% and 57.74% (the backtest's `be` option, which pays 1/break-even).
  - Weeks 10-12 (31 games: weeks 10-11 plus 4 week-12 games from nflverse) are the clean test. Weeks 5-9 (56 games) use the app's re-scored lines and are a second look.
  - Ranges are 90% intervals from resampling games, on the change in positive-edge profit against the current model.
  - The per-game runs add up exactly to a single full backtest run (367 bets, −48.6 units at 30% trust in weeks 10-12).

| Proposal | Weeks 10-12 (test) | Weeks 5-9 | Verdict |
|---|---|---|---|
| Model off for WR1/2, WR3+ and RB2+ (model chance := market), model kept for RB1, TE, QB | Sportsbook prices: +42.0 [+18, +66] at 30%, +47.2 [+18, +76] at 60%, +51.8 [+15, +89] at 100%, +3.0 [−2, +9] at 10%. Pick'em at 54.25%: +25 / +41 / +58 at 30 / 60 / 100%. | +8.0 [−28, +43] at 30%, +12.5 [−34, +58] at 60%, +20.1 [−31, +70] at 100%, −3.2 at 10% | **Supported at trust 30% or more.** Large and clear in the test; positive but not significant in weeks 5-9; not supported at 10%. Still loses at sportsbook prices in weeks 10-12 (−6.6 units at 30%). |
| Halve the RB2+ receiving-yards zero term | +6.2 [+0.5, +12.1] at 30%, −1.3 at 60%, −1.2 at 100%, 0 at 10% | +9.2 [+2, +16] at 30%, +8.4 at 60%, +14.9 [+4, +26] at 100% | **Modestly supported**, clearest at 30%. |
| Cap big edges / raise the edge floor | Edge 5+ was the worst bucket per bet (−25% at 30% trust) | Edge 5+ was the best bucket at 30% trust (+10%) | **Not supported either way. Withdrawn.** |
| Pick'em: choose legs by market chance alone | +29.5 units on 317 legs (59.3% hit) at 54.25%; +15.0 on 153 (63.4%) at 57.74%. vs current at 10% trust: +4.1 (P=0.73). vs current at 30% trust: +18.3 | +65.5 on 528 legs (61.0%); +22.5 on 291 (62.2%). vs current at 10% trust: −11.2 (P=0.17) | **Partly supported.** Profitable on book lines in both periods, and better than the model at 30% trust or more. But not better than the current model at 10% trust. |
| Pick'em, model off for WR/RB2+, at 30% trust | +36.2 at 54.25% (best of all runs) | +76.6 at 54.25% (best of all runs) | **Best pick'em setting at 54.25% in both periods**; mixed at 57.74%. |

- **Caveats:**
  - The pick'em results assume the PrizePicks/Pick6 line equals the book line, and they score each leg on its own, not whole slips.
  - The WR/RB2+ rule came from a weight fit on weeks 5-9, so weeks 5-9 are in-sample for it.
  - The "market chance above 63% falls off" pattern (from the leg hit-rate table) rests on 41 and 30 legs. It was not tested in the backtest.

## Tuning the model on weeks 5-11 (added Nov 27)

- **Goal:** maximise the Backtest tab's "Any positive edge" profit (player props at the saved sportsbook price) on weeks 5-11 (101 games, 10,906 graded prop rows).
- **Settings searched:**
  - model weight per group (WR1/2, WR3+, RB1, RB2+, TE, QB) from 0 to 1.5;
  - the WR1/2 lift (1.00 / 1.035 / 1.07);
  - the zero-production terms for WR3+, RB2+ receiving and RB2+ rushing (scaled 0 to 1);
  - an overall over/under lean.
- **Method:**
  - Weeks 5-9 lines were rebuilt with the current shape from their saved projections.
  - Settings were judged by leave-one-week-out: tune on six weeks, score the seventh, repeat for all seven weeks.
  - Week 12 (4 games) was kept out entirely.

**Held-out results, summed over the seven folds (units):**

| Procedure | 10% | 30% | 60% | 100% |
|---|---|---|---|---|
| Current model | +4.4 | −34.6 | −77.6 | −116.2 |
| **Fixed rule: model off for WR1/2, WR3+, RB2+** | **+4.6** | **+19.0** | **−1.0** | **−31.7** |
| On/off per group, tuned | +2.2 | −2.5 | −18.7 | −44.1 |
| Weights 0-1.5 per group, tuned per trust | −8.5 | −0.1 | −26.1 | −35.6 |
| Weights + shape, tuned per trust | −8.9 | −4.9 | −32.0 | −53.7 |
| Everything incl. lean, tuned per trust | −5.2 | −19.0 | −87.0 | −170.3 |

- **More tuning did worse on held-out weeks.**
  - In-sample, the fully tuned model shows +25 / +32 / +8 units at 30 / 60 / 100%, but that does not survive the held-out test.
  - The fixed rule beat every tuned procedure at every trust level.
  - The rule's group weights came from a fit on weeks 5-9, so only weeks 10-11 are fully held out for it.
- **Add-ons to the rule did not reliably help:** QB half or off, TE half or off, RB1 half, small weight back on WR or RB2+, and lean to under or over. The best of them, QB at half weight, gained 3 units at 30% and 17 at 60%. That is within week-to-week noise, so none is recommended.
- **Rule vs current, game bootstrap over weeks 5-11** (90% ranges): +53.7 [+9, +99] at 30%, +76.6 [+20, +129] at 60%, +84.5 [+18, +148] at 100%, +0.2 [−10, +10] at 10%. The rule is better at 30% or more with about 98% probability.
- **Whether the rule itself is profitable:** about 74% likely at 30% trust (+19 units), even at 60%, and still losing at 100%. It cuts losses more than it creates profit.
- **Per week at 30% trust:** +17, +21, −6, −2, −2, −2, −7 for weeks 5 to 11. The gain comes from avoiding the big losing weeks (current: −22 in week 8, −26 in week 10, −19 in week 11).

**Confirmed with the app's own `PM.backtest()` on the saved lines (positive edge):**

| Weeks | Trust | Current | Rule |
|---|---|---|---|
| 5-11 | 10% | 56 bets, +4.4u | 34 bets, +4.6u |
| 5-11 | 20% (board default) | 599 bets, −19.6u (−3.3%) | 354 bets, +5.3u (+1.5%) |
| 5-11 | 30% | 1,202 bets, −31.1u (−2.6%) | 659 bets, +21.1u (+3.2%) |
| 5-11 | 60% | 2,185 bets, −74.5u (−3.4%) | 1,121 bets, −1.5u (−0.1%) |
| 5-11 | 100% | 2,625 bets, −117.4u (−4.5%) | 1,340 bets, −32.4u (−2.4%) |
| 12 (4 games) | 20 / 30 / 60 / 100% | +0.4 / −6.2 / −0.8 / +2.8u | +4.7 / +0.4 / −2.5 / −5.0u |

- With the rule, the Backtest tab's "Every pick, no filter" row gets worse (−141 vs −121 units at 30%). With no model view on those players, that row just takes the best-priced side, which always has a negative edge. It is not a bet the rule would make.
- **Recommendation:** model off for WR1/2, WR3+ and RB2+; keep it for RB1, TE and QB. Use trust 20-30%, not 60-100%. Do not add the other tuned settings. Re-check when the rest of week 12 is graded. Not published.

## Tuning the projection weights on weeks 5-11 (added Nov 27)

**Method:**
- Stats were rebuilt as they stood before each week (weeks 4-11), using your stats builder (`nfl.py` from the "fetch game results and update stats" task, checksum verified) on nflverse data.
  - The week-11 rebuild matches today's `stats.json` exactly: 623 of 623 player game logs, 32 of 32 team baselines and 32 of 32 defence factors.
- Every saved prop line in weeks 5-12 (10,906 rows) was re-projected with a copy of the app's `project()` in which these weights are settings:
  - recency decay (0.88 per game);
  - last-season weight (0.5);
  - usage vs game-log blend (0.7 usage);
  - shrinkage priors: catch rate 15 targets, yards per catch 10 catches, yards per carry 40 carries, passing 100 attempts;
  - strength of the game-script, defence and calibration effects;
  - the weight on the default spread (4).
- Context (opponent, venue, spread, total, roof, wind) comes from the nflverse schedule. Injury inputs could not be rebuilt, so each tweak is applied as a ratio to the saved projection: saved × rebuilt(tweaked) ÷ rebuilt(current).
  - Rebuilt and saved projections agree to a median ratio of 0.99, with 79% within 10%.
- Settings were picked by coordinate search to maximise positive-edge profit at sportsbook prices (summed over 10/20/30/60/100% trust). They were judged by leave-one-week-out on weeks 5-11.

**Settings chosen on almost every fold:**

| Setting | Chosen | Current | Folds |
|---|---|---|---|
| Recency decay | 1.0 (no fade over the last 10 games) | 0.88 | 14 of 14 |
| Last-season games | full weight | half weight | 13 of 14 |
| Passing efficiency prior | 30 attempts | 100 | 14 of 14 |
| Catch-rate prior | 60 targets | 15 | 12 of 14 |

The other settings (blend, yards-per-carry prior, game-script and calibration strength) changed from fold to fold.

**Held-out weeks (leave-one-week-out), units:**

| | 10% | 20% | 30% | 60% | 100% |
|---|---|---|---|---|---|
| Current model | +4.4 | −19.4 | −34.6 | −77.6 | −116.2 |
| Tuned weights, current model | −0.8 | −0.6 | −21.7 | −35.7 | −39.1 |
| WR/RB2+ rule alone | +4.6 | +5.5 | +19.0 | −1.0 | −31.7 |
| **Rule + tuned weights** | **+10.5** | **+43.8** | **+26.1** | **−13.5** | **+0.2** |

**App's own `PM.backtest()` on the saved lines with the chances overlaid** (positive edge, units; weeks 5-11 are in-sample for the tuned sets):

| Configuration | Weeks 5-11: 10 / 20 / 30 / 60 / 100% | Week 12 (4 games): 10 / 20 / 30 / 60 / 100% |
|---|---|---|
| Current | +4.4 / −19.4 / −33.6 / −77.6 / −117.2 | −3.1 / +1.3 / −7.4 / +0.8 / +0.8 |
| Rule | +4.6 / +5.5 / +19.0 / −1.0 / −31.7 | −4.0 / +4.7 / +0.4 / −2.5 / −5.0 |
| Rule + 4 stable changes | +7.7 / +14.5 / +34.7 / +16.9 / +30.1 | −2.1 / +4.4 / −3.6 / −3.8 / −1.7 |
| Rule + full tuned set | +7.1 / +44.1 / +50.0 / +36.0 / +35.3 | −4.0 / +3.5 / −5.5 / −0.6 / −0.5 |

- **Full tuned set** (with the rule):
  - recency decay 1.0;
  - last season at 75% weight;
  - blend 30% usage / 70% game log;
  - catch-rate prior 60, yards-per-catch prior 25, yards-per-carry prior 100, passing prior 30;
  - game script ×1.5;
  - calibration applied ×1.5;
  - default-spread weight 10.
- **Reading:**
  - Tuning the weights helps mainly in combination with the WR/RB2+ rule.
  - The tuning procedure held up on held-out weeks at 20% trust: +43.8 units held out, against +44.1 in-sample. It also held up at 10%, 30% and 100%, but not at 60%.
  - Individual settings are not stable across folds. Seven weeks is a small sample, and week 12 (4 games) does not confirm the gain.
- Not published. Re-check against the rest of week 12 and week 13 before switching.

## Published Nov 27: pricing selector and sportsbook-only quarter weight

Live app version 331 (version id 1795786541-1816), built on version 1795758316-836b. Diff: `claude/rescore_w10_12/app_pricing_quarter_weight.diff`.

- **"Price picks against" selector** next to Trust in model:
  - 2-leg pick'em (3×, 57.7% a leg), the default;
  - 4-leg pick'em (10×, 56.2% a leg);
  - Sportsbook price.

  It sets the board's edge (in pick'em modes the sub-line reads "wins X, needs Y%") and how the Backtest tab grades props (the backtest's `be` option). It is remembered on the device.
- **"Quarter model weight on WRs and backup RBs (sportsbook pricing)" checkbox,** on by default.
  - It applies only under Sportsbook price: the model gets 25% of its usual weight on every WR and any RB not listed RB1, on the board and in the Backtest. The Backtest uses today's depth chart for past games.
  - Under pick'em pricing the weights are unchanged, including the Nov 26 half weight on fringe unders. The weeks 5-11 backtest showed no gain from the quarter weight for pick'em at 10-30% trust.
- The "How it works" Edge note and the Backtest summary tile now name the pricing mode.
- The website copy picks up the new page on its next scheduled update.
