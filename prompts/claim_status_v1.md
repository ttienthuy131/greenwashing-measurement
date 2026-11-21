You are coding passages from corporate sustainability reports using a fixed research rubric.

Assign Label A (claim status and strength) to the passage below.

- 0: No claim about climate, greenhouse gases, energy transition, or a related environmental outcome.
- 1: General or aspirational. Broad language, ambition, or commitment without a measurable target or reported outcome.
- 2: Specific target or action. A defined action or a measurable future target. A future target is never an achieved result.
- 3: Reported outcome. A realized, quantified climate or emissions result for an identifiable period or activity.
- U: Unclear. The passage does not support a reliable classification.

Use only the passage. Do not use outside knowledge about the company. Do not judge whether the claim is true.

Return only JSON: {"claim_status": "0|1|2|3|U", "rationale": "one sentence"}

Passage:
{passage}
