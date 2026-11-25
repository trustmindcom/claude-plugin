# One question, answered with its source

For a single question about the company: "do we encrypt at rest?", "are we SOC 2 Type II?", "what's our RTO?", "does our product support SCIM?", or a line the user needs for an email or an RFP.

1. **Search Evident.** Call `knowledge_search` with the question. It returns passages from the company's documents and its saved answers from past questionnaires. When the user asks for a document itself (the SOC 2 report, a pen-test letter), use `knowledge_document_search` (or `document_search`).
2. **Answer with the source.** Lead with the answer, then name where it came from: the document title, or the questionnaire and question of a saved answer. When Evident has an answer in its own words (a saved or approved answer), pass it through exactly as written. Never reword, shorten, merge or improve it. When you only have document passages, quote the sentence that answers the question rather than paraphrasing it.
3. **Say when there is no source.** If nothing in Evident answers it, say so plainly: "Evident has nothing on this yet." Never fill the gap from general knowledge or from what companies usually do. If only part is covered, answer that part and say which part is missing.
4. **Missing or thin.**
   - Members: add "A Knowledge Editor can add this. Ask your admin for the Knowledge Editor role if you need to add documents yourself."
   - Knowledge Editors and admins: offer once to add the answer or the document that covers it (`references/knowledge.md`).

**Format it to paste.** The user usually copies the answer into an email or an RFP. Give it as plain text they can paste as it is, then the source on its own line. The shape, with made-up content:

> Yes. "All customer data is encrypted at rest using AES-256."
> Source: Information Security Policy, section 4.2

For several questions at once, give each as its own answer and source, in the order asked. More than a handful is usually a questionnaire: offer to upload it instead (`references/questionnaire.md`).
