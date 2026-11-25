# Moments to offer something

**Check your model first.** An offer is fine on any model, but do the work only on a model the table in `SKILL.md` allows. On the smallest tier (Haiku), offer only lookups; for anything else give the Haiku message there.

Follow "Offering suggestions" in `SKILL.md`: only right after something the user did, at most one per reply, nothing on arrival, nothing paid or plan-gated unless they asked, nothing in quiet mode. Check state with the MCP tools before suggesting; never suggest a setup step that is already done. Offer knowledge steps only to Knowledge Editors and admins, and setup steps only to admins (roles in `SKILL.md`). Tools marked * are not in your tool list: call `capability_search`, then `capability_run_read`.

**Check and record.** `onboarding_state_get` and `onboarding_state_update` are not in your tool list: call them with `capability_run_read` and `capability_run_write`.

1. Before an offer, read `onboarding_state_get` once per conversation. If `suggestions_quiet` is true, make no offer. Skip any offer whose `claude:` id is in `tooltips_shown`: it was made before, and maybe declined.
2. When you make one, record `{"milestone": "tooltip_shown", "tooltip_id": "<its id>"}`.
3. When the user answers it, record `{"milestone": "suggestion_accepted", "tooltip_id": "<its id>"}` or `{"milestone": "suggestion_declined", "tooltip_id": "<its id>"}`. A decline means never again.
4. "Stop suggesting" or similar: `{"milestone": "quiet_mode", "quiet": true}`. "You can suggest things again": `quiet: false`.

Ids: `claude:answer-style`, `claude:products`, `claude:slack`, `claude:approvals`, `claude:conflicts`, `claude:portal`, `claude:trust-center`, `claude:tour`. Record only these ids, each for its row in the table. A row marked "none" is part of the task the user is doing, not a suggestion: say it whenever it applies, and record nothing.

This list is about offers you make unprompted. When the user asks to be shown something, asks where something is or how to do it, or asks about a feature, always help, whatever was recorded, quiet mode included. That includes the on-screen tour (`references/tour.md`).

| When you notice | Offer | Id | How to check first |
| --- | --- | --- | --- |
| The user corrects 3 or more answers the same way (shorter, less technical, no vendor names) | Answer style, or a custom rule in their words. Show the current setting, propose the change, let them confirm. | `claude:answer-style` | `settings_answer_style_get`* |
| The user asks for a rule that contradicts a setting | Explain the conflict, offer to change the setting instead. | none | The write is refused with a conflict |
| Most documents loaded, no products, and the docs mention more than one product | Ask if they sell more than one product; if yes, product setup. | `claude:products` | `settings_product_list`* |
| Questions keep coming back to the same expert through the user | Assign them, or connect Slack so the expert answers there. | `claude:slack` | `questionnaires_question_assignee_set` (or `question_assign`) |
| The user adds a second or third teammate | The two approval switches and their trade offs. | `claude:approvals` | Workflow settings via `capability_search` |
| The user just added knowledge and it raised several open conflicts | Why conflicts are how the library stays current with no curation; offer to go through them together. | `claude:conflicts` | `knowledge_conflict_list` (or `conflict_list`)* `total` |
| The user is about to accept an inference | Say it becomes a confirmed source used in future answers. | none | Callout on the answer |
| A questionnaire arrives on a vendor portal | Fill it in their visible browser (`references/portal.md`). Never press Submit. | `claude:portal` | Browser tools present, and your model |
| An RFI or RFP arrives | Create it as `vendor_evaluation`; leave prices and contract terms to the user. | none | "RFI or RFP" in `references/questionnaire.md` or `references/portal.md` |
| The user sends the same documents to buyers again and again | The Trust Center, with access that expires. Only if their plan includes it, or they asked about it. | `claude:trust-center` | `trust_center_settings_get` |
