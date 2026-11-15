---
description: Get started with Evident in Claude
---

Run the Evident first run. Load the `evident` skill first. Keep it short and use the user's real data; never a canned demo.

1. **Check the connection.** Call `authorization_whoami`. If it fails, explain how to connect the Evident connector and stop.
2. **Show it working on their account.** Call `questionnaire_triage_open_work`. In three or four lines, say what is open, what is waiting on them, and the most urgent item.
3. **Teach the habit.** One or two sentences: everything in Evident can be done from this conversation, including uploading questionnaires, filling vendor portals in their own browser, assigning, and answering. Then offer one concrete next step from step 2, for example "Want to go through the 6 open questions on Acme together?"
4. **Ask what they mostly do** (answer questionnaires, review or approve answers, run Evident for the team, run the Trust Center) and tailor the next suggestion to it. For whoever runs Evident, offer the setup walkthrough in the skill.
5. **Offer the tour, once.** "I can also show you around the Evident app on screen. Want a quick look?" Only if a browser tool is available; follow `references/show-me.md`. End the tour by pointing out that all of it can be done from here.

Do not run all five as a wall of text. Ask, wait, continue.
