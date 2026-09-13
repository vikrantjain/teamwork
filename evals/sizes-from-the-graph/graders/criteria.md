---
type: llm
weight: 1
---

The response must propose exactly three lanes, one per independent stream, and
give each lane a set of paths that no other lane also claims.

It passes if there are three lanes, each lane's paths are disjoint from every
other lane's, and the sizing is justified by which streams can start without
waiting on another.

It fails if it proposes a different number of lanes without explaining why the
dependency graph gives that number, if two lanes are given overlapping paths
(for example both owning `web/` or both owning the exporter package), or if the
lanes are split by topic rather than by which paths they write.
