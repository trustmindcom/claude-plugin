# Evident plugin eval report

Run `20261115T080710Z` · plugin `12e7b4e` · 1180 runs · MCP: yes

Claude usage at API list prices, as the CLI reports it: $100.36. On a subscription login this is a usage measure, not a bill.

Claude login per run (`apiKeySource` from the CLI; `none` means the subscription login): none 1180.

Pass rate counts runs where every decided check passed. Errors (timeouts, CLI failures) and runs with only skipped checks are listed separately, not counted as failures.

## Pass rate by category and model

| Category | haiku | sonnet | opus | All |
| -- | -- | -- | -- | -- |
| should_trigger | 10% (12/120) | 92% (111/120) | 98% (118/120) | 67% (241/360) |
| near_miss | 97% (73/75) | 100% (75/75) | 97% (73/75) | 98% (221/225) |
| routing | 0% (0/105) | 30% (31/105) | 60% (63/105) | 30% (94/315) |
| capability_search | 32% (19/60) | 37% (22/60) | 50% (30/60) | 39% (71/180) |
| must_never | 80% (16/20) | 90% (18/20) | 80% (16/20) | 83% (50/60) |
| role | 10% (1/10) | 10% (1/10) | 50% (5/10) | 23% (7/30) |
| model | 20% (1/5) | 33% (1/3) | 50% (1/2) | 30% (3/10) |
| **all** | 31% (122/395) | 66% (259/393) | 78% (306/392) | 58% (687/1180) |

## How often the skill fired

Every category, including those whose checks don't require it. It should fire on everything except near misses.

| Category | haiku | sonnet | opus |
| -- | -- | -- | -- |
| should_trigger | 11% (13/120) | 93% (112/120) | 100% (120/120) |
| near_miss | 0% (0/75) | 0% (0/75) | 0% (0/75) |
| routing | 7% (7/105) | 36% (38/105) | 69% (72/105) |
| capability_search | 2% (1/60) | 22% (13/60) | 27% (16/60) |
| must_never | 0% (0/20) | 15% (3/20) | 60% (12/20) |
| role | 0% (0/10) | 10% (1/10) | 50% (5/10) |
| model | 20% (1/5) | 0% (0/3) | 0% (0/2) |

## The 20 worst failures

### route-knowledge-3 (routing, role admin): failed 9/9 runs (haiku, opus, sonnet)

> Connect our Google Drive security folder so it learns from our policies

- Failed checks (haiku run 1): skill: fired=False; judge: The run started the work by making five tool calls to search for and browse Drive connection capabilities, and the final reply never says this model is for quick lookups or tells the user to switch to Sonnet or Opus.
- Skill fired: False · references read: none
- Tool calls: capability_search, ToolSearch, knowledge_base_browse, capability_search, capability_search

```text
I couldn't connect the Google Drive folder from here. Evident's tools have no way to add or authorize a Drive source, and the Knowledge Base currently has only an "Uploaded files" section, with no Google Drive source.

To connect it, open the Knowledge Base page in Evident, choose Google Drive, sign in with the account that can see the security folder, and select that folder. Once it appears, I can:

- Check which documents Evident sees as policies with requirements (`obligation_source_scan`), then confirm or dismiss each one.
- Search the folder's content to ground security answers (`knowledge_search`).
- Browse the folder and its documents to confirm the sync worked.

If you'd rather not c
```

### route-portal-4 (routing, role admin): failed 9/9 runs (haiku, opus, sonnet)

> The customer sent a ServiceNow VRM questionnaire link, can you do it in my browser?

- Failed checks (haiku run 2): skill: fired=False; judge: The reply does not start the work, but it never says this model is for quick questions and lookups or tells the user to switch to Sonnet or Opus, and the criteria require both.
- Skill fired: False · references read: none
- Tool calls: none

```text
I can fill this, but I need two things from you first:

1. **The portal link.** Paste the ServiceNow VRM questionnaire URL. If it's an emailed link that needs a login, the page itself must be reachable from the browser I'll use.

2. **Which browser fills it.** There are two options:
   - **Your own browser**, if it's connected to this session. I don't see a browser-driving tool among my tools right now, so this may not be available. If you have Claude Desktop's built-in browser or Claude in Chrome connected, tell me and I'll check.
   - **Evident's browser.** I can run this now. It needs a sign-in handover to the ServiceNow instance, and I'll walk you through that.

I won't press Submit. You
```

