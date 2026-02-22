# Feature Assessment Calibration

> This preamble is injected into every feature-dimension evaluator. It frames the evaluation perspective.

## How Feature Evaluation Differs from Product Evaluation

| Aspect | Product Evaluation | Feature Evaluation |
|--------|-------------------|-------------------|
| Question | Should I build this app? | Should this app add this feature? |
| Baseline | Greenfield, no existing context | Existing app with users, code, identity |
| Risk profile | Wasted build time | Diluting focus, bloating maintenance |
| Success metric | Viable indie product | Strengthens the existing product |
| Failure mode | Building something nobody wants | Adding something that weakens what works |

## Signal Format

Each dimension produces a signal, not a numeric score:

| Signal | Meaning |
|--------|---------|
| **Positive** | Evidence supports adding this feature |
| **Neutral** | Mixed or insufficient evidence; not a clear signal either way |
| **Negative** | Evidence suggests this feature would hurt or is unnecessary |

Each signal includes a confidence level:

| Confidence | Meaning |
|------------|---------|
| **High** | Multiple independent evidence sources agree; code analysis confirms |
| **Medium** | Some evidence supports the signal; some gaps remain |
| **Low** | Limited evidence; signal is based on inference rather than direct observation |

Rule: every signal must cite its strongest evidence (code location, market data, or user signal). "Probably positive" is forbidden; state the signal and the confidence separately.

## Verdict Logic

The skill orchestrator computes the verdict from the 4 dimension signals:

- **GO**: Most dimensions Positive, no High-confidence Negative
- **DEFER**: Mixed signals, or conditions exist that could flip the assessment
- **KILL**: Any High-confidence Negative that cannot be circumvented

One fatal flaw vetoes everything. There is no weighted aggregate.

## Sub-Question Structure

Each dimension's sub-questions are split into two groups:

- **Universal sub-questions:** Always apply regardless of platform. These are platform-neutral analysis questions.
- **Platform-specific sub-questions:** Vary by platform. When an overlay applies (e.g., iOS), the platform-specific questions are replaced with platform-tailored variants. When no overlay is active, use the default platform-specific questions.
