---
paths:
  - "Infrastructure/explorations/**"
---

# Exploration Protocol

**All experimental work goes into `Infrastructure/explorations/` first.** Never mix early experiments into production work. This protocol combines the folder/lifecycle structure with a lightweight fast-track for low-stakes exploration.

## Folder Structure

```
Infrastructure/explorations/
├── ACTIVE_PROJECTS.md
├── [project]/
│   ├── README.md
│   ├── code/
│   ├── notes/
│   ├── output/
│   └── SESSION_LOG.md
└── ARCHIVE/
    ├── completed_[project]/
    └── abandoned_[project]/
```

## Lifecycle

1. **Create** -- `mkdir -p Infrastructure/explorations/[name]/{code,notes,output}` and initialize `README.md` + `SESSION_LOG.md`.
2. **Develop** -- work entirely inside the exploration folder.
3. **Decide:**
   - **Graduate** -- promote validated outputs to production locations used by the active project; record destination in the exploration README.
   - **Keep exploring** -- document next steps in README.
   - **Abandon** -- move to `ARCHIVE/abandoned_[project]/` with a short explanation.

## Fast-Track (lightweight option)

For low-stakes experimental work, use a lighter standard. **Suggested threshold: 60/100 for exploration quality (production remains stricter).**

1. **Research value check** -- does this exploration help answer the project question?
2. **Create folder** -- same as Lifecycle step 1 (`code/`, `notes/`, `output/`, `README.md`, `SESSION_LOG.md`).
3. **Code quickly** -- require runnable code, correct results, and a clear goal; defer polish.
4. **Log progress** -- append 2-3 lines to `SESSION_LOG.md` as you work.
5. **Decision point** -- continue exploring, graduate to production, or archive (see Lifecycle step 3).

### When to Stop (Kill Switch)

If value is low or blockers dominate, stop, archive with a short note, and move on.

## Graduate Checklist

- [ ] Quality threshold for production is met
- [ ] Verification checks pass
- [ ] Results replicate within tolerance (if applicable)
- [ ] Code and notes are understandable without hidden context
- [ ] README explains approach, findings, and final disposition
