# Blueprint Technical (Default Design Template)

This is the default design template for visual-explainer. It provides a professional, technical aesthetic with excellent readability and a sophisticated color palette.

## When to Use

Use this as the default template for most technical documentation, test specifications, architecture diagrams, and data-heavy visualizations. It works particularly well for:
- Test specifications and test case documentation
- Requirements analysis documents
- Technical architecture overviews
- System design documentation
- Data tables and comparison matrices

## Typography

**Font Pairing:** IBM Plex Sans + IBM Plex Mono

```css
--font-body: 'IBM Plex Sans', system-ui, sans-serif;
--font-mono: 'IBM Plex Mono', 'Courier New', monospace;
```

**Google Fonts Import:**
```html
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap" rel="stylesheet">
```

**Characteristics:**
- Highly readable at all sizes
- Professional and precise
- Excellent monospace for technical content
- Neutral enough for any domain

## Color Palette

### Base Colors (Deep Slate/Blue)

```css
--bg: #0d1821;
--surface: #1a2332;
--surface-elevated: #212d3f;
--surface-recessed: #0a1219;
```

### Borders & Grid

```css
--border: rgba(138, 180, 248, 0.15);
--border-bright: rgba(138, 180, 248, 0.25);
--grid: rgba(138, 180, 248, 0.05);
```

### Text

```css
--text: #e8eef5;
--text-dim: #8a9fb8;
--text-dimmer: #5f6e82;
```

### Accent (Bright Cyan)

```css
--accent: #1fb6d6;
--accent-dim: rgba(31, 182, 214, 0.12);
--accent-bright: #3dd5f3;
```

### Status Colors

```css
--pass: #2dd4bf;        /* Teal - success/pass */
--pass-dim: rgba(45, 212, 191, 0.12);

--fail: #fb7185;         /* Rose - error/fail */
--fail-dim: rgba(251, 113, 133, 0.12);

--warning: #fbbf24;      /* Amber - warning/caution */
--warning-dim: rgba(251, 191, 36, 0.12);

--pending: #818cf8;      /* Indigo - pending/info */
--pending-dim: rgba(129, 140, 248, 0.12);
```

## Background Pattern

Subtle grid pattern that evokes technical blueprint drawings:

```css
body {
  background: var(--bg);
  background-image: 
    repeating-linear-gradient(
      0deg,
      transparent,
      transparent 19px,
      var(--grid) 19px,
      var(--grid) 20px
    ),
    repeating-linear-gradient(
      90deg,
      transparent,
      transparent 19px,
      var(--grid) 19px,
      var(--grid) 20px
    );
}
```

**Effect:** Creates a faint 20px × 20px grid that provides structure without distraction. The grid is barely visible but adds a technical, measured feeling to the page.

## Link Styling

```css
a {
  color: var(--accent);
  text-decoration: underline;
  text-decoration-color: rgba(31, 182, 214, 0.4);
  text-underline-offset: 3px;
}

a:hover {
  color: var(--accent-bright);
  text-decoration-color: var(--accent-bright);
}
```

## Visual Characteristics

### Surface Depth Strategy

The template uses subtle elevation to create hierarchy:

1. **Recessed** (`--surface-recessed`): Code blocks, inset details
2. **Base** (`--surface`): Standard cards, table rows
3. **Elevated** (`--surface-elevated`): Important cards, table headers
4. **Accent-tinted**: Hero sections with `background: linear-gradient(to bottom, var(--accent-dim) 0%, transparent 100%)`

### Border Treatment

- **Standard borders:** `1px solid var(--border)` — subtle, barely visible
- **Bright borders:** `1px solid var(--border-bright)` or `2px solid var(--border-bright)` — for emphasis
- **Accent borders:** `border-left: 3px solid var(--accent)` — for section headers and callouts

### Typography Scale

```css
/* Page title */
h1 {
  font-size: 44px;
  font-weight: 700;
  line-height: 1.2;
}

/* Section headers */
h2 {
  font-size: 32px;
  font-weight: 700;
  line-height: 1.3;
}

/* Subsections */
h3 {
  font-size: 24px;
  font-weight: 600;
}

/* Minor headings */
h4 {
  font-size: 18px;
  font-weight: 600;
}

/* Body text */
p, li {
  font-size: 16px;
  line-height: 1.7;
}

/* Monospace labels */
.section-number, .metadata-label {
  font-family: var(--font-mono);
  font-size: 12-14px;
  text-transform: uppercase;
  letter-spacing: 1-2px;
}
```

## Key Patterns

### Section Header with Accent Border

```css
.section-header {
  margin-bottom: 32px;
  padding-left: 24px;
  border-left: 3px solid var(--accent);
}

.section-number {
  font-family: var(--font-mono);
  font-size: 14px;
  font-weight: 600;
  color: var(--accent);
  margin-bottom: 8px;
}
```

### Card with Elevation

```css
.card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 28px;
  margin-bottom: 24px;
}

.card--elevated {
  background: var(--surface-elevated);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
}
```

### Metadata Grid

