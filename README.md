# X posting CLI with queue preview: social-poster

`social-poster` previews X posting queues for content teams. Use its JSONL workflow to inspect eligible items before invoking live publishing.

[Project page](https://scalewithsearch.com/code/social-poster)

## Install

Requirements: Python 3.11 or later.

```bash
gh repo clone b2bvic/social-poster
cd social-poster
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
```

## Quick start

```bash
.venv/bin/python -m pytest -q
```

These checks use synthetic input and perform no live sends.

## Usage

Preview the queue before any live run:

```bash
./blitz-poster --dry-run
```

Post directly to X:

```bash
./post-twitter "Single post text"
./post-twitter --thread "Post 1" "Post 2"
```

The queue file is `~/.cache/social-auto/blitz-queue.jsonl`. X credentials come from `~/.cache/social-auto/twitter-credentials.json`. The `post-twitter` command publishes immediately.

## How it works

- Select pending records for the current date by parsing JSON.
- Preview the first five content lines with --dry-run.
- Publish X posts or threads and record accepted responses.
- Reject the retired post-linkedin command without an API call.

## Limits

- Direct posting has no preview mode and performs live API writes.
- Review the complete text before execution; the queue preview shows only five lines.
- Queue rewrites are not transactional, and duplicate section identities can share status updates.
- Thread parsing and API acceptance do not guarantee complete audience delivery.

## Related repositories

- [watchdog](https://github.com/b2bvic/watchdog)
- [tg-notify](https://github.com/b2bvic/tg-notify)

## Development

```bash
.venv/bin/python -m pytest -q
.venv/bin/python -m ruff check --select E9,F63,F7,F82 tests
```

CI runs the portable tests and checks syntax-related Python lint rules.

## License

MIT. See [LICENSE](LICENSE).
