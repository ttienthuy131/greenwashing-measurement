# Climate-claim coding rubric

**Version:** 0.1
**Status:** Draft for pilot annotation; revise after a small calibration exercise.

## Purpose

Code what a passage claims and how well the passage supports or bounds that claim. Do not assign a definitive "greenwashing" label from a passage alone. Firm-level emissions comparisons are a separate validation exercise and have important coverage limits.

## Annotation unit

Annotate one claim at a time. Include enough adjacent text to identify the subject, reporting period, boundary, and any qualification. Record the company, report title, covered year, publication year, page or section, exact passage, and annotator ID. If context is insufficient, mark the relevant item `unclear` rather than inferring it.

## Label A: claim status and strength

| Code | Label | Rule |
|---|---|---|
| 0 | No relevant claim | The passage makes no claim about climate, greenhouse gases, energy transition, or a related environmental outcome. Exclude from claim scoring. |
| 1 | General or aspirational | Broad language, ambition, or commitment without a measurable target or reported outcome. |
| 2 | Specific target or action | A defined action or a measurable future target is stated. Record the target year and baseline if provided. Do not code a future target as an achieved result. |
| 3 | Reported outcome | A realized, quantified climate or emissions result is stated for an identifiable period or activity. Record whether it describes absolute emissions, emissions intensity, or another measure. |
| U | Unclear | The available passage and context do not support a reliable classification. Record why. |

This label measures the strength and status of a claim, not whether the claim is true or misleading.

## Label B: evidence and boundary flags

Record each flag as `yes`, `no`, or `unclear`. A `no` means the feature is not stated in the reviewed passage or report section; it does not prove that the company omitted it elsewhere.

| Flag | Record `yes` when the passage or cited report context... |
|---|---|
| `quantified` | Gives a numerical value for the outcome or target. |
| `period_and_baseline` | Identifies the comparison period and, for a reduction, its baseline. |
| `absolute_or_intensity` | Makes clear whether the figure is absolute emissions or emissions per unit of output/revenue. |
| `organizational_boundary` | Identifies the entities, facilities, or operations covered. |
| `emissions_scope` | Identifies the emissions scope or gases included, where applicable. |
| `external_assurance` | Identifies external assurance or verification and its scope. |
| `offset_or_credit` | Uses offsets, credits, avoided emissions, or removals as part of the stated result. Record the mechanism and whether it is separated from gross reductions. |
| `qualification` | States a material limitation, uncertainty, or qualification relevant to the claim. |

## Potentially misleading presentation cues

Mark any cue that is explicit in the passage or its cited context. Add a short explanation and supporting text. Do not infer intent.

- A percentage or intensity improvement is presented without the corresponding absolute-emissions trend when both are available in the report.
- An offset, credit, avoided-emissions estimate, or removal is described in a way that could be read as a reduction in gross emissions.
- A claim uses a broad company-level subject while its stated boundary covers only a subset of operations.
- A target or result lacks a stated baseline, time period, or material scope needed to interpret it.
- The passage describes a future commitment as if it were an achieved outcome.
- Other: describe the cue and quote the evidence.

These are review flags, not proof of deception. Annotators must not use outside assumptions about a company to code a passage.

## Annotation procedure

1. Pilot the rubric on a small set of passages and discuss disagreements before labeling the main sample.
2. Keep the final codebook version fixed for the main annotation batch; log any later changes and recode affected passages.
3. Have two human annotators independently code the same subset where feasible. Report Cohen's kappa for categorical labels only when its assumptions are appropriate, alongside class counts and the disagreement table.
4. Compare LLM outputs against the same human-coded passages using the same label definitions. Report confusion matrices and class-specific performance; do not rely on agreement alone or assume model superiority.
5. Preserve the exact prompt, model identifier, settings, and output for every model annotation. Treat prompt/model variation as a robustness test.

## Construct interpretation

Do not collapse claim strength, evidence flags, and emissions performance into a single score until the pilot supports and documents a defensible aggregation rule. Report these dimensions separately first. External emissions data can contextualize realized performance but cannot validate every claim, because facility-level GHGRP coverage does not equal a firm's complete emissions boundary.
