# FRANCHISE ECOES website

Website for FRANCHISE ECOES (mobile charging franchise), split off from the ECOES JV site (https://ecoes.eu/, repo amg7899/SUM) at the client's request on 2026-10-15. The franchise material (PDF, earlier EN/BG pages, text fixes and open questions) is in the history of amg7899/SUM, commit before eee7bcc.

## Skills
Use both for all UI work:
- `.claude/skills/frontend-design` (Anthropic, Apache-2.0; same as the official `frontend-design@claude-plugins-official` plugin): design approach, plan → review against generic defaults → build → screenshot critique.
- `.claude/skills/ui-ux-pro-max` (MIT): UX rules and searchable design data. Run from the repo root, e.g.
  `python3 .claude/skills/ui-ux-pro-max/scripts/search.py "focus visible keyboard" --domain ux`
  (the `${CLAUDE_PLUGIN_ROOT}` paths in its SKILL.md don't apply to this project install).
- `.claude/skills/playwright-cli` (Microsoft, `@playwright/cli`, installed with `playwright-cli install --skills`): drives a browser from the shell (open, click, fill, snapshot, screenshot) to check pages and take the screenshots sent to the client. The cloud container is fresh each session, so install the CLI first: `npm install -g @playwright/cli@0.1.23`. It uses the pre-installed Chromium; do not run `playwright install`. Its output folder `.playwright-cli/` is git-ignored.
- `.claude/skills/impeccable` (Paul Bakaus, pbakaus/impeccable v4.8.0, installed with `npx -y skills add pbakaus/impeccable --skill impeccable --agent claude-code`; `skills-lock.json` records the source for updates): design direction and review commands (init → PRODUCT.md, shape, critique, audit, polish, typeset, layout, animate, …). Run `.claude/skills/impeccable/scripts/impeccable context` once per session from the repo root; on first run it downloads its engine from the author's GitHub releases and checks it against `scripts/engine-checksums.txt` (refuses unverified downloads). After UI edits run `.claude/skills/impeccable/scripts/impeccable detect --json <files>`.
