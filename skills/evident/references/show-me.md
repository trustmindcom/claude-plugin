# Showing the user in the app

Use when a browser tool is present: Claude Desktop's built in browser (`Claude_Browser__*`) or Claude in Chrome (`claude-in-chrome__*`).

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
3. Read the page and decide what to point at from what is actually there. Write the bubble text for this user: name their numbers, their questionnaires, their people. Two or three sentences.
4. Inject `scripts/evident-guide.js` with the JavaScript tool, then call:

   ```js
   evidentGuide.show({
     guide: "settings-approvals-download",  // a data-guide id from the table
     match: "Approve before download",      // visible text, used when the id is not on the page
     climb: 2,                              // parents to climb from the matched text
     tag: "Approvals",
     title: "Want approvals?",
     text: "Two separate switches...",
     buttons: ["Turn on saving only", "Explain more", "Not now"]
   })
   ```

   It returns `{ ok: true }`, or `{ ok: false, reason }`. On `"not ready"` the page is still loading: wait a second and call again. After five tries, call once more with `force: true`. On `"target not found"`, point at something else on the page or explain in chat.
5. Poll `evidentGuide.answer()` to learn which button they pressed, or wait for them to reply in chat. Then show the next thing, do what they chose, or `evidentGuide.clear()`.
6. Opening a new URL reloads the page and removes the guide; inject again on the next page. After the user clicks a link inside the app, the guide stays loaded: call `evidentGuide.clear()`, wait for the new page as in step 1, then show the next bubble.

Rules:
- One bubble at a time. Hand control back after three or four.
- Point first; change a setting only when the user says so, and say what you changed.
- Never press Submit on a portal, delete anything, or send anything to a buyer from the overlay.
