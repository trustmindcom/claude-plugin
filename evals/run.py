#!/usr/bin/env python3
"""Run the Evident plugin eval: each case through `claude -p` with this repo's plugin loaded, scored from the trace.

Usage:
    python3 evals/run.py                      # every case on haiku, sonnet and opus, then write evals/report.md
    python3 evals/run.py --models haiku --category should_trigger --no-mcp
    python3 evals/run.py report evals/results/<run>   # rebuild the report from a finished run

Sign-in to the Evident test org (see evals/README.md): evals/.tokens.json holds the MCP URL, the OAuth client id
and a refresh token per role; the runner refreshes access tokens as they near their 1-hour expiry and saves the
rotated refresh tokens back. EVIDENT_MCP_URL and EVIDENT_TOKEN_<ROLE> (a fixed access token) override the file.

Claude runs on your own subscription login: API key variables are removed from every run's environment.
Standard library only; needs the `claude` CLI on PATH.
"""

from __future__ import annotations

import argparse
import concurrent.futures as futures
import datetime as dt
import fnmatch
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path

EVALS = Path(__file__).resolve().parent
PLUGIN_ROOT = EVALS.parent
MODELS = ("haiku", "sonnet", "opus")
REPEATED = {"should_trigger", "near_miss", "routing"}
MCP_PREFIX = "mcp__evident__"
REF_DIR = "skills/evident/references/"
RUN_TOOLS = ("capability_run_read", "capability_run_write", "capability_run_destructive")
ALLOWED_TOOLS = ["Skill", "Read", "Glob", "Grep", "Bash(curl:*)", f"{MCP_PREFIX}*"]
MCP_CHECKS = {"tools_any", "tools_none", "capability", "run_tool"}
RUN_TIMEOUT_S = 600
EXCERPT_CHARS = 700
TOKEN_FILE = EVALS / ".tokens.json"
REFRESH_MARGIN_S = 900
# Runs use the operator's Claude subscription login, never an API key or a proxy.
API_ENV = ("ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN", "ANTHROPIC_BASE_URL", "CLAUDE_CODE_USE_BEDROCK", "CLAUDE_CODE_USE_VERTEX")
CHILD_ENV = {k: v for k, v in os.environ.items() if k not in API_ENV}


# --- Loading ---------------------------------------------------------------------------------------------------


def load_cases(path: Path) -> list[dict]:
    cases = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    for case in cases:
        missing = {"id", "category", "role", "model", "prompt", "expect"} - case.keys()
        if missing:
            raise SystemExit(f"case {case.get('id')} is missing {sorted(missing)}")
    return cases


class Tokens:
    """MCP access tokens per role, refreshed from the token file before they expire."""

    def __init__(self, path: Path):
        self.path = path
        self.data = json.loads(path.read_text()) if path.exists() else {}
        self.mcp_url = os.environ.get("EVIDENT_MCP_URL") or self.data.get("mcp_url")
        self.lock = threading.Lock()

    def has(self, role: str) -> bool:
        return bool(os.environ.get(f"EVIDENT_TOKEN_{role.upper()}") or self.data.get("roles", {}).get(role))

    def get(self, role: str) -> str | None:
        fixed = os.environ.get(f"EVIDENT_TOKEN_{role.upper()}")
        if fixed:
            return fixed
        with self.lock:
            entry = self.data.get("roles", {}).get(role)
            if not entry:
                return None
            if entry.get("access_token") and entry.get("expires_at", 0) - time.time() > REFRESH_MARGIN_S:
                return entry["access_token"]
            body = urllib.parse.urlencode({
                "grant_type": "refresh_token", "refresh_token": entry["refresh_token"], "client_id": entry.get("client_id") or self.data["client_id"],
            }).encode()  # fmt: skip
            request = urllib.request.Request(f"{self.mcp_url.rstrip('/')}/token", data=body, method="POST")
            with urllib.request.urlopen(request, timeout=30) as response:
                fresh = json.loads(response.read())
            entry.update(
                access_token=fresh["access_token"],
                refresh_token=fresh.get("refresh_token", entry["refresh_token"]),
                expires_at=time.time() + int(fresh.get("expires_in", 3600)),
            )
            self.save()
            return entry["access_token"]

    def save(self) -> None:
        """Write atomically, owner-only: the server rotates refresh tokens, so losing a write loses the sign-in."""
        tmp = self.path.with_suffix(".tmp")
        fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(fd, "w") as fh:
            json.dump(self.data, fh, indent=2)
        os.replace(tmp, self.path)


