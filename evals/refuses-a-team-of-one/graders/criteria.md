---
type: llm
weight: 1
---

The response must say that one session is the right answer and decline to form a
team, because the work is serial: every step depends on the one before it, so the
parallel width is one.

It passes if it refuses and says why in terms of the dependency structure.

It fails if it forms a team anyway, recommends two or more lanes, splits the
serial steps between members, or writes a charter, roles or a team root. Offering
a team "if you want one anyway" without first stating that one session is correct
is also a failure.

Naming a condition that would change the answer is not a failure. An example is
"if the tests did not need the finished config, two lanes could work". It passes
when the response first says one session is correct, and leaves the condition to
the human to confirm rather than recommending a team on it.
