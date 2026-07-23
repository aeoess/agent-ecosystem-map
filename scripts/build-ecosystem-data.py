#!/usr/bin/env python3
"""
Build ecosystem-data.json for docs/index.html (served as GitHub Pages).

Pulls and enriches:
- projects  from projects/*.yaml (curated) plus repos derived from tracked threads
- people    from the contribution-map output, filtered to rows with a post or a
            tracked thread, enriched with GitHub user metadata
- threads   from the contribution-map output + GitHub issue metadata

Caches GitHub responses to .github-cache/ so re-runs don't burn API quota.
"""
import json, yaml, os, shutil, subprocess, time, sys
from pathlib import Path
from datetime import datetime, timezone

# Repo root is two parents up from this script.
ROOT      = Path(__file__).resolve().parent.parent

# Contribution-map data lives in a private directory outside this PUBLIC
# repo, so its absolute path is never hardcoded here. It is resolved in
# order:
#   1. the CONTRIBUTION_MAP_OUT environment variable, if set;
#   2. otherwise the path written in the gitignored pointer file
#      scripts/.contribution-map-path (one line, the output directory).
# The pointer file is the self-healing default: the daily rebuild runs
# `python3 scripts/build-ecosystem-data.py` with no env var and still
# finds the data, while the private location stays out of public source.
# A clear error fires if neither resolves to an existing directory.
def _resolve_map_dir():
    env = os.environ.get('CONTRIBUTION_MAP_OUT')
    if env:
        return Path(env).expanduser()
    pointer = ROOT / 'scripts' / '.contribution-map-path'
    if pointer.is_file():
        line = pointer.read_text().strip()
        if line:
            return Path(line).expanduser()
    return None

MAP = _resolve_map_dir()
if MAP is None or not MAP.is_dir():
    raise SystemExit(
        "Contribution-map output directory is not configured or is missing"
        + (f": {MAP}" if MAP is not None else "") + ".\n"
        "Set CONTRIBUTION_MAP_OUT to the directory containing the "
        "contribution-map JSON outputs (participants_v2.json, "
        "thread_titles.json), or write that path into the gitignored file "
        "scripts/.contribution-map-path."
    )

CACHE     = ROOT / '.github-cache'

# gh CLI binary. Override with GH_BIN env var if not on PATH.
GH_BIN    = os.environ.get('GH_BIN') or shutil.which('gh') or 'gh'

CACHE.mkdir(exist_ok=True)

def gh_api(path, force=False):
    """GET a GitHub API path with disk cache. Returns dict or None on 404."""
    key = path.replace('/', '_').replace('?', '_').replace('&', '_')
    cf  = CACHE / f'{key}.json'
    if cf.exists() and not force:
        try:
            return json.loads(cf.read_text())
        except Exception:
            pass
    try:
        r = subprocess.run(
            [GH_BIN, 'api', path],
            capture_output=True, text=True, timeout=15)
    except Exception as e:
        print(f'  WARN gh api {path}: {e}')
        return None
    if r.returncode != 0:
        if '404' in r.stderr or 'Not Found' in r.stderr:
            cf.write_text('null')
            return None
        print(f'  WARN gh api {path}: {r.stderr.strip()[:150]}')
        return None
    cf.write_text(r.stdout)
    return json.loads(r.stdout)

def extract_repo(url):
    if not url or 'github.com' not in url:
        return None
    s = url.replace('https://','').replace('http://','').replace('www.','')
    s = s.split('github.com/',1)[-1].rstrip('/')
    parts = s.split('/')
    if len(parts) < 2:
        return None
    return f'{parts[0]}/{parts[1]}'

