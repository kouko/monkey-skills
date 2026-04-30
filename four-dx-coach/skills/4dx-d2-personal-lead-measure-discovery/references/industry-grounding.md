# Industry-experience grounding for 4dx-d2-personal-lead-measure-discovery

Supplements the book's lead-measure methodology with documented failure cases the
book under-serves. Sourced from public investigations, regulatory findings, and
academic literature.

## Goodhart's Law (the underlying mechanism)

- **Charles Goodhart, "Problems of Monetary Management: The U.K. Experience"
  (1975)** — paper presented to the Money Study Group at the London School of
  Economics; reprinted in *Papers in Monetary Economics 1*, Reserve Bank of
  Australia. Original formulation: "Any observed statistical regularity will
  tend to collapse once pressure is placed upon it for control purposes."
  ([EconBiz catalog record](https://www.econbiz.de/Record/problems-of-monetary-management-the-u-k-experience-goodhart-charles/10002525062))
- **Marilyn Strathern, "'Improving ratings': audit in the British University
  system" (1997, *European Review*, Vol. 5, No. 3, pp. 305–321, Cambridge
  University Press)** — popularized form: "When a measure becomes a target, it
  ceases to be a good measure."
  ([Cambridge Core record](https://www.cambridge.org/core/journals/european-review/article/abs/improving-ratings-audit-in-the-british-university-system/FC2EE640C0C44E3DB87C29FB666E9AAB),
  [open PDF on gwern.net](https://gwern.net/doc/statistics/decision/1997-strathern.pdf))

Both formulations describe the same dynamic that 4DX leaders face the moment
they attach incentives, visibility, or career stakes to a "predictive +
influenceable" lead measure: humans optimize the metric, not the underlying
behavior the metric was supposed to proxy for.

## Documented industry failures of lead-measure-as-target

### Case I-1: Wells Fargo cross-selling scandal (2011–2016)

Wells Fargo set an internal cross-selling lead measure ("Gr-eight" — eight
products per household) and tied it to branch-level sales quotas, employee
performance reviews, and termination decisions. The measure was both
*predictive* (more products per household correlates with retention and
lifetime value) and *influenceable* (a personal banker can pitch products at
each interaction) — i.e. it passed the book's two-axis test cleanly. It then
collapsed under Goodhart pressure.

The Consumer Financial Protection Bureau's Consent Order dated September 8,
2016 fined Wells Fargo a total of **$185 million** (CFPB $100M + OCC $35M +
City and County of Los Angeles $50M) for "the widespread illegal practice of
secretly opening unauthorized accounts." Initial findings cited **1,534,280
unauthorized deposit accounts and 565,433 credit-card accounts** opened
between 2011 and 2016; a May 2017 expanded review revised the estimate to
roughly **3.5 million** fraudulent accounts. CEO John Stumpf resigned on
October 12, 2016.

Primary citations:
- [CFPB Enforcement Action: Wells Fargo Bank, N.A. (2016)](https://www.consumerfinance.gov/enforcement/actions/wells-fargo-bank-2016/)
- [Congressional Research Service IF11129 — Wells Fargo Timeline of Recent Consumer Protection and Corporate Governance Scandals](https://www.congress.gov/crs-product/IF11129)
- [Stanford Closer Look — The Wells Fargo Cross-Selling Scandal (CGRI-CL-62)](https://www.gsb.stanford.edu/sites/gsb/files/publication-pdf/cgri-closer-look-62-wells-fargo-cross-selling-scandal.pdf)

### Case I-2: Phoenix VA hospital wait-time gaming (exposed 2014)

The Veterans Health Administration adopted a lead measure that new-patient
primary-care appointments be scheduled within **14 days** (later 30 days) of
the requested date. The metric was tied to senior-executive performance
bonuses. It was both predictive (shorter waits correlate with better
outcomes) and influenceable (schedulers could in principle move patients
through faster) — passing both axes, before Goodhart pressure broke it.

The U.S. Department of Veterans Affairs Office of Inspector General final
report **14-02603-267**, *Review of Alleged Patient Deaths, Patient Wait
Times, and Scheduling Practices at the Phoenix VA Health Care System*,
released **August 26, 2014**, documented schedulers maintaining unofficial
"secret" wait lists to make 14-day compliance appear achieved while real
waits stretched to **~115 days** (≈4 months) for new primary care. The OIG
identified **over 3,500 veterans on unofficial lists** in addition to the
1,400 on the official Electronic Wait List, with **more than 1,700 patients
who had requested appointments never enrolled on any waiting list**. Among
patients reviewed, OIG identified 28 patients negatively impacted by care
delays (including 6 deaths) plus 17 additional patients whose care deviated
from expected standards (including 14 deaths). The Phoenix director Sharon
Helman and other senior executives were aware of the unofficial lists.

Primary citations:
- [VA OIG Report 14-02603-267 (PDF, Aug 26 2014)](https://www.vaoig.gov/sites/default/files/reports/2014-08/VAOIG-14-02603-267.pdf)
- [VA OIG Report Page — Review of Alleged Patient Deaths, Patient Wait Times, and Scheduling Practices at the Phoenix VA Health Care System](https://www.vaoig.gov/reports/audit/review-alleged-patient-deaths-patient-wait-times-and-scheduling-practices-phoenix-va)
- [VA OIG Interim Report 14-02603-178 (PDF, May 28 2014)](https://www.vaoig.gov/sites/default/files/reports/2014-05/VAOIG-14-02603-178.pdf)

### Case I-3: Atlanta Public Schools test-score cheating (2009–2015)

Atlanta Public Schools under Superintendent Beverly Hall adopted year-over-
year improvement on the Georgia Criterion-Referenced Competency Test (CRCT)
as a lead measure for school quality, with bonuses, public rankings, and
employment tied to gains. The metric was predictive (genuine learning gains
do correlate with test scores) and influenceable (better instruction moves
scores) — and then Goodhart pressure produced systematic answer-changing
parties after exams.

A Georgia Bureau of Investigation probe released July 2011 found cheating
in **44 of 56 schools investigated** and implicated **178 educators**.
Thirty-five educators were indicted under Georgia's RICO Act. After what
became the **longest criminal trial in Georgia history (8 months)**, on
**April 1, 2015** **eleven of twelve defendants were convicted** of
racketeering. Between 2002 and 2009, eighth-graders' Atlanta NAEP reading
scores had jumped 14 points — the highest of any urban district — a gain
that *Atlanta Journal-Constitution* statistical analyses had flagged as
implausibly large.

Primary citations:
- [CNN — "Atlanta schools cheating scandal: 11 of 12 defendants convicted"](https://www.cnn.com/2015/04/01/us/atlanta-schools-cheating-scandal)
- [Education Week — "Atlanta Educators Convicted in Test-Cheating Trial"](https://www.edweek.org/teaching-learning/atlanta-educators-convicted-in-test-cheating-trial/2015/04)
- Special Investigators' Report to the Governor of Georgia (Volumes 1–3, July 2011) — [summary via Georgia Public Policy Foundation](https://www.georgiapolicy.org/news/the-atlanta-public-schools-cheating-scandal/)

## What 4DX practitioners learn from these cases

The book's two-axis test (predictive + influenceable) is **necessary but not
sufficient** for safe deployment. All three of these lead measures passed
both axes cleanly when they were chosen — they failed only after stakes were
attached to them. Goodhart pressure scales with the visibility and
consequence of the measure, not with the measure's intrinsic quality.
Practitioners should layer three mitigations on top of the two-axis test:
**(1) pair a frequency-based lead with a quality-based lead** so that gaming
the count is caught by the quality check; **(2) re-validate the causal chain
on a 4–8 week cadence** — if leads are green but the lag stays flat, the
lead is being gamed or was wrong (the book endorses this in CE-24, but only
in passing); **(3) keep the falsifiable forecast written down** (D2 Step 7)
so that drift between predicted and observed lag movement is visible rather
than rationalized away. For personal-scale use, the analogue is
*self-Goodharting*: when you attach high stakes to your own lead measure
("I will read 4 books per month"), you will speed-read without
comprehending unless a quality check ("write a one-paragraph summary per
book") is paired in.
