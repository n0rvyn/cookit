---
name: intel
description: "Use when the user says 'intel', 'briefing', 'what's new', 'intel status', 'intel setup', 'intel config', or asks a question about collected domain insights. Single human-facing entry point for domain intelligence: status, briefings, Q&A, configuration, and exploration."
model: haiku
user-invocable: true
---

## Overview

The interactive entry point for domain-intel. Routes user requests to the appropriate action. Runs as haiku for fast routing; dispatches sonnet agents when deep analysis is needed.

## Process

### Step 0: Check Config

Read `~/.claude/domain-intel.local.md`.
- If file does not exist AND user intent is NOT "setup" → output `[domain-intel] Not configured. Run /intel setup to get started.` → **stop**
- If file exists, parse YAML frontmatter and extract `data_dir`.

### Step 1: Parse Intent

Classify the user's input:

| Intent | Trigger Patterns | Requires data_dir |
|--------|-----------------|-------------------|
| **setup** | "setup", "configure", "init", first run | No |
| **status** | no args, "status", "what's new" | Yes |
| **briefing** | "brief", "briefing", "brief me", "catch me up" | Yes |
| **query** | any question about a topic, "what about X", "tell me about X" | Yes |
| **config** | "config", "settings", "add source", "change keywords" | Yes |
| **explore** | an insight ID pattern (YYYY-MM-DD-source-NNN), "show me", "more about" | Yes |

If `data_dir` is required but not configured → redirect to setup.

### Step 2: Execute by Intent

---

#### Intent: setup

Guided first-time configuration.

1. Check if `~/.claude/domain-intel.local.md` already exists:
   - If yes: "Config exists. Use `/intel config` to modify. Current data_dir: {data_dir}"
   - If yes but user explicitly asked for setup: proceed (reconfigure)

2. Read template from the plugin's templates directory:
   ```
   Glob(pattern="${CLAUDE_PLUGIN_ROOT}/templates/default-config.yaml")
   ```
   Read the template file.

3. Ask the user using AskUserQuestion:
   - "Where should domain-intel store its data?" with options:
     - `~/Knowledge/domain-intel` (Recommended)
     - `~/Documents/domain-intel`
     - `~/Notes/domain-intel`
     - Other (custom path)

4. Ask about domains to track (use AskUserQuestion with multiSelect):
   - AI/ML (llm, local-inference, on-device-ai, mlx, core-ml...)
   - iOS Development (swift, swiftui, xcode, swiftdata...)
   - Indie Business (bootstrapping, revenue, pricing, distribution...)
   - Web Development (typescript, react, next.js, edge-computing...)

5. For each selected domain, the template already has keyword profiles. Use defaults unless user specifies custom keywords.

6. Ask about additional RSS feeds (or accept defaults from template).

7. Generate `~/.claude/domain-intel.local.md`:

```markdown
---
data_dir: {chosen_path}

domains:
  {selected domains with keyword profiles from template}

sources:
  github:
    enabled: true
    languages: [swift, python, typescript]
    min_stars: 50
  rss:
    {feeds from template + user additions}
  official:
    {sites from template}

scan:
  max_items_per_source: 20
  significance_threshold: 2
---

# Domain Intel Configuration

Data directory: {data_dir}
Configured: {date}

## Notes

Add custom notes about your tracking preferences here.
```

8. Create the data directory structure:
   ```
   mkdir -p {data_dir}/{insights,digests,trends}
   ```

9. Initialize state:
   Write `{data_dir}/state.yaml`:
   ```yaml
   last_scan: "never"
   total_insights: 0
   total_scans: 0
   ```

10. Output:
```
[domain-intel] Setup complete.
  Data directory: {data_dir}
  Domains: {domain names}
  Sources: {N} RSS feeds, {N} official sites, GitHub enabled

Next steps:
  /scan — run your first collection
  Set up automated scanning with CronCreate:
    CronCreate(cron="47 8 * * *", prompt="/scan")
  Note: cron jobs auto-expire after 3 days.
```

