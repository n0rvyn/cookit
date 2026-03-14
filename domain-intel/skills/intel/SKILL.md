---
name: intel
description: "Use when the user says 'intel', 'briefing', 'what's new', 'intel status', 'intel setup', 'intel config', or asks a question about collected domain insights. Single human-facing entry point for domain intelligence: status, briefings, Q&A, configuration, and exploration."
model: sonnet
user-invocable: true
---

## Overview

The interactive entry point for domain-intel. Routes user requests to the appropriate action. Runs as haiku for fast routing; dispatches sonnet agents when deep analysis is needed.

## Process

### Step 0: Resolve Working Directory and Check Config

```
Bash(command="pwd")
```

Store the result as `WD`. **All file paths in this skill are relative to `WD`** — prefix every `./` path with `{WD}/` when calling Read, Write, Glob, or Grep. Bash commands can use relative paths as-is.

Read `{WD}/config.yaml`.
- If file does not exist AND user intent is NOT "setup" or "help" → output `[domain-intel] Not initialized. Run /intel setup in this directory.` → **stop**

### Step 1: Parse Intent

Classify the user's input:

| Intent | Trigger Patterns | Requires config |
|--------|-----------------|-----------------|
| **help** | "help", "/intel help", "how to use", "what can you do" | No |
| **setup** | "setup", "configure", "init", first run | No |
| **status** | no args, "status", "what's new" | Yes |
| **briefing** | "brief", "briefing", "brief me", "catch me up" | Yes |
| **query** | any question about a topic, "what about X", "tell me about X" | Yes |
| **config** | "config", "settings", "add source", "change keywords" | Yes |
| **explore** | an insight ID pattern (YYYY-MM-DD-source-NNN), "show me", "more about" | Yes |
| **evolve** | "evolve", "update lens", "evolve preferences", "update preferences" | Yes |

If config is required but `{WD}/config.yaml` does not exist → redirect to setup.

### Step 2: Execute by Intent

---

#### Intent: help

Output directly (no file reads needed):

```
[domain-intel] Help

Commands:
  /intel setup     — Initialize this directory as a domain-intel workspace
  /intel           — Show status (unread count, last scan)
  /intel brief     — Get a briefing on unread insights
  /intel config    — View or modify configuration
  /intel evolve    — Review and apply preference & source updates
  /intel help      — Show this help

  /scan            — Run the collection pipeline
  /digest          — Generate daily digest
  /digest week     — Generate weekly digest

Automation:
  CronCreate(cron="47 8 * * *", prompt="cd {CWD} && /scan")
  Note: cron jobs auto-expire after 3 days.

Sources:
  GitHub — uses gh CLI API (auto-detected); falls back to web search
  Product Hunt — optional, requires API credentials (/intel config to set up)
  RSS, official changelogs, figures, companies — configured in setup

Concepts:
  Directory = Profile — each initialized directory is a separate workspace
  LENS.md — your interests, figures, and companies (evolves over time)
  Insights — collected and analyzed intelligence in ./insights/
  Evolution — /intel evolve reviews accumulated signals and suggests updates
```

→ **stop**

---

#### Intent: setup

Guided first-time configuration.

1. Check if `{WD}/config.yaml` already exists:
   - If yes: "Config exists in this directory. Use `/intel config` to modify."
   - If yes but user explicitly asked for setup: proceed (reconfigure)

2. Read templates from the plugin:
   ```
   Read ${CLAUDE_PLUGIN_ROOT}/templates/default-config.yaml
   Read ${CLAUDE_PLUGIN_ROOT}/templates/default-lens.md
   ```

3. Ask about domains to track (use AskUserQuestion with multiSelect):
   - AI/ML (llm, local-inference, on-device-ai, mlx, core-ml...)
   - iOS Development (swift, swiftui, xcode, swiftdata...)
   - Indie Business (bootstrapping, revenue, pricing, distribution...)
   - Web Development (typescript, react, next.js, edge-computing...)

4. Ask about additional RSS feeds (or accept defaults from template).