def plan_runs(cases: list[dict], models: list[str], repeats: int) -> list[tuple[dict, str, int]]:
    jobs = []
    for case in cases:
        case_models = models if case["model"] == "any" else [m for m in models if m == case["model"]]
        runs = repeats if case["category"] in REPEATED else 1
        jobs += [(case, model, i) for model in case_models for i in range(1, runs + 1)]
    return jobs


# --- One run ---------------------------------------------------------------------------------------------------


def prepare_plugin(dest: Path) -> Path:
    """Copy the plugin without its own Evident server, so the run's --mcp-config server is the only one."""
    plugin = dest / "plugin"
    shutil.copytree(PLUGIN_ROOT, plugin, ignore=shutil.ignore_patterns(".git", "evals"))
    manifest = plugin / ".claude-plugin" / "plugin.json"
    data = json.loads(manifest.read_text())
    data.pop("mcpServers", None)
    manifest.write_text(json.dumps(data, indent=2))
    (plugin / ".mcp.json").unlink(missing_ok=True)
    return plugin


def run_claude(case: dict, model: str, mcp_url: str | None, token: str | None) -> dict:
    with tempfile.TemporaryDirectory(prefix="evident-eval-") as tmp:
        tmp_path = Path(tmp)
        plugin = prepare_plugin(tmp_path)
        work = tmp_path / "work"
        work.mkdir()
        for name in case.get("files", []):
            shutil.copy(EVALS / "fixtures" / name, work / name)
        cmd = [
            "claude", "-p", case["prompt"], "--model", model, "--plugin-dir", str(plugin),
            "--setting-sources", "project", "--strict-mcp-config", "--no-session-persistence",
            "--output-format", "stream-json", "--verbose", "--allowedTools", *ALLOWED_TOOLS,
        ]  # fmt: skip
        if mcp_url and token:
            server = {"type": "http", "url": mcp_url, "headers": {"Authorization": f"Bearer {token}"}}
            config = tmp_path / "mcp.json"
            config.write_text(json.dumps({"mcpServers": {"evident": server}}))
            config.chmod(0o600)
            cmd += ["--mcp-config", str(config)]
        started = time.monotonic()
        try:
            proc = subprocess.run(cmd, cwd=work, env=CHILD_ENV, capture_output=True, text=True, timeout=RUN_TIMEOUT_S)
            stdout, error = proc.stdout, (proc.stderr.strip()[-500:] if proc.returncode else "")
        except subprocess.TimeoutExpired as exc:
            raw = exc.stdout or b""
            stdout, error = (raw.decode(errors="replace") if isinstance(raw, bytes) else raw), "timeout"
        trace = parse_stream(stdout)
        trace["duration_s"] = round(time.monotonic() - started, 1)
        if error and not trace.get("error"):
            trace["error"] = error
        return trace


