### D5.1 Skill description overlap

1. Read the `description` field of the skill being reviewed
2. Read the `description` fields of all other skills in the same plugin
3. Flag: if two skills' descriptions would match the same user input (e.g., both trigger on "review code")
4. Quantify overlap: list the ambiguous trigger phrases

### D5.2 Agent description overlap

1. Read the `description` field (including examples) of the agent being reviewed
2. Read descriptions of all other agents in the same plugin
3. Flag: if two agents' example triggers overlap

---

### D7.3 Description quality

| Check | How | Severity if fails |
|-------|-----|-------------------|
| Length < 20 characters | Count characters in `description` field | Logic |
| Length > 500 characters | Count characters in `description` field | Logic |
| No trigger condition | Description lacks patterns: "Use when", "when the user says", "当...时使用", "after", keyword enumeration | Logic |
| Pure noun phrase | Description has no verb or action phrase — just a label (e.g., "App Store review helper") | Minor |
| Trigger overlap with sibling skill | Generate 3 representative user queries from this description; check if another skill in the same plugin would also match | Logic (extends D5.1) |

For `disable-model-invocation: true` skills: trigger condition check is relaxed (these are dispatched programmatically, not by user prompt).

---

### D9.1 Description trigger quality

For each skill being reviewed:

| Check | How | Severity if fails |
|-------|-----|-------------------|
| Description starts with trigger pattern | Grep for patterns: "Use when", "Use for", "Use after", "Use before", "当.*时使用", or equivalent trigger phrase | Logic |
| Description has concrete trigger scenario, not just vague words | Scan for standalone vague terms: "guidance", "best practices", "optional", "helper" without accompanying trigger scenario | Logic |
| For mactools skills: description has both Chinese AND English | Check for presence of both CJK characters and English alphabets | Logic |