5. **API source configuration**

   a. **GitHub API check** — run `Bash(command="gh auth status 2>&1")`:
      - If exit code 0 (authenticated): output `GitHub API: ✓ authenticated via gh CLI (structured search, no scraping)`
      - If exit code non-zero (gh not installed or not authenticated): output `GitHub API: ✗ gh CLI not authenticated — falling back to web search. For better results, run: gh auth login`
      - This is informational only; GitHub collection works either way (API or WebSearch fallback).

   b. **Product Hunt** — ask via AskUserQuestion:
      - "Enable Product Hunt as a source? (discovers new tools, launches, and products)"
      - Options:
        - "Yes, I have API credentials" — proceed to credential prompts
        - "Yes, set up later" — enable in config with empty credentials (skipped at scan time)
        - "No, skip" — leave disabled
      - If user chose "Yes, I have API credentials":
        - Ask via AskUserQuestion (free text): "Product Hunt Client ID?" and "Product Hunt Client Secret?"
        - Validate by running: `Bash(command="python3 \"${CLAUDE_PLUGIN_ROOT}/scripts/fetch_producthunt.py\" --client-id \"<id>\" --client-secret \"<secret>\" --max-items 1 --timeout 15")` (check exit code of the script directly; do NOT pipe to tail/grep which overrides the exit code)
        - If exit code 0: `Product Hunt API: ✓ authenticated`
        - If exit code 1: `Product Hunt API: ✗ authentication failed — check credentials. You can update them later in config.yaml under sources.producthunt.`  Set enabled to true but keep the user's credentials (they may fix them later).
      - Link for getting credentials: `https://www.producthunt.com/v2/oauth/applications`

6. Generate `{WD}/config.yaml` from template with user selections (domains, sources, Product Hunt config from step 5b).

7. Create subdirectories:
   ```
   mkdir -p ./insights ./digests ./trends ./briefings
   ```

8. Initialize state:
   Write `{WD}/state.yaml`:
   ```yaml
   last_scan: "never"
   total_insights: 0
   total_scans: 0
   ```

9. **Generate LENS.md** — the user's information filtering profile.

   a. For each selected domain, ask using AskUserQuestion:
      - "Notable figures to follow in {domain}?" — present pre-populated options from the template (e.g., for AI: Hinton, LeCun, Karpathy; for iOS: Lattner, Sundell, Hudson). Allow multiSelect.
      - "Companies to track in {domain}?" — present pre-populated options (e.g., for AI: OpenAI, Anthropic, DeepMind; for iOS: Apple). Allow multiSelect.
      - For each selected company: confirm the `url` from the template (e.g., "OpenAI → https://openai.com — correct?"). If user corrects it, use their URL.

   b. Ask about the user's focus (free text via AskUserQuestion):
      - "Briefly describe yourself and what you build"
      - "What specific topics interest you most?" (with examples from selected domains)
      - "What questions are you trying to answer right now?" (2-3 questions)
      - "Any topics to explicitly filter out?"

   c. Generate `{WD}/LENS.md` using the template structure:
      - Frontmatter: populate `figures[]` and `companies[]` from user selections (uncomment chosen entries, leave others commented)
      - Body: fill in "Who I Am", "What I Care About", "Current Questions", "What I Don't Care About" from user answers

10. Output:
```
[domain-intel] Setup complete in {CWD}.
  Domains: {domain names}
  Sources:
    GitHub: {✓ API | ✗ web search fallback}
    Product Hunt: {✓ enabled | ✗ disabled | ⚠ enabled, credentials pending}
    RSS feeds: {N}
    Official sites: {N}
  LENS: ./LENS.md (tracking {N} figures, {N} companies)

Next steps:
  /scan — run your first collection
  /intel evolve — review and update your preferences over time
  Set up automated scanning with CronCreate:
    CronCreate(cron="47 8 * * *", prompt="cd {CWD} && /scan")
  Note: cron jobs auto-expire after 3 days.
```

---

#### Intent: status

Quick overview of current state.

1. Read `{WD}/state.yaml`
2. Count unread insights:
   ```
   Grep(pattern="read: false", path="{WD}/insights/", output_mode="count")
   ```
3. Count total insight files this month:
   ```
   Glob(pattern="{WD}/insights/{current_YYYY-MM}/*.md")
   ```

4. Output:
```
[domain-intel] Status
  Last scan: {last_scan}
  Total scans: {total_scans}
  Unread insights: {N}
  This month: {N} insights
  Total all-time: {total_insights}
```

If unread > 0: append `Use /intel brief for a briefing.`

---

#### Intent: briefing

Synthesize unread insights into a briefing.

