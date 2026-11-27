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
- **Recommendation (per the decision rule: shrink, do not revert):**
  1. **Halve the zero-production term for RB2+ receiving yards** (`SHAPE.RB.player_reception_yds.z[2]` 1.545 → 0.7725). It is the only variant tested that improved both periods at every trust level, on both Brier and return. It does not touch RB1.
  2. **Keep the RB2+ rushing shape.** Reverting RB2+ to the old model was worse in weeks 5-9 at every trust level and no better in weeks 10-11. The rushing shape is a large Brier gain in both periods (0.2601 vs 0.2948, and 0.2569 vs 0.2844).
  3. **Do not cut the WR3+ zero-production term yet.** A 25% cut helped weeks 10-11 but cost return in weeks 5-9. A 50% cut fixed the level but worsened weeks 5-9 Brier and return at 60-100% trust. Re-check once week 12 is graded.
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
  - **Week 12 is not graded.** No week 12 results are saved yet, and ESPN was not reachable from this session. On Nov 27 only GB@LAR, CHI@DET, PHI@DAL and KC@BUF had finished.
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
- Week 12 should be added once its results are saved (the "fetch game results" task). Box score lookups should come from ESPN only, with a cache-busting parameter on each link, for example `https://www.espn.com/nfl/boxscore/_/gameId/<id>?_cb=<unix time>` or `https://site.api.espn.com/apis/site/v2/sports/football/nfl/summary?event=<id>&_cb=<unix time>`. Then re-run the steps below with weeks `10,11,12`.
- The four earlier docs this builds on (`recent-weeks-diagnosis-nov-2026.md`, `change-log-fringe-under-trust-nov-26.md`, `wr-receiving-shape-and-opponent-test.md`, `rb-te-shape-test.md`) were not in the repo, its history, the tools zip or Google Drive. So this doc goes by the code, the edit files and the app's own comments.

## How to re-run (scripts in `claude/rescore_w10_12/`)

```
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
