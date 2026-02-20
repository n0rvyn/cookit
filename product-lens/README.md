# product-lens

Product evaluation plugin for indie developers. Assesses demand, market viability, moat, and execution quality using PM frameworks (JTBD, Lean Canvas, RICE) calibrated for solo/small-team developers.

## Commands

| Command | Description |
|---------|-------------|
| `/evaluate` | Full evaluation of a single product (local project or external app) |
| `/compare` | Compare multiple products; produces scoring matrix and recommendations |
| `/demand-check` | Quick first-pass demand validation (5-minute filter) |
| `/teardown` | Deep dive into a single evaluation dimension |

## Evaluation Dimensions

| Dimension | Core Question |
|-----------|--------------|
| **Demand Authenticity (需求真伪)** | Is this pain point painful enough to make people pay an unknown indie? |
| **Journey Completeness (逻辑闭环)** | Is the core journey maintainable by one person and free of dead ends? |
| **Market Space (市场空间)** | Is the niche big enough for indie revenue but small enough to avoid incumbents? |
| **Business Viability (商业可行)** | After platform cuts, can this generate sustainable indie income? |
| **Moat (护城河)** | What stops a well-funded competitor or AI from replicating this? |
| **Execution Quality (执行质量)** | Is tech debt within one person's control? Is it appropriately engineered? |

Each dimension's sub-questions are split into **universal** (always apply) and **platform-specific** (replaced by overlay when applicable).

### Extra Modules

- **Kill Criteria** — auto-generated "stop if" conditions to combat sunk cost fallacy
- **Feature Necessity Audit** — must-keep / simplify / cut analysis (local projects only)
- **Elevator Pitch Test** — can you describe value in a tagline + one sentence?
- **Pivot Directions** — adjacent opportunities based on existing code assets and domain knowledge

## Architecture

### Agents

| Agent | Model | Purpose |
|-------|-------|---------|
| `product-evaluator` | Opus | Core evaluation engine; scores all dimensions and generates the full report |
| `market-scanner` | Sonnet | Market research; gathers competitor data, pricing, and market signals |

### Skills

| Skill | Type | Auto-trigger |
|-------|------|-------------|
| `evaluate` | Full pipeline (market-scanner → product-evaluator) | No |
| `compare` | Parallel evaluations + comparison matrix + maturity signals | No |
| `demand-check` | Demand dimension + elevator pitch only; no agent dispatch | Yes |
| `teardown` | Single-dimension deep dive with sub-scores | No |

## Platform Overlays

When evaluating iOS apps, the plugin loads `references/ios-overlay.md` which **replaces the platform-specific sub-questions** for each dimension with iOS-specific variants. Universal sub-questions are always retained. This includes:

- Sherlock risk assessment with scoring methodology
- App Store category saturation analysis
- WWDC annual maintenance burden
- Apple's 30% revenue cut impact
- CloudKit data lock-in as moat
- ATT impact on ad-supported models
- visionOS/watchOS early-mover opportunities
- Privacy label maintenance burden

The overlay is auto-detected via project files (`.xcodeproj`, `Package.swift`) or user specification.

## Scoring

Each dimension receives a 1-5 star score with evidence-based justification. Scores are combined using configurable weights:

- **Default:** equal weights across all dimensions
- **Validation phase:** demand and market weighted higher
- **Growth phase:** business viability and moat weighted higher
- **Maintenance phase:** execution quality and moat weighted higher

Significance threshold: when comparing products, score differences ≤ 0.5 are not meaningful.

## Usage Examples

```
# Evaluate a local iOS project
/evaluate /path/to/my-ios-app

# Evaluate an external app
/evaluate "Bear"

# Quick demand check on an idea
/demand-check "A markdown note app for developers"

# Compare your projects to decide focus
/compare /path/to/app1 /path/to/app2 "Competitor"

# Deep dive into one dimension
/teardown moat /path/to/my-app
```
