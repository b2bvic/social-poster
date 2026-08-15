# social-poster

Command-line publishing tools with a JSONL queue and a preview path.

The queue command can inspect eligible items without publishing. The
`post-twitter` and `post-linkedin` commands perform live API writes when valid
credentials are present. Review the exact text before using either command.

## Principle cluster

This repository demonstrates **P09 (agency is governed)** and **P10 (production means persistence, bounded autonomy, and observability)** because the queue reader selects pending items for the current date and exits cleanly when no eligible item exists.

[Read the principles](https://victorvalentineromo.com/principles).

## Worked example

```bash
./blitz-poster --dry-run
```

## Requirements and boundaries

- X requires `~/.cache/social-auto/twitter-credentials.json`.
- LinkedIn requires the token and person-ID files documented in `post-linkedin`.
- The direct platform commands have no preview mode.
- A successful API response proves acceptance, not audience delivery.

## License

MIT.

## How this was built

This 2026 README refit used model assistance.

No claim is made about how the underlying code was authored or reviewed.
