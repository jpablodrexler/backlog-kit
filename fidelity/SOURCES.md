# Where the originals live

The kit does not store the source projects' skills. The fidelity tool exports them from their own repositories when a maintainer needs them (it needs access to those repositories):

```
python3 tools/fidelity.py \
  --fetch pablo-web=<path to a pablo-web clone>@1e580fd \
  --fetch jp-photo-manager=<path to a jp-photo-manager clone>@be02b7c
python3 tools/fidelity.py --check
```

The pinned commits are the state of each project's skills the ledgers were written against. `fidelity/base/` is gitignored; without it `--check` says so and the fidelity tests are skipped.
