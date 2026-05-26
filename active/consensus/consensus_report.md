# Stochastic Multi-Agent Consensus Report

**Problem:** Perfect monday.com client PM dashboard for Marc Walden (Coastal Lux `18408242353`) + Claude Monday MCP usage  
**Agents:** 5 spawned (4 substantive, 1 empty)  
**Date:** 2026-05-26

## Consensus (4+/5 agents)

| Recommendation | Agents | Action taken |
|---|---|---|
| **Single photo surface on board rows (Files column)** | 5/5 | Creating **Photos for site** column + **Website Assets** group |
| **Plain-language, Marc-first grouping** | 4/5 | Keep template groups; add Website Assets as dedicated lane |
| **Claude reads board via MCP — use exact item/board names** | 5/5 | Documented in wiki + Marc update |
| **Micro-template for updates (What changed / Need from Marc / Due)** | 3/5 | Included in cover-item update |
| **3-bullet "how to use board" onboarding** | 4/5 | Posted on Project Status cover item |

## Divergences

| Topic | Split | Resolution |
|---|---|---|
| Rename all groups to Marc mental model | 1/5 strong push | **Keep** emoji template names (already deployed 2026-05-24); add plain-language explainer in update |
| Form-only vs board Files column | 1/5 form-first | **Board Files primary**; Form deferred (second hop for Marc) |
| Freeze schema / version columns | 1/5 | Log column IDs in wiki after MCP create |

## Outliers

- **Contrarian:** Form-only intake — rejected for Claude MCP visibility (items must exist on board).
- **Systems:** Repo vs Monday source-of-truth split — adopted in wiki as sync rule for Nick.

## Final ranked implementation (aggregated)

1. **📸 Website Assets** group with per-vehicle rows + **Photos for site** column (confidence 9)
2. Cover-item update @Marc with iPhone steps + Claude magic phrase (confidence 9)
3. Cards view on Website Assets (deferred — requires `create_view` follow-up)
4. Status label migration to Pending Marc / Pending Nick (deferred batch)
5. Daily `download-marc-photos.py` v2 sync (Nick-side, no board block)

## Claude + MCP tip (consensus merge)

Marc: *"What's on my Coastal Lux Monday board that needs my attention?"* — connect Monday in Claude → Connectors. For photos: open **Website Assets** → vehicle row → **Photos for site** → From Photos. When asking Claude about a specific upload, name the **exact item title** (e.g. "Chevrolet Tahoe Z71 — website photos").