```css
.metadata {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 20px;
}

.metadata-item {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 20px;
}

.metadata-label {
  font-family: var(--font-mono);
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 1.2px;
  color: var(--text-dimmer);
  margin-bottom: 10px;
}

.metadata-value {
  font-size: 16px;
  font-weight: 600;
  color: var(--text);
  font-family: var(--font-mono);
}
```

### Callout Box (Warning)

```css
.callout {
  border-radius: 6px;
  padding: 20px 24px;
  margin-bottom: 24px;
  border-left: 4px solid;
}

.callout-warning {
  background: linear-gradient(to right, var(--warning-dim) 0%, transparent 100%);
  border-color: var(--warning);
}

.callout-info {
  background: linear-gradient(to right, var(--accent-dim) 0%, transparent 100%);
  border-color: var(--accent);
}
```

### Status Indicator (for tables)

```css
.status-indicator {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-family: var(--font-mono);
  font-size: 13px;
  font-weight: 600;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.status-pass .status-dot { background: var(--pass); }
.status-fail .status-dot { background: var(--fail); }
.status-warning .status-dot { background: var(--warning); }
.status-pending .status-dot { background: var(--pending); }

.status-pass { color: var(--pass); }
.status-fail { color: var(--fail); }
.status-warning { color: var(--warning); }
.status-pending { color: var(--pending); }
```

### Table Styling

```css
.table-wrapper {
  overflow-x: auto;
  margin-bottom: 28px;
  border: 1px solid var(--border-bright);
  border-radius: 6px;
}

table {
  width: 100%;
  border-collapse: collapse;
  font-size: 15px;
}

thead {
  background: var(--surface-elevated);
  position: sticky;
  top: 0;
  z-index: 10;
}

th {
  text-align: left;
  padding: 16px 20px;
  font-weight: 600;
  font-family: var(--font-mono);
  font-size: 13px;
  text-transform: uppercase;
  letter-spacing: 0.8px;
  color: var(--text);
  border-bottom: 2px solid var(--border-bright);
}

td {
  padding: 16px 20px;
  color: var(--text-dim);
  border-bottom: 1px solid var(--border);
  line-height: 1.6;
}

tbody tr:nth-child(even) {
  background: rgba(255, 255, 255, 0.02);
}

tbody tr:hover {
  background: var(--accent-dim);
}
```

## Animation

Staggered fade-up entrance for sections:

```css
@keyframes fadeUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

section {
  animation: fadeUp 0.6s ease-out backwards;
}

section:nth-child(1) { animation-delay: 0.1s; }
section:nth-child(2) { animation-delay: 0.2s; }
section:nth-child(3) { animation-delay: 0.3s; }
/* ... continue for more sections */

@media (prefers-reduced-motion: reduce) {
  * {
    animation: none !important;
    transition: none !important;
  }
}
```

## Design Philosophy

1. **Technical precision:** Grid background, monospace labels, measured spacing
2. **Excellent readability:** 16px body text, 1.7 line-height, high contrast
3. **Subtle sophistication:** Low-opacity borders, graduated elevation, accent-tinted backgrounds
4. **Professional restraint:** No flashy effects, no gradients on text, no glowing shadows
5. **Information hierarchy:** Clear visual weight differences between primary and secondary content

## Usage Notes

- **When to vary:** If generating multiple documents in a session, use this template for the first 2-3, then switch to Paper/Ink or Editorial for variety
- **When NOT to use:** Avoid for creative/marketing content, slide decks, or highly visual storytelling (use Editorial or Paper/Ink instead)
- **Light mode:** This template is dark-mode only by design. If light mode is needed, use Paper/Ink or Editorial templates instead
- **Complementary templates:** Works well in rotation with Editorial (for prose-heavy docs) and Paper/Ink (for warm, approachable technical docs)

## Complete CSS Variables Reference

```css
:root {
  /* Typography */
  --font-body: 'IBM Plex Sans', system-ui, sans-serif;
  --font-mono: 'IBM Plex Mono', 'Courier New', monospace;

  /* Base colors */
  --bg: #0d1821;
  --surface: #1a2332;
  --surface-elevated: #212d3f;
  --surface-recessed: #0a1219;
  
  /* Borders & structure */
  --border: rgba(138, 180, 248, 0.15);
  --border-bright: rgba(138, 180, 248, 0.25);
  --grid: rgba(138, 180, 248, 0.05);
  
  /* Text */
  --text: #e8eef5;
  --text-dim: #8a9fb8;
  --text-dimmer: #5f6e82;
  
  /* Accent (bright cyan) */
  --accent: #1fb6d6;
  --accent-dim: rgba(31, 182, 214, 0.12);
  --accent-bright: #3dd5f3;
  
  /* Status colors */
  --pass: #2dd4bf;
  --pass-dim: rgba(45, 212, 191, 0.12);
  --fail: #fb7185;
  --fail-dim: rgba(251, 113, 133, 0.12);
  --warning: #fbbf24;
  --warning-dim: rgba(251, 191, 36, 0.12);
  --pending: #818cf8;
  --pending-dim: rgba(129, 140, 248, 0.12);
}
```
