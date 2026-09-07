# SWC Development Workflow

Detailed workflow for creating and updating Software Components (SWCs) for IC3.

## Creating a New SWC

### Step 1: Branch Setup

Create feature branches in both repositories:

```bash
# In app_ic repository
git checkout vbc_master
git pull
git checkout -b feature/VBCESA-XXXXX-{SWC_Name}

# In vap_template repository (or via app_ic submodule)
git checkout -b feature/VBCESA-XXXXX-{SWC_Name}
```

**Naming convention:** `feature/VBCESA-{JIRA_ID}-{SWC_Name}`

Example: `feature/VBCESA-13139-ElectroHydraulicRearAxleSteering_OHdlr`

### Step 2: Configure vap_template

All files are in `app_ic/utils/scripts/autosar_script/lib/vap_template/T2/vap_ic3/components/`

#### 2.1 Create SWC Python Files

Create two files:
- `[SWC].py` - Main component definition
- `[SWC]_swc.py` - SWC-specific configuration

**Reference existing SWCs** in the same directory for structure.

#### 2.2 Register the SWC

Add to `__init__.py`:
```python
from .[SWC] import *
from .[SWC]_swc import *
```

Add to `ic3_comp.py`:
```python
from .[SWC] import SWCClassName
```

#### 2.3 Add CAN Signals

In `ic3_comp.py`, add any new CAN signals to the appropriate signal lists.

#### 2.4 Add APX Signals (if applicable)

For APX (infotainment/presentation) signals, modify:
- `ICHMIProxy_T2_swc.py`
- `ICHMIProxy_T2.py`

### Step 3: SEWS Configuration

1. Open SEWS2: https://sews.volvo.net/Sews2/
2. Create container named `[SWC]_swc`
3. Add parameters and/or fault codes (if any)
4. Leave empty if no parameters/fault codes
5. **Freeze** the container when done

### Step 4: Generate APX Data View (if APX signals added)

```bash
cd app_ic/ic/ICHMIProxy_T2
./gen_dv.sh
```

**IMPORTANT:** Revert the auto-generated ldcxml file:
```bash
git checkout ic/ICHMIProxy_T2/Adapt2/ICHMIProxy_T2.ldcxml
```

### Step 5: Generate AUTOSAR XML

```bash
cd app_ic
make create_app_ic_xml
```

### Step 6: Create SWC Structure

```bash
./utils/scripts/create_IC_solution.sh [SWC_Name]
```

This generates the SWC directory structure in `app_ic/ic/[SWC]/`

### Step 7: Update Requirement Export (Optional)

To update `Requirements/Comp_Ldc_Reqs_Inps_Outs.txt`:

```bash
cd app_ic/utils/ReqExportTool
./bin/release/swexport_req.exe
```

### Step 8: Configure swc_info.json

Edit `app_ic/ic/[SWC]/[SWC]_swc/swc_info.json`:
- Add requirements (XIDs, IDs)
- Add parameters (DOID references)

### Step 9: Implement and Test

Now the SWC structure is ready for development:
1. Implement functionality in the generated `.c` files
2. Write unit tests
3. Run unit tests locally before PR

---

## Updating an Existing SWC

### Signal Updates

1. Modify signal configuration in vap_template files
2. If APX signals changed:
   ```bash
   cd app_ic/ic/ICHMIProxy_T2
   ./gen_dv.sh
   git checkout ic/ICHMIProxy_T2/Adapt2/ICHMIProxy_T2.ldcxml
   ```
3. Regenerate XML:
   ```bash
   make create_app_ic_xml
   ```

### Parameter Updates

1. Update SEWS2 container
2. Modify parameter files in vap_template:
   `T2/vap_ic3/parameters/SEWS_[SWC].py`

**Note:** Parameter templates can be auto-generated (see Confluence for tool).

### Requirement Updates

1. Update SystemWeaver requirements
2. Update `swc_info.json` with new XIDs/versions
3. Run requirement export if needed

---

## File Locations Reference

| Type | Location |
|------|----------|
| SWC Python config | `app_ic/utils/scripts/autosar_script/lib/vap_template/T2/vap_ic3/components/` |
| SWC registration | `...components/__init__.py` and `...components/ic3_comp.py` |
| APX signal config | `...components/ICHMIProxy_T2.py` and `ICHMIProxy_T2_swc.py` |
| Parameter config | `...vap_ic3/parameters/SEWS_[SWC].py` |
| Generated SWC code | `app_ic/ic/[SWC]/` |
| SWC info | `app_ic/ic/[SWC]/[SWC]_swc/swc_info.json` |

---

## Working with Wrappers

Wrappers are SWCs borrowed from GTT (Volvo Trucks) codebase. They appear with a **blue icon** in SystemWeaver.

### Updating a Wrapper

1. Copy from GTT's app_ic:
   https://stash.srv.volvo.com/projects/ICSW/repos/app_ic

2. Paste into VBC repository

3. Check for missing signals in vap_template

4. Run unit tests

### Converting Wrapper to VBC Component

