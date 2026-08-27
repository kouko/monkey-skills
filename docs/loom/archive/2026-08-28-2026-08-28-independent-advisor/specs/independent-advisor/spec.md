## ADDED Requirements

### Requirement: REQ-1 — mode determination bound to a citable fact
The system MUST determine the consultation mode from a citable fact and record that fact verbatim as `mode_basis` alongside the mode.

#### Scenario: implemented commit on the branch
- GIVEN a target branch that carries an already-implemented commit
- WHEN the system determines the mode
- THEN it records `mode` and a `mode_basis` that quotes the commit identifier rather than a paraphrase of the project stage

#### Scenario: approved brief with no implementation
- GIVEN an approved brief and no implementing commit
- WHEN the system determines the mode
- THEN it records the brief approval as `mode_basis` and a mode consistent with an open solution space

#### Scenario: no citable fact is available
- GIVEN no commit, PR, brief state, or user phrasing that can be quoted
- WHEN the system determines the mode
- THEN it does not synthesise a basis and instead asks the user for the mode

#### Scenario: conflicting bases
- GIVEN two mode-relevant facts that point to different modes
- WHEN the system determines the mode
- THEN it records both facts and surfaces the conflict at the user checkpoint instead of silently choosing one

### Requirement: REQ-2 — user override of mode preserves the original basis
The system MUST let the user override the determined mode, and it MUST NOT erase the original `mode_basis` when an override is recorded.

#### Scenario: user overrides the determined mode
- GIVEN a request whose `mode` was determined from a citable fact
- WHEN the user specifies a different mode
- THEN `mode` equals the user's value, `mode_override` is true, and the original `mode_basis` is still readable

### Requirement: REQ-3 — statically failing executors never appear as options
The system MUST exclude any candidate executor whose static check did not pass from the options presented to the user.

#### Scenario: missing binary
- GIVEN a candidate executor whose binary is absent from the host
- WHEN the system builds the option list for the checkpoint
- THEN that executor is absent from the list and the user is never asked about it

#### Scenario: missing credential file
- GIVEN a candidate executor whose credential file is absent
- WHEN the system builds the option list
- THEN that executor is excluded and its exclusion reason is distinguishable from a missing binary

#### Scenario: user names an excluded executor
- GIVEN an executor that failed the static check
- WHEN the user asks for it at the checkpoint
- THEN the system refuses to add it and states the exclusion reason

### Requirement: REQ-4 — static pass is not a verification claim
The system MUST treat a passing static check only as permission to attempt a live probe, and MUST NOT report it downstream as a verified capability.

#### Scenario: static pass reported at the checkpoint
- GIVEN an executor whose static check passed and which has not been probed
- WHEN the checkpoint presents it
- THEN it is labelled as statically available and not yet verified

### Requirement: REQ-5 — live probes run only after user selection
The system MUST run a live probe for an executor only after the user has selected that executor at the checkpoint.

#### Scenario: candidate not selected
- GIVEN a statically available executor the user did not select
- WHEN the request proceeds past the checkpoint
- THEN no live probe is issued for that executor and no probe cost is incurred for it

#### Scenario: user cancels at the checkpoint
- GIVEN a checkpoint awaiting the user's decision
- WHEN the user cancels
- THEN no live probe runs and `actual_cost` is zero

### Requirement: REQ-6 — probe outcome is taken from the probe command's own exit status
The system MUST derive a probe's success or failure from the exit status of the probe invocation itself, and MUST NOT let a surrounding pipeline's exit status determine it.

#### Scenario: probe output passed through a pipeline
- GIVEN a probe invocation whose output is piped to another command
- WHEN the probe process exits non-zero while the pipeline's last stage exits zero
- THEN the probe is recorded as failed

#### Scenario: probe never returns
- GIVEN a probe invocation that does not terminate on its own
- WHEN the invocation is still running past its bound
- THEN it is converged into a recorded failure rather than waited on indefinitely

### Requirement: REQ-7 — a probe passes only with both verified model and verified effort
The system MUST NOT record a probe as passed unless both `verified_model` and `verified_effort` were obtained from the probe response.

#### Scenario: model obtained but effort missing
- GIVEN a probe that exits zero and reports a model but no reasoning effort
- WHEN the probe result is recorded
- THEN it is not `pass`, and the missing value is reported

#### Scenario: response carries no tier fields at all
- GIVEN a probe response that looks well-formed but exposes neither model nor effort
- WHEN the probe result is recorded
- THEN the executor is treated as unverified

### Requirement: REQ-8 — frontier requests fail loud and are never auto-downgraded
The system MUST fail loud with the concrete failure reason when a `frontier` cost tier was requested and the probe failed or verified a lower tier, and it MUST NOT substitute a lower tier without explicit user confirmation obtained after that failure is surfaced.

#### Scenario: frontier probe fails
- GIVEN a leg requesting the `frontier` cost tier
- WHEN its probe fails
- THEN the failure and its reason are surfaced to the user and no lower-tier executor is dispatched in its place

#### Scenario: frontier probe verifies a lower tier
- GIVEN a leg requesting the `frontier` cost tier
- WHEN the probe exits zero but the verified tier is lower
- THEN the mismatch is surfaced naming which of cost tier or effort tier fell short, and dispatch does not proceed on the lower tier

#### Scenario: user confirms a downgrade after fail loud
- GIVEN a frontier failure that has been surfaced to the user
- WHEN the user explicitly approves a lower-tier fallback executor
- THEN the fallback is dispatched and the downgrade is recorded

#### Scenario: non-frontier tier mismatch
- GIVEN a leg requesting a non-frontier cost tier
- WHEN the probe verifies a lower tier
- THEN the request returns to the checkpoint for the user to re-decide rather than continuing automatically

### Requirement: REQ-9 — one checkpoint presents leg count, executors and estimated cost together
The system MUST present the mode, its basis, the leg count, the executor for each leg, and the estimated cost in a single user checkpoint before any spend occurs.

#### Scenario: checkpoint is presented
- GIVEN a request whose dispatch packet is complete
- WHEN the system reaches the checkpoint
- THEN one question presents mode, `mode_basis`, leg count, per-leg executors, and estimated cost together

#### Scenario: split questioning
- GIVEN a request at the checkpoint
- WHEN leg count and executors would be asked in two separate questions
- THEN that is rejected and the values are asked together

#### Scenario: dispatch without approval
- GIVEN a request awaiting the checkpoint decision
- WHEN dispatch is attempted without a recorded user confirmation
- THEN the dispatch is refused

#### Scenario: partial answer
- GIVEN a checkpoint where the user answered the leg count but not the executors
- WHEN the system processes the answer
- THEN it asks for the missing item and does not fill it with a default

