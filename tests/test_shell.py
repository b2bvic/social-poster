import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def sandbox(tmp_path):
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    (bin_dir / "python3").symlink_to(sys.executable)
    calls = tmp_path / "calls.jsonl"
    (bin_dir / "curl").write_text("#!/usr/bin/env python3\nimport json, os, sys\np=os.environ['CALL_LOG']\nwith open(p, 'a') as f: f.write(json.dumps(sys.argv[1:])+'\\n')\nn=len(open(p).readlines())\nprint(json.dumps({'ok': n>1 if os.environ.get('REJECT_FIRST') else True}))\n")
    (bin_dir / "curl").chmod(0o755)
    env = {"HOME": str(tmp_path), "PATH": str(bin_dir) + ":/usr/bin:/bin", "CALL_LOG": str(calls)}
    return tmp_path, bin_dir, calls, env


def run(script, args, env):
    return subprocess.run(["/bin/bash", str(ROOT / script), *args], env=env, capture_output=True, text=True)


def test_dry_run_leaves_queue_pending_and_sends_nothing(sandbox):
    home, _, calls, env = sandbox
    cache = home / ".cache/social-auto"
    cache.mkdir(parents=True)
    content = home / "post.md"
    content.write_text("## Post #1\n---\nSynthetic preview text.\n---\n")
    from datetime import date
    item = {"date": date.today().isoformat(), "platform": "twitter", "content_file": str(content), "status": "pending", "section": "Post #1"}
    queue = cache / "blitz-queue.jsonl"
    queue.write_text(json.dumps(item, separators=(",", ":")) + "\n")
    before = queue.read_bytes()
    result = run("blitz-poster", ["--dry-run"], env)
    assert result.returncode == 0, result.stderr
    assert "Synthetic preview text." in result.stdout
    assert queue.read_bytes() == before
    assert not calls.exists()


def test_retired_platform_exits_without_curl(sandbox):
    _, _, calls, env = sandbox
    result = run("post-linkedin", ["Synthetic text"], env)
    assert result.returncode != 0
    assert result.stderr.strip() == "LinkedIn posting is retired."
    assert not calls.exists()


def test_x_thread_payload_and_reply_chain_use_mocked_curl(sandbox):
    home, bin_dir, calls, env = sandbox
    cache = home / ".cache/social-auto"
    cache.mkdir(parents=True)
    (cache / "twitter-credentials.json").write_text(json.dumps({"access_token": "demo"}))
    stub = bin_dir / "curl"
    stub.write_text("#!/usr/bin/env python3\nimport json, os, sys\na=sys.argv[1:]\np=os.environ['CALL_LOG']\nwith open(p, 'a') as f: f.write(json.dumps(a)+'\\n')\nn=len(open(p).readlines())\nwith open(a[a.index('-o')+1], 'w') as f: json.dump({'data': {'id': str(n)}}, f)\nprint('201', end='')\n")
    result = run("post-twitter", ["--thread", 'First "quoted" tweet', "Second tweet"], env)
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "https://x.com/i/status/1"
    requests = [json.loads(line) for line in calls.read_text().splitlines()]
    payloads = [json.loads(args[args.index("-d") + 1]) for args in requests]
    assert payloads[0] == {"text": 'First "quoted" tweet'}
    assert payloads[1] == {"text": "Second tweet", "reply": {"in_reply_to_tweet_id": "1"}}
    assert all("Authorization: Bearer demo" in request for request in requests)


def test_pretty_json_queue_is_also_eligible(sandbox):
    home, _, calls, env = sandbox
    cache = home / ".cache/social-auto"
    cache.mkdir(parents=True)
    content = home / "post.md"
    content.write_text("## Post #1\n---\nReadable JSON preview.\n---\n")
    from datetime import date
    item = {"date": date.today().isoformat(), "platform": "twitter", "content_file": str(content), "status": "pending", "section": "Post #1"}
    (cache / "blitz-queue.jsonl").write_text(json.dumps(item) + "\n")
    result = run("blitz-poster", ["--dry-run"], env)
    assert result.returncode == 0, result.stderr
    assert "Readable JSON preview." in result.stdout
    assert not calls.exists()


def queued_post(sandbox):
    home, bin_dir, calls, env = sandbox
    cache = home / ".cache/social-auto"
    cache.mkdir(parents=True)
    (cache / "twitter-credentials.json").write_text(json.dumps({"access_token": "demo"}))
    content = home / "post's.md"
    content.write_text('## Post #1\n---\nQuoted "preview" text.\n---\n')
    from datetime import date
    item = {"date": date.today().isoformat(), "platform": "twitter", "content_file": str(content), "status": "pending", "section": "Post #1"}
    queue = cache / "blitz-queue.jsonl"
    queue.write_text(json.dumps(item) + "\n")
    return cache, queue


def test_mocked_publish_records_valid_queue_and_history(sandbox):
    _, bin_dir, calls, env = sandbox
    cache, queue = queued_post(sandbox)
    (bin_dir / "curl").write_text("#!/usr/bin/env python3\nimport json, os, sys\na=sys.argv[1:]\nwith open(os.environ['CALL_LOG'], 'a') as f: f.write(json.dumps(a)+'\\n')\nwith open(a[a.index('-o')+1], 'w') as f: json.dump({'data': {'id': '1'}}, f)\nprint('201', end='')\n")
    result = run("blitz-poster", [], env)
    assert result.returncode == 0, result.stderr
    item = json.loads(queue.read_text())
    assert item["status"] == "posted"
    assert item["post_url"] == "https://x.com/i/status/1"
    history = json.loads((cache / "post-history.jsonl").read_text())
    assert history["preview"] == 'Quoted "preview" text.'
    assert len(calls.read_text().splitlines()) == 1


def test_transport_failure_keeps_queue_pending(sandbox):
    _, bin_dir, _, env = sandbox
    cache, queue = queued_post(sandbox)
    (bin_dir / "curl").write_text("#!/bin/bash\nexit 7\n")
    result = run("blitz-poster", [], env)
    assert result.returncode != 0
    assert json.loads(queue.read_text())["status"] == "pending"
    assert not (cache / "post-history.jsonl").exists()
