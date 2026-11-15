# Evident for Claude

Work in Evident from Claude. The plugin connects the Evident MCP server and adds a skill that knows how Evident works, so you can answer security questionnaires, fill vendor portals in your own browser, assign and approve answers, resolve conflicts and manage knowledge from the conversation. Claude suggests the right feature when it would help, and can show you around the Evident app on screen.

## Install

1. **Install the plugin.** In Claude Code, or a Code session in Claude Desktop, run:

   ```
   /plugin install evident --marketplace trustmindcom/claude-plugin
   ```

   On Claude Code older than 2.1.275, run `/plugin marketplace add trustmindcom/claude-plugin` and then `/plugin install evident@evident`.
2. **Sign in to Evident.** Run `/mcp`, choose `plugin:evident:evident` and sign in in the browser window that opens.
3. **Start.** Run `/evident:start`. Claude checks who you are, shows what is waiting on you, suggests one next step and offers a short tour of the app.

## What's inside

- `.claude-plugin/plugin.json` connects the Evident MCP server at `https://mcp.evident.security/mcp`.
- `skills/evident` teaches Claude how Evident works, when to suggest a feature (`references/moments.md`) and how to point at things in the app (`references/show-me.md`, `scripts/evident-guide.js`).
- `commands/start.md` is the `/evident:start` first run.

The tour never types your password. If the app asks you to sign in, Claude stops and waits for you.

[Privacy policy](https://evident.security/privacy-policy/)
