"""Native delivery edge regressions; Git and PR watcher use local synthetic data."""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LFG = ROOT / 'skills/lfg'
WATCH = ROOT / 'skills/ce-babysit-pr/scripts/pr-snapshot'


def test_prior_unoffered_commit_is_in_review_push_range(tmp_path):
    def git(at, *args):
        return subprocess.check_output(['git', '-C', str(at), *args], text=True).strip()
    remote = tmp_path / 'remote.git'
    subprocess.run(['git', 'init', '--bare', '-q', '-b', 'main', str(remote)], check=True)
    repo = tmp_path / 'work'
    subprocess.run(['git', 'init', '-q', '-b', 'main', str(repo)], check=True)
    git(repo, 'config', 'user.name', 'Fixture')
    git(repo, 'config', 'user.email', 'fixture@example.invalid')
    def commit(name):
        (repo / name).write_text(name)
        git(repo, 'add', '--', name)
        git(repo, 'commit', '-qm', name, '--', name)
        return git(repo, 'rev-parse', 'HEAD')
    base = commit('base')
    git(repo, 'remote', 'add', 'origin', str(remote))
    git(repo, 'push', '-q', '-u', 'origin', 'main')
    git(repo, 'switch', '-qc', 'topic')
    private = commit('unoffered')
    commit('requested')
    commit('review-fix')
    assert private in git(repo, 'rev-list', 'origin/main..HEAD').splitlines()
    assert git(remote, 'rev-parse', 'main') == base
    # This is an instruction contract, not a simulated agent. The fixture above
    # demonstrates why both reachable publishing branches need the same gate.
    entry = (LFG / 'SKILL.md').read_text(encoding='utf-8')
    fix = (LFG / 'references/review-followup.md').read_text(encoding='utf-8')
    ship = (LFG / 'references/shipping.md').read_text(encoding='utf-8')
    assert 'before the first mutating child' in entry
    assert 'all routes' in fix and 'shipping precondition' in fix
    assert 'unoffered or unknown' in ship and 'do NOT invoke' in ship


def test_failed_thread_baseline_leaves_new_request_actionable(tmp_path):
    state = tmp_path / 'state'
    fetch = tmp_path / 'fetch.json'
    def payload(comment):
        fetch.write_text(json.dumps({
            'pr_state': 'OPEN', 'mergeable': 'MERGEABLE', 'merge_state_status': 'BLOCKED',
            'review_decision': 'REVIEW_REQUIRED', 'head_sha': 'a' * 40,
            'url': 'https://example.invalid/fixture/pull/1',
            'threads': [{'thread_id': 'T1', 'last_comment_id': comment,
                         'last_comment_at': '2026-01-01T00:00:00Z'}],
            'feedback': [], 'checks': [],
        }))
    def invoke(cmd, source, *extra):
        return subprocess.run([sys.executable, str(WATCH), cmd, '--pr', '1',
                               '--repo', 'example/fixture', '--state-dir', str(state),
                               '--fetch-file', str(source), *extra],
                              capture_output=True, text=True)
    payload('C1')
    first = invoke('snapshot', fetch, '--start-invocation')
    assert first.returncode == 0, first.stderr
    data = json.loads(first.stdout)
    resume = ['--invocation-id', data['invocation_id'], '--session-started-at',
              data['invocation_started_at'], '--invocation-budget-seconds',
              str(data['invocation_budget_seconds'])]
    failed = invoke('mark', tmp_path / 'unavailable', '--thread', 'T1',
                    '--disposition', 'dispatched', *resume)
    assert failed.returncode != 0 and 'baseline' in failed.stderr
    prior = json.loads((state / 'state.json').read_text())['threads']['T1']
    assert prior['disposition'] == 'open'
    payload('new-reviewer-request')
    tick = invoke('snapshot', fetch, *resume)
    assert tick.returncode == 0, tick.stderr
    assert json.loads(tick.stdout)['counts']['threads'] == 1
    after = json.loads((state / 'state.json').read_text())['threads']['T1']
    assert after['disposition'] == 'open' and after['last_comment_id'] == 'new-reviewer-request'
    marked = invoke('mark', fetch, '--thread', 'T1', '--disposition', 'dispatched', *resume)
    assert marked.returncode == 0, marked.stderr
    final = json.loads((state / 'state.json').read_text())['threads']['T1']
    assert final['acted_identity'][0] == 'new-reviewer-request'
