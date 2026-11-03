---
name: ECOES Franchise
description: The ECOES MultiCharger's own equipment body as a website – red panels in a galvanised frame, glazed compartments, riveted aluminium plates.
colors:
  signal-red: "#c8161d"
  red-deep: "#a51219"
  red-edge: "#8e0f15"
  graphite: "#1d2227"
  text: "#2e363d"
  muted: "#56626c"
  steel-50: "#f6f7f8"
  steel-100: "#eef1f3"
  steel-300: "#c9d0d6"
  steel-500: "#8e99a3"
  field-edge: "#7d8a95"
  line: "#d7dce1"
  amber: "#f2a100"
  error: "#b42318"
  white: "#ffffff"
typography:
  lettering:
    fontFamily: "Sofia Sans Condensed, Sofia Sans, Arial Narrow, sans-serif"
    fontSize: "clamp(46px, 9.4vw, 140px)"
    fontWeight: 700
    lineHeight: 0.9
    letterSpacing: "-0.02em"
  heading:
    fontFamily: "Sofia Sans Condensed, Sofia Sans, Arial Narrow, sans-serif"
    fontSize: "clamp(34px, 4.1vw, 58px)"
    fontWeight: 700
    lineHeight: 1.02
    letterSpacing: "-0.015em"
  compartment-title:
    fontFamily: "Sofia Sans Condensed, Sofia Sans, sans-serif"
    fontSize: "clamp(23px, 1.95vw, 28px)"
    fontWeight: 700
    lineHeight: 1.06
  statement:
    fontFamily: "Sofia Sans, Segoe UI, Arial, sans-serif"
    fontSize: "clamp(26px, 3.1vw, 44px)"
    fontWeight: 500
    lineHeight: 1.2
    letterSpacing: "-0.018em"
  body:
    fontFamily: "Sofia Sans, Segoe UI, Arial, sans-serif"
    fontSize: "18px"
    fontWeight: 420
    lineHeight: 1.6
  label:
    fontFamily: "Sofia Sans, Segoe UI, Arial, sans-serif"
    fontSize: "16px"
    fontWeight: 650
    lineHeight: 1.35
rounded:
  sm: "4px"
  md: "6px"
  lg: "8px"
  panel: "10px"
spacing:
  gutter: "clamp(16px, 4vw, 48px)"
  panel: "clamp(22px, 4.4vw, 64px)"
  section: "clamp(64px, 8vw, 120px)"
  max: "1280px"
components:
  button-red:
    backgroundColor: "{colors.signal-red}"
    textColor: "{colors.white}"
    rounded: "{rounded.md}"
    height: "52px"
    padding: "8px 26px"
  button-red-hover:
    backgroundColor: "{colors.red-deep}"
  button-plate:
    backgroundColor: "{colors.white}"
    textColor: "{colors.red-deep}"
    rounded: "{rounded.md}"
    height: "52px"
    padding: "8px 26px"
  button-line:
    textColor: "{colors.white}"
    rounded: "{rounded.md}"
    height: "52px"
  input:
    backgroundColor: "{colors.white}"
    textColor: "{colors.graphite}"
    rounded: "{rounded.md}"
    height: "48px"
    padding: "10px 14px"
  plate:
    textColor: "{colors.graphite}"
    rounded: "{rounded.lg}"
    padding: "22px 24px"
  locker:
    backgroundColor: "{colors.white}"
    rounded: "{rounded.lg}"
---

# Design System: ECOES Franchise

## Overview

The site is built from the ECOES MultiCharger itself. Its renders show a signal-red powder-coated body in a galvanised steel frame with rivets, two amber marker lights at the top corners, roller-shuttered hatches and a charger with a blue ring – and the same family of special vehicles (BULFIRE fire and airport trucks) stands behind the brand. Every page section is one of four objects from that world: the red **body** (`.panel`), a glazed **compartment** (`.locker`), a clear-glass **hatch** (`.hatch`) or a riveted aluminium **plate** (`.plate`), on a daylight steel ground. The client asked for a futuristic, professional, clean and trustworthy site with transparent containers that show motifs; here the transparency is the frosted glass of the compartments, through which the product's own renders stay visible.

Light ground, because the visitors read in daylight, in offices and on phones in sunny markets (Europe, Africa, Asia, Latin America). The red appears as large bodies, never as scattered accents: one dominant red mass per viewport.

## Colors

### Primary
- **Signal red** `#c8161d` – the MultiCharger body: hero, "Why ECOES Franchise", announcements, the menu, primary buttons, the selected load. White text on it is 5.9:1. Edges and pressed states use **red deep** `#a51219` and **red edge** `#8e0f15`.

