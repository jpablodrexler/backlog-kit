<!-- VENDORED from shared/long-runs.md — do not edit here; edit the source and run `python3 tools/vendor.py`. -->
# Long runs

A run that can take more than a few minutes (a test suite, an end-to-end tier, a build) is started, watched and stopped by the **orchestrator**, never owned by a subagent. This file is shared by `feature-development` and `bug-fix`; the phase that runs something long reads it before starting.

Why: a subagent that starts a long job and then reports "waiting on my own background work" has not reported anything. The orchestrator is left with no progress, no result and no signal line, and an hour can pass before anyone notices that the job hung. Output piped through a filter that only prints at the end (`tail`, `head`) hides every sign of life until the process exits. A task-stop tool may stop the wrapper and leave the real process running, holding a port or most of the memory.

## 1. Who runs it

- The orchestrator runs the long command itself, in its own context.
- A subagent may be used for a **bounded** job: read a failure, fix one named test or file, and report. It never owns a run, and a "waiting" message from it is never treated as a result.

## 2. Progress updates

Before the run starts, start a monitor that tells the user how it is going, without being asked:

- **One line per finished unit** (a chunk, a spec file, a build step): its name, its outcome and how long it took.
- **A heartbeat about every 3 minutes**: the unit running now, when its log last changed, free memory, and units done out of total. A heartbeat that does not advance is how a stall shows.
- **A line for every terminal state**: success, failure, timeout, crash, process exit. If the monitor only reports success, silence looks the same as "still running".
- A monitor has a lifetime. When it expires and the run goes on, start it again from the current position so old results are not repeated.
- **The monitor must not get in the run's way.** Do not follow a file the run writes with a reader that keeps it open (`tail -f` and the like): on some systems (Windows) that blocks the run's own writes to the file, which then stays empty and the monitor says nothing while the run is fine. Poll with short reads (open, read the new lines, close) of the file or of the run's own output, and add a stall line when nothing new has arrived for about twice the heartbeat period.
- **Check the monitor before leaving.** Confirm that the first event arrives (the start line is enough) before leaving a long run unattended. A monitor that was never seen to report is the same as no monitor, and the silence it produces is easy to read as progress.

## 3. Run in chunks

- **The default chunk size is 1 spec file.** Split the suite into one chunk per spec (test) file and run **one chunk at a time**, each in a fresh process. It is a default, not a fixed size: the machine's resources change over time (or the machine is replaced), so when the user sets a different size (several files, a folder), use that one instead.
- Give every chunk a **hard timeout** (about 8 minutes) and write its output to a **log file**. Never pipe the output through a filter that prints only at the end.
- Put a **deadline on every wait loop** (waiting for a port, a file, a process). A loop with no deadline is a hang.
- Write down the list of files of each chunk, so a chunk that times out can be rerun exactly.

## 4. Stopping and cleaning up

- On a timeout, or when asked to stop, end the **whole process tree** by its command line (for example `taskkill /T` on Windows, or the process group elsewhere). Stopping the wrapper is not enough.
- Before the next chunk, check that no stale process still holds the test port or a lock.
- After a stop, list what is still running before starting anything else.

## 5. A chunk that crashes or times out

With the default chunk size a chunk is already a single spec file, so rerun that file once in a fresh process. If a larger chunk size is in use, rerun that chunk one file at a time, each in a fresh process. A crash from memory building up usually does not repeat on a single file. Report which files passed and which failed, and name any file that crashed or timed out twice; never report a multi-file chunk as passed or failed as a whole.

## 6. Memory

- Check free memory before each chunk. When it is low, wait (within a deadline) or say so, and never start a chunk that is likely to be killed.
- When a local container runtime or database stack was started for an earlier tier, stop it once that tier is done and before the browser tiers, and say that you did.
- If the test runner has options that cut its memory use (a lighter browser, fewer results kept in memory), take them from the project's docs or ask once. Never hardcode them in a command the project did not choose.

## 7. What to record

For the Final Summary: how the run was split, any chunk that timed out or crashed and how it was rerun, any file that was skipped and by whose decision, and what was not run at all. A skipped part is a deviation to name, never a pass.
