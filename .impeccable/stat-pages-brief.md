# Stat pages (v2): game log

## Scope and mode
All v2 pages, which become the default site at `/`: the landing page (refined), a new game log (`/games`) and game box score (`/games/<id>`), Career Averages, Matchups, Teammates, Career Highs and Upload. v1 moves to `/v1`. Mode: Operate.

## Audience, job, constraints
The friend group, on phones right after sessions, plus outsiders the site is shown to. Jobs: own numbers, head-to-heads and duos, records. Keep the `Position`, `Name`, `Type` and `cat` query parameters; any new filter parameters must be added to the CloudFront cache key in `template.yaml`. Real data only.

## Direction contract
THESIS: The game is the unit of truth. Every page is a view onto the 152 box scores, and every number opens the exact games behind it. It refuses the category default of stat tables that dead-end at an average.
OWN-WORLD: Arena Night, as shipped on the v2 landing: near-black ground #0e0c14 (light #f6f4fa), purple #8b6cf0/#6a4fd1 for links, focus and state only, gold #f2b441/#b07808 reserved for winners and records, Anton only for page titles and final scores, Barlow with tabular numerals for all UI and data, court-line strokes. The recurring atom is the game row: date, final score with the winning side in gold, and each team's top scorer.
STORY: A visitor sees the latest results first, understands who won and by how much, and can go from any average, matchup, duo or record to the games that produced it, so they trust every number because they can check it.
FIRST VIEWPORT: Landing: the headline "Every game we played." (the user replaced "Who's carrying the squad?" as too corny) on the left and, in place of the leader card, the most recent final (date, score, each side's top scorer) on the right; below, the five latest game rows and a plain index of the stat pages with one live line each. Primary action: "Open the game log". Game log: a filter bar (player, with, against) above dated rows grouped by night. Signature interaction: every stat row links to its filtered game log, whose game count equals the row's games number. Motion: 150-200ms state changes only, no load choreography, reduced motion respected.
FORM: Game log, position 5 of 7 on the ranked list (re-roll 1), seed key e880e605.
FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance

## Data facts the log must respect
- 13 games (ids without the `NBA2K22_` prefix) carry entry timestamps from Jun 16, 2022, not play dates; they are listed as "date not recorded".
- Sessions run past midnight, so games are grouped by night: anything before 6 am belongs to the previous evening.
- Teams have 3-5 recorded players; two team grades have typos (`A -`, `B- -`) and are normalised for display.

## Unresolved
- How combo (lineup) rows filter the game log: exact lineup match rather than "includes these teammates".