### Neutral
- **Graphite** `#1d2227` (headings, footer, the chart display), **text** `#2e363d`, **muted** `#56626c` (labels, notes; ≥ 5:1 on white and on plates).
- **Steel** `#f6f7f8` / `#eef1f3` grounds, `#c9d0d6` and `#8e99a3` for the galvanised frames, `#d7dce1` hairlines, **field edge** `#7d8a95` (form borders, 3.6:1).
- **Amber** `#f2a100` – only the two marker lights on each red body. **Error** `#b42318`.

### Named Rules
- **One red mass per viewport.** Red is the body, not decoration; text links are graphite or red-deep.
- **Glass is white.** Frosted panels are white at 80% with a 14px blur, so text on them stays ≥ 10:1 over any render.

## Typography

Sofia Sans by Lettersoup (a Sofia foundry; OFL, self-hosted, Latin + Cyrillic). The condensed width is the vehicle lettering: the hero sets "ECOES MultiCharger" as large as the lettering on the product's side. Bulgarian pages use the font's default Bulgarian Cyrillic forms; `lang="ru"` (e.g. Chrome translating into Russian) switches to the standard forms.

### Hierarchy
- **Lettering** – Sofia Sans Condensed 700, 46–140px, line-height .9 (hero product name, page titles at 44–96px).
- **Heading** – Condensed 700, 34–58px.
- **Compartment title** – Condensed 700, 23–28px.
- **Statement** – Sofia Sans 500, 26–44px, max 30ch.
- **Body** – Sofia Sans 420, 18px / 1.6; 16.5px inside compartments.
- **Figures** – Condensed 700; tabular numerals in tables and the meter readout.

## Layout

12-column grid inside `max-width: 1280px` (bodies 1320px), gutters `clamp(16px, 4vw, 48px)`. Sections alternate white and steel grounds; a red body sits inside its section with 7px of frame around it. Two-column intro + plate (5/12 + 7/12) for profit and certification, with the intro sticky on wide screens. The compartments of "Why ECOES Franchise" form one body: 6 + 6, 3 + 3, 4 + 4 + 4, 5 + 7 columns from 1100px, two columns from 760px, one below.

## Elevation & Depth

Depth comes from the objects, not from floating cards: the galvanised frame is drawn as box-shadow rings (`0 0 0 1px #949fa9, 0 0 0 6px #d3d9de, 0 0 0 7px #9aa5ae`), rivets as small radial dots, plates have an inner top highlight and a soft offset shadow (`0 10px 22px -14px rgba(29,34,39,.6)`). Buttons carry a neutral offset shadow; nothing glows.

## Shapes

Small industrial radii: 4px (number tags), 6px (buttons, inputs, hatches), 8px (plates, compartments), 10px (bodies). No pills.

## Components

### Buttons
- **Red** (`.btn--red`) on light grounds; **plate** (`.btn--plate`, white plate with red-deep text) on red; **line** (`.btn--line`, white outline) as the second action on red. 52px tall (44px small), 6px radius, weight 650.

### Cards / Containers
- **Body** (`.panel`): red, galvanised frame, rivets along the top and bottom, two amber marker lights. Holds lettering, statements, compartments, plates.
- **Compartment** (`.locker`): a clear window (`aspect-ratio`, render with `object-fit: cover`, or `contain` with `.locker-media--fit` for renders on white) and a frosted panel overlapping its lower 56px; title, one paragraph, then "Learn more" and "Get an offer".
- **Plate** (`.plate`): brushed aluminium with four rivets – key figures, certification pillars, the load meter, forms, offices.
- **Hatch** (`.hatch`): a clear-glass window with a gasket ring and a diagonal reflection, for the hero photo.

### Inputs / Fields
White fields, 48px, 1px field-edge border, red caret, 2px graphite focus outline; choices as 48px tiles with a red ring when checked; numbered red tags (1–8) on the pre-order form; errors in red under the field, the first invalid field takes focus.

### Navigation
White glass header (blur 14px), logo, six links on one line with a red underline for the current page, the language button (the other language), "Get an offer". Below 1200px – or whenever the row does not fit, e.g. translated – only the menu button: a red body with the links as condensed lettering.

### Load meter (signature component)
Five load steps (10–100%) as radio tiles, a segmented charge bar, the monthly gross profit in large figures, per day / year / DC / customer service below, and the client's table with the chosen row marked. Without JavaScript only the table shows.

## Do's and Don'ts

### Do:
- Build every new section from body, compartment, plate or hatch.
- Use the client's renders in the compartments; show renders on white whole (`.locker-media--fit`).
- Keep one red mass per viewport and white glass over images.
- Put a "Get an offer" link (to `contact-us/?topic=…#contact-form`) next to every "Learn more".

### Don't:
- Don't add neon glows, gradient text, eyebrow labels or icon-and-text card rows.
- Don't put text directly on photos; text sits on frosted glass or plates.
- Don't scatter red accents over white sections.
- Don't animate on scroll; the only automatic motion is the single light sweep along the hero's contour strip.
