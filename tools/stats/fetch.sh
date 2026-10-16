#!/bin/sh
# Download the nflverse files the stats builder reads into $1 (default /tmp/nfldata).
set -e; D=${1:-/tmp/nfldata}; mkdir -p "$D"; B=https://github.com/nflverse/nflverse-data/releases/download
for p in schedules/games.csv depth_charts/depth_charts_2026.csv \
  stats_player/stats_player_week_2025.csv stats_player/stats_player_week_2026.csv \
  stats_team/stats_team_week_2025.csv stats_team/stats_team_week_2026.csv \
  snap_counts/snap_counts_2025.csv snap_counts/snap_counts_2026.csv \
  pbp/play_by_play_2025.csv.gz pbp/play_by_play_2026.csv.gz \
  injuries/injuries_2025.csv injuries/injuries_2026.csv rosters/roster_2026.csv; do
  curl -sSLf --retry 2 -o "$D/$(basename $p)" "$B/$p"
done
echo FETCHED