If you need to add new functionality or parameters not in GTT:
1. Rename the component
2. It's no longer considered a wrapper
3. Full ownership transfers to VBC

**Best practice:** Remove unused signals from code rather than leaving them unmapped in integration.

---

## Renaming an Existing SWC

When renaming an SWC (e.g., `OLD_Name` → `New_Name`), follow this workflow.

> **Prerequisites:**
> - This workflow assumes your development environment is already set up and configured
> - All commands should be run manually by the user in their working environment
> - Ensure you have proper access to SEWS2 and the required repositories

For detailed context, see [Creating new SWC](https://confluence.srv.volvo.com/pages/viewpage.action?pageId=456883262).

### Phase 1: VAP Template Updates
Rename and update all Python files in `vap_template/T2/vap_ic3/`:
- `components/OLD_Name.py` → `components/New_Name.py`
- `components/OLD_Name_swc.py` → `components/New_Name_swc.py`  
- `parameters/SEWS_OLD_Name_swc.py` → `parameters/SEWS_New_Name_swc.py`
- Update imports in `__init__.py` and `ic3_comp.py`

### Phase 2: SEWS2 Container (CRITICAL)
**Container name MUST match SWC name exactly.** Create a NEW container at https://sews.volvo.net/Sews2/

See: [SEWS: Add Parameter, DTC and Container](https://confluence.srv.volvo.com/pages/viewpage.action?pageId=460871184)

### Phase 3: Generate New SWC Structure
```bash
make create_app_ic_xml
./utils/scripts/create_IC_solution.sh New_Name
```

### Phase 4: Port Implementation Code
The generation creates skeleton files only. Manually port:
- Source files (`.c`, `.h`)
- `VAP2_workaround_*.h` (NOT auto-generated)
- LDCXML parameters (copy from old `.ldcxml`)
- `swc_info.json` entries
- Test files from `swctest/`

### Phase 5: Run Unit Tests
```bash
# Run tests for the renamed SWC
./gradlew :New_Name_swc:test

# Run with coverage report
./gradlew :New_Name_swc:coverage
```

### Phase 6: Delete Old SWC
Only after tests pass:
```bash
rm -rf app_ic/ic/OLD_Name/
```

### Phase 7: Integration Build
After SEWS container is frozen:
```bash
make gen_dvcfg update_filelist win_build
make et_xml v3_load_package checks unit_tests
```

### Known Issues

**Windows Path Length:** Long SWC names may exceed Windows' 260 character limit in test file paths.
- Symptom: File creation fails, "path too long" errors
- Solution: Shorten test file names (e.g., remove duplicated component name from `cunit_Name_Name_suite.c` → `cunit_Name_suite.c`)

**SEWS Container:** The local `SEWS_*.py` file is just a Python template. The actual SEWS2 online container must exist and be frozen before integration builds will succeed.

---

## Using SEWS Exports in vap_template

After creating and exporting a SEWS container, follow these steps to integrate it into the codebase.

> **Prerequisites:**
> - SEWS container created and frozen at https://sews.volvo.net/Sews2/
> - Container exported as zip (Export SWC → DCM version Asr4Dcm2)
> - Commands should be run manually by the user

For detailed SEWS setup, see: [SEWS: Add parameters, DTC and Container](https://confluence.srv.volvo.com/pages/viewpage.action?pageId=29701318)

### Step 1: Extract and Place SEWS Export

1. Unzip the downloaded file
2. Rename the folder to match your SWC name (e.g., `MyComponent_swc`)
3. Place the folder in:
   ```
   app_ic/utils/scripts/autosar_script/lib/vap_template/util/sews2template/
   ```

### Step 2: Generate SEWS Python Template

```bash
cd app_ic/utils/scripts/autosar_script/lib/vap_template/util/sews2template
python3 sews2template.py MyComponent_swc
```

This generates `SEWS_MyComponent_swc.py`.

### Step 3: Copy Generated File

Copy the generated file to the parameters directory:
```
app_ic/utils/scripts/autosar_script/lib/vap_template/T2/vap_ic3/parameters/
```

### Step 4: Update swc_info.json

Add parameters to `app_ic/ic/<SWC>/<SWC>_swc/swc_info.json`:
```json
{
    "container_version": "1.0",
    "parameters": [
        {"doid": "P1234", "default_value": "100"},
        {"doid": "P5678", "default_value": "0"}
    ],
    "requirements": []
}
```

### Step 5: Generate LDCXML

The LDCXML is generated from `swc_info.json`, NOT edited directly.

Option A - Via gen_dv.sh:
```bash
cd app_ic/ic/MyComponent
./gen_dv.sh
```

Option B - Direct script:
```bash
cd app_ic
python3 utils/scripts/update_ldcxml.py MyComponent
```

This reads `swc_info.json` and generates/updates `Adapt2/MyComponent.ldcxml`.

### Reference Documentation

- README: `app_ic/utils/scripts/autosar_script/lib/vap_template/util/sews2template/README.md`
- Confluence: [SEWS: Add parameters, DTC and Container](https://confluence.srv.volvo.com/pages/viewpage.action?pageId=29701318)
