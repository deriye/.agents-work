# Baseline Management

Guide for managing baselines, tags, and branches in IC3 development.

## Understanding Baselines

Baselines represent software release versions. They follow a naming pattern like:
- **T0**, **U0**, **V0**, **W0** - Major baseline identifiers
- Full format: `B2_T0_2(33)` - Baseline T0, version 2, build 33

ECU instance versions in SystemWeaver reference these baselines.

## Branch Strategy

### IC3 (app_ic, ECU_IC3)

| Branch | Purpose |
|--------|---------|
| `vbc_master` | Main working branch - PRs target here |
| Baseline branches | Release branches (e.g., `B2_T0`) |
| Feature branches | Development work |

**Flow:** Feature → vbc_master → Cherry-pick to baseline branch

### IC-GFX (p9470_ic_hmi_coach)

| Branch | Purpose |
|--------|---------|
| `master` | Main integration branch |
| Baseline branches | Per-release (e.g., `B2_M0_1`, `B2_P0_1`) |

**Flow:** Feature → Baseline branch → Merge to master when baseline complete

---

## Tag Management

### MSW Tags

MSW (Main Software) tags are **critical** for the build system. Many build errors occur when tags are missing.

**Format:** `MSW_[partno]_3.[baseline].0`

**Example:** `MSW_12345678_3.T0.0`

### Creating Tags

```bash
# Create tag locally
git tag MSW_[partno]_3.[baseline].0

# Push tag to remote
git push origin tag MSW_[partno]_3.[baseline].0
```

### Pulling Tags

```bash
# Fetch all tags
git fetch --tags

# Force fetch (if tag was moved)
git fetch --tags --force
```

### Listing Tags

```bash
# List all MSW tags
git tag -l "MSW_*"

# Show tag details
git show MSW_[partno]_3.[baseline].0
```

---

## Commit Message Convention

**All commits must start with the intended baseline:**

```
L0: implemented new feature X
T0: fixed bug in signal handling
U0: updated parameter configuration
```

This convention:
- Indicates which baseline the change targets
- Helps with cherry-picking to correct branches
- Required by team standards

---

## Working with Multiple Baselines

### Cherry-picking Changes

When a fix needs to go to multiple baselines:

```bash
# Start on vbc_master
git checkout vbc_master
# Make your changes and commit
git commit -m "T0: fixed critical bug"
# Note the commit hash
git log -1  # e.g., abc123

# Cherry-pick to baseline branch
git checkout B2_T0
git cherry-pick abc123

# Cherry-pick to another baseline if needed
git checkout B2_U0
git cherry-pick abc123
```

### Merging Baseline to Master (GFX)

For GFX, when a baseline is complete:

```bash
git checkout master
git merge B2_T0
git push
```

---

## SystemWeaver Baseline Correlation

Each ECU instance in SystemWeaver corresponds to a baseline:

| Baseline | ECU Instance |
|----------|--------------|
| T0 | ECU_IC3_T0 instance |
| U0 | ECU_IC3_U0 instance |

When writing tests or requirements, always reference the correct baseline/ECU instance.

### Finding Current Baseline

In SystemWeaver, check the ECU instance under the IC3 node:
- XID: `x04000000006FE457` (IC3 top)

The ECU instance name includes the baseline identifier.

---

## Release Workflow

### Typical Release Steps

1. **Development complete on vbc_master**
2. **Create baseline branch** (if new baseline)
   ```bash
   git checkout vbc_master
   git checkout -b B2_V0
   ```
3. **Add baseline tag**
   ```bash
   git tag MSW_[partno]_3.V0.0
   git push origin B2_V0
   git push origin tag MSW_[partno]_3.V0.0
   ```
4. **Build and test on Jenkins**
5. **Release package created**

### Tag Versioning

For subsequent builds on the same baseline:
- `MSW_[partno]_3.V0.0` - Initial
- `MSW_[partno]_3.V0.1` - Patch 1
- `MSW_[partno]_3.V0.2` - Patch 2

---

## Common Issues

### "Build tag missing"

**Symptom:** Various build errors mentioning tags or incorrect values

**Fix:**
```bash
git tag MSW_[partno]_3.[baseline].0
git push origin tag MSW_[partno]_3.[baseline].0
git fetch --tags --force
```

### "Tag rejected on push"

**Cause:** Tag already exists on remote

**Options:**
1. Use different tag version (`.1` instead of `.0`)
2. Delete and recreate (if you own the tag):
   ```bash
   git push origin :refs/tags/MSW_[partno]_3.[baseline].0
   git tag -d MSW_[partno]_3.[baseline].0
   git tag MSW_[partno]_3.[baseline].0
   git push origin tag MSW_[partno]_3.[baseline].0
   ```

### Wrong baseline in commit message

If you committed with wrong baseline prefix:
```bash
git commit --amend -m "T0: corrected message"
```

**Note:** Only amend if not yet pushed!
