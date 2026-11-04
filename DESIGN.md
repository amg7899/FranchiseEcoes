---
name: ECOES Franchise
description: Night glass – frosted panes over the client's own scene and product renders, glowing line drawings of the MultiCharger and the logo's globe, light display type.
colors:
  night-0: "#06090c"
  night-1: "#0a1015"
  night-2: "#10181f"
  ground: "#112031"
  ground-1: "#162a3f"
  ice: "#f2f5f7"
  text-hi: "#edf2f4"
  text: "#c3ced5"
  text-mute: "#a3b3bf"
  signal: "#4cc3ff"
  line-glow: "#7fd8ff"
  red: "#e3262d"
  error: "#ff8a8f"
  glass-tint: "rgba(30, 50, 72, .36)"
  hairline: "rgba(255, 255, 255, .1)"
typography:
  display:
    fontFamily: "Unbounded, Segoe UI, Arial, sans-serif"
    fontSize: "clamp(30px, 3.4vw, 54px)"
    fontWeight: 300
    lineHeight: 1.08
    letterSpacing: "-0.03em"
  heading:
    fontFamily: "Unbounded, Segoe UI, Arial, sans-serif"
    fontSize: "clamp(28px, 3.1vw, 46px)"
    fontWeight: 300
    lineHeight: 1.12
    letterSpacing: "-0.02em"
  pane-title:
    fontFamily: "Unbounded, Segoe UI, Arial, sans-serif"
    fontSize: "clamp(18px, 1.4vw, 22px)"
    fontWeight: 400
    lineHeight: 1.25
  figure:
    fontFamily: "Unbounded, Segoe UI, Arial, sans-serif"
    fontSize: "clamp(48px, 6vw, 88px)"
    fontWeight: 300
    lineHeight: 1
    letterSpacing: "-0.035em"
  body:
    fontFamily: "Wix Madefor Text, Segoe UI, Arial, sans-serif"
    fontSize: "17px"
    fontWeight: 400
    lineHeight: 1.65
  label:
    fontFamily: "Wix Madefor Text, Segoe UI, Arial, sans-serif"
    fontSize: "15.5px"
    fontWeight: 550
    lineHeight: 1.4
rounded:
  field: "14px"
  pane-small: "20px"
  pane: "28px"
  pill: "999px"
  paper: "3px"
spacing:
  gutter: "clamp(16px, 4.2vw, 64px)"
  section: "clamp(96px, 11vw, 176px)"
  max: "1360px"
components:
  button-primary:
    backgroundColor: "{colors.ice}"
    textColor: "{colors.night-0}"
    rounded: "{rounded.pill}"
    height: "52px"
    padding: "10px 26px"
  button-glass:
    textColor: "{colors.text-hi}"
    rounded: "{rounded.pill}"
    height: "52px"
    padding: "10px 26px"
  input:
    textColor: "{colors.text-hi}"
    rounded: "{rounded.field}"
    height: "50px"
    padding: "12px 16px"
  pane:
    backgroundColor: "{colors.glass-tint}"
    textColor: "{colors.text}"
    rounded: "{rounded.pane}"
  chip:
    textColor: "{colors.text-hi}"
    rounded: "{rounded.pane-small}"
    padding: "14px 18px"
---

# Design System: ECOES Franchise (v2, "night glass")

## Overview

v1 (red equipment body) was rejected by the client on 2026-11-03: "looks made in Paint", "all red strains the eye", "too obvious"; they asked for something nonchalant and mysterious, professional, modern, futuristic and clean, with far more transparency – real blurred glass containers with motifs behind them – and sent three references they like (an eco dashboard on a glass monitor with a glowing globe, a dark engineering site with a glowing wireframe building, a cinematic dark car page). v2 answers that:

- A deep blue-hour ground (#112031, the sky of the hero photo after dusk, with sea light from the upper right and a trace of the sunset on the left); lighter than the first night ground at the client's request (2026-11-04). The Home hero keeps its night (#06090c) exactly as it was, and the section after it fades from that night into the blue.
- Frosted glass panes (`.glass`) in front of the client's own imagery where it means something: the beach scene behind the hero pane, the red MultiCharger renders behind the offer panes. The profit, certification, pre-order and contact panes stand in designed light (the charger's blue and the sea); the cut-outs that once peeked out behind them were removed at the client's request ("I don't see the logic").
- Glowing line drawings in the colour of the charger's ring light (#4cc3ff): the MultiCharger on its trailer as a see-through wireframe, first whole under the "Why" title, then behind the panes, and the globe of the ECOES JV logo with London and Sofia next to the intro statement. Both are drawn by `tools/wireframes.py`.
- Red only where the product is (photos, renders, logo). UI accents are the signal blue.

## Colors

