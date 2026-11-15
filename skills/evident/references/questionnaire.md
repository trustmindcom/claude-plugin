# A questionnaire, RFI or RFP as a file

For a security questionnaire, RFI or RFP the user has as a file (Word, Excel, CSV or PDF), and for assigning its questions.

1. **Check your model first.** Uploading and working a questionnaire needs the middle tier (currently Sonnet) or above. On the smallest tier (Haiku), stop with the Haiku message in `SKILL.md`, even if the user insists.
2. **Never work the file yourself.** Do not open it to read, answer, fill or edit its questions, even if it is right there; you only send its bytes to Evident. Evident extracts the questions, answers them from the company's sources and builds the output file.
3. **Upload it.** Call `questionnaire_create_upload_url` with the file's name, type and size. PUT the file bytes to `upload_url`, sending `upload_headers`. Then call `questionnaire_create_from_upload` with the returned `task_id`, and pass the company that sent it (`company_domain`, preferred, and/or `company_name`) and any `due_date` the user gave. If you can't upload the file from here, say so and stop; never fall back to answering it yourself.
   - **Formats:** Evident takes Word (.docx), Excel (.xlsx, .xls, .xlsm) and CSV. For a PDF or an old .doc, say Evident can't take that format and ask for the Word or Excel original. Never answer it yourself.
   - **RFI or RFP:** pass `questionnaire_kind='vendor_evaluation'`. The type can't be changed afterwards, so ask when you are not sure. Before starting one, read the guide at https://evident.security/guides/rfi-rfp-mcp.md. Never write a price or accept a contract term: leave those for the user.
   - **Products:** when `product_list` says `scope_required_for_questionnaires`, ask the user which products it covers and pass their ids as `product_scope`. `product_list` is not in your tool list: call `capability_search`, then `capability_run_read`.
4. **Wait for it.** Processing takes a few minutes. Tell the user it is running, and check with `questionnaire_get` or `questionnaire_summary` when they come back or ask.
5. **Report.** Say how many questions were answered, how many are inferences, and how many are open, with the open ones that block delivery first. Pass Evident's answers through exactly as written; never reword, shorten or merge them.
6. **Work the open questions** with the user one at a time (`question_get`, `question_get_sources`), or assign them (below). When the user gives an answer, write it with `question_write_answers`.
7. **Finish** with the steps below.

## Assignment

There is one Assign action, `question_assign`. Evident decides what it asks for:
- An unanswered question: the person or team is asked to answer it.
- An answered question assigned to a person: it becomes a review request on that exact answer, and it closes when the answer is approved.
- Teams only receive answer requests; only a person holds a review.

## Finish: triage, review, approve

Questionnaires and portals end the same way.

1. Call `questionnaire_triage_open_work` and say what is still open on this questionnaire and who holds it.
2. Offer to review the answers together (`references/review.md`).
3. **Knowledge Editors and admins** can approve. Approve only answers the user has reviewed or asked you to approve, with `question_review_answers` (`action='approve'` and the `question_ids`).
4. Members: say who can approve (a Knowledge Editor, an admin, or the person assigned to review), and offer to assign the review.
