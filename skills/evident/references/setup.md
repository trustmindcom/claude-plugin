# Helping the owner set things up

For admins only: products, approvals, routing, answer style, members, Slack or Teams, and the Trust Center. Knowledge Editors and members get none of this; tell them an admin can change it.

1. **Check your model first.** Changing a setting needs the middle tier (currently Sonnet) or above. On the smallest tier (Haiku), stop with the Haiku message in `SKILL.md`. Reading the current settings works on any model.
2. **Check what is done.** When `onboarding_get_state` is available, read its setup plan and skip every step that is `completed`. If `setup_plan.dismissed` is true, do not offer the walkthrough unless the user asks. When the user finishes a step with you, record it with `onboarding_record` (`{"milestone": "step_completed", "step_id": "<id from steps>"}`). If these tools are not in your tool list, try `capability_search`; skip the calls if they are not there.

Most settings tools below are not in your tool list. For each one, call `capability_search` with what you want to do, then the run tool its result names: `capability_run_read` to read a setting, and usually `capability_run_destructive` to change one. When a change needs the user's approval, get its summary from `capability_run_read` first, without `confirmation_nonce`, so the user is asked once. Show the current value before you change anything, change only what the user asked for, and say what you changed.

## The order

The owner is whoever runs Evident and usually the questionnaire process. Help them in this order, and stop when they have enough:

1. **Knowledge sources** first (`references/knowledge.md`). Ask where their policies, SOC 2 report and past questionnaires live, and connect those.
2. **Products, after the documents are in.** Settings > Products (`product_list` to read). Evident reads the documents, works out how to tell the products apart, asks the questions the documents do not answer, then sorts existing knowledge, splitting mixed documents. Do not start this before the documents are loaded; it has nothing to work from.
3. **Approvals, once there is a team.** Two independent switches in Settings > Workflow (`organization_set_answer_approval`):
   - *Approve before download*: nobody but admins downloads a questionnaire until every answer is approved. Strongest control, most friction.
   - *Approve before saving for reuse*: answers only enter the knowledge base once approved. Protects the library, no download friction.
   Approvers are Knowledge Editors, admins, and anyone assigned a question for review. Most teams start with saving only.
4. **Routing.** Topics (Security, Legal, Product and so on) can route new questions to a person or team automatically.
5. **Answer style.** Length, voice, technical depth, gaps, partial coverage, plus custom rules (`answer_preferences_get`, `answer_preferences_update`). A new custom rule is checked against the other rules and these settings; if it is refused for a conflict, explain the conflict and offer to change the setting instead.
6. **Chat and people.** Members and roles, Slack or Teams, a directory (Google Workspace or Entra ID), and the Trust Center if they want buyers to serve themselves (`trust_center_get_settings`, `trust_center_edit_faq`; both are in your tool list).

Service providers: onboarding covers adding clients and giving teammates access per client, before the usual setup. Never use one client's settings for another.