- **Ground** `#112031` / `#162a3f` (blue hour) – the page; **Night** `#06090c` – only the Home hero and the ink on light buttons.
- **Text**: `#edf2f4` headings, `#c3ced5` body, `#a3b3bf` notes (lifted with the lighter ground: ≥ 4.5:1 even on the brightest pane; the hero keeps `#8f9ca6`). Glass tint `rgba(30, 50, 72, .36)`, a touch lighter than the ground (the hero pane keeps `rgba(14, 21, 28, .42)`).
- **Ice** `#f2f5f7` – the primary button.
- **Signal** `#4cc3ff` (lines `#7fd8ff`) – the charger's ring light: status dots on "Get an offer", the current page, the selected chart bar and load, radio/checkbox accents, the line drawings.
- **Glass tint** `rgba(14,21,28,.42)` with a 160° white sheen and a light gradient edge; blur 28px, saturate 1.6.

### Named Rules
- **A motif only where it means something.** Behind glass: the hero scene, the product in its offer card, the hologram, the globe – never a random object peeking out from behind a pane. Other panes stand in light, so the glass still reads as glass.
- **Red belongs to the product.** No red UI.

## Typography

Unbounded (NaN; OFL) light for display – wide, calm, futuristic; Wix Madefor Text (Wix/Dalton Maag; OFL) for text and UI. Both self-hosted, Latin + Cyrillic; with `lang="bg"` both use the Bulgarian Cyrillic forms.

## Layout

Max 1360px (hero 1480px), gutters `clamp(16px, 4.2vw, 64px)`, sections `clamp(96px, 11vw, 176px)`. Hero: full-bleed photo, pane bottom left (max 680px), the four key-figure chips bottom right (2 × 2, a row of 4 from 1720px). Intro: statement + globe. Offers: three panes with the product standing behind each. Why: the whole hologram under the title (it fits the viewport), then nine panes (6+6 / 3+3 / 4+4+4 / 5+7 from 1100px) sliding over the sticky wireframe stage, which ends at the last row; on phones the hologram stands only under the title. Profit and certification: sticky intro left, pane right. Sections with motifs clip horizontal overflow (`overflow-x: clip`, which keeps sticky columns working).

## Elevation & Depth

Depth comes from blur and the light edge only: no drop shadows on panes (a 1px edge under a wide soft shadow is the ghost card). Products carry a soft drop shadow of their own; nothing glows except the line drawings (a blurred copy of each line under it).

## Shapes

Fields 14px, chips 20px, panes 28px, buttons and choices are pills; paper (documents, flags) 3px.

## Components

- **Buttons**: primary ice pill; glass pill (white 7% + 1px inner edge); a small signal dot marks "Get an offer".
- **Pane** (`.glass`): see Colors; `.glass--strong` for more tint.
- **Chip**: small pane with a figure (Unbounded 300) and its label.
- **Offer card**: the product render (cut out, `object-fit: contain`) stands behind the pane, sharp above it, frosted where the glass covers it.
- **Tile**: pane with title, one paragraph, "Learn more" + "Get an offer".
- **Inputs**: translucent fields with a light edge; choices as pills; errors in soft red under the field.
- **Navigation**: transparent over the hero, dark glass once scrolled; the logo in its night variant (ecoes.eu's own: globe lines #93a3b6, red #ff3340 with a dark outline), 54px straight on the header, no plate; the current page marked by a signal dot; below 1200px (or when the row does not fit) the menu opens as a full-screen dark glass.
- **Document pages**: the page head is a picture with a `.lead-pane` glass at the lower left (h1 = category + product name with the signal dot, lead, "Get an offer", links to the sections); then `.split` sections with numbered glass lists (`.pillars--numbered`, the client's numbers 1.1, 2.1 … in pills), a `.notice` strip with the signal dot, a `.toc` beside `.read-pane` glass panes for long text, and a `.closing` with the client's last sentence as the statement.
- **Load meter**: pill segments, a thin signal bar, the monthly gross profit in large light figures, and the client's table with the chosen row marked.
- **Product pages** (MultiCharger, Box): a key-figures band of chips under the head; `.doc` sections (reading column 920px, wide galleries, charts and panes), `.doc-sub` headings, `.callout` (signal dot), `.manifest` (a key paragraph in Unbounded light), `.points` (the 12 points, numbers in signal blue), `.panes`, `.bullets`, `.gallery` of framed photos and cut-outs, bar charts (`.hbars`, stacked `.vbars`), the full meter table, `.compare` (truck = MultiCharger + MultiCharger, taxi = Box).
- **About us** (the content of ecoes.eu/about-us/): the head with the logo's globe in light beside the title; ECOES JV and its two companies as an org chart wired in the signal blue (trunk, bus, a drop to each, nodes as signal dots; a rail with ticks on phones); logos on a white plate like the header logo; the CEO's sentence as the statement beside his photo; the documents on a light table (white paper, one page shape), the awards each with its text (subgrid rows), a full-size viewer in night glass; the BULFIRE card and a large closing link with an ice arrow chip.

## Do's and Don'ts

### Do:
- Give every image behind glass a reason; otherwise let the pane stand in light.
- Keep the type light and the layout quiet: one idea per viewport.
- Pair every "Learn more" with "Get an offer".

### Don't:
- Don't use red for UI, don't add drop shadows to panes, don't put text directly on photos.
- Don't let a drawing or product show only in fragments (half a sign, bare wheels) – show it whole or not at all.
- Don't animate on scroll beyond the line drawings drawing themselves once; the only load moment is the hero glass frosting over.
