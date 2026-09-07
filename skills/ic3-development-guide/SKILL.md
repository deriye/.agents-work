---
name: ic3-development-guide
description: "Guide for IC3 software development at Team Cluster Busters. Covers SWC creation/updates/renaming, integration, and common commands. Use when: (1) creating, updating, or renaming Software Components, (2) running integration commands, (3) troubleshooting build errors, (4) working with SEWS containers and exports, (5) running unit tests, (6) understanding IC3 repository structure, (7) tagging builds with MSW tags, (8) configuring parameters via swc_info.json. Triggers on: IC3 development, SWC creation, SWC rename, app_ic, ecu_ic3, vap_template, integration commands, make commands, gradlew, unit tests, SEWS container, sews2template, LDCXML, swc_info.json, update_ldcxml, gen_dv.sh, MSW tags, baseline tags."
---

# IC3 Development Guide

Development guide for IC3 software at Team Cluster Busters (VBC Inhouse SW Development).

## Quick Reference Commands

| Command | Purpose |
|---------|---------|
| `make create_app_ic_xml` | Generate AUTOSAR XML from vap_template |
| `./utils/scripts/create_IC_solution.sh [SWC]` | Generate new SWC structure |
| `./gradlew :$SWC:test` | Run unit tests for one SWC |
| `./gradlew :$SWC:coverage` | Run unit tests with coverage for one SWC |
| `./gradlew :test` | Run unit tests for all SWCs |
| `./gradlew :coverage` | Run unit tests with coverage for all SWCs |
| `python3 utils/scripts/update_ldcxml.py [SWC]` | Generate LDCXML from swc_info.json |
| `make gen_dvcfg update_filelist win_build` | Integration build |
| `make et_xml v3_load_package checks unit_tests` | Full test and package |
| `git tag MSW_[partno]_3.[baseline].0` | Add baseline tag |
| `git push origin tag MSW_[partno]_3.[baseline].0` | Push baseline tag |
| `git fetch --tags --force` | Pull all tags (force if rejected) |

## Repository Overview

| Repository | Purpose | Working Branch |
|------------|---------|----------------|
| `ECU_IC3` | Main ECU integration | baseline branches |
| `app_ic` | SWC application code | `vbc_master` |
| `vap_template` | AUTOSAR signal configs | feature branches |
| `p9470_ic_hmi_coach` | HMI specifications | - |
| `vbc_ic_test_cases` | V3 automated tests | `master` |

**Bitbucket URLs:**
- ECU_IC3: https://stash.srv.volvo.com/projects/VBC/repos/ecu_ic3
- app_ic: https://stash.srv.volvo.com/projects/VBC/repos/app_ic (via submodule or direct)

## Git Way of Working

### IC3 Branch Strategy
- **Working branch**: `vbc_master` - all PRs target this branch
- **Baseline branches**: Cherry-pick/merge from vbc_master
- **Feature branches**: `feature/VBCESA-XXXXX-{SWC_Name}`

### Commit Convention
```
L0: implemented feature X
T0: fixed bug in Y
```
Commit messages **must start with intended baseline** (e.g., L0, T0, U0, V0).

### PR Rules
- Unit tests must pass before merge
- PR creator performs the merge (soft rule for availability)

## SWC Development Workflow

### Creating a New SWC

**Detailed guide:** [references/swc-workflow.md](references/swc-workflow.md)

**Quick Checklist:**

1. **Create branches** in `app_ic` and `vap_template`
   - Naming: `feature/VBCESA-XXXXX-{SWC_Name}`

2. **Configure vap_template** (in `app_ic/utils/scripts/autosar_script/lib/vap_template/T2/vap_ic3/components/`):
   - Create `[SWC].py` and `[SWC]_swc.py`
   - Add to `__init__.py` and `ic3_comp.py`
   - Add CAN signals to `ic3_comp.py`
   - Add APX signals to `ICHMIProxy_T2_swc.py` and `ICHMIProxy_T2.py`

3. **Create SEWS container** (`[SWC]_swc` in SEWS2)
   - Add parameters/fault codes if any
   - Freeze when done

4. **Generate in app_ic**:
   ```bash
   # If APX signals added:
   cd app_ic/ic/ICHMIProxy_T2 && ./gen_dv.sh
   # Revert: ic/ICHMIProxy_T2/Adapt2/ICHMIProxy_T2.ldcxml

   make create_app_ic_xml
   ./utils/scripts/create_IC_solution.sh [SWC]
   ```

5. **Configure swc_info.json**: Add requirements and parameters in `app_ic/ic/[SWC]/[SWC]_swc/swc_info.json`

### Updating Existing SWC

Follow the same signal configuration steps, then rebuild with:
```bash
make create_app_ic_xml
```

## Integration Process

**Detailed guide:** [references/integration-guide.md](references/integration-guide.md)

**Full documentation:** `ecu_ic3/doc/integration.txt`

### Standard Integration Commands

```bash
# Step 1: Generate and build
make gen_dvcfg update_filelist win_build

# Step 2: Test and package
make et_xml v3_load_package checks unit_tests
```

### Adding Missing Signals

When `gen_components.py` reports missing signals:
- CAN signals: Add to `ic3_comp.py`
- APX signals: Add to `ICHMIProxy_T2.py`

### Baseline Tagging

**CRITICAL**: Many build errors occur due to missing tags.

```bash
# Add tag locally
git tag MSW_[partno]_3.[baseline].0

# Push tag to remote
git push origin tag MSW_[partno]_3.[baseline].0

# Pull tags (force if needed)
git fetch --tags --force
```