def parse_stream(stdout: str) -> dict:
    calls: list[dict] = []
    by_id: dict[str, dict] = {}
    trace: dict = {"calls": calls, "final_text": "", "cost_usd": None, "turns": None, "error": None, "mcp_status": None,
                   "api_key_source": None}  # fmt: skip
    for line in stdout.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        kind = event.get("type")
        if kind == "system" and event.get("subtype") == "init":
            servers = event.get("mcp_servers") or []
            trace["mcp_status"] = {s.get("name"): s.get("status") for s in servers}
            trace["api_key_source"] = event.get("apiKeySource")
        elif kind in ("assistant", "user"):
            for block in (event.get("message") or {}).get("content") or []:
                if not isinstance(block, dict):
                    continue
                if block.get("type") == "tool_use":
                    call = {"name": block.get("name", ""), "input": block.get("input") or {}, "result": ""}
                    calls.append(call)
                    by_id[block.get("id", "")] = call
                elif block.get("type") == "tool_result" and block.get("tool_use_id") in by_id:
                    by_id[block["tool_use_id"]]["result"] = result_text(block.get("content"))[:20000]
        elif kind == "result":
            trace["final_text"] = event.get("result") or ""
            trace["cost_usd"] = event.get("total_cost_usd")
            trace["turns"] = event.get("num_turns")
            if event.get("is_error"):
                trace["error"] = event.get("subtype") or "error"
    return trace


def result_text(content) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(part.get("text", "") for part in content if isinstance(part, dict))
    return ""


# --- Scoring ---------------------------------------------------------------------------------------------------


def evident_name(tool: str) -> str | None:
    return tool[len(MCP_PREFIX) :] if tool.startswith(MCP_PREFIX) else None


def evident_calls(calls: list[dict]) -> list[str]:
    """Evident operations in order; a capability run counts as the capability it ran."""
    names = []
    for call in calls:
        name = evident_name(call["name"])
        if name in RUN_TOOLS:
            names.append(str(call["input"].get("name") or name))
        elif name:
            names.append(name)
    return names


def summarize(trace: dict) -> dict:
    calls = trace["calls"]
    refs = [
        Path(str(c["input"].get("file_path", ""))).name
        for c in calls
        if c["name"] == "Read" and REF_DIR in str(c["input"].get("file_path", ""))
    ]
    skill = any(c["name"] == "Skill" and re.search(r"(^|:)evident$", str(c["input"].get("skill", ""))) for c in calls)
    return {"skill_fired": skill, "refs_read": sorted(set(refs)), "evident_calls": evident_calls(calls)}


def search_hits(calls: list[dict]) -> list[list[str]]:
    """Capability names returned by each capability_search, in order."""
    hits = []
    for call in calls:
        if evident_name(call["name"]) != "capability_search":
            continue
        try:
            payload = json.loads(call["result"])
        except (json.JSONDecodeError, TypeError):
            payload = None
        names: list[str] = []
        if payload is not None:
            items = payload if isinstance(payload, list) else next(
                (v for v in payload.values() if isinstance(v, list)), []
            ) if isinstance(payload, dict) else []
            names = [str(i.get("name")) for i in items if isinstance(i, dict) and i.get("name")]
        else:
            names = re.findall(r'"name"\s*:\s*"([a-z0-9_]+)"', call["result"] or "")
        hits.append(names)
    return hits


def local_reads(calls: list[dict], filenames: list[str]) -> list[str]:
    """Fixture files the run opened itself. Uploading the file with curl is the allowed way to touch it."""
    found = []
    for call in calls:
        if call["name"] not in ("Read", "Bash", "Grep"):
            continue
        blob = json.dumps(call["input"])
        upload = call["name"] == "Bash" and re.search(r"\bcurl\b", blob) and re.search(r"(-T\b|--upload-file|@)", blob)
        found += [f for f in filenames if f in blob and not upload]
    return found


def expectations(case: dict, model: str) -> dict:
    """The case's checks, with any per-model override (expect.by_model.<model>) applied."""
    exp = {k: v for k, v in case["expect"].items() if k != "by_model"}
    return {**exp, **case["expect"].get("by_model", {}).get(model, {})}