---

#### Intent: status

Quick overview of current state.

1. Read `{data_dir}/state.yaml`
2. Count unread insights:
   ```
   Grep(pattern="read: false", path="{data_dir}/insights/", output_mode="count")
   ```
3. Count total insight files this month:
   ```
   Glob(pattern="{data_dir}/insights/{current_YYYY-MM}/*.md")
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
   Grep(pattern="read: false", path="{data_dir}/insights/", output_mode="files_with_matches")
   ```

2. If count == 0:
   "No unread insights. Last scan: {date}. Run /scan to collect new data."
   → **stop**

3. Read all unread insight files.

4. Find any convergence signal files from the same dates:
   ```
   Grep(pattern="type: signal", path="{data_dir}/insights/", output_mode="files_with_matches")
   ```

5. Load previous trends (most recent file in `{data_dir}/trends/`).

6. Dispatch `trend-synthesizer` agent with:
   - **insights**: unread insight contents
   - **convergence_signals**: matching signal files
   - **domains**: from config
   - **time_range**: earliest unread date to today
   - **previous_trends**: latest trend snapshot
   - (no query — Mode A)

7. **Save trend snapshot** for continuity (so future digests/briefings can track trend lifecycle):
   ```
   Write trend snapshot to {data_dir}/trends/{today}-briefing-trends.md
   ```
   Use the same format as digest Step 6 (date, range, trends, surprises).

8. Present the synthesis as a briefing (format like digest but labeled "Briefing").

9. Batch mark all briefed insights as `read: true`:
   ```
   Bash: sed -i '' 's/^read: false$/read: true/' {space-separated list of file paths}
   ```

---

#### Intent: query

Answer a specific question from accumulated intelligence.

1. Extract the query topic from user input.

2. Search insights for relevant content:
   ```
   Grep(pattern="{query_terms}", path="{data_dir}/insights/", output_mode="files_with_matches", head_limit=20)
   ```
   Also search trends:
   ```
   Grep(pattern="{query_terms}", path="{data_dir}/trends/", output_mode="files_with_matches", head_limit=5)
   ```

3. If zero results across both searches:
   "No insights found matching '{query}'. Try broader terms, or run /scan to collect new data."
   → **stop**

4. Read matching files.

5. Dispatch `trend-synthesizer` agent with:
   - **insights**: matching insight contents
   - **domains**: from config
   - **time_range**: range of matching insights
   - **query**: the user's specific question

6. Present the query-directed synthesis, including:
   - Direct answer with confidence level
   - Supporting insight IDs (as references)
   - Related queries to explore

---

#### Intent: config

View or modify configuration.

1. Read and display current config from `~/.claude/domain-intel.local.md`:
   - Data directory
   - Active domains (names + keyword counts)
   - Source counts (RSS feeds, official sites, GitHub status)
   - Scan parameters

2. If user provided a modification request:
   - **add RSS feed**: append to sources.rss list
   - **add official site**: append to sources.official list
   - **add domain**: prompt for name + keywords + boost_terms + blacklist_terms, append to domains
   - **change setting**: update the specified value
   - **remove source/domain**: remove from the list

3. After modification: write updated config back to `~/.claude/domain-intel.local.md`, preserving the markdown body below the frontmatter.

4. Confirm the change: "Updated: {description of change}"

---

#### Intent: explore

Deep dive into a specific insight.

1. Parse the insight ID from input (pattern: `YYYY-MM-DD-source-NNN`)

2. Find the file:
   ```
   Grep(pattern="id: {id}", path="{data_dir}/insights/", output_mode="files_with_matches")
   ```

3. If not found: "Insight {id} not found." → **stop**

4. Read and display the full insight file.

5. Find related insights (same tags or category):
   - Extract tags from the insight
   - For each tag (up to 3):
     ```
     Grep(pattern="{tag}", path="{data_dir}/insights/", output_mode="files_with_matches", head_limit=5)
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
