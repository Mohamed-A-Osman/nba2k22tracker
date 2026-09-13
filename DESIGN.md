---
name: 2K22 Stat Tracker
description: The complete box-score record of one group's NBA 2K22 games, where every number opens the games behind it.
colors:
  ground-dark: "#0e0c14"
  surface-dark: "#1a1624"
  card-dark: "#15121e"
  text-dark: "#f4f1fa"
  muted-dark: "#a9a1bd"
  faint-dark: "#8f87a3"
  accent-dark: "#8b6cf0"
  button-dark: "#7a5ae6"
  gold-dark: "#f2b441"
  ground-light: "#f6f4fa"
  surface-light: "#ffffff"
  text-light: "#17131f"
  muted-light: "#5f5870"
  faint-light: "#6f6885"
  accent-light: "#6a4fd1"
  gold-display-light: "#b07808"
  gold-text-light: "#8a5e00"
typography:
  display:
    fontFamily: "Anton, 'Arial Narrow', sans-serif"
    fontSize: "2.75rem"
    fontWeight: 400
    lineHeight: 1
  score-final:
    fontFamily: "Anton, 'Arial Narrow', sans-serif"
    fontSize: "4.5rem"
    fontWeight: 400
    lineHeight: 1
  score-row:
    fontFamily: "Anton, 'Arial Narrow', sans-serif"
    fontSize: "1.75rem"
    fontWeight: 400
    lineHeight: 1
  answer:
    fontFamily: "Barlow, 'Segoe UI', 'Helvetica Neue', sans-serif"
    fontSize: "1.25rem"
    fontWeight: 400
    lineHeight: 1.45
  title:
    fontFamily: "Barlow, 'Segoe UI', 'Helvetica Neue', sans-serif"
    fontSize: "1.25rem"
    fontWeight: 700
    lineHeight: 1.3
  body:
    fontFamily: "Barlow, 'Segoe UI', 'Helvetica Neue', sans-serif"
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.5
  data:
    fontFamily: "Barlow, 'Segoe UI', 'Helvetica Neue', sans-serif"
    fontSize: "0.9375rem"
    fontWeight: 400
    fontFeature: "tnum"
  label:
    fontFamily: "Barlow, 'Segoe UI', 'Helvetica Neue', sans-serif"
    fontSize: "0.75rem"
    fontWeight: 700
    letterSpacing: "0.06em"
rounded:
  focus: "4px"
  field: "10px"
  status: "12px"
  panel: "16px"
  pill: "999px"
spacing:
  gutter-phone: "20px"
  gutter-tablet: "32px"
  gutter-desktop: "64px"
  row-y: "14px"
  cell: "12px 14px"
  tap-min: "44px"
components:
  button-primary:
    backgroundColor: "{colors.accent-light}"
    textColor: "{colors.surface-light}"
    rounded: "{rounded.pill}"
    padding: "12px 24px"
    height: "48px"
  segment:
    backgroundColor: "{colors.surface-light}"
    textColor: "{colors.muted-light}"
    rounded: "{rounded.pill}"
    padding: "0 16px"
    height: "44px"
  segment-selected:
    backgroundColor: "{colors.accent-light}"
    textColor: "{colors.surface-light}"
    rounded: "{rounded.pill}"
  chip:
    backgroundColor: "{colors.surface-light}"
    textColor: "{colors.text-light}"
    rounded: "{rounded.pill}"
    padding: "0 16px"
    height: "44px"
  select:
    backgroundColor: "{colors.surface-light}"
    textColor: "{colors.text-light}"
    rounded: "{rounded.field}"
    padding: "10px 40px 10px 14px"
    height: "44px"
  stat-table:
    backgroundColor: "{colors.surface-light}"
    textColor: "{colors.text-light}"
    typography: "{typography.data}"
    rounded: "{rounded.panel}"
  game-row:
    textColor: "{colors.muted-light}"
    padding: "14px 12px"
  icon-button:
    rounded: "{rounded.pill}"
    size: "44px"
---

# Design System: 2K22 Stat Tracker

## Overview

**Creative North Star: "Arena Night"**

