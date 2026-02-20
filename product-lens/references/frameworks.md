# Product Lens: Evaluation Frameworks

> Indie developer-calibrated product evaluation. Every dimension is framed from the perspective of a solo/small-team developer, not enterprise PM.

---

## Section 1: Indie Developer Calibration

### How Indie Evaluation Differs from Enterprise PM

| Aspect | Enterprise PM | Indie Developer |
|--------|--------------|-----------------|
| Market sizing | TAM in billions | Niche big enough for one person |
| Competition | Market share battles | Finding gaps big companies ignore |
| Revenue model | LTV/CAC optimization | After 30% platform cut, what remains? |
| Team scaling | Can we hire fast enough? | Can one person maintain this? |
| Moat | Network effects, patents | Taste, domain expertise, data accumulation |
| Risk | Market risk | Sunk cost fallacy, Sherlock risk |

### Scoring Rubric (1-5 Stars)

All dimensions use a 1-5 star scale with indie-specific anchors:

| Score | Meaning |
|-------|---------|
| ★☆☆☆☆ (1) | Fatal flaw: this dimension alone could kill the project |
| ★★☆☆☆ (2) | Serious concern: requires major changes to become viable |
| ★★★☆☆ (3) | Acceptable: not a strength, not a blocker; needs monitoring |
| ★★★★☆ (4) | Strong: clear advantage in this dimension |
| ★★★★★ (5) | Exceptional: rare, defensible strength |

Rule: every score must include a one-sentence justification citing specific evidence (code location, market data, or user signal). Vague assessments ("decent", "not bad", "pretty good") are forbidden.

### Sub-Question Structure

Each dimension's sub-questions are split into two groups:

- **Universal sub-questions:** Always apply regardless of platform. These are platform-neutral analysis questions.
- **Platform-specific sub-questions:** Replaced by platform overlay when applicable (e.g., iOS overlay). When no overlay is active, use the default platform-specific questions listed here.

---

## Section 2: Evaluation Dimensions

### Dimension 1: Demand Authenticity (需求真伪)

**Core question:** Is this pain point painful enough to make people pay an unknown indie developer for a no-brand app?

**Universal sub-questions:**
1. **JTBD analysis:** What job is the user "hiring" this product to do? What are the existing alternatives (including "do nothing")?
2. **Pain frequency x severity:** Where does this fall on the matrix?
   - High-frequency + high-pain = must-have (best case)
   - High-frequency + low-pain = utility/tool (viable if friction-free)
   - Low-frequency + high-pain = insurance-type (hard to market)
   - Low-frequency + low-pain = nice-to-have (dangerous for indie)
3. **Sean Ellis test proxy:** If this product disappears tomorrow, do users scramble for alternatives or shrug?
4. **Code signal check:** Is 80% of code serving the core value proposition, or is the value buried under feature bloat? (local projects only)

**Platform-specific sub-questions:** (replaced by overlay when applicable)
5. **Switching cost from alternatives:** What do users give up by not switching to this product? What do they give up by switching?

**Evidence sources:**
- Local: README problem statement, user-facing feature list, code complexity distribution across features
- External: App Store reviews (complaint themes), Reddit/forum discussions, search volume for the problem

**Scoring anchors:**
| Score | Anchor |
|-------|--------|
| ★ | Solving a problem nobody has, or a problem with abundant free solutions |
| ★★ | Real problem but low pain; users tolerate current alternatives |
| ★★★ | Genuine pain point; some users would pay, but alternatives are "good enough" for most |
| ★★★★ | Clear unmet need; existing alternatives have obvious gaps; users actively complain |
| ★★★★★ | Hair-on-fire problem; users already hacking together workarounds; high willingness to pay |

---

### Dimension 2: Journey Completeness (逻辑闭环)

**Core question:** Is the core user journey simple enough that one person can maintain it, and complete enough that users don't hit dead ends?

