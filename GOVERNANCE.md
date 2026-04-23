# Governance

This document describes how decisions are made about what appears in the map and how disputes are resolved. Written before the map goes public so it can't be accused of being reverse-engineered to justify any particular decision.

## Principle

The map is a directory, not a curation. Maintainers review entries for honesty and schema compliance. They do not judge merit, importance, or alignment. If a project exists, has an artifact someone can reach, and fills the schema honestly, it belongs here.

## Review criteria

A PR adding or editing a project entry gets merged if all of the following hold.

**1. Schema valid.** The YAML parses, matches `schema/project.schema.json`, passes CI lint.

**2. Artifact reachable.** At least one of the `venues` URLs resolves to a live page describing a real project. A GitHub repo with commits counts. A marketing landing page alone does not.

**3. Honest self-description.** The `maturity` tag is not visibly inflated. A `production` tag requires evidence of live users or a documented API. A `standard` tag requires ratification in a recognized body (IETF RFC, W3C Recommendation, Ethereum ERC, etc.). Disputed tags default to one step lower.

**4. Not a duplicate.** If a project already has an entry, edits go on the existing entry rather than creating a new one. Same project under a different name is still a duplicate.

**5. Claimant has standing.** Ideally the PR comes from a project maintainer. Third-party submissions are accepted if the claimed project is real and the description is accurate, but a note is added to the entry and the project's maintainers are tagged for review.

Entries are not rejected for:

- Being small, early, or solo
- Being commercial or proprietary (license is a field, not a gate)
- Disagreeing with other projects in the map
- Being outside the authors' region or language

## Disputes

Any project listed in the map may challenge another project's entry by opening an issue. Grounds for challenge are limited to the five review criteria above. "I don't like their framing" is not grounds.

Disputes are resolved by maintainer majority vote within seven days. If a tie, the entry remains as originally claimed (status quo bias, erring toward the claimant's self-description). Votes are posted publicly in the issue thread.

The project under challenge may not vote on its own entry.

## Maintainers

### Current

- [@aeoess](https://github.com/aeoess) — initial author

### Adding co-maintainers

The map is designed to transition to distributed stewardship. Active search is ongoing for co-maintainers from other projects in the map. To be considered:

1. Be a maintainer of a project already listed in the map
2. Open an issue titled `[co-maintainer] <your handle>` with a one-paragraph note on why you'd like to help
3. Existing maintainers vote; simple majority adds

The goal is 3-5 co-maintainers across different projects, at which point this repo migrates to a neutral organization and the `aeoess` handle becomes one maintainer among equals.

### Removing maintainers

Maintainers can step down by opening an issue. Maintainers may be removed for sustained inactivity (no reviews in 90 days) by majority vote of remaining maintainers.

## What this map will never do

- Endorse one project over another
- Accept money to list, promote, or rank projects
- Gate inclusion on commercial terms, licensing terms, or governance-body membership
- Apply interpretive tags ("important," "trending," "legacy") that project maintainers did not self-apply

If the maintainer set ever attempts any of the above, the map has failed its purpose and anyone may fork it.

## Amendments

This document can be amended by maintainer majority vote. Amendment PRs require a 14-day comment period before merge. Projects listed in the map are notified via GitHub issue.
