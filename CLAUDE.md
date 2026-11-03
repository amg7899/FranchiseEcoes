# FRANCHISE ECOES website

Website for FRANCHISE ECOES (mobile charging franchise), split off from the ECOES JV site (https://ecoes.eu/, repo amg7899/SUM) at the client's request on 2026-10-15. The franchise material (PDF, earlier EN/BG pages, text fixes and open questions) is in the history of amg7899/SUM, commit before eee7bcc.

## Skills
Use both for all UI work:
- `.claude/skills/frontend-design` (Anthropic, Apache-2.0; same as the official `frontend-design@claude-plugins-official` plugin): design approach, plan → review against generic defaults → build → screenshot critique.
- `.claude/skills/ui-ux-pro-max` (MIT): UX rules and searchable design data. Run from the repo root, e.g.
  `python3 .claude/skills/ui-ux-pro-max/scripts/search.py "focus visible keyboard" --domain ux`
  (the `${CLAUDE_PLUGIN_ROOT}` paths in its SKILL.md don't apply to this project install).