**Universal sub-questions:**
1. **Entry → Core action → Result → Retention:** Does each stage connect without friction?
2. **Data lifecycle:** Create → Use → Update → Delete/Archive — is the full cycle implemented?
3. **Complexity budget:** How many distinct screens/states exist? Can one developer hold the entire flow in their head?
4. **First-run experience:** Can a new user reach the "aha moment" without a tutorial?

**Platform-specific sub-questions:** (replaced by overlay when applicable)
5. **Exception paths:** Can users recover from errors? Do empty states provide guidance instead of blank screens?

**Evidence sources:**
- Local: View/screen navigation graph, state machine completeness, error handling coverage, empty state implementations
- External: Onboarding flow analysis, user reviews mentioning confusion or missing features

**Scoring anchors:**
| Score | Anchor |
|-------|--------|
| ★ | Core journey has dead ends or broken states; users can't complete basic tasks |
| ★★ | Happy path works but exceptions crash or confuse; missing data lifecycle stages |
| ★★★ | Core journey complete; some edge cases unhandled; manageable complexity |
| ★★★★ | Tight journey with good error recovery; complexity well within one-person capacity |
| ★★★★★ | Elegant minimal journey; every state accounted for; zero dead ends |

---

### Dimension 3: Market Space (市场空间)

**Core question:** Is this niche big enough to sustain one person, and small enough that big companies won't bother?

**Universal sub-questions:**
1. **Niche viability:** Is the addressable market large enough for indie-scale revenue ($5K-$50K/month) but small enough to fly under enterprise radar?
2. **Competition density:** How many direct competitors exist? Are they well-funded or also indie?
3. **Indirect substitutes:** What non-obvious alternatives exist (spreadsheets, manual processes, general-purpose tools)?
4. **Timing:** Why now? What has changed (infrastructure, user habits, platform capabilities, regulations) that makes this viable today?

**Platform-specific sub-questions:** (replaced by overlay when applicable)
5. **Differentiation statement:** One sentence on why a user would switch from the top competitor. If you can't write this sentence, score ≤2.

**Evidence sources:**
- Local: Target audience described in docs, pricing strategy if documented
- External: App Store/web category rankings, competitor count and funding, search volume trends, recent market entrants or exits

**Scoring anchors:**
| Score | Anchor |
|-------|--------|
| ★ | Saturated market with well-funded incumbents; no differentiation angle |
| ★★ | Crowded but possible; differentiation is marginal ("slightly better UI") |
| ★★★ | Viable niche; some competitors but clear angle; timing is neutral |
| ★★★★ | Underserved niche; few competitors; favorable timing signal |
| ★★★★★ | Clear gap in market; timing is perfect; differentiation is obvious and defensible |

---

### Dimension 4: Business Viability (商业可行)

**Core question:** After the platform takes its cut, can this generate sustainable indie-scale income through discoverable channels?

**Universal sub-questions:**
1. **Revenue model clarity:** Who pays, why, how much? Is the model proven in this category?
2. **Willingness-to-pay signals:** Are users already paying for inferior alternatives? Or is "free" the expected price in this category?
3. **Pricing power:** Can you charge premium (>$4.99/month) or is this a race-to-bottom category?

**Platform-specific sub-questions:** (replaced by overlay when applicable)
4. **Unit economics at indie scale:** Not LTV/CAC ratios — can you reach $5K+/month with realistic conversion rates and zero marketing budget?
5. **Discovery channels:** How do users find this product? Is there at least one organic channel (SEO, ASO, word-of-mouth, community)?

**Evidence sources:**
- Local: Pricing/monetization code, subscription tiers, paywall implementation
- External: Competitor pricing, App Store category pricing norms, review volume as demand proxy

**Scoring anchors:**
| Score | Anchor |
|-------|--------|
| ★ | No clear revenue model; category expects free; no discovery channel |
| ★★ | Revenue model exists but unproven in category; discovery requires paid acquisition |
| ★★★ | Standard model for category; at least one organic discovery channel; modest pricing power |
| ★★★★ | Users demonstrably pay in this category; multiple discovery channels; room for premium pricing |
| ★★★★★ | Strong willingness to pay; viral/organic discovery built-in; pricing power from differentiation |

---