### route-review-5 (routing, role admin): failed 9/9 runs (haiku, opus, sonnet)

> Which questions still need review before we can download the Contoso file?

- Failed checks (haiku run 1): skill: fired=False; refs_read: read=[]
- Skill fired: False · references read: none
- Tool calls: ToolSearch, questionnaire_list, questionnaire_triage_open_work, questionnaire_list

```text
I couldn't find a Contoso file in your Evident workspace. Searching for "Contoso" returns no questionnaires, whether or not I filter to ones needing attention. The file may be under a different name, or it may not have been uploaded yet.

The only active questionnaire is **vendor-security-questionnaire.xlsx** (customer: Acme Corp, status: incomplete answers). It has 8 questions, 7 answered, and **1 open question**, with no blockers, conflicts, or flagged items. If that's the file you meant, the one open question is what stands between it and download.

Tell me the Contoso file's name, or whether it's the Acme one, and I'll check its open questions. I can also pull the open question's text fo
```

### route-setup-1 (routing, role admin): failed 9/9 runs (haiku, opus, sonnet)

> Add our new product Atlas Analytics so questionnaires can be scoped to it

- Failed checks (haiku run 1): skill: fired=False; judge: The assistant started the work by running a product_save write for Atlas Analytics instead of saying the model is for quick questions and lookups and telling the user to switch to Sonnet or Opus.
- Skill fired: False · references read: none
- Tool calls: ToolSearch, capability_search, capability_run_read, capability_run_write

```text
I added Atlas Analytics to your product catalog, so questionnaires can now be scoped to it.

- **Name:** Atlas Analytics
- **Slug:** `atlas-analytics`
- **ID:** `<id>`

Your organization had no products before, so this is the only one. Questionnaire scoping only becomes required once there are two or more active products, so nothing changes for existing questionnaires.

I didn't add a description. If you tell me what Atlas Analytics does, I can save one; it improves how Evident suggests knowledge scoping.
```

### route-setup-3 (routing, role admin): failed 9/9 runs (haiku, opus, sonnet)

> Connect to our Slack so people get notified about assignments

- Failed checks (haiku run 2): skill: fired=False; judge: The run started the work with ToolSearch, capability searches, and read calls, and the final reply never says this model is for quick questions and lookups or tells the user to switch to Sonnet or Opus.
- Skill fired: False · references read: none
- Tool calls: ToolSearch, capability_search, capability_run_read, authorization_whoami, capability_search, capability_search, capability_run_read

```text
I couldn't connect Slack from here. The Evident workspace has no Slack integration yet, and I have no tool that starts the Slack install.

- **Current state:** Asking for the Slack channel list returned "Slack integration not found," so nothing is connected.
- **What's needed:** A workspace admin has to install the Slack app and approve it in a browser. I can't complete that OAuth step. I'm signed in as an admin (Plugin Eval Admin), so you can do it from this account.
- **Where it goes:** Assignment alerts are the "Needs you" alert (questions assigned to you). It's email-only today. Once Slack is connected, you can turn on the Slack DM switch for it.
- **Channel alerts:** An admin can route
```

### route-setup-5 (routing, role admin): failed 9/9 runs (haiku, opus, sonnet)

> Change our answer style to be shorter and less formal

- Failed checks (haiku run 1): skill: fired=False; judge: The reply starts the work by confirming the style change and attempting a Write to save a memory, rather than saying this model is for quick questions and lookups and directing the user to switch to Sonnet or Opus.
- Skill fired: False · references read: none
- Tool calls: Write, Read

```text
Got it, shorter and less formal from here on.

I tried to save this as a memory so it sticks across sessions, but the write was blocked by a permission prompt. If you want it saved, approve the write and I'll add it. Otherwise it only applies to this session.
```

### route-tour-1 (routing, role admin): failed 9/9 runs (haiku, opus, sonnet)

> Show me where the approvals settings are in the app

- Failed checks (haiku run 1): skill: fired=False; refs_read: read=[]
- Skill fired: False · references read: none
- Tool calls: Grep, Glob, Bash, Bash

```text
I couldn't find the app. The working directory `<work dir>` is empty, and searching it for "approval" or "settings" returned nothing. The parent folder is also not a git repo.

Which app do you mean? Some options:

- **A different path:** if the app lives somewhere else, give me the path and I'll search it for the approvals settings.
- **Evident:** if you mean your Evident workspace, I can search its capabilities for approval-related settings. I can't see its UI from here, though, so I'd be pointing at the operations and not at screen locations.
```

