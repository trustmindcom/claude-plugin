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

Some work needs a more capable Claude model: portals filled in your own browser need Opus, and anything beyond quick questions needs Sonnet or Opus. Claude says so before it starts.

Evident logs the words Claude uses in `capability_search`, and which capability it then runs, to improve how tools are matched. It never logs your conversation, answers or documents.

The tour never types your password. If the app asks you to sign in, Claude stops and waits for you.

[Privacy policy](https://evident.security/privacy-policy/)