def score(case: dict, model: str, trace: dict, summary: dict, mcp: bool) -> list[dict]:
    exp = expectations(case, model)
    calls = summary["evident_calls"]
    checks: list[dict] = []

    def check(name: str, ok: bool | None, detail: str = "") -> None:
        if name in MCP_CHECKS and not mcp:
            ok, detail = None, "skipped: no MCP server for this run"
        checks.append({"check": name, "pass": ok, "detail": detail})

    if "skill" in exp:
        check("skill", summary["skill_fired"] == exp["skill"], f"fired={summary['skill_fired']}")
    if exp.get("no_evident_tools"):
        check("no_evident_tools", not calls, ", ".join(calls))
    if exp.get("refs_read"):
        missing = [r for r in exp["refs_read"] if r not in summary["refs_read"]]
        check("refs_read", not missing, f"read={summary['refs_read']}")
    if exp.get("refs_not_read"):
        extra = [r for r in exp["refs_not_read"] if r in summary["refs_read"]]
        check("refs_not_read", not extra, f"read={summary['refs_read']}")
    if exp.get("tools_any"):
        check("tools_any", any(t in calls for t in exp["tools_any"]), ", ".join(calls))
    if exp.get("tools_none"):
        bad = [t for t in exp["tools_none"] if t in calls]
        check("tools_none", not bad, ", ".join(bad))
    if exp.get("capability"):
        hits = search_hits(trace["calls"])
        if hits:
            top3 = any(exp["capability"] in names[:3] for names in hits)
            check("capability", top3, f"searches={[names[:3] for names in hits]}")
        else:
            check("capability", None, "no capability_search call")
    if exp.get("run_tool"):
        ran = [
            evident_name(c["name"])
            for c in trace["calls"]
            if evident_name(c["name"]) in RUN_TOOLS and c["input"].get("name") == exp.get("capability")
        ]
        check("run_tool", exp["run_tool"] in ran, f"ran={ran}")
    if exp.get("no_local_read"):
        reads = local_reads(trace["calls"], exp["no_local_read"])
        check("no_local_read", not reads, ", ".join(sorted(set(reads))))
    for phrase in exp.get("text_has", []):
        check("text_has", phrase.lower() in trace["final_text"].lower(), phrase)
    return checks


def judge(case: dict, criteria: str, trace: dict, judge_model: str) -> dict:
    tools = "\n".join(
        f"- {c['name']} {json.dumps(c['input'])[:300]}" for c in trace["calls"] if c["name"] != "Read"
    ) or "(none)"
    prompt = (
        "You grade one run of an AI assistant that has the Evident plugin (a trust and security questionnaire "
        "product). Decide PASS or FAIL using only the criteria.\n\n"
        f"CRITERIA:\n{criteria}\n\nUSER ROLE: {case['role']}\n\nUSER MESSAGE:\n{case['prompt']}\n\n"
        f"TOOL CALLS:\n{tools}\n\nFINAL REPLY:\n{trace['final_text'][:6000]}\n\n"
        'Answer with one line of JSON and nothing else: {"pass": true|false, "reason": "<one sentence>"}'
    )
    cmd = ["claude", "-p", prompt, "--model", judge_model, "--tools", "", "--setting-sources", "project",
           "--strict-mcp-config", "--no-session-persistence", "--output-format", "json"]  # fmt: skip
    try:
        out = subprocess.run(cmd, env=CHILD_ENV, capture_output=True, text=True, timeout=180).stdout
        text = json.loads(out).get("result", "")
        verdict = json.loads(re.search(r"\{.*\}", text, re.S).group(0))
        return {"check": "judge", "pass": bool(verdict.get("pass")), "detail": str(verdict.get("reason", ""))[:300]}
    except Exception as exc:  # a broken judge call is unknown, never a pass or a fail
        return {"check": "judge", "pass": None, "detail": f"judge unavailable: {type(exc).__name__}"}


