# Plugin evals

About 200 realistic requests that check the Evident plugin behaves the way we want: the skill fires on
questions about the company's own practices and not on general ones, it reads the right reference file, it finds
operations through `capability_search`, and it never breaks the must-never rules. Each case runs headless through
`claude -p` with this repo's plugin loaded, on Haiku, Sonnet and Opus, and is scored from the recorded trace.

## Run it again

Point it at an Evident **test** organization (never a customer's) and run one command from the repo root:

```bash
python3 evals/run.py
```

It signs in with `evals/.tokens.json` (ignored by git, owner-only), which holds the test org's MCP URL, the OAuth
client id the tokens were issued to, and a refresh token for each test user:

```json
{
  "mcp_url": "https://<evident-mcp-host>/mcp",
  "client_id": "<oauth client id>",
  "roles": {
    "admin": {"refresh_token": "..."},
    "knowledge_editor": {"refresh_token": "..."},
    "member": {"refresh_token": "..."},
    "member_empty_kb": {"refresh_token": "..."}
  }
}
```

Access tokens last an hour and a full run takes hours, so the runner refreshes each one shortly before it expires
and writes the new refresh token back (the server replaces it on every refresh). Refresh tokens last 30 days.
For a short run you can skip the file and set `EVIDENT_MCP_URL` plus `EVIDENT_TOKEN_<ROLE>` access tokens instead.

That runs every case on all three models (3 runs each for trigger, near-miss and routing cases) and writes
`evals/report.md`, with each run's full record under `evals/results/<timestamp>/runs.jsonl` (ignored by git).
A full run is about 1,200 conversations, so expect a few hours at the default `--concurrency 4`.

Claude runs on your own subscription login (`claude` signed in with your Claude plan). The runner removes
`ANTHROPIC_API_KEY`, `ANTHROPIC_AUTH_TOKEN`, `ANTHROPIC_BASE_URL` and the Bedrock and Vertex switches from every
run, and the report shows the login each run used (`apiKeySource: none` is the subscription).

Useful options:

```bash
python3 evals/run.py --models haiku --category should_trigger --category near_miss   # a slice
python3 evals/run.py --id 'cap-*' --repeats 1                                         # case ids by glob
python3 evals/run.py --no-mcp --no-judge --category routing                           # no server needed
python3 evals/run.py report evals/results/<timestamp>                                 # rebuild report.md
```

## What the test org needs

- Documents in the knowledge base, including two that contradict each other so there are open conflicts.
- One questionnaire with open questions, some assigned to the member.
- The four users above, in one organization, plus the empty-knowledge-base member in a second one.

Cases name customers such as Acme, Globex and Initech. They don't need to exist: the cases check what Claude
does, and asking which questionnaire the user means is a fine answer.

## Cases

`cases.jsonl` holds one case per line:

| Field | Meaning |
| -- | -- |
| `id` | Stable name, prefixed by category |
| `category` | `should_trigger`, `near_miss`, `routing`, `capability_search`, `must_never`, `role`, `model` |
| `role` | `admin`, `knowledge_editor`, `member` or `member_empty_kb`; picks the token |
| `model` | `haiku`, `sonnet`, `opus`, or `any` (runs on all three) |
| `prompt` | What the user types |
| `files` | Optional fixture files from `fixtures/` placed in the working directory |
| `expect` | The checks below |

`expect.by_model` overrides checks for one model. Routing cases use it so that, for work beyond lookups, Haiku
passes by stopping (the skill's model rule) instead of having to read the reference file.

`expect` checks, all scored from the trace:

| Check | Passes when |
| -- | -- |
| `skill` | The `evident` skill fired (`true`) or did not (`false`) |
| `refs_read` / `refs_not_read` | These reference files were read / were not read |
| `no_evident_tools` | No Evident tool was called |
| `tools_any` / `tools_none` | At least one of these Evident operations ran / none of them ran (a capability run counts as the capability it ran) |
| `capability` | A `capability_search` returned this capability in its top 3 |
| `run_tool` | The capability then ran through this run tool |
| `no_local_read` | The fixture file was never opened locally (uploading it with `curl` is fine) |
| `text_has` | The final reply contains this text |
| `judge` | A Haiku judge applies these PASS/FAIL criteria to the reply and tool calls |

A run passes when every check it could decide passed, and fails when any decided check failed, even if the run
later timed out. Checks that need the Evident server, and the judge, are skipped when the run has none. A
capability case with no `capability_search` call leaves the search check undecided rather than counting a miss.
A judge call that fails is recorded as unknown, never as a pass or a fail.

The capability cases cover the 40 most-used operations that are not named tools, from 90 days of real MCP usage.
Routing cases target the reference files `answer`, `questionnaire`, `portal`, `review`, `knowledge`, `setup` and
`tour` from the v2 skill layout. On a plugin without those files, the routing results mean nothing.

## How a run is isolated

Each run gets a fresh temporary copy of the plugin with its own Evident server entry removed, and the test server
passed with `--mcp-config` and `--strict-mcp-config`. `--setting-sources project` keeps your own settings, plugins
and skills out, and the working directory is an empty temporary folder. Allowed tools are `Skill`, `Read`, `Glob`,
`Grep`, `Bash(curl:*)` (for file uploads) and the Evident tools.

Runs call real tools, including writes, on the test organization. Use a test org you can reset.
