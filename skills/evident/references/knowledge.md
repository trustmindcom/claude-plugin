# Knowledge: documents, integrations, conflicts, gaps, saved answers

For Knowledge Editors and admins. Members never get these steps: when something is missing, give them the Knowledge Editor line in `SKILL.md`.

1. **Check your model first.** Uploading a document or saving an answer needs the middle tier (currently Sonnet) or above, and so does helping the user decide a conflict. On the smallest tier (Haiku), stop with the Haiku message in `SKILL.md`. Browsing and searching the knowledge base work on any model.

## Documents

Add only new knowledge: policies, reports, documents and answers a person wrote. A filled-in questionnaire Evident answered, or a finished or exported copy of one, is not new knowledge. Most of its answers are Evident's own, and filed as knowledge they would come back as a person's. When the user hands one back, follow "Changing answers after the file is made" in `references/questionnaire.md`. It goes through the same upload, but it updates that questionnaire, and you report it as that questionnaire's update, never as new knowledge.

1. Call `knowledge_document_upload_url_create` for the file, PUT the bytes to the returned URL, sending `upload_headers`, then call `knowledge_document_create`.
2. Report what was added, in a line or two. Then check for new conflicts (`knowledge_conflict_list` (or `conflict_list`), below) and offer to settle them.
3. `knowledge_document_list` shows what is there, by source and folder, or newest first with `view="flat"`. `knowledge_document_delete` removes a source, folder or document: say exactly what will go and get a yes first.

## Integrations

Supported sources: Google Drive (a Shared Drive or picked files), Confluence, Notion, GitHub, Drata, a website (sitemap.xml or llms.txt), and uploads (PDF, Word, spreadsheets, Markdown, HTML). Connecting one means a sign-in in the app: give the link `https://app.evident.security/dashboard/organization/integrations/`, or show it on screen (`references/tour.md`).

## Conflicts

Conflicts on a questionnaire's answers: open them with `ui_show` `[{"part": "decision", "questionnaireId": "<id>", "kind": "conflict"}]`. It shows one conflict at a time and the user picks the side there, so you never pick one. For conflicts in the knowledge base that are not on a questionnaire, or without `ui_show`:

1. List open ones: `knowledge_conflict_list` (or `conflict_list`) with `status="open"`; `total` is how many. Get one with its options: `knowledge_conflict_get` (or `conflict_get`) with `include=['resolution_options']`. Neither is in your tool list: call `capability_search`, then `capability_run_read`.
2. Show one conflict at a time: both sides, where each came from, and the options.
3. Apply only the user's explicit choice:
   - One of Evident's options from `knowledge_conflict_get` (or `conflict_get`): `knowledge_conflict_resolve` with `strategy='apply'`, its `option_id` and the conflict's `expected_version` (or `conflict_apply_resolution` with the same fields and no `strategy`).
   - Keep the new content: `knowledge_conflict_resolve` (or `conflict_resolve`) with `strategy='keep_new'`.
   - Keep what was there: `knowledge_conflict_resolve` (or `conflict_resolve`) with `strategy='keep_existing'`.
   - Not a real conflict: `knowledge_conflict_resolve` (or `conflict_resolve`) with `strategy='dismiss'`.
   - Leave it for later: call nothing.
   - The user's own guidance ("these apply to different products"): `knowledge_conflict_resolution_preview` (or `conflict_preview_resolution`) with their `hint`, show the proposed revisions, and apply them only after they say so: `knowledge_conflict_resolve` with `strategy='apply'` and the preview's `hint`, `revisions`, `resolution_id` and `expected_version` (or `conflict_apply_resolution` with the same fields and no `strategy`).
4. Then go to the next one.

Never resolve conflicts in bulk, and never pick a side for the user, even when they ask you to choose. A wrong resolution quietly changes every future answer.

## Gaps and saved answers

- A gap is something the company confirms it does not do. How a "no" is worded is the Answer style setting (`references/setup.md`, admins).
- When the user gives an answer worth reusing, say what you will save and wait for a yes, then save it with `knowledge_answer_create`, in the user's words.
- Answers people write or edit are saved for reuse; AI drafts are not. With "Approve before saving for reuse" on, nothing is saved until approved.