def run_one(job, tokens: Tokens | None, judge_model: str | None) -> dict:
    case, model, index = job
    mcp_url = tokens.mcp_url if tokens else None
    mcp = bool(mcp_url and tokens.has(case["role"]))
    try:
        token = tokens.get(case["role"]) if mcp else None
        trace = run_claude(case, model, mcp_url, token)
    except Exception as exc:  # one broken run is recorded, never allowed to stop the batch
        trace = {"calls": [], "final_text": "", "cost_usd": None, "turns": None, "mcp_status": None, "api_key_source": None,
                 "duration_s": 0, "error": f"runner: {type(exc).__name__}: {exc}"}  # fmt: skip
    summary = summarize(trace)
    crashed = str(trace["error"] or "").startswith("runner:")
    checks = [] if crashed else score(case, model, trace, summary, mcp)
    criteria = expectations(case, model).get("judge")
    if criteria and judge_model and not trace["error"]:
        if mcp:
            checks.append(judge(case, criteria, trace, judge_model))
        else:
            checks.append({"check": "judge", "pass": None, "detail": "skipped: no MCP server for this run"})
    decided = [c["pass"] for c in checks if c["pass"] is not None]
    if False in decided:
        status = "fail"  # a violation before a timeout or CLI error still counts
    elif trace["error"]:
        status = "error"
    else:
        status = "pass" if decided else "unknown"
    return {
        "id": case["id"], "category": case["category"], "role": case["role"], "model": model, "run": index,
        "prompt": case["prompt"], "mcp": mcp, "mcp_status": trace["mcp_status"],
        "api_key_source": trace["api_key_source"], "status": status,
        **summary, "checks": checks,
        "tool_calls": [{"name": c["name"], "input": c["input"], "result": c["result"][:2000]} for c in trace["calls"]],
        "final_text": trace["final_text"], "cost_usd": trace["cost_usd"], "turns": trace["turns"],
        "duration_s": trace["duration_s"], "error": trace["error"],
    }  # fmt: skip


# --- Report ----------------------------------------------------------------------------------------------------


def pct(passed: int, total: int) -> str:
    return f"{100 * passed / total:.0f}% ({passed}/{total})" if total else "–"


