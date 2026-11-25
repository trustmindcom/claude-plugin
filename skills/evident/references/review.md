# Review and approve answers

For "what's waiting on me?", a review request, or going through a questionnaire's answers before it goes out. It starts where a questionnaire or portal finishes: triage, review, approve.

1. **Check your model first.** Looking at what is waiting is a lookup and works on any model. Approving or editing an answer needs the middle tier (currently Sonnet) or above. On the smallest tier (Haiku), stop before the first approval or edit with the Haiku message in `SKILL.md`.
2. **Find the work.** `questionnaire_triage_open_work` shows the open questionnaires and what is assigned to the user, including review requests. For one questionnaire, `questionnaires_summary_get` with `include_approval=true` says how many answers are approved, how many wait, and whether it is ready to deliver.
3. **Who reviews.** Anyone can review an answer they were asked to review. Otherwise reviewing and approving is for Knowledge Editors and admins; for a member, say who can approve and offer to assign the review (`question_assign`).
4. **Open the review** with `ui_show` `[{"part": "question_review", "questionnaireId": "<id>"}]`; the user approves and edits there. For its inferred answers ("check the inferred answers"), open `[{"part": "decision", "questionnaireId": "<id>", "kind": "inference"}]` instead; the user accepts or edits each one there. Then act on what they ask you in chat, as in step 5. Without `ui_show`, **show one answer at a time**, in this order: the question, Evident's answer exactly as written, its state (answered, inference, conflict, no information), and its sources (`question_get`, `question_get_sources`). Lead with inferences and conflicts; they need a decision.
5. **Act only on what the user says:**
   - Approve: `questionnaires_answer_review` with `action='approve'` and the `question_ids`.
   - Edit: `questionnaires_answer_update`. Write the user's words, not yours. For an inference or a conflict, use `mode='edit'` with the expected answer id and state from `question_get`.
   - Accept an inference as it is: say first that it becomes a confirmed source future answers will use, then `questionnaires_answer_review` with `action='verify'` and the answer id and state from `question_get`.
   - Sources disagree on an answer: lay out both sides and let the user choose. Settling the conflict itself is `references/knowledge.md`.
   - Ask a teammate: `question_assign`, or `questionnaires_comment_save` with `action="create"` to leave a note on the question.
6. **Report** what was approved and what is still open.

Never:
- Approve an answer the user has not seen or asked you to approve.
- Use `approve_all` unless the user asks to approve everything. It skips inferences and conflicts; say so.
- Reword, shorten or merge Evident's answers when you show them.