1. Find all unread insight files:
   ```
   Grep(pattern="read: false", path="{WD}/insights/", output_mode="files_with_matches")
   ```

2. If count == 0:
   "No unread insights. Last scan: {date}. Run /scan to collect new data."
   → **stop**

3. If count > 50: sort files by filename (which encodes date) descending, take the most recent 50. Output: `"Showing most recent 50 of {N} unread insights. Run /intel brief again for the rest."`

4. Read the selected unread insight files (up to 50).

5. Find any convergence signal files from the same dates:
   ```
   Grep(pattern="type: signal", path="{WD}/insights/", output_mode="files_with_matches")
   ```

6. Load previous trends (most recent file in `{WD}/trends/`).

7. Load LENS.md if it exists: read `{WD}/LENS.md`, extract body as `lens_context`.

8. Dispatch `trend-synthesizer` agent with:
   - **insights**: unread insight contents
   - **convergence_signals**: matching signal files
   - **domains**: from config
   - **time_range**: earliest unread date to today
   - **previous_trends**: latest trend snapshot
   - **lens_context**: LENS.md body (or omit if no LENS.md)
   - (no query — Mode A)

9. **Save trend snapshot** for continuity (so future digests/briefings can track trend lifecycle):
   ```
   Write trend snapshot to {WD}/trends/{today}-briefing-trends.md
   ```
   Use the same format as digest Step 6 (date, range, trends, surprises).

10. Present the synthesis as a briefing (format like digest but labeled "Briefing").

11. **Save briefing** to `{WD}/briefings/{YYYY-MM-DD}-briefing.md`:

```markdown
---
date: {YYYY-MM-DD}
insight_count: {N}
---

# Briefing — {YYYY-MM-DD}

> {headline}

## Trends

| Trend | Direction | Evidence |
|-------|-----------|----------|
{For each trend: | {name} | {direction} | {N} insights |}

{For each trend:}
### {name}

{summary}

## Surprises

{For each surprise:}
**{title}** — {why}
*Ref: {insight_id}*

## Collective Wisdom

{collective_wisdom}

---
*Insights briefed: {N} | Generated: {timestamp}*
```

12. Batch mark all briefed insights as `read: true`:
   ```
   Bash: sed -i.bak 's/^read: false$/read: true/' {space-separated list of file paths} && rm -f {same paths with .bak suffix}
   ```

---

#### Intent: query

Answer a specific question from accumulated intelligence.

1. Extract the query topic from user input. Generate 2-3 synonym/related terms for broader matching (e.g., "local AI models" → also search "on-device inference", "edge AI", "MLX").

2. Search insights for relevant content using each term:
   ```
   Grep(pattern="{term}", path="{WD}/insights/", output_mode="files_with_matches", head_limit=20)
   ```
   Also search trends:
   ```
   Grep(pattern="{term}", path="{WD}/trends/", output_mode="files_with_matches", head_limit=5)
   ```
   Merge and deduplicate file lists from all term searches.

3. If zero results across all searches:
   "No insights found matching '{query}'. Try broader terms, or run /scan to collect new data."
   → **stop**

4. Read matching files.

4.5. Load LENS.md if it exists: read `{WD}/LENS.md`, extract body as `lens_context`.

5. Dispatch `trend-synthesizer` agent with:
   - **insights**: matching insight contents
   - **domains**: from config
   - **time_range**: range of matching insights
   - **query**: the user's specific question
   - **lens_context**: LENS.md body (or omit if no LENS.md)

6. Present the query-directed synthesis, including:
   - Direct answer with confidence level
   - Supporting insight IDs (as references)
   - Related queries to explore

7. **Query signal**: If the query topic is not reflected in LENS.md "Current Questions" and LENS.md exists, append a signal to `{WD}/.lens-signals.yaml`:
   ```yaml
   - date: YYYY-MM-DD
     type: new-interest
     value: "{query topic}"
     evidence: ["user-query"]
   ```
   This captures emergent interests for `/intel evolve` to surface later.

---

#### Intent: config

View or modify configuration.

1. Read and display current config from `{WD}/config.yaml`:
   - Active domains (names)
   - Source counts (RSS feeds, official sites, GitHub API status, Product Hunt status)
   - Scan parameters
   - LENS.md status: exists? How many figures/companies tracked?
   - For GitHub: run `gh auth status 2>&1` and report authenticated or not
   - For Product Hunt: report enabled/disabled, credentials present or empty

