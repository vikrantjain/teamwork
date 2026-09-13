---
max_turns: 12
allowed_tools: [Read, Glob, Grep, Skill]
---

Size a team for this goal, and tell me the lanes and what each owns. Do not write
any files yet.

We are adding CSV export to our product. Three streams have to happen and none of
them needs another to start.

The `exporters/` package: a record-set serialiser, a streaming writer for large
result sets, dialect handling for Excel and RFC 4180, and its unit tests.

The user documentation under `docs/`: an `export.md` page describing the format,
a column reference generated from the schema, and a troubleshooting page for
encodings.

The console panel under `web/settings/`: an `export.tsx` column picker, the
saved-preset list beside it, and the component tests for both. The panel calls an
endpoint that already exists and already returns the column list.