#### Scenario: executor set changed
- GIVEN a user who changes the executor set at the checkpoint
- WHEN the checkpoint is re-presented
- THEN static detection and the cost estimate are recomputed rather than carried over

### Requirement: REQ-10 — the proposer leg never sees the incumbent solution
The system MUST restrict a `proposer` leg's input to the problem, constraints and rejected options, and MUST abort that leg without remedy if its input contains any description of the incumbent solution.

#### Scenario: packet leaks the incumbent
- GIVEN a dispatch packet containing the incumbent proposal
- WHEN it is dispatched to a `proposer` leg
- THEN that leg is aborted and its output is not used

#### Scenario: retry after an empty output
- GIVEN a `proposer` leg being retried after an empty output
- WHEN the retry input is assembled
- THEN it contains no incumbent description and no prior challenger output

### Requirement: REQ-11 — blind judging requires anonymisation and structural order counterbalancing as two separate controls
The system MUST withhold card origin from the blind-judging leg AND MUST cover each explore-mode card pair by two swap runs in opposite presentation orders; a prompt instruction about order MUST NOT substitute for the second run.

#### Scenario: origin withheld
- GIVEN a pair of normalised cards
- WHEN they are submitted to the blind-judging leg
- THEN neither card carries its origin, nor register, length, or person-reference residue that identifies the incumbent

#### Scenario: only one swap run has a verdict
- GIVEN a card pair with a verdict for the forward-order run only
- WHEN the pair is evaluated for completion
- THEN it is not treated as verdicted

#### Scenario: prompt reminder instead of a second run
- GIVEN a card pair judged once with a prompt instruction to ignore order
- WHEN the pair is evaluated for completion
- THEN the reminder does not satisfy order counterbalancing

#### Scenario: anonymisation without counterbalancing
- GIVEN an anonymised card pair judged in a single order
- WHEN the pair is evaluated for completion
- THEN it is rejected

#### Scenario: counterbalancing without anonymisation
- GIVEN a card pair judged in both orders with origins visible
- WHEN the pair is evaluated for completion
- THEN it is rejected

#### Scenario: judge learns who the incumbent is
- GIVEN a blind-judging leg that received the incumbent's identity
- WHEN its verdicts are collected
- THEN those verdicts are voided

#### Scenario: the two swap runs disagree
- GIVEN two swap runs of the same pair that reach opposite conclusions
- WHEN the report is produced
- THEN the outcome is recorded as inconclusive rather than one run being selected

#### Scenario: de-anonymisation before all verdicts
- GIVEN a card pair with an outstanding swap run
- WHEN de-anonymisation is attempted
- THEN it is refused until every scheduled swap run has a verdict

### Requirement: REQ-12 — audit mode runs no proposer leg
The system MUST NOT dispatch a `proposer` leg when the mode is `audit`.

#### Scenario: audit mode dispatch
- GIVEN a request with `mode=audit`
- WHEN legs are dispatched
- THEN a single leg with full context runs and no blind proposal leg is dispatched

### Requirement: REQ-13 — leg output passes a mechanical shape contract before entering the report
The system MUST validate every leg's output mechanically — non-empty, not a refusal, all template fields present, and not a restatement of its own input — before that output is used in the report; a leg's own claim of completion MUST NOT satisfy this.

#### Scenario: empty output
- GIVEN a leg that returned no content
- WHEN the output is validated
- THEN it fails and is not written into the report

#### Scenario: refusal
- GIVEN a leg that returned a policy refusal
- WHEN the output is validated
- THEN it fails the contract

#### Scenario: missing template field
- GIVEN a leg output missing one of the four template fields
- WHEN the output is validated
- THEN it fails and is not retried blind

#### Scenario: output restates the input
- GIVEN a leg output that reproduces its input without new content
- WHEN the output is validated
- THEN it fails the contract

#### Scenario: claim without a checkable basis
- GIVEN a shape-valid output whose claims cite a path that does not exist
- WHEN the output is validated
- THEN it is recorded as a fabrication suspect, listed item by item, and never silently accepted

#### Scenario: conclusion without reasoning trace
- GIVEN a leg output containing conclusions and no reasoning trace
- WHEN the output is validated
- THEN it fails the contract

### Requirement: REQ-14 — degraded or failed legs are disclosed in the report
The system MUST list every degraded or failed leg in the report and MUST NOT present a run as having completed more legs than actually produced usable output.

#### Scenario: one leg aborted
- GIVEN a three-leg run in which one leg aborted
- WHEN the report is produced
- THEN the aborted leg appears in `degraded_legs` with its failure attribution

#### Scenario: all legs failed
- GIVEN a run in which no leg produced usable output
- WHEN the report is produced
- THEN a failure report is produced listing each leg's failure attribution, rather than an empty report

#### Scenario: unverified leg output used
- GIVEN a leg dispatched without a live probe
- WHEN its output is written into the report
- THEN the report marks that leg's tier as having no verification evidence

#### Scenario: several independent defects on one leg
- GIVEN a leg with both a tier mismatch and a fabrication suspicion
- WHEN the report is produced
- THEN the two defects are listed separately rather than merged into one statement

### Requirement: REQ-15 — agreement across legs is not presented as a strong signal
The system MUST record only which legs raised a finding in `corroborated_by`, MUST NOT derive increased credibility from that count, and MUST NOT use the number of legs mentioning a finding as an input to `confidence`.

#### Scenario: two legs raise the same finding
- GIVEN a finding raised by two legs
- WHEN the report is produced
- THEN `corroborated_by` lists the legs without any claim that the finding is therefore more credible

#### Scenario: confidence assignment
- GIVEN a finding raised by multiple legs
- WHEN `confidence` is assigned
- THEN the mention count is not an input to it

#### Scenario: standing weakness note
- GIVEN any delivered report
- WHEN `known_weaknesses` is read
- THEN it states that anonymisation and order counterbalancing remove relative preference differences between reviewers but cannot detect blind spots shared by all reviewers

### Requirement: REQ-16 — no completeness wording in the report
The system MUST NOT use "complete", "comprehensive", "exhaustive" or equivalent coverage claims anywhere in the report, and MUST include a coverage disclaimer.

#### Scenario: report is scanned for coverage claims
- GIVEN a generated report
- WHEN it is scanned for completeness wording
- THEN no such wording is present

#### Scenario: disclaimer missing
- GIVEN a report without `coverage_disclaimer`
- WHEN it is validated for delivery
- THEN delivery is refused

### Requirement: REQ-17 — actual cost is reported truthfully [deferred]
The system MUST record in `actual_cost` the spend that actually occurred, including probe cost already paid for legs that later failed or were cancelled, and MUST NOT backfill it with the estimate.

