# Quick Commands Reference

Complete command reference for IC3 development.

## app_ic Commands

### SWC Generation
```bash
# Generate AUTOSAR XML configuration
make create_app_ic_xml

# Create new SWC structure
./utils/scripts/create_IC_solution.sh [SWC_NAME]

# Example:
./utils/scripts/create_IC_solution.sh AcceleratorPedalDisable_OHdlr
```

### APX Signal Generation
```bash
# Generate APX data view (after adding APX signals)
cd app_ic/ic/ICHMIProxy_T2
./gen_dv.sh

# IMPORTANT: Revert the ldcxml file after generation
git checkout ic/ICHMIProxy_T2/Adapt2/ICHMIProxy_T2.ldcxml
```

### Requirement Export
```bash
# Update Requirements/Comp_Ldc_Reqs_Inps_Outs.txt
cd app_ic/utils/ReqExportTool
./bin/release/swexport_req.exe
```

## ecu_ic3 Commands

### Integration Build
```bash
# Standard integration sequence
make gen_dvcfg update_filelist win_build

# Full test and package
make et_xml v3_load_package checks unit_tests

# DWM configuration (if hex missing)
cd dwm_config
make all
make release
```

### Individual Make Targets

| Target | Purpose |
|--------|---------|
| `gen_dvcfg` | Generate DaVinci configuration |
| `update_filelist` | Update file lists for build |
| `win_build` | Windows build |
| `et_xml` | Generate ET XML |
| `v3_load_package` | Create V3 load package |
| `checks` | Run validation checks |
| `unit_tests` | Run unit tests |

## Git Commands

### Baseline Tagging
```bash
# Add baseline tag
git tag MSW_[partno]_3.[baseline].0

# Push tag to remote
git push origin tag MSW_[partno]_3.[baseline].0

# Pull all tags (force to overwrite)
git fetch --tags --force

# List tags matching pattern
git tag -l "MSW_*"
```

### Branch Operations
```bash
# Create feature branch
git checkout -b feature/VBCESA-XXXXX-SWCName

# Cherry-pick to baseline branch
git checkout B2_T0
git cherry-pick <commit-hash>
```

## PAQR Test Commands

```bash
# Generate all test XMLs
paqr generate

# Generate with specific tag filter
paqr generate -m tags="Test" -v

# Generate verbose output
paqr generate -v
```

## Jenkins Build Agents

### Start Windows Agent
```powershell
# Connect via Remote Desktop to SEGOTN16049 or SEGOTN16050
# Run PowerShell as Administrator
cd d:\J
.\Startslave.bat  # or applicationSEGOTL3770.bat
```

### Start Linux Agent
```bash
ssh segotl4364
sudo su vbcadmin
cd ../vbcadmin/swarm
./start_jenkins_onprem.sh
```

## Common Command Sequences

### New SWC Development
```bash
# 1. Create feature branches
git checkout -b feature/VBCESA-12345-NewSWC  # in app_ic
git checkout -b feature/VBCESA-12345-NewSWC  # in vap_template

# 2. Configure signals in vap_template (edit Python files)

# 3. Generate APX if needed
cd app_ic/ic/ICHMIProxy_T2 && ./gen_dv.sh
git checkout ic/ICHMIProxy_T2/Adapt2/ICHMIProxy_T2.ldcxml

# 4. Generate SWC
cd app_ic
make create_app_ic_xml
./utils/scripts/create_IC_solution.sh NewSWC

# 5. Develop and test
```

### Integration Build
```bash
# 1. Ensure tag exists
git tag MSW_PARTNO_3.T0.0
git push origin tag MSW_PARTNO_3.T0.0

# 2. Build
make gen_dvcfg update_filelist win_build

# 3. Test
make et_xml v3_load_package checks unit_tests
```

### Fix Missing DWM Hex
```bash
cd ecu_ic3/dwm_config
make all
make release
```
