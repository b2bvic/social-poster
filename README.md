# social-poster

Command-line publishing tools with a JSONL queue and a dry-run path.

## Principle cluster

This repository demonstrates **P09 (agency is governed)** and **P10 (production means persistence, bounded autonomy, and observability)** because the queue reader selects pending items for the current date and exits cleanly when no eligible item exists.

[Read the principles](https://victorvalentineromo.com/principles).

## Worked example

```bash
./blitz-poster --dry-run
```

## License

MIT.

## How this was built

This 2026 README refit used model assistance.

No claim is made about how the underlying code was authored or reviewed.
