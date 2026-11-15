---
description: Get started with Evident in Claude
---

Run the Evident first run. Load the `evident` skill first. Keep it short and use the user's real data; never a canned demo.

1. **Check the connection.** Call `authorization_whoami`. If it fails, explain how to connect the Evident connector and stop. Then call `onboarding_get_state` if it is available. It returns the setup plan steps with `completed`, the org's counts, and `tooltips_shown`. Never suggest a step that is completed or a tip already in `tooltips_shown`.
2. **Show it working on their account.** Call `questionnaire_triage_open_work`. In three or four lines, say what is open, what is waiting on them, and the most urgent item.
3. **Teach the habit.** One or two sentences: everything in Evident can be done from this conversation, including uploading questionnaires, filling vendor portals in their own browser, assigning, and answering. Then offer one concrete next step from step 2, for example "Want to go through the 6 open questions on Acme together?"
4. **Ask what they mostly do** (answer questionnaires, review or approve answers, run Evident for the team, run the Trust Center) and tailor the next suggestion to it. For whoever runs Evident, offer the setup walkthrough in the skill, starting from the first setup step that is not completed.
5. **Offer the tour, once.** Skip this if `claude:tour` is in `tooltips_shown`. "I can also show you around the Evident app on screen. Want a quick look?" Only if a browser tool is available; follow `references/show-me.md`. End the tour by pointing out that all of it can be done from here.

After you make a suggestion or offer the tour, call `onboarding_record` with `{"milestone": "tooltip_shown", "tooltip_id": "claude:<topic>"}` (for the tour, `claude:tour`) so it is not offered again. When the user finishes a setup step with you, record `{"milestone": "step_completed", "step_id": "<id from steps>"}`. Skip these calls if the tools are not available.

Do not run all five as a wall of text. Ask, wait, continue.
