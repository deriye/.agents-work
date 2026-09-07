---
name: confluence-doc-navigator
description: "Navigate and search Confluence documentation using Loom tools. Use this skill when the user wants to: (1) find documentation on a specific topic starting from a team/project page, (2) explore the page hierarchy under a Confluence page, (3) search for documentation across spaces, (4) determine if documentation exists for a specific topic. Triggers on: Confluence search, find documentation, team page exploration, 'do we have docs for', 'is there documentation about', check Confluence, search wiki."
---

# Confluence Documentation Navigator

Guide for navigating and searching Confluence documentation using Loom MCP tools.

## Available Tools

| Tool | Purpose |
|------|---------|
| `loom_confluence_get_page` | Get content of a specific page by ID or title+space |
| `loom_confluence_get_page_children` | Get child pages under a parent page |
| `loom_confluence_search` | Search for pages using text or CQL queries |

## Workflow: Starting from a Known Page

When the user provides a Confluence URL or page ID:

1. **Extract page ID** from URL (e.g., `pageId=454234679`)
2. **Get the page content:**
   ```
   loom_confluence_get_page(page_id="454234679", include_metadata=true)
   ```
3. **Explore children** to understand hierarchy:
   ```
   loom_confluence_get_page_children(parent_id="454234679", limit=50)
   ```
4. **Search within the space** for related content:
   ```
   loom_confluence_search(query="topic AND space = SPACENAME")
   ```

## Workflow: Topic-Based Search

When searching for documentation on a topic:

1. **Broad search first:**
   ```
   loom_confluence_search(query="SEWS container", limit=20)
   ```
2. **Review results** - note which spaces have relevant content
3. **Get full content** of promising pages:
   ```
   loom_confluence_get_page(page_id="XXXXX")
   ```
4. **Narrow search** if needed with CQL:
   ```
   loom_confluence_search(query="text ~ \"SEWS container\" AND space = \"VBCESA\"")
   ```

## Common CQL Queries

| Query Pattern | Purpose |
|---------------|---------|
| `text ~ "keyword"` | Search in page content |
| `title ~ "keyword"` | Search in page titles |
| `space = "KEY"` | Filter by space |
| `ancestor = PAGEID` | Search under a parent page |
| `type = page` | Only pages (not attachments) |
| `label = "labelname"` | Pages with specific label |

**Example combined query:**
```
text ~ "SEWS" AND space = "VBCESA" AND type = page
```

## Key Confluence Spaces for IC3/GFX

| Space Key | Name | Common Content |
|-----------|------|----------------|
| VBCESA | VBC Electrical & Software Architecture | Team docs, development guides |
| DESD | DUXI Agile Release Train | IC development workflows |
| VAP | VAP2.0 | AUTOSAR/VAP platform docs |
| BBL | BBL | BBM/LDC development |
| SEWS2 | SEWS2 | SEWS system documentation |

## Team Cluster Busters Page Hierarchy

Starting point: [Team Cluster Busters](https://confluence.srv.volvo.com/pages/viewpage.action?pageId=454234679)

Key child pages:
- **IC3** (454236764) - IC3 development docs
  - Creating new SWC (456883262)
  - Update existing SWC (456883394)
  - Integration (454237172)
- **GFX** (454236762) - GFX development docs
- **V3** (454238566) - V3 testing docs
- **Onboarding** (454241431) - New member setup

## Best Practices

1. **Always note the space key** - helps understand which team owns the documentation
2. **Check page version** - older pages may have outdated info
3. **Look for attachments** - images often contain key information
4. **Summarize with URLs** - always provide page links for easy user access
5. **Cross-reference spaces** - same topic may be documented differently in different spaces

## Output Format

When reporting findings, include:
- Page title
- Space name
- Direct URL
- Brief summary of relevant content
- Note if documentation is complete or partial
