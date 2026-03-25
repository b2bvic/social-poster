# social-poster

Post to Twitter/X and LinkedIn from the command line. Includes a JSONL queue system for scheduled multi-platform posting.

Built by [Victor Valentine Romo](https://victorvalentineromo.com) at [Scale With Search](https://scalewithsearch.com).

## Scripts

| Script | What |
|--------|------|
| `post-twitter` | Post tweets and threads via X v2 API |
| `post-linkedin` | Post to LinkedIn via v2 Posts API |
| `blitz-poster` | Read JSONL queue, dispatch to platforms, track status |

## Usage

### Single tweet
```bash
export TWITTER_BEARER_TOKEN="..."
./post-twitter "Just shipped 8 open source repos in one session."
```

### Twitter thread
```bash
./post-twitter --thread "First tweet" "Second tweet" "Third tweet"
```

### LinkedIn post
```bash
export LINKEDIN_ACCESS_TOKEN="..."
export LINKEDIN_PERSON_URN="urn:li:person:YOUR_ID"
./post-linkedin "New article on AI memory infrastructure."
```

### Scheduled queue
```bash
# Add to queue (JSONL format)
echo '{"date":"2026-03-26","platform":"twitter","content":"Morning post","status":"pending"}' >> ~/.cache/social-auto/blitz-queue.jsonl

# Process today's queue
./blitz-poster

# Dry-run (see what would post)
./blitz-poster --dry-run
```

## Queue Format

```jsonl
{"date":"2026-03-26","platform":"twitter","content":"Tweet text here","status":"pending"}
{"date":"2026-03-26","platform":"linkedin","content":"LinkedIn post here","status":"pending"}
```

Status lifecycle: `pending` → `posted` (with timestamp added)

## Auth Setup

### Twitter/X
Create an app at developer.x.com. Get a Bearer token with tweet.write scope.

### LinkedIn
Create an app at linkedin.com/developers. Get an access token with `w_member_social` scope.

Store tokens as environment variables or in `~/.cache/social-auto/twitter-credentials.json` and `~/.cache/social-auto/linkedin-credentials.json`.

## License

MIT
