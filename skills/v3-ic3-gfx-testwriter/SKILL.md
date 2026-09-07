---
name: v3-ic3-gfx-testwriter
description: Orchestrates automated test generation for IC3 and GFX requirements using parallel and sequential subagent workflows. Use this skill when the user provides a requirement XID (or swap:// URL) and/or wants to generate PAQR test cases from SE-TOOL/SystemWeaver requirements, analyze requirements and create test specifications, or visualize requirement analysis with test case mapping. Triggers on mentions of test generation, PAQR tests, IC3/GFX testing, requirement XID with test creation, automated test writing, test case generation from requirements. Use this when the user ask you to write a test specifically when accompanied by an XID such as `x040000000000...` or a a software component/requirement or a file that contains refrences to them.
---

# V3 IC3/GFX Test Writer

Orchestrates parallel and sequential subagent workflows to analyze requirements and generate
PAQR test cases with visual documentation.

## Workflow Overview

This skill coordinates three specialized subagents:

1. **Requirement Analyzer** (parallel start) - Deep requirement analysis using loom-requirement-analysis skill
2. **Visual Reporter** (after analyzer) - Concise visual report using visual-explainer skill
3. **PAQR Test Generator** (after analyzer) - Test case generation using PAQR framework

```
Input: Requirement XID
    |
    v
[Requirement Analyzer] ─────┬──> [Visual Reporter] ──> HTML Report
                            │
                            └──> [PAQR Test Generator] ──> Test Files
```

## Step 1: Launch Requirement Analyzer

Start with requirement analysis as the foundation for both visualization and test generation.

**Launch the analyzer subagent:**

```
Task(
  description="Analyze requirement for testing",
  prompt="""Use the loom-requirement-analysis skill to analyze requirement XID: {requirement_xid}
  
  Return a comprehensive analysis with signal flows, boundary conditions, DOID parameters,
  dependencies, and any ambiguities.
  
  Requirement analyzer must NOT generate any visualizations or HTML.
  Requirement analyzer must NOT generate any artifacts on disk including md files, etc.

  DO NOT OVER ANALYZE OR DRAW WILD CONCLUSIONS! 
  Attempt to do it quickly when possible or if the requirement is straightforward.
   """,
  """,
  subagent_type="general"
)
```

Wait for the analyzer to complete before proceeding to Step 2.

## Step 2: Launch Parallel Subagents

Once requirement analysis completes, launch the visual reporter and test generator in parallel.
Both operate on the analysis result independently.

### Subagent 2A: Visual Reporter (in parallel with test generator)

**Purpose:** Generate a concise, scannable HTML visualization of the requirement analysis.

**Launch the visual reporter:**

```
Task(
  description="Generate visual requirement report",
  prompt="""Use the visual-explainer skill to create a concise HTML report from this requirement analysis, make sure to use a full width layout (within reason, perhaps 80 percent) to maximize space for visuals and have a table of contents for easy navigation on the left side, if any graph is used you must make sure you use proper mermaid and not mix with ascii art, arrows etc. also make sure the font sizes are not too small and are easy to read:
  
  {analysis_result}
  
  Focus on visual clarity - use cards, diagrams, and tables rather than long paragraphs.
  Make it scannable and information-dense.
  
  Visual Analyzer must use the current directory to store the HTML file.
  Open the report in the browser automatically as soon as it's generated.

  DO NOT FILL THE REPORT WITH TOO MUCH INFORMATION!
  The goal is to create a clear and concise visual summary of the requirement analysis, not to dump the entire analysis into the report. Use your judgment to include only the most relevant and important information.
  """,
  subagent_type="general"
)
```

The visual-explainer skill will handle aesthetic choices and browser opening automatically.

### Subagent 2B: PAQR Test Generator (in parallel with visual reporter)

**Purpose:** Generate PAQR test cases from the requirement analysis.

**Launch the test generator:**

```
Task(
description="Generate PAQR test cases",
prompt="""Generate PAQR test cases for this requirement analysis using paqr-framework-docs skill that is available on the system. You must use LSP to verify correctness and also use `uv run paqr generate ...` to verify successful XML generation. Debug and fix any issues.

{analysis_result}

Cover normal operation, boundary conditions, error handling, and integration scenarios.
Use PAQR framework conventions and generate runnable test code.

Coding standards:

  - Define helper functions for common test patterns to reduce duplication.
  - Do not overuse comments. Prefer clear, self-explanatory code.
  - Do not use complex patterns. Keep it straightforward and maintainable.

Confidence markers (REQUIRED):

  - You must mark sections of generated test code with AIGR confidence blocks.
  - These blocks are temporary review markers used by the pipeline and will later be extracted automatically.
  - Place the block immediately above the code section it refers to.

Use `aigr-annotator` skill to generate the confidence blocks with appropriate HIGH, MEDIUM, or LOW confidence levels based on the certainty of the generated code's correctness and alignment with the requirement analysis. And make sure to process it with its script to generate the AIGR metadata files.

Confidence levels:

  - HIGH: straightforward implementation based directly on explicit requirement analysis.
  - MEDIUM: implementation required interpretation or assumptions.
  - LOW: speculative implementation or incomplete information. These must be validated manually.


Rules for confidence blocks:

  - Most generated test case must have a confidence block, you can skip this for trivial or self-evident cases.
  - Keep descriptions short but precise.
  - Do NOT overdo it! The goal is to provide useful signals for reviewers, not to annotate every line of code.

  Additionally:
    - You must mark signals that are not exact matches from the database for manual review using a LOW confidence block.

Checklist:

- [ ] Use paqr-framework-docs skill for generation
- [ ] Verify correctness with LSP
- [ ] Verify with `uv run ruff check` and `uv run ruff format`
- [ ] Use `uv run paqr generate ...` to verify successful XML generation
- [ ] Debug and fix any generation issues
- [ ] Ensure every generated test case includes an AIGR confidence block

""",
subagent_type="general"
)

```

## Step 3: Provide Summary

After both subagents complete, provide a brief summary of deliverables and key findings.

## Completion Checklist

After completing the workflow, verify:

- [ ] Requirement XID was successfully resolved and analyzed
- [ ] Requirement analyzer subagent completed and returned analysis
- [ ] Visual reporter subagent completed and generated HTML report
- [ ] PAQR test generator subagent completed and generated test files
- [ ] HTML report location provided to user
- [ ] Test file locations provided to user
- [ ] Key findings or risks highlighted in summary
- [ ] User knows next steps (review report, run tests)
