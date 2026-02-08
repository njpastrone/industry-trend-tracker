# UI Design: Industry Intelligence Tracker

## Pages

Two main views: **Sector Dashboard** (home) and **Sector Detail** (drill-down).

## Page 1: Sector Dashboard

The home page. Shows all 11 GICS sectors at a glance.

### Layout

```
┌─────────────────────────────────────────────────────────┐
│  Industry Intelligence Tracker          [Last run: 2h]  │
│  Macro sector trends for IR professionals    [Refresh]  │
├─────────────────────────────────────────────────────────┤
│  Filters: [Time: 7d ▼] [Signal Type: All ▼]            │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │ Technology  │  │ Health Care │  │ Financials  │    │
│  │ XLK  -3.2% │  │ XLV  +1.1% │  │ XLF  -0.8% │    │
│  │ 12 signals  │  │ 8 signals   │  │ 6 signals   │    │
│  │ ● negative  │  │ ● mixed     │  │ ● neutral   │    │
│  │             │  │             │  │             │    │
│  │ "AI reg..." │  │ "FDA pol.." │  │ "Rate exp.."│    │
│  └─────────────┘  └─────────────┘  └─────────────┘    │
│                                                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │ Energy      │  │ Industrials │  │ Cons. Disc. │    │
│  │ ...         │  │ ...         │  │ ...         │    │
│  └─────────────┘  └─────────────┘  └─────────────┘    │
│                                                         │
│  ... (remaining 5 sectors)                              │
└─────────────────────────────────────────────────────────┘
```

### Sector Card Component

Each card shows:
- **Sector name** (bold) + ETF ticker (muted)
- **ETF 7D performance** — color coded (green positive, red negative)
- **Signal count** — number of classified signals in time window
- **Sentiment dot** — colored indicator (red negative, green positive, yellow mixed, gray neutral)
- **One-line summary** — AI-generated `summary_short` from latest narrative
- Click anywhere on card to drill into detail

### Card Sorting

Default: sorted by signal count (most active sectors first).

Options:
- Signal count (descending)
- ETF performance (worst first — "sectors under pressure")
- ETF performance (best first — "sectors with momentum")
- Alphabetical

### Filters Bar

- **Time window**: 7 days / 14 days / 30 days (same as sales tracker)
- **Signal type**: All / Regulatory / Analyst / Earnings / M&A / Competitive / Macro / ESG

### Header

- App title + subtitle
- Last pipeline run timestamp
- "Refresh" button to trigger pipeline manually

### Color Scheme

Blue/white to match the sales tracker. Consistent design language across both apps.

## Page 2: Sector Detail

Drill-down view for a single sector.

### Layout

```
┌─────────────────────────────────────────────────────────┐
│  ← Back to Dashboard                                    │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Information Technology                    XLK          │
│  ┌────────────────────────────────────────────────┐    │
│  │  7D: -3.2%  │  30D: +1.8%  │  YTD: +4.5%     │    │
│  │  vs SPY:     -1.5% (7D)     +0.3% (30D)       │    │
│  └────────────────────────────────────────────────┘    │
│                                                         │
│  ┌─ Sector Narrative ─────────────────────────────┐    │
│  │  Key themes: [AI regulation] [Export controls]  │    │
│  │                                                 │    │
│  │  The technology sector faces mounting regulatory │    │
│  │  pressure as EU AI Act enforcement begins and   │    │
│  │  US semiconductor export controls tighten...    │    │
│  │  ... (2-3 paragraphs)                           │    │
│  └─────────────────────────────────────────────────┘    │
│                                                         │
│  Signal Breakdown: [All 12] [Regulatory 4] [Analyst 3] │
│                                                         │
│  ┌─ Signals ──────────────────────────────────────┐    │
│  │  ● EU AI Act Takes Effect with New Compliance   │    │
│  │    Reuters · Feb 6 · regulatory · ● negative    │    │
│  │    "EU AI Act enforcement creates compliance     │    │
│  │    costs across the tech sector..."              │    │
│  │                                                 │    │
│  │  ● Goldman Downgrades Software Sector Outlook   │    │
│  │    Bloomberg · Feb 5 · analyst · ● negative     │    │
│  │    "Goldman cuts 2026 software growth forecast..." │    │
│  │                                                 │    │
│  │  ... (more signals)                             │    │
│  └─────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

### Sector Header

- Sector name (large) + ETF ticker
- Performance stats in a horizontal bar: 7D, 30D, YTD + relative vs SPY
- Color-coded performance numbers

### Narrative Section

- Key themes as tags/badges
- Full narrative text (2-3 paragraphs from AI)
- Timestamp of when narrative was generated

### Signal Type Tabs

Horizontal tabs showing signal count per type:
- "All (12)" | "Regulatory (4)" | "Analyst (3)" | "Earnings (2)" | ...
- Clicking a tab filters the signal list below

### Signal Feed

Chronological list of signals (newest first). Each signal shows:
- Article headline (linked to source)
- Source name + publish date
- Signal type badge (colored)
- Sentiment indicator
- AI summary (1-2 sentences)
- IR relevance score (subtle, maybe as opacity/prominence of the card)

## Components

### New Components (to build)

| Component | Description |
|-----------|-------------|
| `SectorCard.tsx` | Dashboard card for one sector |
| `SectorGrid.tsx` | Grid layout of sector cards |
| `SectorDetail.tsx` | Full detail page for one sector |
| `NarrativeBlock.tsx` | AI-generated narrative display |
| `SignalFeed.tsx` | List of classified signals |
| `SignalCard.tsx` | Single signal display |
| `SectorHeader.tsx` | Performance stats bar |
| `SignalTypeTabs.tsx` | Tab filter for signal types |
| `Filters.tsx` | Time window + type filter bar (reuse pattern from sales tracker) |

### Reusable Patterns from Sales Tracker

- Filter bar layout and styling
- Time window dropdown
- Loading spinner
- Color scheme (blue/white)
- TanStack Query patterns (queryKey, staleTime, invalidation)
- API client structure (axios instance, typed functions)

## Navigation

Simple two-page app:
- `/` — Sector Dashboard
- `/sector/:sectorId` — Sector Detail

Use React Router (or just conditional rendering if we want to keep it minimal like the sales tracker).

## Responsive Behavior

- **Desktop (>1024px)**: 3 cards per row on dashboard
- **Tablet (768-1024px)**: 2 cards per row
- **Mobile (<768px)**: 1 card per row, stacked layout

No sidebar needed (unlike the sales tracker). The dashboard is the primary interface, and sector detail is a drill-down. Keep it simpler.

## Interactions

| Action | Result |
|--------|--------|
| Click sector card | Navigate to sector detail |
| Click "Back to Dashboard" | Return to sector grid |
| Change time window | Refetch data with new `days` param |
| Change signal type filter | Filter sector cards (dashboard) or signal feed (detail) |
| Click "Refresh" | Trigger pipeline, show progress, reload data |
| Click signal headline | Open article URL in new tab |
