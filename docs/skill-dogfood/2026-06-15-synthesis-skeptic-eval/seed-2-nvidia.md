# SEED 2 — Nvidia (investing / trim decision)

## QUESTION
Should I trim my Nvidia position?

## CONFIRMED CLAIMS BLOCK
### [0] Data-center revenue $22.6B Q3 FY2025, +112% YoY.
Vote: 4-0 · Source: investor.nvidia.com q3-fiscal-2025 (primary)
Quote: "Data Center revenue was $22.6 billion, up 112% from a year ago"
Verifier evidence (high): official release cross-checked vs 10-Q.

### [1] GAAP gross margin 74.6% Q3 FY2025, up from 56.1% a year earlier.
Vote: 4-0 · Source: investor.nvidia.com q3-fiscal-2025 (primary)
Quote: "GAAP gross margin was 74.6 percent, up 18.5 percentage points"
Verifier evidence (high): primary release; driven by Hopper mix + software attach.

### [2] Management guided GM to low-70% range as Blackwell ramps (higher initial costs).
Vote: 3-1 · Source: seekingalpha.com blackwell-margin-trajectory (secondary)
Quote: "CFO noted Blackwell gross margins will be 'in the low 70s' before recovering as yields improve"
Verifier evidence (medium): paraphrased CFO; one verifier flagged wording as lightly editorialized.

### [3] Google/Amazon/Microsoft shipping or announcing custom AI accelerators to reduce Nvidia reliance for inference.
Vote: 4-0 · Source: theverge.com custom-silicon (secondary)
Quote: "hyperscalers are pouring billions into in-house silicon to claw back margin from Nvidia"
Verifier evidence (medium): supported by announcements; quote from editorial summary.

### [4] Four hyperscalers ~40–45% of Nvidia DC revenue FY2024 (analyst est).
Vote: 3-1 · Source: barclays.com hyperscaler-concentration-2024 (secondary)
Quote: "top four cloud customers represent roughly 40–45% of NVDA DC revenue"
Verifier evidence (medium): analyst model, not Nvidia-disclosed; varies by house.

### [5] U.S. export controls (Oct 2023, expanded Oct 2024) ban most-advanced DC GPUs to China without license.
Vote: 4-0 · Source: commerce.gov export-controls (primary)
Quote: "updated controls restrict export of advanced computing chips to destinations of concern"
Verifier evidence (high): Commerce official release; BIS names covered classes.

### [6] China revenue declined from ~20–25% of DC sales (early 2023) to mid-single-digit % by late 2024.
Vote: 3-1 · Source: wsj.com nvidia-china-revenue-share (secondary)
Quote: "China exposure shrunk from a fifth of DC revenue to a rounding error for some quarters"
Verifier evidence (medium): WSJ on unnamed analyst sources; Nvidia doesn't break out China DC.

### [7] CUDA 4M+ registered developers; dominant LLM-training stack → high switching costs.
Vote: 4-0 · Source: blogs.nvidia.com cuda-4-million (primary)
Quote: "more than 4 million developers use CUDA, the world's most adopted GPU computing platform"
Verifier evidence (high): Nvidia internal data; corroborated by framework surveys.

### [8] AMD MI300X deployed at Azure + Meta for inference; AMD guiding $5B DC GPU revenue 2024.
Vote: 3-1 · Source: anandtech.com mi300x-hyperscaler (secondary)
Quote: "MI300X now in production at multiple major cloud providers, 2024 AI accelerator guidance of $5B"
Verifier evidence (medium): $5B public; deployment scale doesn't quantify workload share.

### [9] Forward P/E ~35–38x FY2026 consensus (late 2024), premium to S&P but below mid-2024 peak >45x.
Vote: 3-1 · Source: finviz.com NVDA (secondary)
Quote: "NVDA forward P/E sits in the mid-30s, reflecting strong but decelerating earnings growth expectations"
Verifier evidence (medium): screen-scraped daily data; aggregator editorial summary.

