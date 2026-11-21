---
description: Get started with Evident in Claude
---

Run the Evident first run. Load the `evident` skill first. Keep it short and use the user's real data; never a canned demo. Ask, wait, continue: never send all of it as one wall of text.

1. **Check the connection.** First call `capability_run_write` with name `onboarding_record` and `{"milestone": "plugin_seen", "plugin_version": "0.2.6"}`; if that one call fails, carry on. Then call `authorization_whoami`, and ignore any `plugin_suggestion` in it. If it fails, tell the user to connect Evident from the plugin's Connectors tab (in Claude Code, run `/mcp` and sign in to `plugin:evident:evident`), and stop. Its `role` is `admin`, `knowledge_editor` or `member`; treat any custom or unknown role as member.
2. **Read their workspace in one parallel round:**
   - `questionnaire_triage_open_work`: open work, what is assigned to them, and review requests.
   - `questionnaire_list`.
   - `onboarding_get_state`: the setup plan steps with `completed`, the org's counts (including `kb_stats.total_docs`) and `tooltips_shown`. It is not in your tool list: call `capability_run_read` with name `onboarding_get_state` and `{}`.
   - Editors and admins only: the knowledge base size, from `kb_stats` when `onboarding_get_state` gave it, otherwise `knowledge_base_browse` with `view="flat"`; and the open conflict count, from `conflict_list` with `status="open"` (its `total`). `conflict_list` is not in your tool list: call `capability_run_read` with name `conflict_list` and `{"status": "open"}` in the same round.

   Then show their workspace with `ui_show` (load it with tool search if it is deferred): `[{"part": "questionnaires", "view": "waiting_on_you"}]` when something is assigned to them or waits for their review, otherwise `[{"part": "questionnaires"}]`. This is the first thing they see. If `questionnaire_triage_open_work` replied "Shown to the user in the Evident widget", it is already on screen: do not show it again. Without `ui_show`, say in a line or two what is open and what waits on them.
3. **State the model rules once, briefly, only if your current model limits anything** (the table in the skill's `SKILL.md`). On Haiku: lookups only, and the Haiku message. On Sonnet: everything except filling a portal in their visible browser, which needs Opus. On Opus, say nothing about models. Never offer Evident's browser. When they ask to fill a portal, follow `references/portal.md`; if controls are missing, the first portal reply gives setup and a concrete resume step before a run exists.
4. **One line under the widget for their role**, using their numbers. Do not repeat what the widget shows. Without the widget, two or three lines:
   - Admins: answer questionnaires and portals from here, keep the knowledge base current, and set Evident up for the team.
   - Knowledge Editors: answer questionnaires and portals, load documents, settle conflicts, approve answers.
   - Members: ask about the company's security and product and get answers with sources, work questionnaires and portals, and answer what is assigned to them.
5. **Recommend the first step that matches**, in this order. When they accept, open the widget it names (step 8), not in this first reply:
   1. Editor or admin with an empty knowledge base: load knowledge (`references/knowledge.md`). Opens `[{"part": "manager", "tab": "documents"}]`.
   2. Editor or admin with open conflicts: resolve them, one at a time. On a questionnaire, opens `[{"part": "decision", "questionnaireId": "<id>", "kind": "conflict"}]`; otherwise `references/knowledge.md`.
   3. Anyone with assigned questions or review requests: work through them. Opens `question_review` on the questionnaire that holds them.
   4. Editor or admin with questionnaires waiting for approval: review and approve (`references/review.md`). Opens `question_review` on that questionnaire.
   5. Member with an empty knowledge base: say answers will be thin until their team adds documents, and add: "A Knowledge Editor can add this. Ask your admin for the Knowledge Editor role if you need to add documents yourself." Then go to 6.
   6. Otherwise ask: "Do you have a questionnaire or portal to work on, or a question you need answered?"
   Never recommend a setup step that `onboarding_get_state` marks `completed`. If `setup_plan.dismissed` is true, do not offer the setup walkthrough unless they ask. For admins, the setup walkthrough is `references/setup.md`, from the first step that is not completed.
   Record which one you recommended: `{"milestone": "start_recommended", "recommendation": "<id>"}`, with `load_knowledge` for 1, `resolve_conflicts` for 2, `assigned_work` for 3, `review_approve` for 4, and `ask` for 5 and 6.
6. **Show the other steps that apply on one "Also available:" line.** Offer the tour once, only if a browser tool is available, `claude:tour` is not in `tooltips_shown` and `suggestions_quiet` is false: "I can also show you around the Evident app on screen. Want a quick look?" Follow `references/tour.md`, and end the tour by pointing out that all of it can be done from here.
7. **End with these two prompts they can copy**, for their role, under "Or try one of these:", each on its own line:
   - Members: "Do we encrypt customer data at rest?" and "What's assigned to me?"
   - Knowledge Editors: "Show open conflicts" and "Add our SOC 2 report"
   - Admins: "Who needs to approve answers?" and "Set up approvals"
8. **When they reply, carry straight on into the step they accept**, reading its reference file first and opening the widget step 5 names for it.

This command is the only place you suggest anything on arrival. Its offers follow the recording rules in `references/moments.md`, all through `onboarding_record` (not in your tool list: `capability_run_write` with name `onboarding_record`):

- After you offer the tour: `{"milestone": "tooltip_shown", "tooltip_id": "claude:tour"}`. When they answer: `suggestion_accepted` or `suggestion_declined` with the same `tooltip_id`.
- When the user finishes a setup step with you: `{"milestone": "step_completed", "step_id": "<id from steps>"}`.
- Do not record anything for other offers, such as working through open questions.

Skip these calls if the tools are not available.
