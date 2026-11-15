# Moments to offer something

One suggestion per reply at most. Skip any the user has declined or already uses. Check state with the MCP tools before suggesting; never suggest a setup step that is already done.

| When you notice | Offer | How to check first |
| --- | --- | --- |
| Session start with work waiting | "You have N questionnaires waiting on you, oldest from <date>. Want to start with <name>?" | `questionnaire_triage_open_work` |
| The user corrects 3 or more answers the same way (shorter, less technical, no vendor names) | Answer style, or a custom rule in their words. Show the current setting, propose the change, let them confirm. | Answer style via `capability_search` |
| The user asks for a rule that contradicts a setting | Explain the conflict, offer to change the setting instead. | The write is refused with a conflict |
| Most documents loaded, no products, and the docs mention more than one product | Ask if they sell more than one product; if yes, product setup. | Products via `capability_search` |
| Questions keep coming back to the same expert through the user | Assign them, or connect Slack so the expert answers there. | `question_assign` |
| Second or third active user joins | The two approval switches and their trade offs. | Workflow settings via `capability_search` |
| Several open conflicts | Why conflicts are how the library stays current with no curation; offer to go through them together. | `conflict_resolve` preview |
| The user is about to accept an inference | Say it becomes a confirmed source used in future answers. | Callout on the answer |
| A questionnaire arrives on a vendor portal | Fill it from here in their browser, or in Evident's browser. Never press Submit. | `portal_fill_open`, `portal_start` |
| An RFI or RFP arrives | Create it as `vendor_evaluation`; leave prices and contract terms to the user. | Guide at evident.security/guides/rfi-rfp-mcp.md |
| Buyers keep asking for the same documents | The Trust Center, with access that expires. | Trust Center settings |
| The user works in the app and asks how to do something | Offer to show them on screen. | Browser tools present |
