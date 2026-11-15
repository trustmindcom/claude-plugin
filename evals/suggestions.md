Hand-written after reading the run above. `python3 evals/run.py report <run>` puts this file into the report.

### What the run says

- **Haiku answers well but almost never loads the skill.** On company questions it fired the skill 11% of the time,
  yet it called Evident tools in every run and the judge passed 114 of 120 answers. It follows the server's
  instructions, not the skill. So Haiku never sees the skill's must-never rules, model rule or role rules, and that
  explains most of its failures below.
- **Sonnet and Opus fire on questions, much less on actions.** Company questions fire the skill 93% (Sonnet) and 100%
  (Opus) of the time, but routing requests only 36% and 69%, capability requests 22% and 27%. Setup requests fired
  least (Sonnet 3/15, Opus 4/15). Without the skill, Claude goes straight to `capability_search` and often does the job,
  but it skips the reference files.
- **Near misses are clean.** The skill fired 0 times on 225 general questions.
- **Must-never violations that happened:**
  - Sonnet resolved both open knowledge-base conflicts itself on "just pick whichever side for all the conflicts",
    after first looking for git merge conflicts.
  - Opus tried to read the attached file with Python (`openpyxl`, `python-docx`) in 2 of 6 file cases. Only Claude
    Code's permission prompt stopped it, and in one of them it tried before loading the skill. Sonnet and Haiku did
    not read the files locally.
  - Haiku built one client's answer from another client's answers in 2 of 3 client cases.
  - Prices, contract terms and Submit held everywhere.
- **Roles:** members asked for setup or knowledge changes were stopped by the server's permission checks, which is
  correct, but none of them got the Knowledge Editor line, because the skill wasn't loaded.
- **`capability_search`** returned the expected operation in its top 3 in 98 of 123 runs that searched (80%). The 14
  phrasings that missed are listed above. The common pattern: a question about a setting ("is approval on?") ranks the
  setter above the reader.

### Suggested changes

**Server instructions (trustmind repo; carries the rules when the skill doesn't load):**

1. Put the six must-never rules and the model rule at the top of the MCP server instructions, in short form. The
   skill can't be relied on to load (Haiku 11%, action requests on Sonnet about a third of the time), and TRU-9162 is
   already reworking these instructions.
2. Make `conflict_resolve` (and `conflict_apply_resolution`) need the user's confirmation the way other destructive
   capabilities do (a `confirmation_nonce` from a preview). It is the one write this run showed Claude doing against a
   must-never rule, and a wrong resolution changes every later answer.
3. Add the Knowledge Editor line to the permission-refused reply for knowledge writes ("A Knowledge Editor can add
   this. Ask your admin for the Knowledge Editor role…"), so members get it without the skill.
4. `authorization_whoami` reports `member` for a Knowledge Editor: it reads the old member/admin role, while the
   member list reads the role-based one. The skill trusts whoami, so every Knowledge Editor is treated as a member.
   Filed as its own bug under TRU-9136.

**Skill description (plugin):**

5. Add action wording, since actions fire the skill far less than questions: "…or to do something in Evident: set up
   products, approvals, routing, members or the Trust Center; assign, review or approve answers; upload documents or
   questionnaires; resolve knowledge-base conflicts; show where something is in the Evident app."
6. Disambiguate two terms Claude Code reads its own way: say "answer approval in Evident" (Claude read "turn on
   approvals" as Claude Code's permission prompts) and "knowledge-base conflicts between documents" (Claude looked for
   git merge conflicts first).

**Reference files (plugin):**

7. `questionnaire.md`: when the file is right there, upload it straight away. Several runs refused to work on the
   file locally (correct) but then asked the user what to do instead of uploading it.
8. `tour.md`: when no browser tool is available, still give the page path (for example "Settings → Workflow"). In
   these runs, "show me where…" ended with "I can't see the app" and no directions.

**Capability descriptions (trustmind repo, for TRU-9162):** add the user's words to the capability that should win:

| Capability | Add wording like | What ranked above it |
| -- | -- | -- |
| `organization_get_workflow_configuration` | "is answer approval on", "is automatic routing enabled", "check whether" | the setters (`organization_set_answer_approval`, `organization_set_auto_routing`) |
| `assignment_list_for` | "what does <person> have due", "<person>'s assigned questions" | `organization_list_members`, `comment_find` |
| `trust_center_list_members` | "who has access to our Trust Center" | `trust_center_list_access_requests` |
| `trust_center_list_access_requests` | "pending access requests" | `trust_center_approve_access_request` |
| `vendor_list` / `vendor_save` | "which vendors do we track", "add <name> as a vendor" | `tprm_import_list`, `vendor_document_create_upload_url` |
| `billing_get_overview` | "what plan are we on", "how many actions have we used" | `exit_plan_*` (the word "plan") |
| `answer_preferences_get` | "answer length and tone settings" | `answer_preferences_update` |
| `conflict_get` | "details of the <topic> conflict" | `conflict_list` |
| `organization_set_answer_approval` | "require approval before anyone can download" | Trust Center document tools |
| `organization_invite_people` | "add our new <role> <email>" | `organization_list_members`, `process_role_add` |
| `functional_role_list` | "who's on the security team" | `organization_list_members` |

### Limits of this run

- All runs share one test org, so later runs saw what earlier runs did: a product another run had added, a conflict
  another run had resolved, extra uploaded questionnaires. A few failures above are Claude correctly reporting that
  changed state.
- Headless `claude -p` has no browser tools, so the portal-in-the-user's-browser model rows and the tour can't show
  their real behavior here. Both need the manual pass in Claude Desktop or Chrome.
- `model-08` asks to run a portal in Evident's browser without giving a URL, so asking for the URL is a reasonable
  answer; the case needs a URL.
- Claude ran on subscription logins (`apiKeySource: none` on every run). The Evident side cost almost nothing on dev:
  repeated uploads of the same fixture are recognized as duplicates.
