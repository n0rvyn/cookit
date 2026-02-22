# Alternative Directions

**Purpose:** For DEFER/KILL verdicts -- suggest alternative features that are lower cost, complement the core loop better, or clarify the product boundary.

## Methodology

1. **Lower-cost variants:** Can the same user need be addressed with a simpler feature?
   - Subset of the proposed feature that captures most of the value
   - Different implementation approach (e.g., Widget instead of full screen, automation instead of UI)
   - Leveraging existing infrastructure more heavily
2. **Complementary features:** What alternative features would strengthen the core loop instead?
   - Features that improve the existing core action
   - Features that improve retention without adding new paths
   - Features that deepen the existing moat
3. **Signal clarification paths:** What would resolve the uncertain signals?
   - Experiments to validate demand (e.g., "add a button that counts interest")
   - Market research to fill evidence gaps
   - Technical spikes to reduce build cost uncertainty

## Output Format

```markdown
## Alternative Directions

### Lower-Cost Variants
- **[Variant A]:** [Description] -- addresses [which user need] at [fraction of build cost because...]
- **[Variant B]:** [Description] -- ...

### Complementary Features (strengthen core instead)
- **[Feature A]:** [Description] -- strengthens [which part of core loop]
- **[Feature B]:** [Description] -- ...

### Clarify Before Deciding
- **[Uncertainty 1]:** [What's uncertain] -- validate by [specific action with expected outcome]
- **[Uncertainty 2]:** [What's uncertain] -- validate by [specific action]
```
