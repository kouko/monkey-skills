# Architecture complexity lens

Use this plan-time lens for non-mechanical work that changes boundaries,
dependencies, migrations, configuration, operational duties, reuse, and
deletion. Record the assessment in the plan before execution.

- **Added complexity**: new boundaries, dependencies, transitions, or duties.
- **Why it is worthwhile**: the value that justifies each retained moving part.
- **Removed or avoided complexity**: deletions, reuse, or simpler shapes.
- **Downstream risk**: runtime, operational, or integration burden reaching implementation.

Accept a simpler shape only when it still reaches the brief's required end
state. If it cannot, record the lost outcome as a scope trade-off rather than a
complexity reduction.

Optional upstream evidence may inform the assessment. When upstream evidence is
absent, make the local assessment from the brief and plan. A mechanical edit
may use the `N/A — mechanical edit: <reasoned exemption>` form only when it
adds none of the triggers above.
