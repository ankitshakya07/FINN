# Prompt registry

Keep prompts versioned as plain text/Markdown files. Recommended split:
- `filing_classification_v1.md` — small tier; classify exchange filing and extract evidence.
- `document_extraction_v1.md` — small tier; chunk-level structured extraction.
- `research_synthesis_v1.md` — strong tier; reason only over retrieved primary-source evidence.

Every prompt must instruct the model:
1. Use only supplied source excerpts.
2. Attach document + page/quarter + short verbatim quote to each factual claim.
3. Return `not found in sources` for unsupported fields.
4. Never calculate financial metrics; return source values for deterministic code to calculate.
