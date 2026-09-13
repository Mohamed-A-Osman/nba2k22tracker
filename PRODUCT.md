# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

- **Primary:** a group of about 16 friends who played NBA 2K22 5v5 games together, each at a position (PG, SG, SF, PF, C). They check the site mostly on their phones, usually right after a session, to see who's been carrying and to settle arguments.
- **Secondary:** people outside the group the site gets shown to. They have never played with the group, so pages must make sense without insider context: what a game is, what a number covers, and who qualifies for a list.

## Product Purpose

Keep the group's complete record of its NBA 2K22 games and answer three questions: how good each player is over their career, who they beat and who they win with, and who holds the records. Success is getting any of those answers in a few taps on a phone, with an outsider still able to tell what they're looking at.

## Positioning

It is the only record of this group's games. NBA 2K does not keep a friend group's box scores across sessions, let alone lineup combinations and position-against-position matchups; this site holds every box score the group played and breaks them down that way.

## Operating Context

- Viewed mostly on phones, often in the same room or call right after games; links get shared to settle arguments.
- Each game is 5v5. A box score row holds player, position, team (T1 or T2), points, rebounds, assists, steals, blocks, fouls, turnovers, FGM/FGA, 3PM/3PA and a grade. Team totals decide the winner.
- Pages: Career Averages (all positions or one), Matchups (a player against same-position opponents), Teammates (full lineups, or one teammate at a time), Career Highs (per stat), and Upload (a placeholder until OCR works).

## Capabilities and Constraints

- An archive of NBA 2K22 only: 152 games, 16 players, November 2021 to June 2022. No game or season switcher is needed.
- New games will come from uploaded box-score screenshots read by OCR. OCR is not built yet, so the upload page saves nothing.
- Career Averages for all positions lists only players with 10 or more games. The landing page's best-duo highlight needs 15 or more games together.
- Stack: Flask with server-rendered Jinja templates; data in Parquet files queried in memory with DuckDB; hosted on AWS Lambda behind CloudFront at roughly $0 a month. Pages are cached for 5 minutes, and the query parameters `Position`, `Name`, `Type` and `cat` (plus the game log's `With`, `Vs` and `Lineup`) are the cache key, so page URLs keep using them and any new parameter must be added to `template.yaml`.
- Player names are gamer tags; their exact case and punctuation matter (King_Slayer-101, moh-_-1).
- v2 becomes the default site at `/`; v1 stays reachable for comparison.

## Brand Commitments

- Name: 2K22 Stat Tracker.
- No NBA or Getty photography and no league or team marks (copyright). The group's own data and gamer tags are the content.
- Light and dark themes, with a toggle that remembers the choice.
- The user chose the "Arena Night" direction for v2.

## Evidence on Hand

- Real data: `data/player_stats.parquet` (1,398 player-game rows) and `data/game_totals.parquet` (304 team rows), exported from the local Postgres master copy.
- Box-score screenshots (console captures) for all 152 games, imported into `data/screenshots/` by `scripts/import_screenshots.py` and shown on each game's page. Seven extra captures taken before a game's final buzzer are left out.
- There are no photos of the group and no testimonials. Do not invent any.

## Product Principles

1. Every number is real and comes from the box scores; nothing is decorative.
2. Answer the question first: each page leads with its answer (who leads, who wins), then the full detail.
3. Phone first: a page has to work one-handed on a phone before it works on a desktop.
4. Legible to outsiders: say in plain words what a stat covers and who qualifies.
5. Fast and nearly free to run.

## Accessibility & Inclusion

WCAG 2.1 AA: text contrast, full keyboard access (including table sorting), labelled controls, and reduced-motion support. Titles use neutral wording that assumes nothing about who is playing.
