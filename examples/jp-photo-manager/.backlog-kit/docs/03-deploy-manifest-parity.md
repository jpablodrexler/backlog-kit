# Deploy manifest parity

Read when: a change touches `docker-compose.yml`, `k8s/*.yaml`, `.env.example`, or an environment variable; and on every full sweep

## 2. Deploy Manifest Parity

`k8s/configmap.yaml`'s own header comment states the requirement directly:
"Mirrors the plain environment variables set in `../docker-compose.yml`'s
`backend` service" — but nothing checks that this stays true after either
file changes.

**Check:** every non-secret environment variable in `docker-compose.yml`'s
`backend` service block has a matching key in `k8s/configmap.yaml` (or, for
values that must differ between the two — e.g. `KAFKA_BOOTSTRAP: kafka:9092`
in both, since both use the in-cluster/in-network service name `kafka` — a
deliberate, in-cluster-appropriate value). Do the same check in the other
direction: every `k8s/configmap.yaml` key should trace back to a
`docker-compose.yml` env var or an explicit Kubernetes-only reason for its
existence (there shouldn't be many — the whole point of the ConfigMap is to
mirror Compose).

**Secrets are out of scope for this check.** `JWT_SECRET`,
`POSTGRES_PASSWORD`, and `GRAFANA_ADMIN_PASSWORD` live in `.env` /
`k8s/secret.yaml` respectively — **never read `k8s/secret.yaml` or
`k8s/catalog-volumes.yaml`** (per `CLAUDE.md`'s "Never read these files").
Confirming a secret *key* is present in both `.env.example` and
`k8s/secret.yaml.example` (the safe-to-read templates) is fine; confirming
*values* match is not something this skill does or needs to do.

🔴 Flag a new environment variable added to `docker-compose.yml`'s `backend`
service with no corresponding `k8s/configmap.yaml` entry (or vice versa) —
this is a live bug, not just a doc gap: the Kubernetes deployment will
silently run with a stale/default value for that property until someone
notices.

**Fix:** add the missing key directly to whichever manifest is missing it,
matching the existing formatting/comment style in that file. This is a
config file edit, not a markdown edit — still covered by this skill's
"apply directly" workflow (§ above), but flag it clearly in the chat summary
since it's a higher-stakes file than a doc.
