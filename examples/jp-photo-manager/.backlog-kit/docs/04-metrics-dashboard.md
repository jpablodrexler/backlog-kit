# Custom metrics and dashboard

Read when: a change adds, renames or removes a custom `photomanager_*` metric, or touches the Grafana dashboard; and on every full sweep

## 3. Custom Metrics ↔ Grafana Dashboard

Every custom application metric follows the pattern documented in
`docs/architecture.md`'s "Observability" section (also see `java-developer`
if a similar convention gets added there): `photomanager_<name>` via an
injected `MeterRegistry`, with `.description(...)`. As of the last full
sweep the existing metrics are `photomanager_catalog_assets_total`
(Counter), `photomanager_thumbnail_generation_seconds` (Timer), and
`photomanager_active_sse_connections` (Gauge) — but this list drifts the
moment a new one is added, so re-derive it rather than trusting this list.

**Check:** grep the backend for `Counter.builder("photomanager_`,
`Timer.builder("photomanager_`, and `Gauge.builder("photomanager_` to get
the current, real list. For each one, confirm
`grafana/provisioning/dashboards/photomanager.json` has a panel querying
that metric name (search the dashboard JSON's `"expr"` fields).

🟡 Flag any `photomanager_*` metric registered in code with no corresponding
dashboard panel — it's being collected and scraped but nobody can see it
without writing an ad-hoc PromQL query first.

🟢 Flag a dashboard panel querying a `photomanager_*` metric name that no
longer exists in code (the reverse drift — a removed/renamed metric leaving
a dead panel).

**Fix:** add a panel to `photomanager.json` following the existing panels'
structure (same `datasource`, similar `gridPos` placement, a PromQL `expr`
appropriate to the metric type — `rate(...)` for a counter, a raw gauge
value, `histogram_quantile`/`_sum`/`_count` for a timer, matching the
existing `HTTP p95/p99 Latency` panels' shape).
