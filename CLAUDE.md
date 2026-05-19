# CLAUDE.md

## Read Order

Before making changes, read:

1. `.claude/rules.md`
2. `.claude/architecture.md`
3. `.claude/current-state.md`

For roadmap and migration:
- `.claude/roadmap.md`

For commands:
- `.claude/commands.md`

---

## Project

Legacy Flask-based facial recognition attendance system.

Current goal:
- stabilize legacy system
- migrate gradually toward FastAPI + async AI pipeline

---

## YOU MUST

- Keep business logic out of routes
- Never store plaintext passwords
- Never hardcode configs/secrets
- Read roadmap before architecture changes
- Prefer service-layer architecture