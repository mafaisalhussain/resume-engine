# Evidence Classification Framework

Use this framework whenever classifying resume claims against the knowledge base.

## Classification Labels

- **DIRECT** — the exact tool, metric, date, company, or fact appears verbatim in profile.md or a projects/*.md file. Fully verifiable. No bridging required.
- **ADJACENT** — the same underlying work appears in the KB but under different vocabulary (e.g., resume says "agentic pipeline" and KB shows multi-model Ollama orchestration). Legitimate gap-bridging — valid only if the substance is real and the candidate can explain it in an interview.
- **TRANSFERABLE** — from a different domain but the technique or skill genuinely applies (e.g., anomaly detection expertise applied to a new industry). Valid if not overstated.
- **UNSUPPORTED** — no backing in the KB whatsoever. Every instance must be flagged and penalizes Truthfulness (D8) and Interview Defensibility (D7).
- **HARD_GAP** — (optimizer only) no KB backing of any kind → accept the gap, do not fabricate.

## Rules

1. When in doubt between ADJACENT and UNSUPPORTED, classify as UNSUPPORTED unless you can cite the exact KB passage that supports the bridge.
2. A vocabulary bridge is ADJACENT only if the underlying work is documented in the KB — never use ADJACENT to introduce tools or companies the candidate has not used.
3. TRANSFERABLE claims must not be overstated. "I did X in domain A therefore I did X in domain B" is only valid if the technique is genuinely domain-agnostic.
4. Build a complete claim ledger before scoring. The ledger drives fabrication_risks, D7, and D8 scores.
