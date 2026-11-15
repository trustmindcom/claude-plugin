# Plugin evals

About 200 realistic requests that check the Evident plugin behaves the way we want: the skill fires on
questions about the company's own practices and not on general ones, it reads the right reference file, it finds
operations through `capability_search`, and it never breaks the must-never rules. Each case runs headless through
`claude -p` with this repo's plugin loaded, on Haiku, Sonnet and Opus, and is scored from the recorded trace.

## Run it again

Point it at an Evident **test** organization (never a customer's) and run one command from the repo root:

```bash
export EVIDENT_MCP_URL=https://<evident-mcp-host>/mcp
export EVIDENT_TOKEN_ADMIN=...            # MCP access token for each test user
export EVIDENT_TOKEN_KNOWLEDGE_EDITOR=...
export EVIDENT_TOKEN_MEMBER=...
export EVIDENT_TOKEN_MEMBER_EMPTY_KB=...  # a member in an organization with no documents
python3 evals/run.py
```

That runs every case on all three models (3 runs each for trigger, near-miss and routing cases) and writes
`evals/report.md`, with each run's full record under `evals/results/<timestamp>/runs.jsonl` (ignored by git).
It uses your own `claude` login. A full run is about 1,200 conversations, so expect a few hours at the default
`--concurrency 4`.

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