#### Scenario: probe paid then user cancels
- GIVEN a probe that was paid for before the user cancelled the request
- WHEN the run's cost is recorded
- THEN the paid probe cost is included and not zeroed

#### Scenario: early stop saves spend
- GIVEN a run that stopped early and spent less than estimated
- WHEN `actual_cost` is recorded
- THEN it reflects the spend that occurred, not the estimate

#### Scenario: rescoped rerun
- GIVEN a delivered report and a user request to rerun with a new scope
- WHEN the rerun starts
- THEN a new request is created linked by `rerun_of` and the original report and its cost are left unchanged

### Requirement: REQ-18 — early stop degrades to a single leg after normalisation
The system MUST skip blind review and degrade to a single leg when the challenger and incumbent cards are substantially identical, and this determination MUST be made only after both cards have been normalised into the same template.

#### Scenario: cards are substantially identical
- GIVEN two normalised cards judged substantially identical
- WHEN the run continues
- THEN blind review is skipped, `early_stopped` is true, and the run reports a single leg

#### Scenario: early stop claimed before normalisation
- GIVEN two cards that have not been normalised
- WHEN an early stop is attempted
- THEN it is refused

#### Scenario: report after early stop
- GIVEN a run that stopped early
- WHEN the report is produced
- THEN `leg_count` and `early_stopped` reflect the degraded run rather than the originally planned leg count

### Requirement: REQ-19 — the dispatch packet is complete before dispatch
The system MUST hold a request before dispatch until the decision statement, rejected options, evidence paths, and incumbent proposal are all present, naming any missing section rather than filling it.

#### Scenario: one section missing
- GIVEN a packet whose evidence paths are absent
- WHEN the request is evaluated for dispatch
- THEN it is held, the missing section is named, and no empty placeholder is substituted

#### Scenario: no rejected options exist
- GIVEN a decision with no previously rejected options
- WHEN the packet is assembled
- THEN the rejected-options section is present and explicitly marked empty

#### Scenario: evidence path unreadable by the executor
- GIVEN an evidence path the external executor cannot read
- WHEN the packet is validated before dispatch
- THEN that section is treated as missing

#### Scenario: packet cannot be completed
- GIVEN a packet that cannot be completed with available material
- WHEN the user is informed
- THEN the gap is stated, the run ends without entering any spending path, and the partial packet is retained

### Requirement: REQ-20 — no usable external executor means the run stops rather than self-reviewing
The system MUST end the run and state that the precondition failed when no external executor passes static detection, and MUST NOT substitute a same-host self-review presented as an independent opinion.

#### Scenario: candidate set is empty
- GIVEN no executor that passes static detection
- WHEN the run reaches the checkpoint stage
- THEN the run ends with each executor's exclusion reason stated and no leg is dispatched

#### Scenario: only same-family executors are available
- GIVEN candidates that are all from the same model family as the controller
- WHEN the checkpoint is presented
- THEN the user is told that same-family review amplifies shared blind spots and decides whether to proceed

### Requirement: REQ-21 — the verified executor is the dispatched executor
The system MUST dispatch a leg to the same executor binding that its probe verified.

#### Scenario: alias swapped after verification
- GIVEN a probe that verified one model alias
- WHEN dispatch would use a different alias
- THEN the dispatch is refused

#### Scenario: judge and proposer are the same executor
- GIVEN a run where the blind-judging leg and the proposer leg would use the same executor
- WHEN legs are assigned
- THEN the assignment is refused

#### Scenario: swap runs judged with different settings
- GIVEN two swap runs of a pair executed with different effort settings
- WHEN the verdicts are collected
- THEN they are rejected as not judged by the same measure

### Requirement: REQ-22 — probes run without write access
The system MUST invoke live probes in a read-only mode with no write capability.

#### Scenario: probe invocation is assembled
- GIVEN an executor selected for probing
- WHEN the probe command is assembled
- THEN it grants no write access to the host

### Requirement: REQ-23 — normalisation preserves the claims it compresses
The system MUST limit normalisation to compressing both proposals into the shared template, and MUST NOT let the normaliser rewrite the substance of either proposal.

#### Scenario: normaliser alters a claim
- GIVEN a normaliser leg whose output changes a proposal's core claim
- WHEN the output is validated
- THEN it is rejected

#### Scenario: normaliser authored the incumbent
- GIVEN a normaliser that is also the incumbent's author
- WHEN the report is produced
- THEN `normalized_by_is_incumbent_author` is disclosed in the report as-is

#### Scenario: cards differ greatly in length
- GIVEN two cards of very different length after drafting
- WHEN normalisation completes
- THEN the cards are compressed to comparable length before anonymisation

### Requirement: REQ-24 — the report is a read-only record centred on divergence points
The system MUST present divergence points as the body of the report and MUST NOT alter `verdict`, `findings` or `actual_cost` when the user adopts, rejects or defers an item.

#### Scenario: user adopts a divergence point
- GIVEN a delivered report
- WHEN the user adopts one divergence point
- THEN only that item's resolution status changes and the verdict, findings and cost are unchanged

#### Scenario: no divergence points found
- GIVEN a run that produced no divergence point
- WHEN the report is produced
- THEN a verdict of inconclusive stands without requiring any finding

#### Scenario: user asks for the target to be changed
- GIVEN a delivered report the user wants acted on
- WHEN the user asks for the target to be modified
- THEN the system states this is outside the consultation's scope and does not modify the target

### Requirement: REQ-25 — cancellation stops in-flight legs and outranks a degrade offer [deferred]
The system MUST abort in-flight legs when the request is cancelled, MUST NOT ask the user to approve a downgrade after cancellation, and MUST still record the probe cost already paid.

#### Scenario: cancellation with a leg still running
- GIVEN a cancelled request with a dispatched leg still running
- WHEN the cancellation is processed
- THEN the leg is aborted and the already-paid probe cost is recorded

#### Scenario: cancellation while a downgrade is pending
- GIVEN a pending downgrade proposal and a cancelled request
- WHEN the cancellation is processed
- THEN the downgrade is not put to the user

#### Scenario: early stop while a downgrade is pending for the judging leg
- GIVEN an early-stopped card pair and a pending downgrade for the blind-judging leg
- WHEN the run continues
- THEN the downgrade proposal is withdrawn rather than put to the user

### Requirement: REQ-26 — a leg abort invalidates the swap runs it was serving [deferred]
The system MUST mark a swap run without a verdict when the leg serving it aborts, MUST return the pair to the sequenced state rather than completing it from one side, and MUST re-run the pair as a whole if a replacement executor is approved.