The site is a box score read under arena lights: a near-black ground (a pale lilac ground in light mode), purple that only ever means "you can act here", gold that only ever means "this side won" or "this is the record", and thin court-line strokes that belong to the game itself. The game is the unit of truth. Every page is a view onto the box scores, and every number is a door back to the games that produced it, so the visual system spends its emphasis on outcomes and links and nothing else.

Density is that of a scoreboard, not a dashboard. Pages lead with a plain-language answer in muted text with the key name or number in full-strength weight, then the full table or game list. Surfaces are flat and hairline-bordered; there is no photography, no league or team marks, and no ornament beyond the court. Motion is limited to 150 ms state changes, with no load choreography, and is switched off under reduced motion.

Light and dark themes are both first-class (light is the default; the toggle remembers the choice). Every colour role has a value in each theme.

**Key Characteristics:**
- Two display moments only: the page title and the final score, both in Anton.
- Everything else, including every number in every table, is Barlow with tabular numerals.
- Gold marks winners and records; purple marks links, focus and state.
- Court lines are structural on the landing hero and the box score divider, decorative in one clipped header band, and absent from data.
- The game row is the atom; a games count in a table always opens exactly that many games.

## Colors

A cool violet-black night with one action colour and one reward colour.

### Primary
- **Arena Purple** (dark: accent-dark, button-dark; light: accent-light): links, text buttons, the primary button, selected segments, the current-nav underline, focus rings, selection, caret and form accents. It is never used for data emphasis or decoration. The filled button uses the slightly deeper button tone in dark mode so white text keeps contrast.

### Secondary
- **Trophy Gold** (dark: gold-dark; light: gold-display-light for large display text and icons, gold-text-light for small text): the winning side's score in game rows and the box score, "won" results, table leaders, and career-high values. Light mode splits gold in two for contrast: the brighter tone is only legible at display size, so any text under display size uses the darker tone.

### Neutral
- **Night Ground / Lilac Ground** (ground-dark / ground-light): page background.
- **Raised Surface** (surface-dark / surface-light) and **Table Card** (card-dark / white): fields, segments, chips, dropzone, and table panels. The sticky name column shares the card colour so scrolled cells pass beneath it.
- **Ink** (text-dark / text-light): names, headings, emphasised answer words, the winning side's top scorer.
- **Muted** (muted-dark / muted-light): answer copy, losing scores, nav links at rest, table headers.
- **Faint** (faint-dark / faint-light): times, counts, side labels (T1/T2), ranks, footer, arrows.
- **Hairline**: `rgba(255,255,255,0.08)` dark, `rgba(23,19,31,0.1)` light, for every border and row divider.
- **Court Stroke**: purple at 14 to 16% alpha for the header arc and box-score divider; 45 to 50% alpha ("court-strong") for the landing hero's floor lines.
- **Row Hover**: purple at 6 to 8% alpha behind hovered rows.

### Named Rules
**The Trophy Rule.** Gold is reserved for winners and records only. If a gold element does not mark a winning score, a win result, a table leader, or a career high, it is wrong. In light mode, text below display size uses the darker gold text tone, never the display tone.

**The Purple Means Act Rule.** Purple is for links, focus and state only: a purple element is something you can press, the thing that has focus, or the option currently selected. It never highlights data.

## Typography

**Display Font:** Anton (with Arial Narrow), self-hosted, weight 400 only.
**Body Font:** Barlow (with Segoe UI, Helvetica Neue), self-hosted at 400, 500, 600 and 700.

**Character:** Anton is the arena scoreboard, tall and condensed, used sparingly enough to stay loud. Barlow is the stat sheet: a plain grotesque whose tabular numerals keep every column of numbers aligned.

### Hierarchy
- **Display** (Anton 400, 2.75rem, 1.0, uppercase; 2.125rem on phones): the page title, once per page.
- **Final score** (Anton 400, 4.5rem, 1.0; 3.5rem on phones): the two team totals at the top of a box score.
- **Row score** (Anton 400, 1.75rem, 1.0): the two totals inside each game row.
- **Answer** (Barlow 400, 1.25rem, 1.45, max 62ch; 1.0625rem on phones): the lead sentence under each title, muted with the key facts in 600-weight ink.
- **Title** (Barlow 700, 1.25rem, 1.3): section heads such as "Latest games"; the landing caption uses 700 at 1.5rem.
- **Body** (Barlow 400, 1rem, 1.5): default text; notes run at 0.9375rem in the faint tone, max 70ch.
- **Data** (Barlow 400, 0.9375rem, tabular numerals): table cells, game rows, record holders; name cells at 600.
- **Label** (Barlow 700, 0.75rem, 0.06em tracking, uppercase): stat table column headers only. Field labels are 600 at 0.8125rem in sentence case.

