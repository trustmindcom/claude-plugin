# Showing the user in the app

Use when a browser tool is present: Claude Desktop's built in browser (`Claude_Browser__*`) or Claude in Chrome (`claude-in-chrome__*`).

1. Open the page. Pages render client side; wait until the text you expect is on the page before doing anything else (poll `document.querySelector('main').innerText`).
2. If the URL is `/login/`, stop and ask the user to sign in. Never type credentials.
3. Read the page and decide what to point at from what is actually there. Write the bubble text for this user: name their numbers, their questionnaires, their people. Two or three sentences.
4. Inject `scripts/evident-guide.js` with the JavaScript tool, then call:

   ```js
   evidentGuide.show({
     guide: "workflow.approvals",          // a data-guide id, when the app has one
     match: "Approve before download",     // or visible text to find
     climb: 2,                              // parents to climb from the matched text
     tag: "Approvals",
     title: "Want approvals?",
     text: "Two separate switches...",
     buttons: ["Turn on saving only", "Explain more", "Not now"]
   })
   ```

5. Poll `evidentGuide.answer()` to learn which button they pressed, or wait for them to reply in chat. Then show the next thing, do what they chose, or `evidentGuide.clear()`.
6. Navigation reloads the page and removes the guide; inject again on the next page.

Rules:
- One bubble at a time. Hand control back after three or four.
- Point first; change a setting only when the user says so, and say what you changed.
- Never press Submit on a portal, delete anything, or send anything to a buyer from the overlay.
