# Forecasting and cycles

`backlog-forecast` says what the backlog can deliver and by when. `backlog-cycle` records a cycle and checks the estimates against what was delivered. This page explains the figures they print, above all **P50, P85 and P95**.

## Where the pace comes from

The pace is not typed in. It is what the backlog delivered in each of the last 12 complete weeks (`--weeks`, or `--since DATE` to start the window later): the points and the number of features archived per week, dated as `backlog-report` dates them. Those weekly figures already contain the limits of the Claude subscription, the time spent on bugs and the interruptions, so none of them is an input. The price is the assumption that the next weeks look like the window.

## What P50, P85 and P95 mean

The forecast takes the weekly figures of the window and resamples them at random 20,000 times (a bootstrap, with a fixed seed, so the same data always prints the same result). That gives 20,000 possible cycles, or 20,000 possible ways of working through the backlog. A **percentile** reads one value off those runs: P85 is the value reached or passed in 85 of every 100 runs.

| Label | In the output | Means |
| --- | --- | --- |
| P50 | typical, likely | Half of the runs do at least this. A coin flip. |
| P85 | prudent | 85 of 100 runs do at least this. A bet with margin. |
| P95 | very prudent | 95 of 100 runs do at least this. Only used for the date the whole backlog is done. |

It is a statistic of the simulation, not a percentage of progress.

### The two directions

The same percentile reads in opposite directions for a capacity and for a date, because more is good for one and bad for the other.

- **Capacity of a cycle (points):** "prudent 22 points" means that in 85 of 100 simulated cycles the work delivered was 22 points or more. A higher percentile gives a smaller number, because it asks for a capacity that almost every cycle reached.
- **Date or number of cycles to finish:** "prudent: 27 November" means that in 85 of 100 runs the work was done by that date. A higher percentile gives a later date, because it asks for the date by which almost every run had finished.

### An example

A window of weekly points `52, 22, 18, 28, 6, 15, 51, 0, 24, 31, 68, 0` gives a typical 2-week cycle of about 51 points and a prudent one of about 22. Both are right: half of the two-week cycles in the simulation reached 51, and 85 of 100 reached 22. The prudent figure is lower because it has to hold in almost every cycle, bad ones included. In a one-week cycle the prudent capacity of the same window is 0: about one week in six delivered nothing, so a week of 0 shows up in more than 15 of 100 simulated weeks. That is why the cycles are two weeks long by default.

## Cycles

A cycle is a window of time, 2 weeks by default (`[cycles] weeks` in `.backlog-kit.toml`, or `--cycle-weeks N` for one run). `backlog-forecast` uses it to size the next cycle and to table the cycles ahead. `backlog-cycle` keeps a file per cycle in `<backlog>/cycles/`:

- **plan:** the features committed, taken from the prudent set unless the user asks for the likely one or picks the features, and the capacity the forecast gave at that moment.
- **close:** what was archived in the cycle (read from the same dates as `backlog-report`, so it covers features done inside a batch run and outside one), what was carried over and why, and whether the forecast capacity was reached.
- **retro:** one or two lines the user gives. Nothing is invented.

The cycle file is the committed record; a batch report stays a local log to resume a cut run. The only thing `close` takes from a batch report is the reason a feature was blocked.

## Calibration

The closed cycles are the evidence that the estimates were right or wrong:

- **Forecast reached:** in how many closed cycles the prudent and the likely capacity were reached. If the prudent one is reached in much fewer than 85 of 100 cycles, the forecast is optimistic.
- **Delivered share:** the median share of the committed points that was delivered.
- **Carried over by size:** how often a feature of each size slips.

From 4 closed cycles that delivered less than they committed, `backlog-forecast` scales the capacity of the next cycle by the median delivered share (never below 0.3). Before that it only says how many cycles are missing. `--no-calibration` shows the sets unscaled. The weekly pace already contains what the project delivered, so the factor corrects the commitment, not the pace; the finishing dates are not scaled.

## What it does not say

- Only the known backlog is forecast: features added later are not in it, and bugs are not forecast apart (their cost is in the pace).
- Story points are ordinal, not proportional. A sum of points is a rough size, which is why the finish is also given by number of features. When the two differ a lot, the remaining features are bigger or smaller than the delivered ones.
- With few weeks of history (fewer than 8), a recent pause, or many weeks with nothing delivered, the range is a first impression. The **Read this first** list says which of these apply.
- With no delivery in the window there is no pace: the forecast asks for a window (`--since`) or a pace by hand (`--capacity POINTS_PER_WEEK`) instead of inventing one.
- It is a range under the assumption that the pace continues, not a promise.