def write_report(rows: list[dict], out: Path, meta: dict) -> None:
    suggestions = EVALS / "suggestions.md"
    meta = {**meta, "suggestions": suggestions.read_text() if suggestions.exists() else None}
    models = [m for m in MODELS if any(r["model"] == m for r in rows)]
    categories = sorted({r["category"] for r in rows}, key=lambda c: list(CATEGORY_ORDER).index(c) if c in CATEGORY_ORDER else 99)
    decided = [r for r in rows if r["status"] in ("pass", "fail")]
    lines = [
        "# Evident plugin eval report", "",
        f"Run `{meta['run_id']}` · plugin `{meta['plugin_commit']}` · {len(rows)} runs · "
        f"MCP: {'yes' if meta['mcp'] else 'no'} · cost ${sum(r['cost_usd'] or 0 for r in rows):.2f}", "",
        "Claude login per run (`apiKeySource` from the CLI; `none` means the subscription login): "
        + ", ".join(f"{k} {v}" for k, v in sorted(Counter(str(r.get("api_key_source")) for r in rows).items())) + ".", "",
        "Pass rate counts runs where every decided check passed. Errors (timeouts, CLI failures) and runs with only "
        "skipped checks are listed separately, not counted as failures.", "",
        "## Pass rate by category and model", "",
        "| Category | " + " | ".join(models) + " | All |", "| -- | " + " | ".join("--" for _ in models) + " | -- |",
    ]  # fmt: skip
    for cat in categories:
        cells = []
        for m in models + [None]:
            sel = [r for r in decided if r["category"] == cat and (m is None or r["model"] == m)]
            cells.append(pct(sum(r["status"] == "pass" for r in sel), len(sel)))
        lines.append(f"| {cat} | " + " | ".join(cells) + " |")
    totals = [pct(sum(r["status"] == "pass" for r in decided if m is None or r["model"] == m),
                  sum(1 for r in decided if m is None or r["model"] == m)) for m in models + [None]]  # fmt: skip
    lines += [f"| **all** | " + " | ".join(totals) + " |", ""]
    other = [r for r in rows if r["status"] in ("error", "unknown")]
    if other:
        lines += [f"Not scored: {sum(r['status'] == 'error' for r in other)} errors, "
                  f"{sum(r['status'] == 'unknown' for r in other)} with no decided check.", ""]  # fmt: skip

    lines += ["## Skill firing and routing", "", "| Model | Fired on should-trigger | Fired on near-miss | Right reference only |",
              "| -- | -- | -- | -- |"]  # fmt: skip
    for m in models:
        trig = [r for r in rows if r["model"] == m and r["category"] == "should_trigger" and not r["error"]]
        near = [r for r in rows if r["model"] == m and r["category"] == "near_miss" and not r["error"]]
        route = [r for r in decided if r["model"] == m and r["category"] == "routing"]
        lines.append(f"| {m} | {pct(sum(r['skill_fired'] for r in trig), len(trig))} | "
                     f"{pct(sum(r['skill_fired'] for r in near), len(near))} | "
                     f"{pct(sum(r['status'] == 'pass' for r in route), len(route))} |")  # fmt: skip

    by_case: dict[str, list[dict]] = defaultdict(list)
    for r in decided:
        by_case[r["id"]].append(r)
    worst = sorted(
        ((cid, rs) for cid, rs in by_case.items() if any(r["status"] == "fail" for r in rs)),
        key=lambda item: (-sum(r["status"] == "fail" for r in item[1]) / len(item[1]), -len(item[1]), item[0]),
    )[:20]
    lines += ["", "## The 20 worst failures", ""]
    if not worst:
        lines.append("No failures.")
    for cid, rs in worst:
        failed = [r for r in rs if r["status"] == "fail"]
        sample = failed[0]
        bad = [f"{c['check']}: {c['detail']}" for c in sample["checks"] if c["pass"] is False]
        lines += [
            f"### {cid} ({sample['category']}, role {sample['role']}): failed {len(failed)}/{len(rs)} runs "
            f"({', '.join(sorted({r['model'] for r in failed}))})", "",
            f"> {sample['prompt']}", "",
            f"- Failed checks ({sample['model']} run {sample['run']}): " + "; ".join(bad),
            f"- Skill fired: {sample['skill_fired']} · references read: {sample['refs_read'] or 'none'}",
            f"- Tool calls: {', '.join(c['name'].removeprefix(MCP_PREFIX) for c in sample['tool_calls']) or 'none'}", "",
            "```text", (sample["final_text"] or "(no final text)")[:EXCERPT_CHARS].strip(), "```", "",
        ]  # fmt: skip

    lines += ["## Capability search misses", "",
              "Phrasings where `capability_search` did not return the expected capability in its top 3 "
              "(input for TRU-9162).", "", "| Phrasing | Expected | Models missed | What came back (top 3) |",
              "| -- | -- | -- | -- |"]  # fmt: skip
    misses = 0
    for cid, rs in sorted(by_case.items()):
        cap_fails = [r for r in rs for c in r["checks"] if c["check"] == "capability" and c["pass"] is False]
        if cap_fails:
            misses += 1
            expected = cid.removeprefix("cap-").rsplit("-", 1)[0]
            got = next((c["detail"] for c in cap_fails[0]["checks"] if c["check"] == "capability"), "")
            lines.append(f"| {rs[0]['prompt']} | `{expected}` | {', '.join(sorted({r['model'] for r in cap_fails}))} "
                         f"| {got.removeprefix('searches=')} |")  # fmt: skip
    if not misses:
        lines.append("| (none) | | | |")
    lines += ["", "## Suggested changes", "", meta.get("suggestions") or "_Written by hand after reading the failures above._", ""]
    out.write_text("\n".join(lines))