#### Scenario: judging leg aborts mid-pair
- GIVEN a pair under blind review whose judging leg aborts
- WHEN the pair's state is updated
- THEN the affected swap run is marked as having no verdict and the pair is not treated as verdicted

#### Scenario: replacement executor approved
- GIVEN a pair whose judging leg was replaced by an approved fallback executor
- WHEN judging resumes
- THEN both swap runs are re-run by the replacement rather than mixing verdicts from two executors

#### Scenario: leg aborts before anonymisation
- GIVEN a normalised card whose leg aborted before anonymisation
- WHEN the run's state is updated
- THEN the card remains normalised and does not proceed partially anonymised

### Requirement: REQ-27 — the checkpoint discloses what leaves the machine and to whom
The system MUST name, at the single checkpoint and for each leg, the external vendor that will receive material and MUST enumerate the categories of local material that will leave the host, and it MUST NOT dispatch until the user has acknowledged that transfer.

#### Scenario: checkpoint names vendor and egress categories
- GIVEN a request at the checkpoint with one or more legs bound to external executors
- WHEN the checkpoint question is assembled
- THEN it names the receiving vendor per leg and lists the packet sections and the file paths the executor will be authorised to read

#### Scenario: approval covers cost only
- GIVEN a checkpoint answer that approves the estimated cost without acknowledging the transfer
- WHEN dispatch is attempted
- THEN dispatch is refused and the transfer acknowledgement is requested

#### Scenario: cancellation after a transfer already happened
- GIVEN a request cancelled after at least one external invocation
- WHEN the cancellation outcome is reported
- THEN it states that material already transmitted to that vendor cannot be recalled

### Requirement: REQ-28 — every leg carries a stated permission boundary, not only probes [deferred]
The system MUST assemble each leg invocation with no write access, with the executor's readable paths bounded by the request's `scope_boundary`, and with the outbound network capability the executor retains stated; it MUST NOT dispatch a leg whose write-access control is unavailable without surfacing that absence at the checkpoint.

#### Scenario: leg invocation is assembled
- GIVEN a leg about to be dispatched to an external executor
- WHEN the invocation is assembled
- THEN it grants no write access, confines readable paths to `scope_boundary`, and records the retained outbound network capability

#### Scenario: no read-only mode exists for an executor
- GIVEN an executor for which no read-only invocation mode is available on this host
- WHEN a probe or leg would be dispatched to it
- THEN the absence of the control is surfaced at the checkpoint and the run does not proceed on an unstated assumption

#### Scenario: unbounded leg invocation
- GIVEN a leg invocation whose readable set is not bounded to the declared evidence paths
- WHEN it is validated before dispatch
- THEN it is refused

### Requirement: REQ-29 — the dispatch packet is scanned for credential-shaped content before it leaves the host [deferred]
The system MUST mechanically scan the dispatch packet and the file contents its evidence paths resolve to for credential-shaped and personal-data-shaped content before dispatch, MUST block dispatch on a hit, and MUST NOT echo the matched value.

#### Scenario: a credential is reachable from the packet
- GIVEN a packet whose decision statement, incumbent proposal, or a file reachable from its evidence paths contains a credential-shaped secret
- WHEN the packet is validated before dispatch
- THEN dispatch is refused, the offending location is named without reproducing the secret value, and the scan result is recorded on the request

#### Scenario: static credential detection
- GIVEN a static check for an executor's credential file
- WHEN it runs
- THEN it tests existence only and does not read, log, or echo the file's contents

### Requirement: REQ-30 — external output is handled as data, never as instructions [deferred]
The system MUST treat every leg output and normalised card as untrusted content, MUST NOT let any imperative text inside it change the run's mode, scope boundary, executor binding, anonymisation state, or evidence paths, and MUST record the attempt in the report.

#### Scenario: output addresses the controller
- GIVEN a leg output containing imperative text addressed to the controlling agent
- WHEN the output is ingested
- THEN no instruction inside it takes effect and the attempt is recorded in the report

#### Scenario: instruction embedded in reviewed material
- GIVEN reviewed material containing text shaped as instructions that an executor reproduced into its card
- WHEN the card is ingested
- THEN it is handled as reviewed content only

### Requirement: REQ-31 — cancellation and timeout terminate the spawned processes [deferred]
The system MUST terminate every process it spawned, and its process group, when a run is cancelled, times out, or the controller exits, MUST confirm termination before recording a leg as `Aborted`, and MUST NOT leave an external executor running after the run has ended.

#### Scenario: cancellation with a child still running
- GIVEN a dispatched leg whose external CLI process is still running
- WHEN the request is cancelled
- THEN the process is signalled, its termination is confirmed within the run's stated bound, escalated if it does not exit, and the leg is not recorded as `Aborted` until termination is confirmed

#### Scenario: retry after a timeout
- GIVEN a leg attempt that exceeded its timeout
- WHEN a retry is dispatched
- THEN the prior attempt is confirmed terminated first and any output it later produces is discarded rather than merged

#### Scenario: controller exits unexpectedly
- GIVEN spawned executor processes and a controlling session that ended without processing a cancellation
- WHEN the next run starts
- THEN the orphaned processes are detected and reported rather than left running unrecorded

### Requirement: REQ-32 — a durable per-run record answers what was sent, approved, and paid [deferred]
The system MUST maintain an append-only per-run record that is readable without re-running anything, covering the approving actor, the approval timestamp, the vendor and model binding, the packet sections sent, the paths the executor was authorised to read, exit status, and the cost incurred per attempt.

#### Scenario: the user asks what left the machine
- GIVEN any completed, failed, or cancelled run
- WHEN the record is read
- THEN it yields the timestamp, vendor and model binding, packet sections sent, authorised read paths, exit status, and cost, without re-running anything

#### Scenario: run interrupted by controller termination
- GIVEN a run interrupted while legs were in flight
- WHEN the user next asks about that consultation
- THEN the dispatched legs, their process identifiers, and the spend incurred so far are recoverable from the record

#### Scenario: early stop still records egress
- GIVEN a run that early-stopped after normalisation by an external executor
- WHEN the record is produced
- THEN it lists the material already transmitted to that executor even though the blind-review stage never ran

### Requirement: REQ-33 — every leg runs under a declared timeout bound [deferred]
The system MUST declare a per-leg timeout for the run, MUST terminate a leg that exceeds it, and MUST record the outcome as `FailedTimeout` with the elapsed time rather than waiting without bound.

#### Scenario: a leg produces no output
- GIVEN a dispatched leg that produces no output
- WHEN its elapsed time exceeds the run's declared per-leg timeout
- THEN the leg is terminated, recorded as `FailedTimeout` with the elapsed time, and the run proceeds down the degraded path

