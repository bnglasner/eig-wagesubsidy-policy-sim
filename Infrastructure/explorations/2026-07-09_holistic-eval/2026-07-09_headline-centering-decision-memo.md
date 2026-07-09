# Decision Memo — Where Should the Entry Headline Sit?

**To:** Ben Glasner / Adam Ozimek · **From:** holistic evaluation (2026-07-09) · **Decision owner:** you (this is a genuine judgment call, not a bug)
**One-line ask:** Is the entry headline the *evidence-central potential response* (~1.1–1.5M) or a *deliberately conservative floor* (0.83M)? Pick one and label it accordingly.

---

## The situation in one paragraph

The current headline, **0.83M**, is the number you get when three independent knobs on the potential-wage side are *simultaneously* set to their entry-minimizing ends: no non-employment wage penalty (0%), trimmed offer dispersion (λ=0.75), and a residual dispersion estimated on accepted wages (which understates the low tail). Each choice is defensible alone. Stacked, they make 0.83M a **floor presented as a center**. The drafts say "our central estimate is 0.83 million" as if it were neutral; the model's structure does not support that reading.

## The evidence (verified against live outputs)

| If you relax one knob toward the evidence | Entry becomes |
|---|---|
| 10% non-employment penalty (Schmieder-vWB 0.8%/mo; pool is mostly long-detached) | **1.21M** |
| 20% penalty (long-spell bound) | **1.70M** |
| Offer dispersion λ=1.0 (full residual) | **1.12M** |
| Status-differentiated penalty, ~15% mean (skewstat) | **1.46M** |
| **Current headline (all knobs at conservative end)** | **0.83M** |

Two facts make the direction unambiguous:
1. **penalty = 0 is not neutral.** Offer decay during non-employment is directly measured (Schmieder–von Wachter–Bender 2016; Krueger–Mueller 2016). This pool is dominated by long-detached NILF, disabled, and retired members. A ~10–15% mean penalty is the evidence-central; 0% is a floor.
2. **The "0.83 vs 1.46" choice is a penalty-magnitude choice.** Your own delta note shows the skew *shape* is ≈ neutral at matched mean penalty; 1.46M is essentially "the ~15%-penalty outcome." So the real question is simply: *what non-employment wage penalty does the evidence support for this pool?* — and the answer is not zero.

**Corroborating check:** at 1.42M (the pre-dispersion era) your reality assessment placed the central *above* the 1990s-EITC-alone precedent, between Paycheck Plus and SSP. At 0.83M (3.4pp of the reachable pool) the central now sits *at or below* the single most conservative macro precedent. The dispersion rebase quietly moved the headline from "generous side of the record" to "the floor of the record."

## Why 0.83M is not indefensible (the two-sided balance)

The independent methodology review makes a fair push-back: the model also carries offsetting *upward* biases, and the net direction is genuinely two-sided.
- **Take-up < 100%** (0.66M row) is a clean separable scalar — do **not** fold it into the potential central (that double-uses it).
- **Frictionless matching (find-rate 1), no fixed cost of work, and UI/SSDI omitted from `NI(0)`** are upward biases baked into the potential count and *not* separated out — they partially offset the downward MPL conservatism.
- So the honest reading is not "the answer is clearly ~1.5M." It is: the potential-wage side is understated *and* the matching/fixed-cost side is overstated. The one thing that is not defensible is leaving the penalty at exactly 0 while calling the result neutral.
- **Advocacy credibility:** a lower, harder-to-attack headline is a legitimate choice for a policy piece — *if labeled as conservative.*

## Recommendation

**Option A (recommended) — re-center on a coherent evidence bundle, keep 0.83M as the explicit floor, disclose both bias sets.**
Compute a single *jointly-specified* "evidence-central" scenario — a status-differentiated non-employment penalty (~10–15% mean, the skewstat generator is the evidence-grounded form) **and** λ=1.0 (correcting the penalty alone gets you to ≈1.1–1.2M; adding λ pushes toward the mid-1M's). Headline that, with 0.83M as the labeled conservative lower anchor. **Attach the two-sided bias disclosure**: the MPL-side conservatism (penalty, dispersion) is offset by upward biases (frictionless matching at find-rate 1, no fixed cost of work, UI omitted from the counterfactual), so the re-center corrects a mislabeled floor without claiming precision the two-sided uncertainty does not support. Take-up (0.80) scales the *realized* number separately.
*Effort:* one new joint scenario row + prose/figure re-label; ~0.5–1 day. Requires the Q2 fix (scenario grid) to display cleanly.

**Option B (acceptable) — keep 0.83M, but relabel it.**
Stop calling it "central." Call it "a deliberately conservative estimate that applies no non-employment wage penalty and trims offer dispersion," lead with the *range* (0.25M–1.7M) rather than the point, and state that the evidence-central of the potential response is higher. Cheapest (prose only), but leaves a defensible-looking point estimate that a skeptic will re-derive upward.

**Not recommended — status quo.** Presenting 0.83M as the neutral "central" while three same-direction conservatisms produced it is the one option the model's structure does not support.

## What I am *not* claiming

I am **not** saying "the answer is 1.46M." The skewstat 1.46M is one specific penalty mixture. The defensible statement is: **the evidence-weighted center of the potential response lies materially above 0.83M, most plausibly ~1.1–1.5M, and its exact value is governed by the non-employment-penalty assumption — the single largest lever, currently pinned at its no-effect floor.** The right way to fix this is to compute the joint bundle (Option A), not to swap one point for another.

## Decision requested

☐ **A** — re-center on the joint evidence bundle (~1.1–1.5M), 0.83M as labeled floor *(recommended)*
☐ **B** — keep 0.83M, relabel as conservative + lead with the range
☐ **status quo** — (documented as not recommended)

Whichever you pick propagates through both drafts and every entry/cost figure, so decide this **before** the next full review (Q9).
