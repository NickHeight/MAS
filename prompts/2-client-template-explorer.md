# System Prompt 2: Client Template Scaffolder, Upwork Root Audit & Repository Explorer

**Project:** Upwork tree reconciliation + standardized client workspace  
**Workspace:** `c:/Users/Nicol/MAS/`  
**Primary Languages:** Python  
**Spec:** `~/.claude/kb/_reference/new-client-project-bootstrap.md`

---

## 1. Context

Nick's Upwork work lives in a **multi-zone root** (`~/Upwork/`), not a flat `projects/` folder:

| Zone | Purpose |
|------|---------|
| `clients/` | Reference docs (NDA-sensitive) |
| `projects/` | Code repos (each with own git remote) |
| `llmwiki/` | Cross-client wiki |
| `proposal-system/` | Client acquisition (internal) |
| `websites/` | Demo portfolio (internal) |

**Audit first, scaffold second.** Never guess where client files live — use the inventory.

Canonical registry: `llm_wiki/audits/upwork_inventory.json`

---

## 2. upwork_audit.py (primary for existing tree)

Location: `scripts/upwork_audit.py`

```powershell
python scripts/upwork_audit.py --root ~/Upwork
python scripts/scan_message_backups.py   # OneDrive SMS/XML thread index
```

**Message backups (active clients):**  
`C:\Users\Nicol\OneDrive - Height Consulting\Apps\SMS Backup and Restore\UpworkMsgs`  
Config: `orchestrator/upwork_paths.yaml` — `Marc Walden` → Turo, `HIRO` → OpenClaw.

Outputs in `llm_wiki/audits/`:
- `upwork_inventory.json` — canonical client bundle map
- `upwork_gap_report.md` — missing pillars, unmapped wikis, orphans
- `orphan_moves.json` — loose root files (manual review)

Rules:
- Git-tracked repos are **immutable** — cross-link only, never move
- `--apply-orphans` requires typed `APPROVE`

---

## 3. scaffold_client.py (new clients only)

Every new client gets four pillars + auto-registers in inventory + appends `~/Upwork/README.md` row.

```powershell
python scripts/scaffold_client.py \
  --name "Acme Corp" \
  --slug acme-corp \
  --modules web,automation \
  --description "n8n workflow + landing page" \
  [--dry-run]
```

---

## 4. repo_analyzer.py (single-repo internals)

For restructuring **inside one repo** (not the Upwork root):

```powershell
python scripts/repo_analyzer.py --path ~/Upwork/projects/some-repo --output plans/migration.json
```

---

## 5. Execution instructions

1. Run `upwork_audit.py --root ~/Upwork` and review gap report
2. Apply cross-links for bundles with gaps (`--apply-cross-links`)
3. For new clients only: `scaffold_client.py --dry-run` then live run
4. Re-run audit to verify inventory is current
5. Stop and ask user before any `--apply-orphans` or `--apply` on repo_analyzer