#### Scenario: timeout not declared
- GIVEN a run whose per-leg timeout has not been declared
- WHEN dispatch is attempted
- THEN dispatch is refused rather than proceeding without a bound

### Requirement: REQ-34 — approval has a stated scope and a spend ceiling [deferred]
The system MUST state in the approval record whether retries, the second swap run, downgrade re-dispatches, and re-probes are covered, MUST halt and return to the checkpoint before any invocation that is not covered or that would carry cumulative spend past the approved ceiling, and MUST express estimated and actual cost in a stated unit.

#### Scenario: an invocation beyond the approved set
- GIVEN a recorded approval and an additional external invocation that the approval does not cover
- WHEN that invocation would be dispatched
- THEN the run returns to the checkpoint before spending

#### Scenario: spend passes the approved ceiling
- GIVEN a run whose cumulative actual spend reaches the approved ceiling
- WHEN the next leg would be dispatched
- THEN the run halts and both the estimate and the actual figure are shown to the user in the stated unit

### Requirement: REQ-35 — a repository or organisation declaration can forbid or restrict external dispatch [deferred]
The system MUST honour a declaration in the working repository that forbids external dispatch or that names an allowed vendor list, refusing or restricting candidates before the checkpoint is presented and citing the declaration.

#### Scenario: dispatch declared disallowed
- GIVEN a repository that declares external-model dispatch as disallowed
- WHEN the system is invoked in that repository
- THEN it refuses to dispatch, cites the declaration, and presents no checkpoint

#### Scenario: allowed-vendor list declared
- GIVEN a repository that declares an allowed-vendor list
- WHEN the candidate set is built
- THEN candidates outside the list are excluded with the declaration cited as the reason

### Requirement: REQ-36 — a run with no interactive channel spends nothing [deferred]
The system MUST end a run without dispatching when no interactive channel exists to present the checkpoint, and MUST state that the checkpoint precondition could not be satisfied.

#### Scenario: headless or scheduled invocation
- GIVEN an invocation with no interactive channel able to answer the checkpoint
- WHEN the run reaches the checkpoint
- THEN no spend occurs and the run ends stating that the checkpoint precondition cannot be satisfied

#### Scenario: checkpoint left unanswered
- GIVEN a checkpoint the user leaves unanswered
- WHEN the request is later resumed
- THEN it is still awaiting the checkpoint with no spend incurred, and static detection and the cost estimate are recomputed before the checkpoint is re-presented

### Requirement: REQ-37 — the target is pinned and its drift is surfaced [deferred]
The system MUST pin the target revision when the dispatch packet is frozen and MUST state that revision in the report, flagging that the target changed if it did rather than presenting findings as current.

#### Scenario: target changes during the run
- GIVEN a target pinned at packet freeze whose branch or files changed before delivery
- WHEN the report is produced
- THEN the report states the pinned revision and flags that the target moved during the run

#### Scenario: unresolved prior report on the same target
- GIVEN a delivered report on a target the user has not yet adopted, rejected, or deferred
- WHEN a new consultation on the same target is requested
- THEN the prior report is linked and its unresolved status is surfaced before any spend

### Requirement: REQ-38 — the executor's own execution environment is confined and recorded [deferred]
The system MUST run a `proposer` leg from a location from which the incumbent material is unreadable, MUST record which environment files the external executor loaded (project instructions, hooks, skills, MCP servers), and MUST NOT pass credentials belonging to other vendors into the child process environment.

#### Scenario: proposer leg started in the incumbent's working directory
- GIVEN a `proposer` leg whose working directory would contain the incumbent plan
- WHEN the leg's execution environment is prepared
- THEN the leg is confined to a location from which the incumbent material is unreadable

#### Scenario: environment files loaded by the executor
- GIVEN an external executor that loads project instructions, hooks, skills, or MCP servers from the working directory
- WHEN the leg completes
- THEN the run records which of those were loaded

#### Scenario: child process environment assembled
- GIVEN a leg invocation
- WHEN the child process environment is assembled
- THEN it carries only the variables that executor needs and credentials belonging to other vendors are not inherited

### Requirement: REQ-39 — the reversed swap run carries no state from the forward run
The system MUST dispatch the reversed-order swap run in a fresh executor process with no transcript, session, or cache carried from the forward run, and MUST record that isolation.

#### Scenario: reversed run dispatched
- GIVEN a card pair scheduled for two swap runs
- WHEN the reversed-order run is dispatched
- THEN it runs in a fresh executor process with no state carried from the forward run and the isolation is recorded

#### Scenario: one session reused for both orders
- GIVEN a pair whose two swap runs were executed in one executor session
- WHEN the verdicts are collected
- THEN they are rejected as not counterbalanced

### Requirement: REQ-40 — a missing pipeline stage is not reported as a degraded comparison [deferred]
The system MUST state which stage failures a run can survive, MUST report an inconclusive verdict when the blind-judging stage produced no verdict, and MUST NOT present a run that made no comparison as a degraded multi-leg comparison.

#### Scenario: judging leg aborted after proposer and normaliser succeeded
- GIVEN a run where the proposer and normaliser succeeded and the blind-judging leg aborted
- WHEN the report is produced
- THEN the verdict is inconclusive, the report states that no comparison was made, and the run is not presented as a degraded three-leg comparison

#### Scenario: leg count reported after a stage failure
- GIVEN a run that lost one pipeline stage
- WHEN the report states its leg count
- THEN it names which stage is absent rather than counting the legs as interchangeable contributors

### Requirement: REQ-41 — verification evidence expires and is re-checked before dispatch [deferred]
The system MUST treat a probe result as stale once its declared freshness bound has passed, or once a quota or credential failure has been observed on any leg of that executor, and MUST re-verify or return to the checkpoint rather than dispatching on the old evidence.

#### Scenario: dispatch past the freshness bound
- GIVEN a probe that verified an executor
- WHEN dispatch occurs after the verification's declared freshness bound
- THEN the executor is re-verified or the run returns to the checkpoint

#### Scenario: quota failure observed on a sibling leg
- GIVEN a quota failure observed on one leg of an executor
- WHEN another leg of that same executor is pending
- THEN it is held and the exhaustion is surfaced once rather than dispatched on the earlier verification

### Requirement: REQ-42 — concurrent consultations are isolated or refused [deferred]
The system MUST either refuse or queue a second consultation started while a run has legs in flight, stating the reason, or isolate the second run's workspace and cost ledger, and it MUST NOT attribute one request's spend or failure to another.

#### Scenario: second consultation while legs are in flight
- GIVEN a request with legs in flight
- WHEN the user initiates a second consultation
- THEN the system refuses or queues it with the reason stated, or isolates its workspace and cost ledger from the first

