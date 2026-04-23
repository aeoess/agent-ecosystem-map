#!/usr/bin/env python3
"""
Build ecosystem-data.json for site/index.html.

Pulls and enriches:
- 18 projects   from projects/*.yaml + GitHub repo metadata
- 130 people    from aeoess_web contribution map + GitHub user metadata
- 93 threads    from aeoess_web contribution map + GitHub issue metadata

Caches GitHub responses to .github-cache/ so re-runs don't burn API quota.
"""
import json, yaml, os, subprocess, time, sys
from pathlib import Path
from datetime import datetime, timezone

ROOT      = Path('/Users/tima/agent-ecosystem-map')
MAP       = Path('/Users/tima/aeoess_web/specs/contribution-map/out')
CACHE     = ROOT / '.github-cache'
GH_BIN    = '/Users/tima/.local/bin/gh'

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
skip_logins = {'aeoess'}  # self
for i, (login, d) in enumerate(people_raw.items()):
    if login in skip_logins:
        continue
    score = d.get('final_score', 0)
    if score < 5:  # drop pure noise
        continue
    record = {
        'login': login,
        'score': score,
        'posts': d.get('comment_count', 0),
        'threads': d.get('threads', []),
        'topics': d.get('topics', []),
        'repos': d.get('repos', []),
        'first_seen_ours': d.get('first_seen'),
        'last_seen_ours':  d.get('last_seen'),
        'ship':    d.get('ship', 0),
        'propose': d.get('propose', 0),
        'review':  d.get('review', 0),
        'mentions_received': d.get('mentions_received', 0),
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
print(f'  {len(people)} people, {sum(1 for p in people if p["github"]) } with GitHub metadata')

# -------------------------------------------------------------------
# THREADS: load contribution map + enrich each via GitHub issue API
# -------------------------------------------------------------------
print('Loading threads...')
with open(MAP / 'thread_titles.json') as f:
    thread_titles = json.load(f)

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

out_path = ROOT / 'site' / 'ecosystem-data.json'
with open(out_path, 'w') as f:
    json.dump(out, f, indent=2, default=str)

print()
print(f'Wrote {out_path}')
for k, v in out['stats'].items():
    print(f'  {k}: {v}')
