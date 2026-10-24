# Estimating a feature

`feature-plan` asks for the story points of every new feature and suggests a value. The user decides: the suggestion comes first in the question, marked "(Recommended)", and any value on the scale (`1` / `2` / `3` / `5` / `8` / `13`) can be chosen instead.

## The rubric

Start from the reach, then apply the steps that hold.

| Step | Question | Effect |
| --- | --- | --- |
| Reach | How many layers does the mechanism in the technical notes touch (UI, service or API, data)? | One layer: start at `1`. Two or more: start at `3`. |
| Breadth | Does the story hold eight or more acceptance criteria, or three or more independent flows, screens or endpoints? | One step up the scale. |
| Schema | Does it add or change a table, column or access policy? | Single-layer story only: one step up. A full-stack story with a schema change is already a `3`; the step is never added on top of the reach. |
| Novelty | Is a new external integration, subsystem or concept for the project involved? A library added to an established pattern does not count. | One step up. |
| Familiarity | Is it a near copy of an existing feature, with five or fewer acceptance criteria? | One step down. |

A result above `8` is a candidate for splitting into several features.

The scale is ordinal, not proportional. In the backlogs the rubric was tested on, a `5` changed about 25 times the code of a `1`, and a `3` about 6 times. Compare a new story with existing ones; do not add smaller features up. Story points are not hours: the Gantt chart of a project that draws one may assume a conversion (for example 1 point = 1 workday), but that is the project's choice.

## Where it comes from

The factors were tested against the finished backlogs of two projects (147 features with points, with the lines of code each one changed where its branch merge could be found):

- **Held up:** the number of layers touched, a schema change, and the breadth of the acceptance criteria. The number of OpenSpec scenarios and tasks tracked size best, but they only exist after the spec step, so the rubric uses the acceptance criteria as their plan-time stand-in.
- **Did not hold up:** "a new dependency" and the length of the technical notes. They are not in the rubric.
- **Limits:** only `1`, `3` and `5` occurred, so the rubric is untested for the other values. Applied to the old labels it matched about half of them exactly and three quarters within one step; those labels were guesses made at planning time. Treat the suggestion as a starting point.

## Estimation anchors (optional)

`<backlog>/estimation-anchors.md` lists finished features of the project as reference examples of each value, each with the one reason it belongs there. `feature-plan` reads it when it exists, compares the new story with the examples, and names the closest one as the reason for its suggestion. The kit never creates or requires the file. A project writes it once it has finished features to point at, and updates it when a better example turns up. Example:

```markdown
# Estimation anchors

Finished features that show what each value means here. Compare a new story with these.

## 1
- Feature <n> `<change-name>`: <what it touches and how big, e.g. one component, no schema change, 5 acceptance criteria>.

## 3
- Feature <n> `<change-name>`: <e.g. UI, service and a new table with its policies, 7 acceptance criteria>.

## 5
- Feature <n> `<change-name>`: <e.g. several screens and flows across all layers, 11 acceptance criteria>.
```
