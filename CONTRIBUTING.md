# Contributing

Read [`CLAUDE.md`](CLAUDE.md) before changing the plugin. It holds the
conventions and the design choices already refused, with their reasons.

Run these from the repository root before a change lands:

```
python3 -m unittest discover -s scripts -p 'test_*.py'   # the validator and the hook
claude plugin test .                                     # the board
claude plugin validate .                                 # both manifests and the plugin
```

The first ends in `OK`, the second in `0 fail`, and the third in
`Validation passed with warnings`.

Leave `--strict` off the validate command. It turns two expected warnings into
failures. One is `CLAUDE.md` at the repository root, which is not plugin
context and is not meant to be. The other is the missing icon.

The behaviour that is prose rather than code has an eval suite under
[`evals/`](evals/). Each case is read-only and runs three times against a
judge, so a run spends usage. Run one case by name while you work on it:

```
claude plugin eval . --case 'finish-*'
claude plugin eval .
```