### route-tour-2 (routing, role admin): failed 9/9 runs (haiku, opus, sonnet)

> Can you give me a quick tour of the app?

- Failed checks (haiku run 1): skill: fired=False; refs_read: read=[]
- Skill fired: False · references read: none
- Tool calls: Bash, Bash, Bash, Bash

```text
I couldn't find an app to tour. The primary working directory, `<work dir>`, is empty. It has no files and no hidden files, and it isn't a git repository. The parent directory is outside the session's allowed paths, so I couldn't look there.

Could you tell me where the app lives? Either of these would work:
- A path inside the allowed `work` directory, if the code was meant to be copied there.
- A different directory I'm allowed to read, or a git URL I can clone.

If you meant the Evident workspace (the questionnaire, knowledge base and Trust Center app this session connects to), I can give that tour through the Evident tools instead. Tell me
```

### route-tour-4 (routing, role admin): failed 9/9 runs (haiku, opus, sonnet)

> Point me to the conflicts page on screen

- Failed checks (haiku run 2): skill: fired=False; refs_read: read=[]
- Skill fired: False · references read: none
- Tool calls: none

```text
I can't see your screen, so I can't point to the page directly.

Two things I can see from here:

- The working directory (`<work dir>`) is not a git repository, so it has no merge-conflict page.
- Evident has conflict tools (`conflict_preview_resolution`, `conflict_resolve`, `conflict_apply_resolution`), so the conflicts page may be in your Evident workspace. I haven't queried those tools yet.

To point you to the right place, tell me which applies:

1. **Evident conflicts**: If the conflicts are answer conflicts in a questionnaire, tell me the questionnaire or question, and I can pull up the conflicting answers and their sources.
2. **A web p
```

### route-tour-5 (routing, role admin): failed 9/9 runs (haiku, opus, sonnet)

> show me what Evident can do

- Failed checks (haiku run 3): refs_read: read=[]
- Skill fired: True · references read: none
- Tool calls: Skill, Skill, ToolSearch

```text
I can't reach Evident from this session, so I can't read your workspace yet. The Evident MCP server failed to connect (HTTP 502 Bad Gateway), and none of its tools are loaded.

To connect:

1. In Claude Code, run `/mcp`.
2. Find `plugin:evident:evident` and sign in. You can also use the Connectors tab if you're in the desktop app.
3. Start a new message or session so the tools load, then ask me again.

If the 502 comes back after you sign in, the Evident endpoint may be down, and it's worth retrying later or checking with whoever runs your Evident instance. I haven't changed anything.
```

### cap-answer_context_search-1 (capability_search, role admin): failed 3/3 runs (haiku, opus, sonnet)

> how did we answer the encryption at rest question on past questionnaires?

- Failed checks (haiku run 1): run_tool: ran=[]
- Skill fired: False · references read: none
- Tool calls: ToolSearch, question_search, knowledge_search, question_search, knowledge_search, question_get_sources, ToolSearch, question_get

```text
We answered it once, for Acme Corp, and that answer hasn't been approved yet.

**Past answer (Acme Corp, `vendor-security-questionnaire.xlsx`, Security sheet, Q1):**

> "Yes, we encrypt customer data at rest using AES-256. Keys are managed through AWS KMS customer master keys that rotate every 365 days, and customer-managed keys (BYOK) are not offered."

- **Status:** answered, but not approved (`is_approved: false`, no approver).
- **Source:** the "Security and Compliance Overview (2026)" document, Encryption section. The same section says data in transit uses TLS 1.2 or higher, which is how we answered the separate in-transit question in that questionnaire.

The search for the exact phrase
```

### cap-answer_context_search-2 (capability_search, role admin): failed 3/3 runs (haiku, opus, sonnet)

> find previous answers we've given about data retention

- Failed checks (sonnet run 1): run_tool: ran=[]
- Skill fired: True · references read: ['answer.md']
- Tool calls: Skill, Read, ToolSearch, knowledge_search, question_search

```text
I found no saved answers about data retention. No past questionnaire question matches "retention" in the statuses I searched (completed, in review, in progress, incomplete, and waiting for input). I didn't search questionnaires in other statuses, such as received or pending.

The knowledge base does have documented statements on the topic:

> Customer data is deleted within 30 days of contract termination. Customer data is never used to train AI models.
> Source: Security and Compliance Overview (2026), "Data retention and AI"

It also has related backup retention:

> Production databases are backed up continuously with point-in-time recovery, and full snapshots are taken daily and kept for
```

