# Method

How Submission Desk turns a judgement call into a procedure, which parameters come from published data, and where the model is known to be weak.

## 1. Why gates come first

The gates are binary and non-negotiable: scope match, indexing, legitimacy, APC within budget, article type accepted. A journal that fails any one is removed before scoring.

This ordering is doing real work. If eligibility were folded into the score as another weighted criterion, a sufficiently high impact factor could compensate for a journal that does not index where you need or does not publish your article type — which is never the right trade. Separating elimination from ranking also removes the step where most of the arguing happens.

## 2. Acceptance probability

```
fitFactor = [0.5, 0.75, 1.0, 1.3, 1.6]   indexed by fit score 1–5
P_accept  = clamp( (rate / 100) × fitFactor , 0.02 , 0.95 )
```

The published acceptance rate is a property of the journal; your manuscript is not the average submission to it. `fitFactor` is the correction, and the clamp keeps the extremes away from certainty in either direction.

The **direction** of this correction is supported: Rees et al. found that authors who prioritised fit had roughly double the odds of acceptance at their first-choice journal (OR 2.11, 95% CI 1.55–2.88). The **magnitude** is not. The specific multipliers are a guess with a plausible shape — see the provenance table below.

Fit is scored against a rubric so it is not a mood reading:

| Score | Meaning |
|:-----:|---------|
| 5 | The journal has published closely comparable work recently; your methods meet or exceed the level in those papers; the audience is exactly its readership. |
| 4 | Clearly in scope; rigor is comparable to what it publishes; audience overlaps substantially. |
| 3 | In scope but not central; rigor is at the journal's floor rather than its median. |
| 2 | Adjacent to scope; you would be arguing for relevance in the cover letter. |
| 1 | Out of scope, or below the journal's methodological bar. Usually a desk reject. |

Score it before you look at the impact factor. Scoring after produces motivated reasoning in one direction, reliably.

## 3. Expected Yield (default mode)

```
EIM = P_accept × IF / (weeks / 4.345)
```

Expected impact per month. The numerator is standard expected value — payoff times probability of realizing it. The denominator converts it to a rate, so a journal that takes four months to reject you is penalized against one that decides in four weeks.

This is a simplification of a published model. Salinas & Munch (2015) formulated submission as a Markov decision process maximizing expected citations over a finite horizon *T*, and derived a per-journal index

```
V_j = α_j λ_j (1 − τ_j/T) / [ 1 − (1 − τ_j/T − t_R/T)(1 − α_j)(1 − s)^(t_R + τ_j) ]
```

where α is acceptance rate, λ the expected citation rate (approximated by IF), τ submission-to-decision time, t_R revision time, and s the daily probability of being scooped. That index reproduced their full pairwise model at Spearman ρ = 0.920.

`EIM` differs in three ways, all simplifications:

1. It divides by time instead of discounting against a horizon *T*, so it has no notion of career stage. A first-year PhD student and someone eighteen months from a tenure review get the same ranking; under the original model they should not.
2. It drops the scooping term *s* entirely.
3. It does not model the sequence — only which journal to try first. The published model determines an ordered ladder.

If you need the real thing, use the published model. `EIM` is for the common case where you want a defensible first choice in five minutes.

## 4. Balanced mode

Each criterion is min-max normalized across the current candidate set, then combined under user weights:

```
score = 100 × Σ (wᵢ / Σw) × normalizedᵢ
```

with prestige and acceptance odds normalized against the set maximum, and speed and cost as ratios against the set minimum (so faster and cheaper score higher).

Because normalization is relative to the candidate set, **Balanced scores are not comparable across different shortlists**. Adding or removing a journal changes everyone's score. Expected Yield does not have this property — its values are absolute. This is a real advantage of the default mode and a reason to treat Balanced as a sensitivity check rather than the primary ranking.

## 5. Parameter provenance

| Parameter | Value | Source | Status |
|---|---|---|---|
| Fit multipliers | 0.5 / 0.75 / 1.0 / 1.3 / 1.6 | — | **Heuristic.** Direction supported by Rees et al.; magnitude invented. |
| Functional form | `rate × fitFactor` | — | **Heuristic.** Multiplicative interaction is assumed, never tested. |
| Probability clamp | 0.02 – 0.95 | — | **Heuristic.** Arbitrary but conservative. |
| Weeks per month | 4.345 | Calendar | Exact. |
| Default Balanced weights | 35 / 30 / 20 / 15 | — | **Heuristic.** Starting point only; move the sliders. |
| Time to first decision | 8 weeks | Rees et al. 2022 (mean 8.4) | Empirical. |
| Submission → acceptance | 19 weeks | Rees et al. 2022 (mean 19.6) | Empirical. |
| Second-journal decision | 6.7 weeks | Rees et al. 2022 | Empirical. |
| Journals per paper | 1.5 | Rees et al. 2022 | Empirical. |
| Revision rounds | 1.4 | Rees et al. 2022 | Empirical. |
| Pre-submission formatting | 2 weeks | — | **Heuristic.** Not covered by the source data. |
| Production after acceptance | 3 weeks | — | **Heuristic.** Varies enormously by publisher. |

All timeline values derive from one survey of one field (health professions education, 691 respondents, 21.7% response rate, respondents reporting on a paper that was eventually published). Survivorship is baked in: manuscripts that were never accepted anywhere are absent by construction. Expect your field to differ, and overwrite the defaults.

## 6. Known limitations

**Impact factor is a journal-level average used as an article-level prediction.** This is the standard objection and it holds here. Citation distributions within a journal are heavily skewed, so the mean is a poor forecast for any individual paper. Salinas & Munch acknowledged the same assumption in their model. If your field has a better prestige proxy, put that in the IF column instead — the arithmetic does not care what the number means.

**Fit is self-assessed.** The one input the model cannot check is the one it weights most heavily. The rubric constrains it; it does not eliminate the bias. Having a co-author score fit independently, before seeing your scores, costs ten minutes and is the cheapest available correction.

**Acceptance rates and decision times are often unavailable.** Salinas & Munch got usable data from 61 of 131 journals contacted, and ended their paper by urging journals to publish these figures. Where you cannot find a number, record the estimate and its source rather than silently typing something plausible.

**The model optimizes for time-adjusted impact, which may not be your objective.** If a specific journal is a hard requirement for a grant, a thesis, or a promotion committee, no scoring model applies — submit there. The tool is for the case where several journals are genuinely acceptable.

**No sequence optimization.** The ranked ladder is scored independently per journal, not solved as an optimal submission sequence. For short ladders these usually agree; for long ones they can diverge.

## 7. What would improve this most

In rough order of value:

1. **Calibrating the fit multipliers** against real outcome data — submissions with a pre-recorded fit score and a known accept/reject result. Even a few hundred observations from one field would replace the weakest part of the model.
2. **Testing the functional form.** Multiplicative is an assumption. Additive or logistic forms may fit better.
3. **Field-specific presets** with real acceptance rates and decision times, contributed as JSON.
4. **Adding the horizon term** *T* so the ranking responds to career stage the way the published model does.

See [CONTRIBUTING.md](../CONTRIBUTING.md).
