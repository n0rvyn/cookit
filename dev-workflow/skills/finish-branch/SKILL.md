---
name: finish-branch
description: "Use when implementation is complete and you need to decide how to integrate the work. Verifies tests, presents structured options, handles cleanup."
allowed-tools: Bash(git:*) Bash(gh:*) Bash(npm:*) Bash(cargo:*) Bash(pytest:*) Bash(go:*) Bash(xcodebuild:*) Bash(ls:*)
---

## Process

### Step 1: Verify Tests

Run the project's test suite:
```bash
# Auto-detect: npm test / cargo test / pytest / go test ./... / xcodebuild test
```

- If tests fail: **Stop.** Cannot proceed until tests pass.
- If tests pass: Continue to Step 2.

### Step 1.5: Check Documentation

Before presenting integration options, check if project docs need updates:

```bash
ls docs/05-features/ docs/07-changelog/ docs/03-decisions/ 2>/dev/null
```

If these directories exist, remind the user:
- New features completed → run `dev-workflow:write-feature-spec` to generate feature specs
- Architectural decisions made → update `docs/03-decisions/`
- Changes worth logging → update `docs/07-changelog/`

This is a reminder, not a gate. Do not block on documentation.

### Step 2: Determine Base Branch

```bash
git merge-base HEAD main 2>/dev/null || git merge-base HEAD master 2>/dev/null
```

### Step 3: Present Options

Present exactly these 4 options:

```
Implementation complete. All tests passing. What would you like to do?

1. Merge back to <base-branch> locally
2. Push and create a Pull Request
3. Keep the branch as-is (I'll handle it later)
4. Discard this work
```

### Step 4: Execute Choice

**Option 1: Merge Locally**
```bash
git checkout <base-branch>
git pull
git merge <feature-branch>
# Run tests again after merge
git branch -d <feature-branch>
```

**Option 2: Push and Create PR**
```bash
git push -u origin <feature-branch>
gh pr create --title "<title>" --body "$(cat <<'EOF'
## Summary
<2-3 bullets>

## Test Plan
- [ ] <verification steps>
EOF
)"
```

**Option 3: Keep As-Is**
Report: "Keeping branch `<name>`. You can return to it later."

**Option 4: Discard**
Ask user to type "discard" to confirm. Then:
```bash
git checkout <base-branch>
git branch -D <feature-branch>
```

### Step 5: Worktree Cleanup (conditional)

Check if currently in a worktree:
```bash
git worktree list | grep $(git branch --show-current)
```

- If in a worktree and chose Option 1, 2, or 4: clean up the worktree
- If in a worktree and chose Option 3: keep the worktree
- If not in a worktree: skip this step

## Completion Criteria

- Tests pass (Step 1)
- User has selected an integration option (Step 3)
- Chosen option fully executed (Step 4)
- Worktree cleaned up if applicable (Step 5)
