# Industry Intelligence Tracker - Scoping Documents

Detailed scoping docs for a new standalone app that tracks macro trends across major industries. Designed for IR professionals who need to anticipate investor questions about sector-wide themes.

**Companion to**: [Sales Intelligence Tracker](../../README.md) (company-level outreach tool)

## Why a separate app?

The Sales Intelligence Tracker answers "which company should I call today." Industry Intelligence answers "what macro themes should I be aware of across sectors." Different question, different data sources, different classification logic, different UI.

| Dimension | Sales Intelligence Tracker | Industry Intelligence Tracker |
|-----------|---------------------------|-------------------------------|
| Unit of analysis | Individual company | GICS sector / industry |
| Data sources | Company-specific RSS feeds | Sector news, regulatory feeds, macro data |
| AI classification | "Does this create IR work for Company X?" | "What's the macro narrative for this sector?" |
| Output | Ranked outreach list with talking points | Sector dashboard with trend lines and alerts |
| User action | Call a specific company | Prepare for sector-wide investor questions |

## Documents

| Document | Contents |
|----------|----------|
| [product-spec.md](product-spec.md) | Vision, user stories, feature set, what's in/out of scope |
| [data-model.md](data-model.md) | Database schema, entity relationships, GICS taxonomy |
| [pipeline-design.md](pipeline-design.md) | Data sources, ETL pipeline, AI classification prompts, batch strategy |
| [api-design.md](api-design.md) | Backend endpoints, request/response shapes |
| [ui-design.md](ui-design.md) | Pages, components, user flows, wireframe descriptions |
| [tech-stack.md](tech-stack.md) | Architecture, deployment, cost estimates, shared patterns with sales tracker |
| [lessons-learned.md](lessons-learned.md) | What we learned building the sales tracker that applies here |

## Relationship to Sales Intelligence Tracker

These apps are complementary:
- **Industry app** surfaces a sector trend (e.g., "3 healthcare companies downgraded this week")
- **Sales app** helps you act on it (which specific companies to call, what to say)

Future integration: deep-link from an industry trend to the sales tracker's filtered view of affected companies. But build them independently first.

## Cost Target

Same philosophy as the sales tracker: **under $5/month** for the full stack. All data sources identified are free or have generous free tiers.