#### Scenario: quota exhausted by the other run
- GIVEN two concurrent runs sharing a vendor account
- WHEN one run exhausts the quota and the other's leg fails
- THEN the failure is not attributed to the other run's executor as its own defect

### Requirement: REQ-43 — a decision with no incumbent yet is distinct from an incomplete packet
The system MUST record the incumbent section as not yet existing when the decision has no incumbent proposal at all, MUST distinguish that from missing material, and MUST NOT hold such a request as an incomplete packet.

#### Scenario: exploratory request with no incumbent
- GIVEN a request whose decision has no incumbent proposal at all
- WHEN the dispatch packet is assembled
- THEN the incumbent section is recorded as not yet existing and the run either proceeds as a single blind-proposal run or states that this consultation shape does not apply

#### Scenario: incumbent exists but was not written down
- GIVEN a decision with an incumbent proposal that the user has not supplied
- WHEN the packet is assembled
- THEN it is held as incomplete and the missing section is named, distinct from the not-yet-existing case

### Requirement: REQ-44 — a single available executor surfaces the distinct-executor conflict
The system MUST surface at the checkpoint the conflict between the distinct-executor rule and an explore-mode run when exactly one external executor passes static detection, and MUST NOT assign the same executor to the proposer and blind-judging legs.

#### Scenario: exactly one executor passes static detection
- GIVEN exactly one external executor that passes static detection
- WHEN an explore-mode run assigns the proposer and blind-judging legs
- THEN the conflict is surfaced at the checkpoint with the available degraded options and the same executor is not silently assigned to both

### Requirement: REQ-45 — an unusable candidate is excluded with a distinguishable reason
The system MUST exclude a candidate whose binary exists but is not executable, or whose credential file exists but is unreadable, empty, or malformed, with an exclusion reason distinguishable from both a missing binary and a missing credential file.

#### Scenario: binary present but not executable
- GIVEN a candidate whose binary exists on the host but is not executable
- WHEN the option list is built
- THEN the candidate is excluded with a reason distinguishable from a missing binary

#### Scenario: credential file present but unusable
- GIVEN a candidate whose credential file exists but is unreadable, empty, or malformed
- WHEN the option list is built
- THEN the candidate is excluded with a reason distinguishable from a missing credential file

### Requirement: REQ-46 — oversize input and oversize output are attributed as size failures [deferred]
The system MUST record a dispatch packet that exceeds the executor invocation's input bound as an input-size failure distinct from an executor failure, MUST NOT retry it unchanged, MUST NOT send a silently truncated packet, and MUST record an oversize leg output as an oversize failure distinct from a shape failure.

#### Scenario: packet exceeds the invocation bound
- GIVEN a dispatch packet that exceeds the executor invocation's input bound
- WHEN dispatch is attempted
- THEN it is recorded as an input-size failure, it is not retried unchanged, and no truncated packet is sent

#### Scenario: leg output exceeds the stated bound
- GIVEN a leg output exceeding the run's stated output size bound
- WHEN it is read
- THEN it is recorded as oversize with that attribution rather than as a shape-contract failure

### Requirement: REQ-47 — an unavailable cost estimate is shown as unknown, never as zero
The system MUST present an estimate that cannot be computed as unknown with its reason, and MUST keep a zero estimate distinguishable from an unavailable one.

#### Scenario: executor whose cost cannot be estimated
- GIVEN an executor whose cost cannot be estimated
- WHEN the checkpoint is presented
- THEN the estimate is shown as unknown with the reason rather than as zero or omitted

#### Scenario: genuinely zero-cost executor
- GIVEN an executor whose cost is genuinely zero
- WHEN the checkpoint is presented
- THEN that zero is distinguishable from an unavailable estimate

### Requirement: REQ-48 — the external CLI is invoked as an argument vector without shell interpretation [deferred]
The system MUST invoke external executors as an argument vector without shell interpretation, and MUST NOT expand packet text as shell syntax.

#### Scenario: packet contains shell metacharacters
- GIVEN a dispatch packet containing shell metacharacters or quote sequences
- WHEN the external CLI is invoked
- THEN the invocation is made as an argument vector and the packet text is never expanded as shell syntax

### Requirement: REQ-49 — a retried leg reuses its original input and accumulates its cost [deferred]
The system MUST assemble a leg retry from input byte-identical to the original dispatch input and MUST accumulate every attempt's incurred cost into `actual_cost`.

#### Scenario: leg retried after a transport failure
- GIVEN a leg retried after a transport failure
- WHEN the retry input is assembled
- THEN it is byte-identical to the original dispatch input

#### Scenario: cost of failed attempts
- GIVEN a leg that failed twice before succeeding
- WHEN `actual_cost` is recorded
- THEN the cost incurred by every attempt is included

### Requirement: REQ-50 — the audit entry is written before the dispatch it describes [deferred]
The system MUST persist a dispatch-intent entry — vendor, model binding, the packet sections to be sent, the authorised read paths, and the child process identifier — before the child process is spawned, and MUST refuse the dispatch when that write fails.

#### Scenario: controller terminated between spawn and record
- GIVEN a leg whose dispatch-intent entry is persisted before the child process is spawned
- WHEN the controller is terminated immediately after the spawn
- THEN the record already names the vendor, the packet sections, the authorised paths, and the child identifier

#### Scenario: the per-run record cannot be written
- GIVEN a run whose per-run record cannot be written
- WHEN a leg would be dispatched
- THEN dispatch is refused and the write failure is surfaced rather than spending with no record

### Requirement: REQ-51 — concurrent appends to the run record stay individually readable [deferred]
The system MUST keep each appended entry individually parseable when two consultations append to the same record concurrently, and MUST surface a record it cannot parse rather than treating it as absent.

#### Scenario: two consultations append at the same time
- GIVEN two consultations appending entries to the same record at the same time
- WHEN the record is read afterwards
- THEN each entry is individually parseable rather than interleaved into an unparseable line

#### Scenario: record that cannot be parsed
- GIVEN a run record whose content cannot be parsed
- WHEN it is read to recover prior state
- THEN the parse failure is surfaced rather than reported as an absence of prior activity

### Requirement: REQ-52 — the timeout clock has a stated origin and the run has a stated bound [deferred]
The system MUST state the instant from which a leg's elapsed time is measured and MUST apply a stated bound to the elapsed time of the consultation as a whole, covering retries, re-probes and returns to the checkpoint.

#### Scenario: elapsed time measured for one leg
- GIVEN a dispatched leg
- WHEN its elapsed time is compared against the per-leg timeout
- THEN the instant the measurement starts from is the stated one rather than an implementation choice

