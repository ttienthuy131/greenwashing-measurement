Classify the strongest climate-related statement in the text.

Ask these questions in order and stop at the first "yes":
1. Does the text report a realized, quantified climate or emissions result for a stated period? If yes, code 3.
2. Does it state a measurable future target or a specific action? If yes, code 2.
3. Does it make any other statement about climate, greenhouse gases, or the energy transition? If yes, code 1.
4. Otherwise, code 0.
If the text is too fragmentary to answer these questions, code U.

Base the code on the text alone. Do not use outside information and do not evaluate truthfulness.

Output JSON only: {"claim_status": "0" | "1" | "2" | "3" | "U", "rationale": "one sentence"}

Text:
{passage}