### Named Rules
**The Two Moments Rule.** Anton appears only in page titles and final scores (game rows and the box score). Section heads, captions, stat values and records are Barlow.

**The Tabular Rule.** Every number a reader compares is set with tabular numerals.

**The Unbroken Tag Rule.** Gamer tags never break across lines: each tag sits in a no-wrap span, and a lineup of several tags wraps only at the comma between names. Exact case and punctuation of tags are preserved.

## Layout

A single centred column, max 1440px, with side gutters of 64px on desktop, 32px under 1100px, and 20px under 760px. The top bar is an 80px grid (wordmark, nav, theme toggle) with a hairline beneath; on phones it becomes two rows and all nav links stay visible, wrapping onto the second row, each with a 44px tap height. Pages open with a page head (48px top, 28px bottom; 32/20 on phones): title, answer, optional note, then filters, then content.

Filters sit in a wrapping row (16px by 20px gaps) of labelled selects and segmented position radios; on phones each field takes the full width. Forms submit through a hidden-by-JS "apply" button so they still work without scripts.

The landing is two stacked grids: the court hero (court up to 600px beside the caption and primary action, 56px gap) and, 72px below, latest games beside the stat page index (1.4fr to 1fr, 64px gap). Both collapse to one column under 1100px.

Game rows are a five-column grid on desktop (time 5.5rem, score 11.5rem, top scorers, player line, 20px arrow), so the arrow sits at the row's right edge whether or not a player line is present. On phones the row reflows to score and time on the first line, top scorers and the player line beneath, and the arrow spanning the right edge.

### Named Rules
**The 44 Rule.** Every tap target is at least 44px tall: segments, chips, selects, the icon button, and nav links on phones. The primary button is 48px.

**The Court Stays Out of the Data Rule.** Court lines are structural in exactly two places: the landing's half-court hero and the half-court divider (a line with a centre circle) between the two teams on the box score. The only other court drawing is the decorative arc in the header band, clipped to 240px tall (200px on phones), hidden on the landing, and it must never cross a table, a game row, or a form control.

## Elevation & Depth

The system is flat. There are no shadows. Depth comes from tonal layering (card and surface tones over the ground), hairline borders, and the sticky name column's right border when a table scrolls sideways. Hover is a faint purple row tint or a border shift to a purple glow tone; the primary button brightens slightly (brightness 1.08). Focus is a 2px purple outline at 2px offset.

### Named Rules
**The Flat Floor Rule.** Nothing floats. If a component needs separation, it gets a hairline or a surface tone, not a shadow.

## Shapes

Two shape families. Everything you press is a full pill (999px): the primary button, segments, chips and the round icon button. Everything that holds content is a softly rounded panel: tables and the upload dropzone at 16px, status messages at 12px, selects at 10px. Lists of rows (game rows, records, the stat page index) are not boxed at all; they are open rows separated by hairlines. The dropzone alone uses a 2px dashed purple-glow border. Arrows, chevrons and the theme icons are 2px round-capped stroke SVGs, matching the court's line weight.

## Components

### Buttons
- **Shape:** full pill (999px).
- **Primary:** Arena Purple fill (button tone), white Barlow 600 at 16px, 12px by 24px padding, 48px minimum height, optional trailing arrow icon. Full width on phones. One per view at most ("Open the game log").
- **Hover / Focus:** brightness 1.08 over 150ms; 2px purple focus outline.
- **Text button:** unfilled purple Barlow 600 at 0.9375rem, used for table tools ("More stats" / "Fewer stats", "Show the lineups played only once").
- **Icon button:** 44px round chip-tone circle, used for the theme toggle.

### Chips
- **Style:** surface background, hairline border, full pill, 44px tall, Barlow 600 ink. Used as a list of player names that each open a filtered view.
- **State:** hover moves the border to the purple glow tone.

### Segmented control
- **Style:** a row of pill radios with a sentence-case label above; unselected are surface with hairline and muted text.
- **State:** selected (checked or current page) fills with Arena Purple and white text; keyboard focus draws the purple outline around the pill.