### Dimension 5: Moat (护城河)

**Core question:** What stops a well-funded competitor or AI from replicating this in a weekend?

**Universal sub-questions:**
1. **Taste moat:** Is the product's quality a result of opinionated design that's hard to copy without the same sensibility?
2. **Data accumulation:** Do users build up valuable data over time that increases switching costs?
3. **Domain expertise:** Does the product encode rare domain knowledge that competitors would need years to acquire?
4. **Network effects:** Does more users = better product? (Rare for indie apps, but powerful if present)

**Platform-specific sub-questions:** (replaced by overlay when applicable)
5. **AI disruption risk:** If LLM capabilities advance another generation, does this product still provide value? Or does AI make it obsolete?

**Evidence sources:**
- Local: Data model complexity, domain-specific logic, unique algorithms, user data storage patterns
- External: AI tool landscape in this category, competitor feature velocity, platform risk signals

**Scoring anchors:**
| Score | Anchor |
|-------|--------|
| ★ | Pure feature play; AI or a weekend project could replicate; no switching costs |
| ★★ | Minor taste advantage; some user data but easily exported; AI could approximate |
| ★★★ | Meaningful taste or domain moat; moderate data accumulation; AI augments but doesn't replace |
| ★★★★ | Strong domain expertise encoded; significant user data lock-in; AI-resistant core value |
| ★★★★★ | Multiple moat layers; deep data + domain + taste; competitors would need to match years of iteration |

---

### Dimension 6: Execution Quality (执行质量)

**Core question:** Is the technical debt within one person's control, and is the codebase appropriately engineered (not over or under)?

**Universal sub-questions:**
1. **Architecture health:** Are there tech debt signals (massive files, circular dependencies, TODO/FIXME density)?
2. **Dependency burden:** How many third-party dependencies? Are any unmaintained or risky?
3. **Over-engineering detection:** Is there premature abstraction, unused infrastructure, or enterprise patterns in an indie codebase?
4. **Completeness:** Feature completeness vs. polish level — is the core solid or half-finished?

**Platform-specific sub-questions:** (replaced by overlay when applicable)
5. **Maintenance burden:** Can one person realistically keep this running (platform updates, dependency updates, bug fixes)?

**Evidence sources:**
- Local: Code structure analysis, dependency count, TODO/FIXME grep, test coverage, file size distribution
- External: Technology choices vs. category norms, update frequency, changelog quality

**Scoring anchors:**
| Score | Anchor |
|-------|--------|
| ★ | Severe tech debt; fragile architecture; unmaintainable by one person |
| ★★ | Significant issues but functional; over-engineered or under-tested; risky dependencies |
| ★★★ | Adequate quality; some debt but manageable; appropriate engineering level |
| ★★★★ | Clean architecture; minimal debt; good dependency choices; one person can maintain confidently |
| ★★★★★ | Exemplary for indie scale; tight codebase; zero unnecessary complexity; sustainable indefinitely |

---

## Section 3: Extra Modules

### Kill Criteria

**Purpose:** Indie developers' biggest enemy is sunk cost fallacy. Every evaluation auto-generates concrete "stop if" conditions.

**Generation rules:**
1. Each criterion must be **verifiable** — not "if it doesn't work out" but "if [specific measurable condition]"
2. Include a **timeframe** where applicable — "if after 3 months of launch, [condition]"
3. Derive criteria from the weakest dimensions (scored ≤2 stars)
4. Always include at least one **external trigger** (market event, competitor action, platform change)

**Output format:**
```
## Kill Criteria
1. [Verifiable condition with timeframe]
2. [External trigger condition]
3. [Metric-based condition]
```

---

### Feature Necessity Audit

**Purpose:** "Strip down to what minimum, and the product still works?" — identify the features one person can realistically maintain.

**Methodology:**
1. List all user-facing features (from code analysis, not documentation claims)
2. For each feature, assess:
   - Does it serve the core JTBD? (Yes = must keep)
   - Can it be simplified without losing core value? (Yes = simplify)
   - Would removing it reduce maintenance burden significantly? (Yes = candidate for cutting)
