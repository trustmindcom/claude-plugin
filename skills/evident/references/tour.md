# Showing the user in the app

**Check your model first.** Showing works on any model: it only points at things.

**The tour is pulled, never pushed.** Offer it only when the user asks where something is or how to do something in the app, or when they accept the one offer in `/evident:start`. Offering it in answer to their question is helping, not a suggestion: do it even in quiet mode or after an earlier decline, and record no offer. Never offer it on your own otherwise. Its point is the lesson in `SKILL.md`: here is the app, and you can do all of it from the conversation.

Use it when a browser tool is present: Claude Desktop's built-in browser (`Claude_Browser__*`) or Claude in Chrome (`claude-in-chrome__*`). Without one, explain in chat and give a direct link on `https://app.evident.security` (paths below). Many pages accept a tab parameter, for example `https://app.evident.security/dashboard/organization/answer-style/?tab=gaps`.

**Rules for every tour:**

- **Three or four bubbles at most.** Decide how many before the first one, and pass `step` and `steps` so each bubble shows "2 of 4". Then hand control back.
- **The user clicks.** Point at the control and say what it does; the user clicks it themselves. Never click, type or change anything in the app during a tour. If they ask you to do it instead, do it from here through Evident's tools, saying first what will change and waiting for a yes.
- **Re-read the page before every bubble.** Write each bubble from what is on the page now, after the user's click, not from a script. If the page is not what you expected, say so and adapt.
- **Every bubble shows "Evident is showing this" and a close button.** The script draws both. If the user closes a bubble, the tour is over: clear it and continue in chat.
- **Only on Evident's own app.** Never inject the script into any other site, such as a customer's portal. As a backstop, the script refuses to draw anywhere but Evident's app.
- If the page shows the sign-in screen, stop and ask the user to sign in. Never enter credentials.

**Record progress** with `onboarding_record` (`capability_run_write`): `{"milestone": "tour_started"}` when the first bubble shows, then `{"milestone": "tour_step", "step": <n>, "steps": <total>}` for each bubble shown, including the first.

The app is at `https://app.evident.security`. Pages to point at:

| What | Path | `guide` ids | `match` text if the id is missing |
| --- | --- | --- | --- |
| Approvals | `/dashboard/organization/workflow/` | `settings-approvals-download`, `settings-approvals-reuse` | "Approve before download", "Approve before saving for reuse" |
| Products | `/dashboard/organization/` | `settings-products` | "Products" |
| Answer style | `/dashboard/organization/answer-style/` | `settings-answer-style` | "Answer style" |
| People | `/dashboard/organization/people/` | `settings-members`, `settings-teams` | "Members" |
| Integrations | `/dashboard/organization/integrations/` | `connect-integration` (one per integration) | "Integrations" |
| Questionnaires | `/dashboard/answer-questions/` | `upload-questionnaire` | "Questionnaires" |
| One questionnaire | `/dashboard/answer-questions/detail?id=<id>` | `sheet-toggle`, `question-assign`, `question-approve`, `question-sources`, `inferred-answer-accept` (per row; the first match is the first row) | |
| Knowledge | `/dashboard/manage-data/` | `upload-document` | "Knowledge Base" |
| Conflicts | `/dashboard/manage-data/conflicts/` | `conflict-resolve` (the two sides; choosing a side resolves it) | "Conflicts" |

The sidebar, on every page: `nav-questionnaires`, `nav-knowledge`, `nav-conflicts`, `nav-trust-center`, `nav-settings`, `chat-open`, and `client-switcher` when the organization can switch clients.

1. Open the page. Pages render client side; poll until either the text you expect is on the page (`document.querySelector('main')?.innerText`) or the path starts with `/login`.
2. If the path starts with `/login`, stop and ask the user to sign in in that browser, then continue when they say they have. Never type credentials, and never fill or submit the sign in form.
3. Read the page and decide what to point at from what is actually there. Write the bubble text for this user: name their numbers, their questionnaires, their people. Two or three sentences. When the next step needs a click, say which control to click.
4. Inject `scripts/evident-guide.js` (in this skill's folder) with the JavaScript tool, then call:

   ```js
   evidentGuide.show({
     guide: "settings-approvals-download",  // a data-guide id from the table
     match: "Approve before download",      // visible text, used when the id is not on the page
     climb: 2,                              // parents to climb from the matched text
     step: 2,                               // this bubble's number
     steps: 4,                              // how many bubbles this tour has, 4 at most
     title: "Want approvals?",
     text: "Two separate switches...",
     buttons: ["Next", "Explain more"]
   })
   ```

   It returns `{ ok: true }`, or `{ ok: false, reason }`. On `"not ready"` the page is still loading: wait a second and call again. After five tries, call once more with `force: true`. On `"target not found"`, point at something else on the page or explain in chat. On `"not evident"`, you are not on Evident's app: draw nothing and explain in chat.
5. Poll `evidentGuide.answer()` to learn which button they pressed (`"dismissed"` when they closed the bubble), or wait for them to reply in chat. After they click a control in the app, wait for the page to change, re-read it as in step 1, then show the next bubble.
6. Opening a new URL reloads the page and removes the guide; inject again on the next page. After the user clicks a link inside the app, the guide stays loaded: call `evidentGuide.clear()`, wait for the new page as in step 1, then show the next bubble.
7. After the last bubble, `evidentGuide.clear()` and point out that all of it can be done from here.

Never press Submit on a portal, delete anything, or send anything to a buyer from the overlay.