CATEGORY_ORDER = ("should_trigger", "near_miss", "routing", "capability_search", "must_never", "role", "model")


# --- CLI -------------------------------------------------------------------------------------------------------


def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1] == "report":
        run_dir = Path(sys.argv[2])
        rows = [json.loads(l) for l in (run_dir / "runs.jsonl").read_text().splitlines() if l.strip()]
        meta = json.loads((run_dir / "meta.json").read_text())
        write_report(rows, Path(sys.argv[3]) if len(sys.argv) > 3 else EVALS / "report.md", meta)
        return

    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--cases", type=Path, default=EVALS / "cases.jsonl")
    ap.add_argument("--models", default=",".join(MODELS))
    ap.add_argument("--category", action="append", help="only these categories (repeatable)")
    ap.add_argument("--id", action="append", help="only case ids matching this glob (repeatable)")
    ap.add_argument("--repeats", type=int, default=3, help="runs per model for trigger, near-miss and routing cases")
    ap.add_argument("--concurrency", type=int, default=4)
    ap.add_argument("--judge-model", default="haiku")
    ap.add_argument("--no-judge", action="store_true")
    ap.add_argument("--no-mcp", action="store_true", help="run without the Evident server (trigger and routing only)")
    ap.add_argument("--out", type=Path, help="results directory (default evals/results/<timestamp>)")
    ap.add_argument("--tokens", type=Path, default=TOKEN_FILE, help="token file (default evals/.tokens.json)")
    ap.add_argument("--report", type=Path, default=EVALS / "report.md")
    args = ap.parse_args()

    tokens = None if args.no_mcp else Tokens(args.tokens)
    mcp_url = tokens.mcp_url if tokens else None
    if not args.no_mcp and not mcp_url:
        raise SystemExit(f"No MCP URL: create {args.tokens} or set EVIDENT_MCP_URL, or pass --no-mcp (see evals/README.md).")
    cases = load_cases(args.cases)
    if args.category:
        cases = [c for c in cases if c["category"] in args.category]
    if args.id:
        cases = [c for c in cases if any(fnmatch.fnmatch(c["id"], g) for g in args.id)]
    if mcp_url:
        skipped = sorted({c["role"] for c in cases if not tokens.has(c["role"])})
        if skipped:
            print(f"No token for role(s) {skipped}; their cases run without the Evident server.", file=sys.stderr)
    jobs = plan_runs(cases, [m.strip() for m in args.models.split(",") if m.strip()], args.repeats)

    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = args.out or EVALS / "results" / run_id
    out.mkdir(parents=True, exist_ok=True)
    commit = subprocess.run(["git", "-C", str(PLUGIN_ROOT), "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()
    meta = {"run_id": run_id, "plugin_commit": commit or "unknown", "mcp": bool(mcp_url), "jobs": len(jobs)}
    (out / "meta.json").write_text(json.dumps(meta, indent=2))
    print(f"{len(jobs)} runs from {len(cases)} cases -> {out}", file=sys.stderr)

    lock, rows = threading.Lock(), []
    judge_model = None if args.no_judge else args.judge_model
    with futures.ThreadPoolExecutor(max_workers=args.concurrency) as pool, open(out / "runs.jsonl", "w") as sink:
        pending = [pool.submit(run_one, job, tokens, judge_model) for job in jobs]
        for n, fut in enumerate(futures.as_completed(pending), 1):
            row = fut.result()
            with lock:
                rows.append(row)
                sink.write(json.dumps(row) + "\n")
                sink.flush()
            print(f"[{n}/{len(jobs)}] {row['status']:7} {row['model']:6} {row['id']}", file=sys.stderr)
    write_report(rows, args.report, meta)
    print(f"Report: {args.report}", file=sys.stderr)


if __name__ == "__main__":
    main()
