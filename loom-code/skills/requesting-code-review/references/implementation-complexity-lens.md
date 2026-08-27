# Implementation complexity lens

Review actual additions against optional planned complexity evidence. Judge
whether the burden that landed is worth its maintenance cost now. Verify
landed deletions, identify unplanned implementation burden, and assess
downstream operational risk. Every concern must name a concrete simpler
alternative that preserves the required outcome.
If an alternative loses a required outcome, describe it as a scope trade-off,
not as a complexity reduction.

When planned evidence is absent, perform an independent local assessment from
the diff. Do not repeat upstream verdicts; this lens judges what landed.