## Common Errors & Fixes

**Detailed guide:** [references/integration-guide.md](references/integration-guide.md)

| Error | Cause | Fix |
|-------|-------|-----|
| `TypeError: cannot use a string pattern on a bytes-like object` | Missing build tag | Add MSW tag (see above) |
| `Value of "xx_BUILD_xx" in "result/load/xx.hex" is incorrect` | Missing build tag on branch | Push MSW tag to remote |
| `TypeError: unicode argument without an encoding` | Missing tag locally | `git fetch --tags --force` |
| `First character not "S" in S-record` | DWM hex not uploaded | Run `cd dwm_config && make all && make release` |

## SystemWeaver (SE-TOOL) XIDs

### Key Items
| Item | XID | Link |
|------|-----|------|
| IC3 (top) | `x04000000006FE457` | [swap://](swap://setoolvbc.srv.volvo.com:3001/x04000000006FE457) |
| P9470_HMI_Specification_Coach | `x04000000006BCF9C` | [swap://](swap://setoolvbc.srv.volvo.com:3001/x04000000006BCF9C) |
| Test & Verification Area | `x04000000000BE2DD` | [swap://](swap://setoolvbc.srv.volvo.com:3001/x04000000000BE2DD) |

### SEWS2 Roles Required
- ApciDBDownloader
- DataViewer
- NodeIntegrator
- NodeOwner
- PreReleaseSoftware
- SoftwareDeveloper

## SEWS Container Documentation

### Key Documentation Pages

| Page | Space | Topic |
|------|-------|-------|
| [SEWS: Add Parameter, DTC and Container](https://confluence.srv.volvo.com/pages/viewpage.action?pageId=460871184) | VBCESA | IC3-specific guide |
| [Modify Export Import SEWS Container](https://confluence.srv.volvo.com/pages/viewpage.action?pageId=103331998) | VAP | Detailed export/import |
| [SEWS: Add parameters, DTC and Container](https://confluence.srv.volvo.com/pages/viewpage.action?pageId=29701318) | DESD | Full workflow with script |

### Quick Reference: Export SEWS Container

1. **In SEWS2:** View Data → Container → Search for SWC
2. Click SWC link → **Edit Container** → **Export SWC** tab
3. Select DCM Version: **Asr4Dcm2**
4. Click **"Create SWC file (Validation)"**
5. Download and unzip the file
6. Place in: `app_ic/utils/scripts/autosar_script/lib/vap_template/util/sews2template/`
7. Run: `python3 sews2template.py {export_dir}`
8. Copy generated `SEWS_{swc_name}_swc.py` to `app_ic/utils/scripts/autosar_script/lib/vap_template/T2/vap_ic3/parameters/`

### SEWS Links

- Create new case: https://sews.volvo.net/Sews2/Case/CaseCreate.aspx
- Create container: http://sews.volvo.net/Sews2/Workflow/AllocateDOToContainer.aspx
- My Profile (roles): https://sews.volvo.net/Sews2/Information/MyProfile.aspx

## Build Infrastructure

| Resource | URL/Info |
|----------|----------|
| Jenkins | https://segotl3770.got.volvo.net/ |
| Build agents | SEGOTN16049, SEGOTN16050 |
| Linux swarm | segotl4364 (user: vbcadmin) |

### Starting Build Agents (if offline)

**Windows agents** (SEGOTN16049/SEGOTN16050):
1. Remote connect (user: A351444)
2. Run PowerShell as admin
3. `cd d:\J`
4. Run `.bat` file (Startslave.bat or applicationSEGOTL3770.bat)

**Linux agent** (segotl4364):
```bash
ssh segotl4364
sudo su vbcadmin
cd ../vbcadmin/swarm
./start_jenkins_onprem.sh
```

## V3 Testing

Test procedures in `vbc_ic_test_cases/testprocedures/ic by SWC/`

### Running Tests with PAQR
```bash
# Generate all tests
paqr generate

# Generate specific tests by tag
paqr generate -m tags="Test" -v
```

### Remote Test Rigs
- SEGOTWHJZ0KR3 (user: A507735)
- SEGOTW22FT2T3 (user: A507735)
- SEGOTWCLZV0Z2 (user: A456399)

## Reference Documentation

- **[Quick Commands](references/quick-commands.md)** - Full command reference
- **[SWC Workflow](references/swc-workflow.md)** - Detailed SWC creation steps
- **[Integration Guide](references/integration-guide.md)** - Integration and troubleshooting
- **[Baseline Management](references/baseline-management.md)** - Tags and branching

## Confluence Links

| Page | ID | Topic |
|------|----|-------|
| Team Cluster Busters | 454234679 | Team overview |
| Onboarding | 454241431 | New member setup |
| Git Way of Working | 460461458 | Branch strategy |
| Creating New SWC | 456883262 | SWC creation guide |
| Integration (IC3) | 454237172 | Integration tips |
| Build Servers | 577439390 | CI/CD setup |
| V3 Way of Working | 612079068 | Test automation |
| CANoe Setup | 425552733 | Test environment |

## Wrappers (GTT Components)

Wrappers are SWC components borrowed from GTT codebase (blue icon in SystemWeaver).

**To update a wrapper:**
1. Copy from GTT's app_ic: https://stash.srv.volvo.com/projects/ICSW/repos/app_ic
2. Paste into VBC repository
3. Check for missing signals in vap_template
4. Run unit tests

**Note:** Adding new functionality requires renaming the component (no longer a wrapper).