3. Check dependency graph: does cutting feature X break feature Y?

**Output format:**
```
## Feature Necessity Audit
- Must keep: [feature] — [why it serves core JTBD]
- Can simplify: [feature] — [what to simplify and why]
- Recommend cutting: [feature] — [maintenance cost vs. value delivered]
```

**Constraint:** Only available for local projects (requires code access). Skip for external evaluations.

---

### Elevator Pitch Test

**Purpose:** If you can't explain the value concisely, you haven't found the value.

**Constraints:**
- Short tagline: ≤30 characters (App Store subtitle length)
- Plus first description sentence: one line that makes users act
- Combined: tagline + sentence must convey the core value proposition

**Judgment criteria:**
| Verdict | Meaning |
|---------|---------|
| Clear | Tagline + sentence immediately convey value; target user would act |
| Vague | Value is there but expression is unclear; needs refinement |
| Cannot articulate | Cannot express value concisely; signals unclear product vision |

**Process:**
1. Attempt to write the tagline + sentence based on product understanding
2. Judge: would the target user understand what this does AND why they need it?
3. If "cannot articulate": this signals the product vision needs clarification, not just the copy

---

### Pivot Directions

**Purpose:** Not starting from zero — given existing code assets and domain knowledge, what adjacent directions could you pivot to?

**Methodology:**
1. Inventory existing assets:
   - Code: what reusable components, data models, integrations exist?
   - Knowledge: what domain expertise has been accumulated?
   - Data: what user data or content has been created?
   - Audience: what users or community has been built?
2. For each asset, brainstorm adjacent problems it could solve
3. Filter: which pivot directions have better dimension scores than the current direction?

**Output format:**
```
## Pivot Directions
- **Direction A:** [description] — leverages existing [asset X]
- **Direction B:** [description] — leverages existing [asset Y]
- **Direction C:** [description] — leverages existing [asset Z]
```

---

## Section 4: Scoring & Weighting

### Default Weights

All dimensions weighted equally by default:

| Dimension | Default Weight |
|-----------|---------------|
| Demand Authenticity | 1.0 |
| Journey Completeness | 1.0 |
| Market Space | 1.0 |
| Business Viability | 1.0 |
| Moat | 1.0 |
| Execution Quality | 1.0 |

### Weight Presets

**Validation phase** (idea stage, pre-build):
| Dimension | Weight |
|-----------|--------|
| Demand Authenticity | 2.0 |
| Market Space | 1.5 |
| Business Viability | 1.5 |
| Moat | 0.5 |
| Journey Completeness | 0.5 |
| Execution Quality | 0.0 |

**Growth phase** (launched, seeking traction):
| Dimension | Weight |
|-----------|--------|
| Business Viability | 2.0 |
| Moat | 1.5 |
| Demand Authenticity | 1.0 |
| Market Space | 1.0 |
| Journey Completeness | 1.0 |
| Execution Quality | 0.5 |

**Maintenance phase** (established, sustaining):
| Dimension | Weight |
|-----------|--------|
| Execution Quality | 2.0 |
| Moat | 1.5 |
| Business Viability | 1.0 |
| Demand Authenticity | 1.0 |
| Journey Completeness | 1.0 |
| Market Space | 0.5 |

### Weighted Score Formula

```
Weighted Total = Sum(dimension_score * weight) / Sum(weight)
```

Result is a 1.0-5.0 scale. Display as one decimal place (e.g., 3.7).

### Significance Threshold

When comparing products, a weighted total difference ≤ 0.5 is not meaningful. Mark such pairs as "difference not significant — compare individual dimensions."

Do not recommend Focus/Maintain/Stop based solely on total score when the gap between two products is ≤ 0.5.

### Comparison Ranking

When comparing multiple products:
1. Compute weighted total for each product
2. Rank by total score (highest first)
3. Apply significance threshold — flag pairs within 0.5 of each other
4. Flag any product with a dimension scored ≤2 (potential kill criteria trigger)
5. Provide Focus / Maintain / Stop recommendation for each (respecting significance threshold)
