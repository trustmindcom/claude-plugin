---
description: Get started with Evident in Claude
---

Run the Evident first run. Load the `evident` skill first. Keep it short and use the user's real data; never a canned demo. Ask, wait, continue: never send all of it as one wall of text.

1. **Check the connection.** Call `authorization_whoami`. If it fails, tell the user to connect Evident from the plugin's Connectors tab (in Claude Code, run `/mcp` and sign in to `plugin:evident:evident`), and stop. Its `role` is `admin`, `knowledge_editor` or `member`; treat any custom or unknown role as member.
2. **Read their workspace in one parallel round:**
   - `questionnaire_triage_open_work`: open work, what is assigned to them, and review requests.
   - `questionnaire_list`.
   - `onboarding_get_state`: the setup plan steps with `completed`, the org's counts (including `kb_stats.total_docs`) and `tooltips_shown`. It is not in your tool list: call `capability_run_read` with name `onboarding_get_state` and `{}`.
   - Editors and admins only: the knowledge base size, from `kb_stats` when `onboarding_get_state` gave it, otherwise `knowledge_base_browse` with `view="flat"`; and the open conflict count, from `conflict_list` with `status="open"` (its `total`). `conflict_list` is not in your tool list: call `capability_run_read` with name `conflict_list` and `{"status": "open"}` in the same round.
3. **State the model rules once, briefly, only if your current model limits anything** (the table in the skill's `SKILL.md`). On Haiku: lookups only, and the Haiku message. On Sonnet: everything except filling a portal in their own browser, which needs Opus; Evident's browser works. On Opus, say nothing about models.
4. **A two or three line tour for their role**, using their numbers:
   - Admins: answer questionnaires and portals from here, keep the knowledge base current, and set Evident up for the team.
   - Knowledge Editors: answer questionnaires and portals, load documents, settle conflicts, approve answers.
   - Members: ask about the company's security and product and get answers with sources, work questionnaires and portals, and answer what is assigned to them.
5. **Recommend the first step that matches**, in this order:
   1. Editor or admin with an empty knowledge base: load knowledge (`references/knowledge.md`).
   2. Editor or admin with open conflicts: resolve them, one at a time.
   3. Anyone with assigned questions or review requests: work through them.
   4. Editor or admin with questionnaires waiting for approval: review and approve (`references/review.md`).
   5. Member with an empty knowledge base: say answers will be thin until their team adds documents, and add: "A Knowledge Editor can add this. Ask your admin for the Knowledge Editor role if you need to add documents yourself." Then go to 6.
   6. Otherwise ask: "Do you have a questionnaire or portal to work on, or a question you need answered?"
   Never recommend a setup step that `onboarding_get_state` marks `completed`. If `setup_plan.dismissed` is true, do not offer the setup walkthrough unless they ask. For admins, the setup walkthrough is `references/setup.md`, from the first step that is not completed.
6. **Show the other steps that apply on one "Also available:" line.** Offer the tour once, only if a browser tool is available and `claude:tour` is not in `tooltips_shown`: "I can also show you around the Evident app on screen. Want a quick look?" Follow `references/tour.md`, and end the tour by pointing out that all of it can be done from here.
7. **Carry straight on into the step they accept**, reading its reference file first.

After you offer the tour or one of the suggestions listed in `references/moments.md`, call `onboarding_record` (not in your tool list: `capability_run_write` with name `onboarding_record`) with `{"milestone": "tooltip_shown", "tooltip_id": "<its claude: id from that list>"}` (for the tour, `claude:tour`) so it is not offered again. Do not record anything for other offers, such as working through open questions. When the user finishes a setup step with you, record `{"milestone": "step_completed", "step_id": "<id from steps>"}`. Skip these calls if the tools are not available.
