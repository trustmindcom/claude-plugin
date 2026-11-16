# Evident for Claude

Ask Claude about your company's security, privacy, compliance and product ("do we encrypt at rest?", "are we SOC 2?") and it answers from your Evident workspace, with the source. Claude can also answer security questionnaires, RFIs and RFPs, fill vendor portals in your own browser, review and approve answers, manage knowledge and conflicts, and show you around the Evident app on screen.

## Install

1. **Install the plugin.** In Claude Code, or a Code session in Claude Desktop, run:

   ```
   /plugin install evident --marketplace trustmindcom/claude-plugin
   ```

   On Claude Code older than 2.1.275, run `/plugin marketplace add trustmindcom/claude-plugin` and then `/plugin install evident@evident`.
2. **Sign in to Evident.** Run `/mcp`, choose `plugin:evident:evident` and sign in in the browser window that opens.
3. **Start.** Run `/evident:start`. Claude checks who you are, shows what is waiting on you, suggests one next step and offers a short tour of the app.

## What's inside

- `.mcp.json` connects the Evident MCP server at `https://mcp.evident.security/mcp`.
- `skills/evident` is one skill that Claude uses for any question about your company's own security, trust or product. Its `SKILL.md` holds the rules every task follows and sends Claude to one short file in `references/` for each kind of work: one answer, a questionnaire file, a vendor portal, review, knowledge, setup, the tour of the app (`scripts/evident-guide.js`), and when to suggest a feature.
- `commands/start.md` is the `/evident:start` first run.

## What the plugin sends to Evident

Claude talks to Evident only through Evident's tools, and sends only what a task needs:

- the questions you ask it to look up, as search text;
- files you ask it to upload: questionnaires (Word, Excel, CSV) and knowledge documents;
- on a vendor portal you fill in your own browser: the page address, and each question's text, field, choices and current value;
- answers you write, edit or approve, and the choices you make (resolving a conflict, assigning a question, changing a setting);
- which suggestions Claude offered and how you answered, whether you turned suggestions off, and how far a tour got.

## What Evident stores

- The files, questionnaires, answers and knowledge you send, in your organization's workspace, like anything added in the app.
- Who changed what and when: answer edits keep their author, and approvals, conflict resolutions and knowledge changes go in your organization's audit log. Ask Claude "what did you change today?" to see your own changes, with an undo where Evident has one.
- The words Claude uses in `capability_search`, and which capability it then runs, to improve how tools are matched.
- Usage events for each tool call: the tool name, whether it worked, and the ids of what it touched, plus the suggestion and tour progress above. They never carry text you wrote.

Evident never logs your conversation with Claude, your answers or your documents in these events.

## What it never does

- Press Submit on a portal. You submit.
- Pick a side in a knowledge conflict. You choose, one conflict at a time.
- Write a price, discount or other commercial figure, or accept a contract term.
- Read, answer or edit a questionnaire file on your computer. It uploads the file to Evident instead.
- Mix two clients' data, for service providers working for several companies.
- Change anything without saying first what will change and waiting for your go ahead.

## Which Claude model

Some work needs a more capable model, and Claude says so before it starts:

- Quick questions and lookups work on any model.
- Anything that changes data, and whole questionnaires, need Sonnet or Opus.
- Filling a portal in your own browser needs Opus.
- Evident's own browser can fill a portal from Sonnet.

## Suggestions and the tour

Claude suggests a feature rarely: only right after something you did, never one you declined, and never a paid feature you did not ask about. To stop suggestions, tell Claude "stop suggesting". To start them again, tell it "you can suggest things again". The setting is kept in Evident, not in Claude.

The on-screen tour runs only when you ask where something is or how to do it, or accept the one offer in `/evident:start`. It draws only on the Evident app, marks each bubble "Evident is showing this", and you can close it at any time. It never types your password. If the app asks you to sign in, Claude stops and waits for you.

## Uninstall

- In Claude Code, run `/plugin uninstall evident`. To also forget the marketplace, run `/plugin marketplace remove evident`.
- To disconnect Evident from claude.ai or the Claude desktop app, remove the Evident connector in Settings > Connectors.

Uninstalling removes the plugin from Claude. Your data in Evident stays in your workspace.

[Privacy policy](https://evident.security/privacy-policy/)