### Inputs / Fields
- **Style:** native select with custom chevron, surface background, hairline border, 10px radius, 44px tall, 1rem text; label above at 0.8125rem 600 muted.
- **Focus:** 2px purple outline; hover shifts the border to the glow tone.
- **Upload dropzone:** 16px-radius surface panel with a 2px dashed glow border that turns solid purple on hover and focus.

### Navigation
- **Style:** Barlow 500 at 15px, muted at rest, ink on hover; the current page is ink with a 2px purple underline. Wraps to a second row on phones with no hidden menu.
- **Footer:** faint 14px line of site facts with an underlined link to the previous version.

### Stat Table
The comparison surface on averages, matchups, teammates and highs.
- **Container:** card-tone panel, hairline border, 16px radius, horizontal scroll with keyboard focus.
- **Columns:** the name column is pinned (sticky left, card background, hairline right edge) and left-aligned; every other column is right-aligned tabular data. Headers are the uppercase label style and sort on click, with a chevron that appears on the sorted column.
- **Games link:** every games number is a purple underlined link to the game log filtered to that row; the log it opens must contain exactly that many games.
- **Density:** less-used columns are hidden behind "More stats"; the table tools line states the row count and, on phones, that the table swipes sideways. On phones names wrap (min 9.5rem, max 45vw) so the columns beside them stay in view, still breaking only between tags.
- **Leaders:** the best value in a column is 700 weight in the gold text tone.

### Game Row (signature)
The recurring atom on the landing, the game log, and filtered logs.
- **Content, in order:** time or date (faint, tabular), the final score (small T1/T2 side labels, Anton totals, the winning total in gold and the losing total muted), each side's top scorer (the winning side in ink 600 marked "won"), an optional player line when the log is filtered to one player (Won in gold or Lost muted, then points, rebounds, assists, position), and a chevron arrow at the right edge.
- **Behaviour:** the whole row is one link to the box score; hover tints the row purple at low alpha. Rows are grouped by night under a hairline heading with a faint count; games before 6 am belong to the previous evening.

### Box Score
- **Final:** the two final totals in Anton at 4.5rem, winner in gold, with the margin beside them.
- **Teams:** two stat tables with fixed, identical column widths so the stats line up, separated by the half-court divider: a 2px court-tone line with a 64px centre circle.

### Landing Court Hero (signature)
A half court drawn in court-strong strokes (2.5 width). Each position spot is a purple dot with its position label in white, the name of the player with the most games at that position beneath it, and their games count; each spot links to that position's averages and has an invisible 40-unit tap area. On phones the court shrinks, so dots and labels grow to compensate (dot radius 22, labels 20/30/25px), SF and PF labels anchor at the start, and SG labels anchor at the end so they stay inside the court.

### Records List
Open hairline rows of category, value (Barlow 700 at 1.5rem in the gold text tone) and holders; reflows to two lines on phones.

## Do's and Don'ts

### Do:
- **Do** use gold only for a winning score, a win result, a table leader, or a career high; in light mode use the darker gold tone for any text below display size.
- **Do** keep purple to links, focus rings, selected states and the primary button.
- **Do** set page titles and final scores in Anton, and everything else, including all numbers, in Barlow with tabular numerals.
- **Do** wrap every gamer tag in a no-wrap span so lineups break only between names.
- **Do** make every games number in a stat table link to a game log filtered to exactly that many games.
- **Do** pin the name column and put less-used columns behind "More stats".
- **Do** keep every tap target at least 44px tall.
- **Do** build new lists of games from the game row: time or date, score with the winner in gold, top scorers, optional player line, arrow at the right edge.
- **Do** keep state changes at 150ms and disable them under reduced motion.

### Don't:
- **Don't** draw court lines anywhere except the landing hero, the box-score half-court divider, and the clipped header band; the header arc must never cross data or form controls, and it stays hidden on the landing.
- **Don't** use gold for hover, focus, branding or decoration.
- **Don't** use Anton for section heads, captions, stat values or records.
- **Don't** add shadows; separate with hairlines and surface tones.
- **Don't** use NBA or Getty photography, or league or team marks.
- **Don't** add small uppercase labels above headings; the only uppercase small text is the stat table column header.
