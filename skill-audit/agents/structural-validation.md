### Dimension 1: Structural Validation

Check the YAML frontmatter and file organization.

**For skills (SKILL.md):**

| Check | How | Severity if fails |
|-------|-----|-------------------|
| `name` field exists | Read frontmatter | Bug |
| `name` matches directory name | Compare `name:` value with parent directory name | Bug |
| `description` field exists and is non-empty | Read frontmatter | Bug |
| File has `## Process` or equivalent workflow section | Scan headings | Logic |
| File has `## Completion Criteria` section | Scan headings | Logic |

**For agents (.md):**

| Check | How | Severity if fails |
|-------|-----|-------------------|
| `name` field exists | Read frontmatter | Bug |
| `name` matches filename (without .md) | Compare `name:` with filename | Bug |
| `description` field exists | Read frontmatter | Bug |
| `description` has `<example>` blocks | Grep for `<example>` in description | Logic |
| `model` is valid (`opus` / `sonnet` / `haiku`) | Read frontmatter | Bug |
| `tools` lists only valid tools | Check against: Glob, Grep, Read, Bash, Write, Edit, WebSearch, WebFetch, NotebookEdit, Task | Bug |
| Read-only agent has `## Constraint` section | Scan headings + check for "Do NOT modify" language | Logic |
| Read-only agent does NOT list Write/Edit/NotebookEdit in `tools` | Cross-check tools list with constraint | Bug |
| `color` is valid if present | Check against: yellow, blue, cyan, green, purple | Minor |

---

### Dimension 2: Reference Integrity

Check that all cross-references between artifacts resolve correctly.

**Skill → Agent references:**
1. Grep the skill file for patterns: `` `{name}` agent ``, `launch the`, `dispatch`, `Task tool`
2. Extract every agent name referenced
3. For each: verify a matching `.md` file exists in the plugin's `agents/` directory
4. If the reference uses cross-plugin syntax (`plugin:agent`), verify both the plugin directory and the agent file exist

**Agent dispatch prompt ↔ Agent inputs:**
1. In the skill, find the dispatch prompt template (usually in a code block after "Structure the task prompt as")
2. In the agent, find the `## Inputs` section
3. Check: does every field the agent's Inputs section requires appear in the skill's dispatch template?
4. Check: does the skill's template include fields the agent doesn't expect? (not necessarily a bug, but worth noting)

**Agent description examples ↔ Skill trigger:**
1. Read agent description `<example>` blocks
2. Check: do the example user messages align with what would actually trigger the dispatching skill?
3. Flag if examples describe direct user invocation but the agent is only ever dispatched by a skill (misleading routing)
