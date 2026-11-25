# Helping the owner set things up

For admins only: products, approvals, routing, answer style, members, Slack or Teams, and the Trust Center. Knowledge Editors and members get none of this; tell them an admin can change it.

1. **Check your model first.** Changing a setting needs the middle tier (currently Sonnet) or above. On the smallest tier (Haiku), stop with the Haiku message in `SKILL.md`. Reading the current settings works on any model.
2. **Check what is done.** Read the setup plan from `onboarding_state_get` (not in your tool list: `capability_run_read` with name `onboarding_state_get`) and skip every step that is `completed`. If `setup_plan.dismissed` is true, do not offer the walkthrough unless the user asks. When the user finishes a step with you, record it with `onboarding_state_update` through `capability_run_write` (`{"milestone": "step_completed", "step_id": "<id from steps>"}`).

Most settings tools below are not in your tool list. For each one, call `capability_search` with what you want to do, then the run tool its result names: `capability_run_read` to read a setting, and usually `capability_run_destructive` to change one. When a change needs the user's approval, get its summary from `capability_run_read` first, without `confirmation_nonce`, so the user is asked once. Show the current value before you change anything, change only what the user asked for, and say what you changed.

## The order

The owner is whoever runs Evident and usually the questionnaire process. Help them in this order, and stop when they have enough:

1. **Knowledge sources** first (`references/knowledge.md`). Ask where their policies, SOC 2 report and past questionnaires live, and connect those.
2. **Products, after the documents are in.** Settings > Products (`settings_product_list` to read). Evident reads the documents, works out how to tell the products apart, asks the questions the documents do not answer, then sorts existing knowledge, splitting mixed documents. Do not start this before the documents are loaded; it has nothing to work from.
3. **Approvals, once there is a team.** Two independent switches in Settings > Workflow (`settings_workflow_update`, its `approval_before_download` and `approval_before_saving` fields; `settings_workflow_get` reads them):
   - *Approve before download*: nobody but admins downloads a questionnaire until every answer is approved. Strongest control, most friction.
   - *Approve before saving for reuse*: answers only enter the knowledge base once approved. Protects the library, no download friction.
   Approvers are Knowledge Editors, admins, and anyone assigned a question for review. Most teams start with saving only.
4. **Routing.** Topics (Security, Legal, Product and so on) can route new questions to a person or team automatically.
5. **Answer style.** Length, voice, technical depth, gaps, partial coverage, plus custom rules (`settings_answer_style_get`, `settings_answer_style_update`). A new custom rule is checked against the other rules and these settings; if it is refused for a conflict, explain the conflict and offer to change the setting instead.
6. **Chat and people.** Members and roles (show them with `ui_show` `[{"part": "manager", "tab": "members"}]`, or `"teams"`; to add someone to teams, pass their `member` and `teams` and the user saves), Slack or Teams, a directory (Google Workspace or Entra ID), and the Trust Center if they want buyers to serve themselves (`trust_center_settings_get`, and `trust_center_settings_update`, which also adds or edits one FAQ entry with `faq`; both are in your tool list).

Service providers: onboarding covers adding clients and giving teammates access per client, before the usual setup. Never use one client's settings for another.
