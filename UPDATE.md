# Updating the website

This repo is the public, read-only copy of the NFL Bet Analyzer artifact
(https://claude.ai/artifact/4QvMvgV5MuaH3B725gmMtj), served by GitHub Pages at
https://joshxyli.github.io/NFL-Bet-Analyzer/ . A scheduled Claude task runs these steps.

1. Export the artifact database. For each collection `lines`, `pulls`, `meta`, `slips`, `log`, `results`, `rescore`,
   call ArtifactData `list` with url https://claude.ai/artifact/4QvMvgV5MuaH3B725gmMtj, `query: {"limit": 1000}` and
   `out_dir: "/tmp/site_db"` (so files land at /tmp/site_db/<collection>/<doc_id>.json and stay out of context).
2. Fetch the current page and model data. Artifact `read` with the url above saves the page's HTML (the result names the
   file); copy it to `index.html`. Artifact `read` with `path: "stats.json"` saves the stats file; copy it to `stats.json`.
   Only replace `index.html` if the saved page contains the text `loadSnapshot` (the website mode); otherwise keep the
   current one and say so in the summary.
3. Build the snapshot: `python3 -I tools/build_data.py /tmp/site_db data.json`.
   It keeps only games that have not ended, drops run-state and usage documents, and never contains API keys
   (keys live only in the owner's browser).
4. Commit and push to `main` if anything changed:
   `git add -A && git commit -m "Update data <UTC time>" && git push origin HEAD:main`.
   The site updates about a minute after the push.
