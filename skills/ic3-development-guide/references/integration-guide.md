# IC3 Integration Guide

Guide for integrating SWCs and troubleshooting common build errors.

## Integration Overview

Integration combines all SWCs and configurations into a buildable ECU image. The process is documented in `ecu_ic3/doc/integration.txt`.

## Standard Integration Workflow

### Step 1: Prepare

Ensure you have:
- Latest code from the working branch
- Correct baseline tag (see Baseline Management)
- All dependencies resolved

### Step 2: Generate and Build

```bash
# Generate DaVinci config, update file lists, build
make gen_dvcfg update_filelist win_build
```

### Step 3: Test and Package

```bash
# Generate ET XML, create load package, run checks and unit tests
make et_xml v3_load_package checks unit_tests
```

---

## Handling Missing Signals

When `gen_components.py` reports missing signals:

### CAN Signals
Add to `app_ic/utils/scripts/autosar_script/lib/vap_template/T2/vap_ic3/components/ic3_comp.py`

### APX Signals
Add to:
- `...components/ICHMIProxy_T2.py`
- `...components/ICHMIProxy_T2_swc.py`

After adding APX signals:
```bash
cd app_ic/ic/ICHMIProxy_T2
./gen_dv.sh
git checkout ic/ICHMIProxy_T2/Adapt2/ICHMIProxy_T2.ldcxml
```

---

## Common Errors and Fixes

### Error: `TypeError: cannot use a string pattern on a bytes-like object`

**Cause:** Missing build tag on your branch.

**Fix:**
```bash
git tag MSW_[partno]_3.[baseline].0
git push origin tag MSW_[partno]_3.[baseline].0
```

### Error: `Value of "xx_BUILD_xx" in "result/load/xx.hex" is incorrect`

**Cause:** Missing build tag on branch (same as above).

**Fix:**
```bash
git tag MSW_[partno]_3.[baseline].0
git push origin tag MSW_[partno]_3.[baseline].0
```

### Error: `TypeError: unicode argument without an encoding`

**Cause:** Missing build tag locally (tag exists on remote but not pulled).

**Fix:**
```bash
git fetch --tags

# If rejected, force:
git fetch --tags --force
```

### Error: `First character not "S" in S-record`

**Cause:** DWM hex file not uploaded to Artifactory with the new part number.

**Fix:**
```bash
cd ecu_ic3/dwm_config
make all
make release
```

---

## DaVinci Integration Tips

GTT has extensive DaVinci guides at their Confluence. Key points:

- Configuration files are generated, not manually edited
- Use `make gen_dvcfg` to regenerate after signal changes
- Check output for warnings about unmapped signals

---

## Build Targets Reference

| Target | Description |
|--------|-------------|
| `gen_dvcfg` | Generate DaVinci Developer configuration |
| `update_filelist` | Update source file lists for compiler |
| `win_build` | Compile for Windows target |
| `et_xml` | Generate ET (Engineering Test) XML |
| `v3_load_package` | Create load package for V3 testing |
| `checks` | Run static analysis and validation |
| `unit_tests` | Execute unit test suite |

### Combined Targets

```bash
# Full integration build
make gen_dvcfg update_filelist win_build et_xml v3_load_package checks unit_tests

# Quick build (skip tests)
make gen_dvcfg update_filelist win_build

# Tests only (after successful build)
make checks unit_tests
```

---

## Troubleshooting Checklist

When integration fails:

1. **Check tags:** `git tag -l "MSW_*"` - is your baseline tag present?
2. **Pull tags:** `git fetch --tags --force`
3. **Check signals:** Review `gen_components.py` output for missing signals
4. **Check DWM:** If S-record error, rebuild DWM config
5. **Check Jenkins:** Are build agents online?
6. **Check branch:** Are you on the correct baseline branch?

---

## Jenkins Build Status

Check build status at: https://segotl3770.got.volvo.net/

### Build Agents
- SEGOTN16049
- SEGOTN16050

If agents are offline, see [Build Servers documentation](https://confluence.srv.volvo.com/pages/viewpage.action?pageId=577439390) for restart procedures.

---

## Pre-PR Checklist

Before creating a Pull Request:

- [ ] All unit tests pass locally
- [ ] `make gen_dvcfg update_filelist win_build` succeeds
- [ ] `make et_xml v3_load_package checks unit_tests` succeeds
- [ ] Commit message starts with baseline (e.g., "T0: ...")
- [ ] Feature branch named correctly (`feature/VBCESA-XXXXX-...`)
- [ ] PR targets `vbc_master` (for IC3)