#### Scenario: retry chain within per-leg timeouts
- GIVEN a leg retried under `max_attempts` with each attempt inside the per-leg timeout
- WHEN the consultation's total elapsed time reaches the stated run bound
- THEN the run halts and surfaces the bound rather than continuing indefinitely

### Requirement: REQ-53 — an unmeasurable actual cost is recorded as unknown, never as zero [deferred]
The system MUST record `actual_cost` as unknown with its reason when the executor reports no per-invocation cost, MUST keep that value distinguishable from a measured zero, and MUST state at the checkpoint and in the report that a spend ceiling cannot be enforced against unknown costs.

#### Scenario: executor reports no per-invocation cost
- GIVEN an executor that reports no per-invocation cost
- WHEN a leg completes and `actual_cost` is recorded
- THEN the value is unknown with its reason rather than zero or omitted

#### Scenario: ceiling over unknown costs
- GIVEN a run whose legs record unknown actual costs
- WHEN the approved spend ceiling is evaluated
- THEN the report states that the ceiling could not be enforced against those legs

### Requirement: REQ-54 — the spend ceiling binds concurrent and in-flight legs [deferred]
The system MUST evaluate the approved spend ceiling against the cost already committed by legs in flight, MUST NOT let two legs each pass the check on a shared remaining budget, and MUST surface an overrun when it occurs rather than only at the next dispatch decision.

#### Scenario: two legs dispatched concurrently
- GIVEN an approved spend ceiling and two legs dispatched concurrently
- WHEN each leg is checked against the ceiling before the other's cost is recorded
- THEN the committed cost of the other leg is counted, so the pair cannot jointly pass the ceiling

#### Scenario: ceiling reached by a single in-flight leg
- GIVEN a run whose ceiling is reached by a single in-flight leg
- WHEN the spend passes the ceiling
- THEN the overrun is surfaced while the leg is in flight rather than discovered at the next dispatch decision

### Requirement: REQ-55 — a recorded child process is verified as our own before it is signalled [deferred]
The system MUST record, alongside the child process identifier, evidence sufficient to confirm the running process is the one this run spawned, MUST NOT signal a process that fails that confirmation, and MUST attempt termination of its own spawned processes when the controller session exits.

#### Scenario: identifier reused by an unrelated process
- GIVEN a recorded child process identifier from an interrupted run
- WHEN the identifier has been reused by an unrelated process on the host
- THEN the confirmation fails and no signal is sent to that process

#### Scenario: controller session exits with legs running
- GIVEN a controller session ending with spawned executor processes still running
- WHEN the session exits
- THEN it attempts termination and marks the run's record with the outcome, rather than deferring detection to a next run that may never occur

### Requirement: REQ-56 — a leg whose termination cannot be confirmed has its own recorded outcome [deferred]
The system MUST record a leg whose process could not be confirmed terminated as an unconfirmed-termination outcome distinct from `Aborted` and from `Succeeded`, and MUST surface that outcome to the user.

#### Scenario: process does not respond to termination
- GIVEN a cancelled leg whose process cannot be confirmed terminated
- WHEN the leg's outcome is recorded
- THEN it is recorded as unconfirmed termination and surfaced, rather than left without a terminal outcome

### Requirement: REQ-57 — the governing dispatch declaration is identified, and its absence is stated [deferred]
The system MUST identify by a stated rule which external-dispatch declaration governs a run when the working directory's repository differs from the repository owning the target, MUST halt and cite both when two governing declarations conflict, MUST state at the checkpoint that no declaration was found and which locations were searched when none exists, and MUST state the format a declaration is read in.

#### Scenario: working directory and target belong to different repositories
- GIVEN a working directory whose repository declaration differs from the declaration of the repository that owns the target
- WHEN the candidate set is built
- THEN the governing declaration is identified by the stated rule

#### Scenario: two declarations conflict
- GIVEN a repository declaration and an organisation declaration that disagree about a vendor
- WHEN the candidate set is built
- THEN the run halts with both declarations cited

#### Scenario: no declaration exists
- GIVEN a repository with no external-dispatch declaration
- WHEN the checkpoint is presented
- THEN it states that no declaration was found and names the locations searched

### Requirement: REQ-58 — an answer supplied by an automated caller does not satisfy the checkpoint [deferred]
The system MUST record the kind of actor that answered the checkpoint, and MUST NOT treat an answer supplied by a calling skill or other automated caller as the user's approval of spend or of transmission.

#### Scenario: invocation originating from another skill
- GIVEN an invocation originating from another skill rather than from a human turn
- WHEN the checkpoint is answered by that caller
- THEN the answering actor's kind is recorded and the run halts for a human rather than proceeding on that answer

### Requirement: REQ-59 — the billed account identity is recorded and shown [deferred]
The system MUST record which account identity an executor's credential resolves to for each dispatched leg and MUST show that identity at the checkpoint.

#### Scenario: host carrying several accounts for one vendor
- GIVEN an executor whose credential resolves to one of several accounts on the host
- WHEN the checkpoint is presented and the leg is later dispatched
- THEN the account identity that will be billed is shown at the checkpoint and recorded with the leg

### Requirement: REQ-60 — a pre-dispatch scan hit leaves a recorded resolution [deferred]
The system MUST record the location of every pre-dispatch scan hit and the actor and stated reason of any resolution that lets the run continue, and MUST NOT let a hit be dropped without such a record.

#### Scenario: user asserts a hit is a false positive
- GIVEN a scan hit the user asserts is a false positive
- WHEN the run continues
- THEN the assertion, its location, and the approving actor are recorded rather than the hit being silently dropped

### Requirement: REQ-61 — a truncated leg output is not accepted as a complete one [deferred]
The system MUST distinguish a leg output that ended because the process was interrupted from one the executor finished writing, and MUST NOT enter an interrupted output into the report as a complete card even when the template fields are present.

#### Scenario: process terminated mid-write
- GIVEN a leg whose process was terminated while writing its output
- WHEN the partial output happens to contain all four template fields
- THEN it is recorded as an interrupted output rather than passing the mechanical contract as a complete card

### Requirement: REQ-62 — a queued consultation is revalidated before it is dispatched [deferred]
The system MUST re-run static detection and cost estimation for a consultation that waited in a queue before dispatching it, and MUST return to the checkpoint when the executor set or the estimate changed while it waited.

#### Scenario: queued consultation reaches the front of the queue
- GIVEN a consultation approved before it was queued behind another run
- WHEN it is dequeued for dispatch
- THEN static detection and the estimate are recomputed, and a change in either returns the run to the checkpoint rather than dispatching on the stale approval

