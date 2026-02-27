---
name: commit
description: "Use when the user says 'commit' or wants to save progress after completing a task. Analyzes uncommitted changes, groups them logically, and commits with conventional format messages."
context: fork
model: haiku
allowed-tools: Bash(git:*)
---

## Input

Trigger this command when:
- User says "commit", "提交", or similar
- After completing a task, user wants to save progress

On trigger:
1. Run `git status` and `git diff --stat` to understand current state
2. If no uncommitted changes, inform user and stop
3. If changes exist, proceed with analysis

## Process

1. **Check git status**
   - Run `git status` to see uncommitted files
   - Run `git diff --stat` to see summary of changes
   - Identify all modified, added, or deleted files

2. **Analyze changes**
   - For each modified file, understand the changes
   - Use `git diff <file>` to see exact changes if needed
   - Group related changes logically:
     - Same feature/component -> same commit
     - Different concerns -> separate commits
     - Bug fixes vs features -> separate commits
     - Documentation -> separate commit

3. **Create commit messages**
   - Follow conventional commit format: `type(scope): description`
   - Types: `feat`, `fix`, `docs`, `refactor`, `style`, `test`, `chore`
   - Scope: component/service name (e.g., `sync`, `home`, `repository`)
   - Description: concise summary of what changed
   - Multi-line body: explain why and how (if needed)

4. **Commit in logical order**
   - Start with foundational changes (models, protocols)
   - Then service layer changes
   - Then view/viewmodel changes
   - Finally documentation/comments
   - One commit per logical group

   **CRITICAL: Execute add+commit per group, NOT batch add then batch commit**
   ```
   # CORRECT (per-group cycle):
   git add <group1-files> && git commit -m "..."
   git add <group2-files> && git commit -m "..."
   git add <group3-files> && git commit -m "..."

   # WRONG (batch add, then separate commits):
   git add <all-files>
   git commit -m "..."  # <-- commits EVERYTHING staged
   git commit -m "..."  # <-- nothing left to commit!
   ```

5. **Verify**
   - After all commits, run `git log --oneline -5` to show recent commits
   - Run `git status` to confirm working tree is clean
   - Report summary of commits created

## Special Cases

**Merge commits**: When merging branches, use default merge message. Do not re-split changes.

**Fixup previous commit**: If user says "add to last commit" or "amend":
- Use `git commit --amend` only when explicitly requested
- Warn user this rewrites history

**Partial staging**: If user wants to commit only some files:
- Stage only specified files with `git add <file>`
- Leave other changes unstaged

## Commit Message Guidelines

**Format:**
```
type(scope): brief description

Optional body explaining:
- What changed
- Why it changed
```

**Examples:**
- `fix(sync): use healthKitWorkoutId for stable log binding`
- `feat(home): auto-refresh on sync success`
- `docs(readme): add setup instructions`
- `refactor(repository): check persistentModelID before inserting`

**Grouping Rules:**
- Same file, same concern -> one commit
- Same file, different concerns -> separate commits
- Related files, same feature -> one commit
- Unrelated changes -> separate commits

## Output Format

After completing commits, provide:
1. Summary of commits created (list with hashes)
2. Total number of commits
3. Confirmation that working tree is clean

## Completion Criteria

- All logical change groups committed
- `git status` shows clean working tree (or only intentionally unstaged files)
- Commit summary with hashes presented