### cap-answer_preferences_update-1 (capability_search, role admin): failed 3/3 runs (haiku, opus, sonnet)

> make our answers shorter and less formal

- Failed checks (haiku run 1): run_tool: ran=[]
- Skill fired: False · references read: none
- Tool calls: none

```text
Got it. Shorter, less formal answers from here on.
```

### cap-answer_preferences_update-2 (capability_search, role admin): failed 3/3 runs (haiku, opus, sonnet)

> answers should be more technical from now on

- Failed checks (haiku run 1): run_tool: ran=[]
- Skill fired: False · references read: none
- Tool calls: none

```text
Understood. I'll switch to a more technical register: precise terminology, concrete mechanisms, specific file/line references, and explicit tradeoffs, with less hand-holding prose.

What would you like me to work on in `<work dir>`? Note that it isn't a git repository, so I'll need to rely on direct file inspection for any diffs or history.
```

### cap-assignment_list_for-1 (capability_search, role admin): failed 3/3 runs (haiku, opus, sonnet)

> what does Priya have due this week?

- Failed checks (haiku run 1): run_tool: ran=[]
- Skill fired: False · references read: none
- Tool calls: ToolSearch, question_search, questionnaire_list, question_search

```text
I couldn't find anything for Priya. Evident has no organization member matching "Priya" or "pri", so I can't pull her assigned questionnaire work for this week (Nov 15–22, 2026).

Your workspace may list her under a different display name or email. If you give me her full name or email, I'll check her questions and questionnaires with due dates this week. I can also list everything with due dates this week, or open work for a different teammate.
```

### cap-assignment_list_for-2 (capability_search, role admin): failed 3/3 runs (haiku, opus, sonnet)

> show me Marcus's assigned questions

- Failed checks (haiku run 1): run_tool: ran=[]
- Skill fired: False · references read: none
- Tool calls: ToolSearch, question_search, question_search, questionnaire_triage_open_work, questionnaire_triage_open_work, question_search, question_get

```text
I couldn't find any questions assigned to Marcus. The workspace doesn't have an organization member matching "Marcus" (I tried "Marcus" and "marcus"), so the assignee filter returned nothing.

The workspace does have assigned questions, but the results don't show who each one is assigned to. These are the four assigned questions in the only active questionnaire, `vendor-security-questionnaire.xlsx` (Acme Corp):

| # | Question | Status | Open gap |
|---|---|---|---|
| 1 | Do you encrypt customer data at rest? Describe the algorithm and key management. | Answered | No |
| 2 | Do you encrypt data in transit? Which TLS versions are supported? | Answered | No |
| 3 | Do you maintain a current SO
```

### cap-assignment_list_mine-1 (capability_search, role admin): failed 3/3 runs (haiku, opus, sonnet)

> what's assigned to me?

- Failed checks (haiku run 1): run_tool: ran=[]
- Skill fired: False · references read: none
- Tool calls: ToolSearch, questionnaire_triage_open_work

```text
Nothing is assigned to you in Evident right now.

There is one active questionnaire in the workspace, which isn't assigned to you:

- **vendor-security-questionnaire.xlsx** (customer: Acme Corp, security review)
  - 7 of 8 questions answered, 1 open
  - No blockers, no due date, last updated 2026-11-15 07:55 UTC

I can pull up the open question and its sources if you want to work on it. I can also assign it to you, but that changes the questionnaire, so I'd confirm with you first.
```

### cap-assignment_list_mine-2 (capability_search, role admin): failed 3/3 runs (haiku, opus, sonnet)

> what should I work on next, what's on my plate

- Failed checks (sonnet run 1): run_tool: ran=[]
- Skill fired: False · references read: none
- Tool calls: ToolSearch, questionnaire_triage_open_work

```text
Your plate is light. Evident shows one active questionnaire and nothing assigned to you personally.

**Open work**
- **`vendor-security-questionnaire.xlsx`** is a security review for Acme Corp. It's marked "incomplete answers", with 7 of 8 questions done and 1 still open. It has no flags, conflicts or blockers, and no due date is set. It was uploaded today and last updated a few minutes after that.

**What I'd do next**
1. Finish the one open question on the Acme questionnaire. It's the only thing in the way of a complete response.
2. After that, check the answers Evident drafted before sending the questionnaire back. I can pull up the open question and its sources if you'd like.
3. Set a du
```

