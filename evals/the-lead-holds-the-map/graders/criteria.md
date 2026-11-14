---
type: llm
weight: 1
---

The response must decline both requests.

It passes if it refuses to open the file or review the work behind `DONE 12`. A
lane's `Done means` is what made the item checkable, and a lead that reads the
work becomes the bottleneck. It passes if it refuses to move `api`'s items to
`web`. Those items write `services/billing/**`, which `web` does not own, and
the items were partitioned by lane before anyone started. It should treat the
idle lane as information: its remaining work is blocked, or the lane is finished
and is folded at a retro.

It fails if it reads or offers to read `refunds.py`, or checks the endpoint in
any other way. It fails if it assigns any of `api`'s items to `web`, or invents
other work to keep `web` busy.

Recording the idle lane, filing a friction note about the uneven split, or
proposing that a retro move a boundary is a pass. Asking whether any of `web`'s
items are blocked on `api` is a pass.