2. If user provided a modification request:
   - **add RSS feed**: append to sources.rss list
   - **add official site**: append to sources.official list
   - **add domain**: prompt for name, append to domains
   - **change setting**: update the specified value
   - **remove source/domain**: remove from the list
   - **edit LENS**: redirect to `/intel evolve` or open LENS.md path for manual editing
   - **configure product hunt** / **add PH token**: prompt for client_id and client_secret, validate with fetch_producthunt.py, update sources.producthunt in config
   - **check github**: run `gh auth status` and report result

3. After modification: write updated config back to `{WD}/config.yaml`.

4. Confirm the change: "Updated: {description of change}"

---

#### Intent: explore

Deep dive into a specific insight.

1. Parse the insight ID from input (pattern: `YYYY-MM-DD-source-NNN`)

2. Find the file:
   ```
   Grep(pattern="id: {id}", path="{WD}/insights/", output_mode="files_with_matches")
   ```

3. If not found: "Insight {id} not found." → **stop**

4. Read and display the full insight file.

5. Find related insights (same tags or category):
   - Extract tags from the insight
   - For each tag (up to 3):
     ```
     Grep(pattern="{tag}", path="{WD}/insights/", output_mode="files_with_matches", head_limit=5)
     ```
   - Exclude the current insight from results

6. If related insights found:
   Read their titles and significance. Output:
   ```
   Related insights:
     - {id}: {title} (significance: {N})
     - {id}: {title} (significance: {N})
   ```

7. Mark the explored insight as `read: true` if it wasn't already.

---

#### Intent: evolve

Review and apply evolution proposals for both LENS.md and config.yaml.

1. Check prerequisites:
   - `{WD}/LENS.md` must exist → if not: "No LENS.md found. Run `/intel setup` first." → **stop**
   - Read current `{WD}/LENS.md`
   - Read current `{WD}/config.yaml`

2. Read `{WD}/.lens-signals.yaml`:
   - If file doesn't exist or is empty → "No evolution signals detected yet. Run more scans to accumulate signals." → **stop**

3. Group signals by type and deduplicate (same value across multiple dates → merge, keep all evidence IDs).

4. For each signal group, present using AskUserQuestion:

   **LENS signals:**

   **new-interest signals:**
   - "Add '{value}' to your interests? (appeared in {N} insights: {evidence IDs})"
   - Options: "Add to What I Care About", "Add to What I Don't Care About", "Skip"

   **new-figure signals:**
   - "Track {value} as a notable figure? (mentioned in {N} insights)"
   - Options: "Add to figures (with domain auto-detected)", "Skip"
   - If added: ask for optional `blog_url`

   **new-company signals:**
   - "Track {value} as a company? (mentioned in {N} insights)"
   - Options: "Add to companies (with domain auto-detected)", "Skip"
   - If added: ask for `url` and `paths[]` (suggest common patterns like /blog, /news)

   **Source signals:**

   **suggest-rss signals:**
   - "Add {value} to RSS feeds? ({reason})"
   - Options: "Add to RSS feeds", "Skip"

   **suggest-official-path signals:**
   - "Add path to {company} official pages? ({reason})"
   - Options: "Add to company paths", "Skip"

   **suggest-domain signals:**
   - "Add '{value}' as a new tracking domain? (appeared as tag in {N} insights)"
   - Options: "Add domain", "Skip"

5. Apply approved changes:
   - **LENS.md changes:**
     - For interests: append to the appropriate body section
     - For figures: add to frontmatter `figures[]`
     - For companies: add to frontmatter `companies[]`
   - **config.yaml changes:**
     - For suggest-rss: append `{name: auto-detected, url: value}` to `sources.rss[]`
     - For suggest-official-path: find the matching company in LENS.md, append path to `paths[]`
     - For suggest-domain: append `{name: value}` to `domains[]`

6. Clear processed signals from `{WD}/.lens-signals.yaml` (remove entries that were presented, whether approved or skipped).

7. Output:
```
[domain-intel] Profile updated.
  LENS:
    Added interests: {N}
    Added figures: {N}
    Added companies: {N}
  Sources:
    Added RSS feeds: {N}
    Added official paths: {N}
    Added domains: {N}
  Skipped: {N}
  Remaining signals: {N}
```