### cap-billing_get_overview-1 (capability_search, role admin): failed 3/3 runs (haiku, opus, sonnet)

> what plan are we on and how many actions have we used?

- Failed checks (haiku run 1): run_tool: ran=[]
- Skill fired: False · references read: none
- Tool calls: none

```text
I can't see your plan or account usage from here. Nothing in this session reports the subscription tier or a billing counter.

- **Plan:** Check `/status` in Claude Code, or your account page at claude.ai.
- **Usage:** `/usage` shows your current limits and consumption.

For this conversation, I've made **0 tool calls** so far. The system also reports a context budget of 15,000,000 tokens remaining, but that's a context limit, not your plan's usage.
```

### cap-conflict_get-1 (capability_search, role admin): failed 3/3 runs (haiku, opus, sonnet)

> show me the details of the password length conflict

- Failed checks (sonnet run 1): capability: searches=[['conflict_list', 'knowledge_document_list_versions', 'knowledge_base_browse']]; run_tool: ran=[]
- Skill fired: False · references read: none
- Tool calls: ToolSearch, capability_search, capability_run_read

```text
There is one open conflict about passwords. It covers rotation as well as length. Evident rates it a "supersedes" conflict with 98% confidence.

**Conflict ID:** `<id>`
**Topic:** Are employee passwords rotated every 90 days, or is periodic rotation not required?

| | Existing: Password Policy 2024 | Incoming: Access Control Standard 2026 |
|---|---|---|
| **Minimum length** | 12 characters | 16 characters |
| **Rotation** | Every 90 days | Not required. Passwords change only on suspected compromise. |
| **File** | `password-policy-2024.docx` | `access-control-standard-2026.docx` |

- **Modified dates:** Both files show a last-modified date of Dec 23, 2013. Th
```

## Capability search misses

Phrasings where `capability_search` did not return the expected capability in its top 3 (input for TRU-9162).

| Phrasing | Expected | Models missed | What came back (top 3) |
| -- | -- | -- | -- |
| what are our answer length and tone settings | `answer_preferences_get` | haiku, sonnet | [['organization_set_answer_approval', 'answer_preferences_update', 'organization_get_workflow_configuration']] |
| what does Priya have due this week? | `assignment_list_for` | opus, sonnet | [['organization_list_members', 'organization_deactivate_member', 'organization_get_member_access']] |
| show me Marcus's assigned questions | `assignment_list_for` | opus, sonnet | [['comment_find', 'organization_list_members', 'organization_get_details']] |
| what plan are we on and how many actions have we used? | `billing_get_overview` | opus | [['exit_plan_create', 'exit_plan_list', 'exit_plan_record_review']] |
| show me the details of the password length conflict | `conflict_get` | haiku, sonnet | [['conflict_list', 'knowledge_document_list_versions', 'knowledge_base_browse']] |
| who's on the security team for questionnaires? | `functional_role_list` | sonnet | [['organization_list_members', 'organization_set_member_role', 'organization_get_member_access']] |
| is answer approval turned on for us? | `organization_get_workflow_configuration` | haiku, sonnet | [['organization_set_answer_approval', 'organization_set_answer_approval', 'question_review_answers']] |
| do we have automatic routing enabled? | `organization_get_workflow_configuration` | haiku, sonnet | [['organization_set_auto_routing', 'question_assign', 'trust_center_update_settings']] |
| add our new GRC analyst sam@example.com | `organization_invite_people` | haiku | [['organization_list_members', 'organization_set_member_role', 'process_role_add']] |
| make answers require approval before anyone can download the file | `organization_set_answer_approval` | sonnet | [['trust_center_list_group_documents', 'document_download', 'questionnaire_download_url']] |
| any pending trust center access requests? | `trust_center_list_access_requests` | sonnet | [['trust_center_approve_access_request', 'trust_center_deny_access_request', 'trust_center_restore_access_request']] |
| who currently has access to our Trust Center? | `trust_center_list_members` | haiku, opus, sonnet | [['trust_center_list_access_requests', 'trust_center_restore_access_request', 'trust_center_approve_access_request']] |
| which vendors do we track? | `vendor_list` | haiku, opus, sonnet | [['tprm_import_list', 'risk_list', 'tprm_import_commit']] |
| add Datadog as a vendor | `vendor_save` | haiku, opus | [['vendor_document_create_upload_url', 'risk_create', 'holding_create']] |

## Suggested changes

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