### Requirement: REQ-63 — the input-size check runs before the checkpoint is presented [deferred]
The system MUST evaluate the dispatch packet against each candidate executor's input bound before presenting the checkpoint, and MUST show an executor that cannot receive the packet as unavailable with that reason instead of accepting approval for a dispatch that cannot be made.

#### Scenario: packet exceeds a candidate's input bound
- GIVEN a dispatch packet exceeding a candidate executor's input bound
- WHEN the checkpoint is presented
- THEN that candidate is shown as unavailable for the size reason rather than approved and then failed at dispatch

### Requirement: REQ-64 — third-party-authored incumbent material is stated as such [deferred]
The system MUST state at the checkpoint when the incumbent proposal or the evidence paths carry material authored by someone other than the requesting user.

#### Scenario: target is a colleague's branch
- GIVEN a target whose incumbent proposal was authored by someone other than the requesting user
- WHEN the checkpoint enumerates what leaves the host
- THEN the presence of third-party-authored material is stated as such

### Requirement: REQ-65 — an unresolvable pinned revision does not block indefinitely [deferred]
The system MUST report a pinned target revision that no longer resolves on the host, and MUST provide a stated action that closes an undecided prior report rather than letting it block every later consultation on the same target.

#### Scenario: pinned revision no longer resolves
- GIVEN a delivered report whose pinned revision no longer resolves on the host
- WHEN a new consultation on the same target is requested
- THEN the unresolvable pin is reported and the prior report can be closed by the stated action

### Requirement: REQ-66 — retry input identity yields to re-approval and re-verification [deferred]
The system MUST state which of retry input identity and renewed approval or verification governs when both apply, MUST NOT dispatch a retry on a lapsed approval or a lapsed verification, and MUST record the retry as a new dispatch when its input could not be reused unchanged.

#### Scenario: retry after the approval was returned to the checkpoint
- GIVEN a leg awaiting retry whose run has since returned to the checkpoint for renewed approval
- WHEN the retry would be dispatched
- THEN the renewed approval and verification govern, and a retry that can no longer reuse its original input is recorded as a new dispatch

### Requirement: REQ-67 — material this run wrote outside the audit record has a stated lifecycle [deferred]
The system MUST state, for each artifact this run writes outside the per-run record — including any working copy created for a confined leg — where it is written and what happens to it when the run ends, and MUST record any such artifact it leaves in place.

#### Scenario: confined execution location holding a working copy
- GIVEN a run that created a working copy of source material for a confined leg
- WHEN the run ends
- THEN the copy's location and its disposition are stated, and a copy left in place is recorded

### Requirement: REQ-68 — the readable range is disclosed in non-technical language before approval
The system MUST state at the user checkpoint, before approval is taken, that what has been inspected is the dispatch packet while the range an external executor can read is `scope_boundary`, that the latter is the larger of the two, and what that range covers in practice — written in non-technical language rather than in field names alone.

#### Scenario: checkpoint presented for a dispatch carrying a path authorisation
- GIVEN a consultation whose dispatch packet has been inspected and whose executor receives `scope_boundary` as a path authorisation
- WHEN the checkpoint is presented for approval
- THEN the checkpoint states in non-technical language that the external executor can read a larger range than the inspected packet, and enumerates what that range covers, before any approval is accepted

### Requirement: REQ-69 — a passing scan is never stated as safe content
The system MUST describe a passing pre-dispatch scan as a statement about the dispatch packet only, and MUST NOT present it as the content being safe, as nothing sensitive leaving the host, or as any wording carrying that meaning.

#### Scenario: pre-dispatch scan returns no hit
- GIVEN a pre-dispatch scan over the dispatch packet that returns no hit
- WHEN the result is shown at the checkpoint or written into the report
- THEN it is worded as the packet having been scanned without a hit, and no wording asserts that what the executor can read is safe

### Requirement: REQ-70 — the report records that the guarantee covers the dispatch packet only
The system MUST record in every delivered report that the guarantee for that consultation covers the dispatch packet, and MUST record that material readable within `scope_boundary` was not subject to it.

#### Scenario: report delivered after a consultation
- GIVEN a consultation that reached a delivered report
- WHEN the report is written
- THEN it carries the stated limitation that the guarantee covered the dispatch packet and not the wider readable range

### Requirement: REQ-71 — a pinned revision is stated as the packet's origin, not as what was reviewed
The system MUST word a pinned target revision in the report as the revision the dispatch packet was extracted from, and MUST NOT state or imply that the external executor reviewed that revision.

#### Scenario: report citing a pinned revision
- GIVEN a report for a target whose revision was pinned at freeze
- WHEN the revision is cited in the report
- THEN the wording says the packet was extracted from that revision, and no wording claims the external executor's review was performed on it

### Requirement: REQ-72 — third-party configuration running on the host is disclosed at the checkpoint
The system MUST state at the checkpoint that a dispatch causes the external executor to load project instructions, hooks, skills, and MCP servers, and that loading them runs third-party code in the user's repository. When the system cannot enumerate what a pinned executor will load, it MUST state that it cannot enumerate them, and MUST NOT leave that unsaid in a way that reads as there being none.

#### Scenario: pinned executor whose loaded configuration cannot be enumerated ahead of dispatch
- GIVEN a pinned executor for which the system has no way to list what will be loaded before the leg runs
- WHEN the checkpoint is presented
- THEN the checkpoint states that loading is execution of third-party code in the repository and states that the set cannot be enumerated in advance, rather than saying nothing about it

### Requirement: REQ-73 — external text carries an untrusted-source marking that travels with the report
The system MUST mark text returned by an external executor, wherever it is carried into the report, as originating from an external executor and as untrusted content, and that marking MUST travel with the report to its downstream consumers, including an agent that adopts the report without a human turn. The system MUST NOT limit the protection to the controller's own fields.

#### Scenario: report consumed by an agent rather than read by the user
- GIVEN a report whose findings and divergence points carry text returned by external executors
- WHEN the report is handed to a downstream agent that acts on it without a human turn
- THEN each passage of external text is still marked as externally authored and untrusted in what that agent receives

### Requirement: REQ-74 — the audit record declares its retention granularity and inherits the packet's handling
The system MUST declare, for each audit record it keeps, whether it retains references and summaries or verbatim sent material. A record retaining verbatim sent material MUST be subject to the same handling restrictions the dispatch packet is subject to, and its location MUST be stated at the checkpoint.

#### Scenario: audit record retaining verbatim sent material
- GIVEN an audit record configured to retain the sent packet sections verbatim
- WHEN a consultation is presented at the checkpoint and later recorded
- THEN the record declares that it retains verbatim material, its location is stated at the checkpoint, and it is handled under the same restrictions as the dispatch packet