# -------------------------------------------------------------------
# PROJECTS: load YAML + enrich each repo via GitHub API
# -------------------------------------------------------------------
print('Loading projects...')
projects = []
for p in sorted((ROOT / 'projects').glob('*.yaml')):
    with open(p) as f:
        d = yaml.safe_load(f)
    d['_id'] = p.stem
    repos = []
    for v in d.get('venues', []):
        r = extract_repo(v.get('url', ''))
        if r and r not in repos:
            repos.append(r)
    d['_repos'] = repos
    # enrich primary repo if present
    d['_github'] = None
    if repos:
        meta = gh_api(f'repos/{repos[0]}')
        if meta:
            d['_github'] = {
                'repo': repos[0],
                'created_at':     meta.get('created_at'),
                'pushed_at':      meta.get('pushed_at'),
                'updated_at':     meta.get('updated_at'),
                'stargazers':     meta.get('stargazers_count'),
                'forks':          meta.get('forks_count'),
                'open_issues':    meta.get('open_issues_count'),
                'license':        (meta.get('license') or {}).get('spdx_id'),
                'description':    meta.get('description'),
                'homepage':       meta.get('homepage'),
                'archived':       meta.get('archived'),
                'default_branch': meta.get('default_branch'),
                'language':       meta.get('language'),
            }
    projects.append(d)
print(f'  {len(projects)} projects, {sum(1 for p in projects if p["_github"])} with GitHub metadata')

# -------------------------------------------------------------------
# PEOPLE: load contribution map + enrich each with GitHub user metadata
# -------------------------------------------------------------------
print('Loading people...')
with open(MAP / 'participants_v2.json') as f:
    people_raw = json.load(f)

people = []
for i, (login, d) in enumerate(people_raw.items()):
    score = d.get('final_score', 0)
    # Everyone who actually took part in a tracked thread is in the lane
    # and is shown, however small the footprint. Rows with no posts and
    # no threads are not participants; they sit in the private map for
    # other reasons (watch or placeholder) and are skipped so this public
    # directory stays a record of real participation only. Score is used
    # for ranking below, then stripped from the emitted records.
    if d.get('comment_count', 0) == 0 and not d.get('threads'):
        continue
    record = {
        'login': login,
        # score is computed for admission + internal ranking only. It is
        # stripped from every record before emit so the public directory
        # carries no per-person reputation number.
        'score': score,
        'posts': d.get('comment_count', 0),
        'threads': d.get('threads', []),
        'topics': d.get('topics', []),
        'repos': d.get('repos', []),
        'first_seen_ours': d.get('first_seen'),
        'last_seen_ours':  d.get('last_seen'),
        'word_count': d.get('word_count', 0),
    }
    # enrich
    meta = gh_api(f'users/{login}')
    if meta:
        record['github'] = {
            'name':         meta.get('name'),
            'bio':          meta.get('bio'),
            'company':      meta.get('company'),
            'location':     meta.get('location'),
            'blog':         meta.get('blog'),
            'email':        meta.get('email'),
            'twitter':      meta.get('twitter_username'),
            'created_at':   meta.get('created_at'),
            'followers':    meta.get('followers'),
            'following':    meta.get('following'),
            'public_repos': meta.get('public_repos'),
            'type':         meta.get('type'),
        }
    else:
        record['github'] = None
    people.append(record)
    if (i + 1) % 20 == 0:
        print(f'  ...{i+1}/{len(people_raw)}')
people.sort(key=lambda p: -p['score'])
# Reputation is internal. Strip score from every record so it never lands
# in the published docs/ecosystem-data.json. Admission (score >= 5) and the
# ranking above already used it.
for p in people:
    p.pop('score', None)
print(f'  {len(people)} people, {sum(1 for p in people if p["github"]) } with GitHub metadata')

# -------------------------------------------------------------------
# THREADS: load contribution map + enrich each via GitHub issue API
# -------------------------------------------------------------------
print('Loading threads...')
with open(MAP / 'thread_titles.json') as f:
    thread_titles = json.load(f)

# -------------------------------------------------------------------
# DERIVED PROJECTS: every repo that hosts a tracked thread but has no
# hand-written project file becomes a project too, so the directory shows
# all projects in the lane, not only the curated ones. Derived entries
# carry GitHub metadata and are marked _derived so a curated file can
# supersede one later.
# -------------------------------------------------------------------
_curated_repos = {r for pr in projects for r in pr['_repos']}
_seen = set(_curated_repos)
_derived_repos = []
for _tmeta in thread_titles.values():
    if not isinstance(_tmeta, dict):
        continue
    _r = _tmeta.get('repo')
    if _r and _r not in _seen:
        _seen.add(_r)
        _derived_repos.append(_r)