### [10] Blackwell GB200 NVL72 up to 30x inference perf over H100 per Nvidia benchmarks.
Vote: 3-1 · Source: nvidia.com gb200-nvl72 (primary)
Quote: "GB200 NVL72 delivers up to 30x faster real-time trillion-parameter LLM inference compared to H100"
Verifier evidence (medium): Nvidia's own benchmark, specific config.

### [11] Sovereign AI emerged 2024; mgmt cites double-digit % contribution to DC revenue.
Vote: 3-1 · Source: semianalysis.com sovereign-ai (blog)
Quote: "Jensen Huang flagged sovereign AI as a multi-billion dollar driver, though exact breakdown not disclosed"
Verifier evidence (low): CEO commentary + analyst blog; no audited segment.

## ARM A — SINGLE-PASS SYNTHESIS
SUMMARY: Nvidia's business fundamentals remain exceptional — 112% YoY data-center revenue growth, 74.6% GAAP gross margins, and a forthcoming Blackwell architecture that claims 30x inference gains over Hopper — yet the stock already prices in continued dominance at a forward P/E of 35–38x FY2026 earnings. The bull case rests on CUDA's deep software moat (4M+ developers), diversifying demand via sovereign AI, and a customer base that has consistently spent ahead of expectations. The bear case centers on three compounding risks: hyperscaler customer concentration (~40–45% of DC revenue from four cloud giants), U.S. export controls that have already compressed China exposure from ~20–25% to mid-single digits, and a credible competitive threat from custom silicon (Google TPU, Amazon Trainium, Microsoft Maia) and AMD's MI300X. Whether to trim depends on your cost basis, position sizing, and conviction on whether Blackwell's ramp sustains margin recovery after a guided dip to the low-70% range.

FINDINGS:
- [high] Core momentum extraordinary: DC revenue $22.6B (+112% YoY); GAAP GM +18.5pp to 74.6%. | evidence: primary release vs 10-Q; 4-0.
- [medium] Blackwell sustains the moat but compresses near-term margins: 30x inference vs H100 (Nvidia config); GM guided to low-70s during ramp, recovery as yields improve. | evidence: primary product page + paraphrased CFO; 30x is best-case config.
- [high] CUDA lock-in durable: 4M+ developers, dominant training stack → switching costs. | evidence: Nvidia data + surveys; 4-0.
- [medium] Hyperscaler concentration double-edged: four customers ~40–45% of DC revenue, all simultaneously largest buyers AND most-resourced competitors shipping custom silicon; AMD MI300X in production at Azure/Meta, guiding $5B 2024. | evidence: analyst estimate; announcements; AMD $5B public; mixed 3-1.
- [high] Export controls materially + permanently reduced China exposure: from ~20–25% to mid-single digits by late 2024 — a resolved headwind, base already adjusted, but licensing risk remains. | evidence: Commerce rule; WSJ/analyst on share; 4-0 / 3-1.
- [medium] Valuation elevated but decompressed from peak: ~35–38x fwd P/E vs >45x mid-2024. | evidence: aggregator data, daily; treat directional.
- [low] Sovereign AI emerging but unquantified: mgmt cites double-digit % contribution. | evidence: single blog source.

CAVEATS: Not financial advice; depends on cost basis/tax/concentration/horizon. China share is analyst-estimated. Blackwell 30x is Nvidia-controlled specific config. Hyperscaler custom silicon is medium-to-long-term displacement; near-term capex still flows to Nvidia. Valuation is late-2024 snapshot. Sovereign AI rests on a single blog source — weight lightly.

OPEN QUESTIONS:
- At what GM floor does Blackwell ramp become EPS-negative, and how long does the trough last?
- How fast are custom accelerators displacing Nvidia in inference specifically (vs training)?
- Will controls expand to lower-tier "China-compliant" chips (e.g. H20)?
- Is 35–38x supported by FY2027 estimates, or does it compress if growth decelerates below consensus?
