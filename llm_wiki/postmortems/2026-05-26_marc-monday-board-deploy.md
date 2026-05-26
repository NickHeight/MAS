---
tags: [postmortem, turo, monday, marc, upwork-ops]
date: 2026-05-26
domain: upwork-ops
board_id: 18408242353
---

# Postmortem — Marc Monday client portal + photo upload lane

## What shipped

- Monday board `18408242353`: group **Website Assets** (`group_mm3qv6ht`), column **Photos for site** (`file_mm3q41g2`)
- Anchor item for Marc: `12105215044` (START HERE — upload all website photos)
- Vehicle/section seed items + cover-item update `5225939914` + bell notification to Marc `102059234`
- Stochastic consensus report: `active/consensus/consensus_report.md`
- Canonical wiki (Upwork llmwiki): `Turo/decisions/2026-05-26_marc_monday_consensus_research.md`, `Turo/decisions/2026-05-26_marc_monday_board_redesign.md`

## Marc workflow (one place)

Monday app → **Website Assets** → vehicle row or START HERE → **Photos for site** → **From Photos**. No Gmail/Drive.

## Claude + Monday

Marc connects Monday in Claude; asks with exact item titles. Repo remains ship target after Nick syncs assets.

## Remaining

Cards/Gallery views, status relabels, automations, wiki↔board reconciliation, `download-marc-photos.py` v2.

## Links

- Upload row: https://height-consultingfirm.monday.com/boards/18408242353/pulses/12105215044
- Board: https://height-consultingfirm.monday.com/boards/18408242353
