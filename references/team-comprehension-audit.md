# Team comprehension audit

Read this file at core-model approval, result freeze, and final audit.

## Protocol

Use `assets/templates/全员理解审计模板.json`. Each member must answer without reading the paper while a different member audits. Rotate the auditor. Score each topic from 0 to 5 using the template definition and attach concise evidence.

Every member must score at least 3 on:

- problem interpretation and subproblem dependencies;
- assumptions, scope, and failure conditions;
- variables, objective, and constraints;
- solver, parameters, and reproducibility command;
- headline numbers and units;
- validation, uncertainty, and limitations;
- AI-assisted content and the team’s verification or modification.

At least one member must score 4 or above on every topic, but expertise by one member never compensates for another member scoring below 3. Any failed topic blocks the corresponding approval gate.

## Challenge questions

Ask one problem-specific counterfactual per member, such as:

- Which conclusion changes first if the most influential assumption fails?
- How do you know the chosen parameter is identifiable rather than merely fitted?
- Which constraint is binding, and what happens if it is relaxed by 5%?
- Why is the comparator independent rather than a cosmetic variant?
- Which exact file and command reproduce the number in the abstract?
- What evidence would make the team reject the claimed innovation?

Record the question, answer evidence, auditor, repair, and retest. Do not convert this audit into rehearsed slogans.