for _r in _derived_repos:
    _m = gh_api(f'repos/{_r}')
    _g = None
    if _m:
        _g = {
            'repo': _r,
            'created_at':     _m.get('created_at'),
            'pushed_at':      _m.get('pushed_at'),
            'updated_at':     _m.get('updated_at'),
            'stargazers':     _m.get('stargazers_count'),
            'forks':          _m.get('forks_count'),
            'open_issues':    _m.get('open_issues_count'),
            'license':        (_m.get('license') or {}).get('spdx_id'),
            'description':    _m.get('description'),
            'homepage':       _m.get('homepage'),
            'archived':       _m.get('archived'),
            'default_branch': _m.get('default_branch'),
            'language':       _m.get('language'),
        }
    projects.append({
        '_id': 'repo--' + _r.replace('/', '--'),
        'name': _r,
        'slug': _r.replace('/', '--'),
        'description': (_g or {}).get('description') or '',
        'topics': [],
        'maturity': '',
        'license': (_g or {}).get('license') or '',
        'venues': [{'kind': 'repository', 'url': f'https://github.com/{_r}', 'label': _r}],
        '_repos': [_r],
        '_github': _g,
        '_derived': True,
    })
print(f'  +{len(_derived_repos)} derived projects from tracked thread repos')

repo_to_project = {}
for p in projects:
    for r in p['_repos']:
        repo_to_project[r] = p['_id']

threads = []
for topic_slug, meta in thread_titles.items():
    if not isinstance(meta, dict):
        continue
    repo   = meta.get('repo')
    number = meta.get('number')
    if not (repo and number):
        continue
    tid = f'{repo}#{number}'
    title = meta.get('title', tid)
    pid = repo_to_project.get(repo)
    participants = [p['login'] for p in people if tid in p['threads']]
    record = {
        'id': tid,
        'topic': topic_slug,
        'title': title,
        'repo': repo,
        'number': number,
        'project_id': pid,
        'url': f'https://github.com/{repo}/issues/{number}',
        'participants': participants,
        'participant_count': len(participants),
    }
    # enrich via issue API — may be a PR, both share endpoint
    issue = gh_api(f'repos/{repo}/issues/{number}')
    if issue:
        record['github'] = {
            'state':       issue.get('state'),
            'created_at':  issue.get('created_at'),
            'updated_at':  issue.get('updated_at'),
            'closed_at':   issue.get('closed_at'),
            'comments':    issue.get('comments'),
            'is_pr':       bool(issue.get('pull_request')),
            'author':      (issue.get('user') or {}).get('login'),
            'labels':      [l.get('name') for l in issue.get('labels', [])],
        }
    else:
        record['github'] = None
    threads.append(record)
print(f'  {len(threads)} threads, {sum(1 for t in threads if t["github"])} with GitHub metadata')

# -------------------------------------------------------------------
# Emit
# -------------------------------------------------------------------
out = {
    'generated_at': datetime.now(timezone.utc).isoformat(),
    'projects': projects,
    'people':   people,
    'threads':  threads,
    'stats': {
        'projects': len(projects),
        'people':   len(people),
        'people_total_raw': len(people_raw),
        'threads':  len(threads),
        'threads_mapped_to_project': sum(1 for t in threads if t['project_id']),
        'projects_enriched': sum(1 for p in projects if p['_github']),
        'people_enriched':   sum(1 for p in people   if p['github']),
        'threads_enriched':  sum(1 for t in threads  if t['github']),
    },
}

out_path = ROOT / 'docs' / 'ecosystem-data.json'
with open(out_path, 'w') as f:
    json.dump(out, f, indent=2, default=str)

print()
print(f'Wrote {out_path}')
for k, v in out['stats'].items():
    print(f'  {k}: {v}')
