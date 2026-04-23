# Agent Ecosystem Directory

A living, community-maintained directory of the protocols, specifications, implementations, contributors, and threads in the AI agent identity, delegation, governance, and commerce space.

Live at [aeoess.github.io/agent-ecosystem-map](https://aeoess.github.io/agent-ecosystem-map/) (or wherever GitHub Pages points after first deploy).

## What this is

A navigation layer for a field that's moving faster than any single project can track. If you're a developer evaluating options, a researcher orienting yourself, a founder scoping, or a contributor who wants to know who else is in the same threads you are, this directory exists to answer a few questions in under a minute:

- What does the landscape look like?
- Who is actually building in it?
- Where is the work happening?
- What's new, what's active, and what's gone quiet?

Every row is hard data pulled from public GitHub. Account ages are real. Project creation dates are real. Thread state is real. Filter chips surface "new accounts," "hot threads," "multi-contributor projects" so you can see the field's shape at a glance.

## What this is not

- A ranking. No scores-of-importance, no tiers, no editorial endorsements.
- A coalition. Listing here implies no shared governance, no shared monetization, no shared anything.
- A curation. Project entries are self-claimed and self-described; people and threads are pulled automatically from public GitHub activity. Maintainers review projects for schema compliance, not for merit.
- A property of AEOESS. It's hosted here to ship quickly; it's designed from day one to transition to neutral stewardship once other project maintainers want to co-steward it.

## How it's organized

Three tables, all sortable and filterable:

- **Projects** — 18 curated entries (add your own via a PR). Columns: name, maturity, stars, contributors, threads, created, last push, license.
- **People** — 115 contributors pulled automatically from public governance threads, filtered to score ≥ 5. Columns: login, company, score, posts, threads, account age, first seen, last active, followers. Account age is a pill: amber for accounts under 60 days old, green for 60-365 days, plain for older. Makes the difference between a 3-week-old promo account and a 10-year veteran visible at a glance.
- **Threads** — 93 GitHub issues and PRs where the work is happening. Columns: thread, state, participants, comments, opened, last activity, project.

Click any row for the full detail drawer. Drawer chips cross-link between tabs: click a contributor in a project drawer to filter the people table to that login; click a project in a person drawer to see the project entry.

## How to claim or edit your project's entry

1. Fork this repo.
2. Copy `schema/project.example.yaml` to `projects/<your-project>.yaml`.
3. Fill in the fields. All fields are self-reported. If you don't know or don't want to say, leave it out.
4. Open a PR.

Review is a schema check plus a live-endpoint verification for anything the entry links to. See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## How the data is refreshed

`scripts/build-ecosystem-data.py` reads every `projects/*.yaml`, pulls the contribution map from `aeoess_web/specs/contribution-map/`, and enriches everything via the GitHub API. Responses are cached to `.github-cache/` (gitignored) so reruns don't burn API quota. Output is `site/ecosystem-data.json`, which the page fetches at load time.

Rebuild with `python3 scripts/build-ecosystem-data.py`. Takes a few minutes if the cache is cold, seconds if warm.

## Governance

See [GOVERNANCE.md](GOVERNANCE.md). Short version: schema-only review, disputes resolved by maintainer vote, active search for co-maintainers from other projects in the directory.

## License

Content under [CC-BY-4.0](LICENSE). Code under MIT. Your project's entry remains yours; this repo just publishes it.

## Current maintainers

- [@aeoess](https://github.com/aeoess) — initial author, actively seeking co-maintainers from other projects. If you're a maintainer of a project listed here and want to co-maintain the directory, open an issue titled `[co-maintainer] <your handle>`.
