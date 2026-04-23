# Contributing

## Adding your project

1. **Fork this repository.**

2. **Copy the example file.**
   ```bash
   cp schema/project.example.yaml projects/<your-project-slug>.yaml
   ```
   Use a slug matching your project name, lowercase, hyphens instead of spaces. If your project is already listed, edit the existing file instead of creating a new one.

3. **Fill in the fields.**
   See [schema/project.schema.json](schema/project.schema.json) for the full field list and constraints. Required fields: `name`, `description`, `topics`, `maturity`, `license`, `venues`. Everything else is optional.

4. **Validate locally.**
   ```bash
   node site/validate.js projects/<your-project-slug>.yaml
   ```
   This catches schema errors before review.

5. **Open a PR.** Title: `add: <project-name>` or `edit: <project-name>`. Body: a one-line note on what changed.

## Field guidance

**`name`** — your project's canonical name, spelled how you want people to reference it.

**`description`** — one sentence. What does the project do? What problem does it address? Keep under 200 characters. Write it like you'd write it for a sibling project's README link to you.

**`topics`** — pick one or more from the fixed vocabulary: `identity`, `delegation`, `commerce`, `governance`, `data-lifecycle`, `attribution`, `audit`, `coordination`. If your project genuinely covers a topic not on this list, open an issue proposing the addition.

**`maturity`** — self-declared, but honest. Options:
- `research` — paper published, no running code
- `draft` — specification written, no shipped implementation
- `beta` — implementation shipped, pre-production
- `production` — live users, documented API, stable releases
- `standard` — ratified in a recognized standards body (IETF RFC, W3C Rec, ERC, etc.)

If contested, maturity defaults to one step below your declared level. Don't contest this; it's faster to just accurately declare.

**`license`** — SPDX identifier (`Apache-2.0`, `MIT`, `GPL-3.0`, `BSD-3-Clause`, `CC-BY-4.0`, or `proprietary`).

**`venues`** — at least one reachable URL. Acceptable: GitHub repo, IETF datatracker draft, W3C spec, ERC page, project website with real documentation. A logo and a marketing hero does not count as a venue.

**`implements`** — technical primitives your project uses. This populates the convergence view. Use fixed vocabulary where possible (`ed25519`, `x25519`, `jwt`, `did`, `vc`, `macaroon`, `biscuit`, `merkle-tree`, `erc-721`, `erc-20`, `oauth-2.1`, `rfc-8693`, etc.). Free text is OK but won't cluster with others.

**`relates_to`** — other projects in the map you interoperate with or extend. Use their slugs. Relationships are declarative ("I extend X") not evaluative ("X is better"). If your project uses someone else's vocabulary or primitive, say so here.

**`contact`** — optional. One of: primary maintainer's GitHub handle, project email, or project Discord/Slack invite.

## What won't get merged

- Entries for projects that don't have a reachable artifact (no repo, no spec, no docs)
- Duplicate entries — edit the existing one
- Entries that embed marketing copy instead of technical description
- Entries that tag maturity levels not supported by evidence
- Entries submitted by parties with no connection to the project and no effort to verify accuracy

## Questions

Open an issue labeled `question`. Before opening, search closed issues; the answer may already be there.
