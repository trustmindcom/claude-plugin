# Moments to offer something

**Check your model first.** An offer is fine on any model, but do the work only on a model the table in `SKILL.md` allows. On the smallest tier (Haiku), offer only lookups; for anything else give the Haiku message there.

One suggestion per reply at most. Skip any the user has declined or already uses. Check state with the MCP tools before suggesting; never suggest a setup step that is already done. Offer knowledge steps only to Knowledge Editors and admins, and setup steps only to admins (roles in `SKILL.md`). Tools marked * are not in your tool list: call `capability_search`, then `capability_run_read`.

`onboarding_get_state` and `onboarding_record` are not in your tool list: call them with `capability_run_read` and `capability_run_write`. Skip any suggestion whose `claude:` id is in `tooltips_shown`, and after making one, record it with `onboarding_record` (`tooltip_shown`). Ids: `claude:answer-style`, `claude:products`, `claude:slack`, `claude:approvals`, `claude:conflicts`, `claude:portal`, `claude:trust-center`, `claude:tour`. Record only these ids. This list is about offers you make unprompted: when the user asks to be shown something or asks about a feature, always help, whatever was recorded.

| When you notice | Offer | How to check first |
| --- | --- | --- |
| Session start with work waiting | "You have N questionnaires waiting on you, oldest from <date>. Want to start with <name>?" | `questionnaire_triage_open_work` |
| The user corrects 3 or more answers the same way (shorter, less technical, no vendor names) | Answer style, or a custom rule in their words. Show the current setting, propose the change, let them confirm. | `answer_preferences_get`* |
| The user asks for a rule that contradicts a setting | Explain the conflict, offer to change the setting instead. | The write is refused with a conflict |
| Most documents loaded, no products, and the docs mention more than one product | Ask if they sell more than one product; if yes, product setup. | `product_list`* |
| Questions keep coming back to the same expert through the user | Assign them, or connect Slack so the expert answers there. | `question_assign` |
| Second or third active user joins | The two approval switches and their trade offs. | Workflow settings via `capability_search` |
| Several open conflicts | Why conflicts are how the library stays current with no curation; offer to go through them together. | `conflict_list`* `total` |
| The user is about to accept an inference | Say it becomes a confirmed source used in future answers. | Callout on the answer |
| A questionnaire arrives on a vendor portal | Fill it from here in their browser, or in Evident's browser (`references/portal.md`). Never press Submit. | Browser tools present, and your model |
| An RFI or RFP arrives | Create it as `vendor_evaluation`; leave prices and contract terms to the user. | "RFI or RFP" in `references/questionnaire.md` or `references/portal.md` |
| Buyers keep asking for the same documents | The Trust Center, with access that expires. | `trust_center_get_settings` |
| The user works in the app and asks how to do something | Offer to show them on screen. | Browser tools present |
