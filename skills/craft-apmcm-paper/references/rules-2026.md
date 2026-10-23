# 2026 APMCM rules audit — checked 2026-10-23

Scope: November English APMCM, not the separate Chinese event. The organizer published [current participation rules on October 20](https://www.apmcm.org/detail/2513), [six-page PDF](https://files.apmcm.org/uploads/files/20261020/1792484391858628.pdf). All six rendered pages were read; SHA-256 `f50d011b6aa99c6ecff3877973fc1f67e95ceb87ff86c1e9db5eb589cf318fa8`. The PDF is image-only: empty text extraction is not evidence of an absent clause. Machine facts and locators are in `assets/rules-2026.json`.

## Confirmed current requirements

- **Schedule:** p1 §II gives November 26 06:00 to November 30 09:00, China time: 99 hours. Paper, control sheet and applicable attachments share the latter deadline. P2 §V(A)1(1) says register before November 25 24:00, normalized as the exclusive midnight starting November 26. The previously retrieved mobile display said 23:59; do not treat its minute precision as a different contest date or wait until cutoff.
- **Paper:** p3–4 §V(B)3(4) puts Summary on the first page. Describe methods and the most important conclusions; repeating the question or introduction boilerplate is uncompetitive. Other listed components include restatement, assumptions, notation, model evaluation/analysis, references and appendix. This list does not specify a full page sequence or a contents-page position.
- **Language and identity:** p4 §V(B)3(5),(7),(8) requires English and readable type, typically 11/12 points. Each solution page has actual team identifier and page number at the top. Member/adviser names, institution names and other identifying information apart from team number are excluded throughout the solution. Keep the identity-bearing control sheet separate. The sample total page count and identifier are examples, not a page limit or a required identifier length.
- **Upload files:** p4–5 §V(C)1–3 gives paper PDF stem `problem letter + actual assigned team identifier`; separate signed control PDF/JPG/PNG adds `cns`, applicable support RAR/ZIP adds `fj`. Use the corresponding registration-platform fields; the final live UI has not been inspected. A student or adviser may upload; that does not authorize adviser help in solving.
- **Control and support:** form is described as released with the questions; the actual form has not been retrieved. Each member signs; p5 allows electronic signing when printing is inconvenient. Use genuine signatures. Support is conditional unless the question requires it, but written source programs belong in both paper appendix and support archive; include related data except original problem data and the outputs.
- **Retention:** p5 §V(C)4 asks teams to retain PDF and Word paper versions, programs, results and attachments until after the final award list. This is a retention clause, not a second paper-upload instruction. If using LaTeX, reconcile the explicit Word wording with current format guidance instead of silently replacing it with a `.tex`-only rule.
- **Judging:** p1–2 §IV confirms seven principles already used by this skill: interpretation, justified assumptions, modeling rationale, effective model, stability, strengths/weaknesses and clear conclusions, accurate complete Summary. P3 accepts incomplete papers and describes no numeric score; missing answers remain a competitive weakness, not automatically a disqualification rule.
- **Awards:** p6 §V(D)3 table lists Innovation Prize as the highest tier, two teams per problem, and First Prize at 5%. Judging is described by group and problem; do not infer a whole-event total from the table. These are stated allocations, not observed final rates or this team's probability. Use `judging-priorities.md` for the work implications.

The [September collective-registration notice](https://m.saikr.com/contest/notice_detail/47643) and [September general notice](https://www.apmcm.org/detail/2512) remain provenance for earlier partial facts; the October general rules now supply the clauses above. The [October FAQ](https://m.saikr.com/contest/notice_detail/49050) also restricts adviser guidance during the contest.

## AI and remaining unknowns

P3 §V(B)3(1) permits nonliving resources/software with citations; (2) prohibits help/discussion outside the team, including online chat and other Q&A systems. The general document does **not explicitly resolve generative-AI/LLM permission or disclosure**. Do not convert its software allowance into permission for Codex/Modex, or import a 2025 AI notice as a current authorization. Current specific organizer clarification is needed before live assistance; preparation and historical rehearsals may continue. Do not contact organizers without user authorization.

The actual English template, page cap and complete sequence/contents rule remain unverified. Machine `summary_position`, `page_headers` and `anonymity` now hold confirmed facts, while aggregate `page_structure` stays unverified because full ordering is unresolved. An anonymous Summary-first rehearsal is still not a fully cleared official-format submission. Unknown required fields must keep `--final` failing.

The October 9–10 pending-policy replies were evidence available in the earlier snapshot, not permission. The current mobile registration page was inaccessible in this recheck; the new PDF was retrieved directly and its clauses are recorded separately. No new AI-specific notice or English-template attachment was established by this bounded search.

## Historical materials (not 2026 requirements)

The [2024 official archive](https://www.apmcm.org/detail/2487) contains `APMCM2024 论文提交规范、论文模板、承诺书.zip`: Summary Sheet and Control Sheet DOCX, English format PDF, Chinese submission instructions and LaTeX ZIP. These remain historical artifacts, not rebranded current templates.

The 2024 English specification says: English body/charts; summary first, contents second, then body; body within 25 pages and unlimited appendix; anonymous team/page headers; PDF paper and separate signed control sheet. Support material is conditional on the problem. Its sample paper filename has an inconsistent year; reconcile the stated pattern with the separate instructions instead of copying that example. Do not infer a 2026 pattern.

The [2023 template notice](https://www.apmcm.org/detail/2471) separates the identity-bearing control sheet and describes the template as a reference. The [2025 FAQ](https://www.apmcm.org/detail/2497) permits adviser guidance before, not during, the contest. Neither establishes current AI rules.

## CUMCM separation

Never import CUMCM's no-contents rule, page sequence, page limits, `AI工具使用详情.pdf`, Chinese declarations, two-file upload contract, or national-award rubric. This skill's English template is a provisional authoring aid. Use confirmed current documents for final layout.

## Recheck protocol

For every updated field store event/year, status, value, exact source URL, relevant clause, source artifact hash and date. Distinguish verified, historical, unverified and conflict. Resolve conflicts against current organizer clarification, not convenience. Unknown required fields fail final readiness but do not prevent pre-contest rehearsals.
