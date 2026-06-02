# ATS Compliance Rules

These rules are non-negotiable and must be applied during resume generation, review, and optimization.

1. **Standard section headers only:** Professional Summary, Education, Technical Skills, Experience, Projects, Certifications. No custom or creative section names.
2. **No tables, columns, or text boxes** — ATS parsers cannot read them. Use only plain text blocks and `\begin{itemize}` lists.
3. Contact info must be **plain text** in `\begin{center}` — no custom boxes or colored backgrounds.
4. All section headers must use the `\section{}` command.
5. **Exact keyword matching** — use the precise term from the JD, not a synonym. ATS is literal.
6. Target **1.5–2 pages** — use the space fully; include all JD-relevant detail.
7. **No Unicode special characters** in bullet text — no `∼`, no `→`, no `•` outside LaTeX commands, no smart quotes. Never use `$\sim$` (math tilde, Unicode U+223C) — it breaks ATS text parsing.
8. **Dates on all experience entries** — every entry must have `\textit{Month YYYY -- Month YYYY}` immediately after the job title line. Missing dates cause ATS to calculate 0 years of experience.
