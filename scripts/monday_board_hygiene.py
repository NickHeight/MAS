#!/usr/bin/env python3
"""Daily hygiene for Marc's Coastal Lux client Monday board.

Moves Done / shipped items into the Completed group and keeps action items tidy.
Run from Task Scheduler or manually after shipping work.

Requires: MONDAY_API_TOKEN in environment.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.request
from pathlib import Path

BOARD_ID = 18408242353
COVER_ITEM_ID = 11805693950
COMPLETED_GROUP_ID = "topics"
ACTION_GROUP_ID = "group_mm2az700"
WEBSITE_GROUP_ID = "group_mm3qv6ht"
STATUS_COLUMN_ID = "color_mm2aqns9"
API_URL = "https://api.monday.com/v2"

# Status labels treated as shipped
DONE_LABELS = frozenset({"Done", "done"})


def _gql(query: str, variables: dict | None = None) -> dict:
    token = os.environ.get("MONDAY_API_TOKEN")
    if not token:
        raise SystemExit("MONDAY_API_TOKEN is not set")
    payload: dict = {"query": query}
    if variables:
        payload["variables"] = variables
    req = urllib.request.Request(
        API_URL,
        data=json.dumps(payload).encode(),
        headers={"Authorization": token, "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        body = json.loads(resp.read().decode())
    if body.get("errors"):
        raise RuntimeError(json.dumps(body["errors"], indent=2))
    return body["data"]


def fetch_items(board_id: int) -> list[dict]:
    items: list[dict] = []
    cursor: str | None = None
    while True:
        query = """
        query ($boardId: ID!, $cursor: String) {
          boards(ids: [$boardId]) {
            items_page(limit: 100, cursor: $cursor) {
              cursor
              items {
                id
                name
                group { id title }
                column_values(ids: ["color_mm2aqns9"]) {
                  id
                  text
                }
              }
            }
          }
        }
        """
        data = _gql(query, {"boardId": str(board_id), "cursor": cursor})
        page = data["boards"][0]["items_page"]
        items.extend(page["items"])
        cursor = page.get("cursor")
        if not cursor:
            break
    return items


def move_item(item_id: int, group_id: str) -> None:
    mutation = """
    mutation ($itemId: ID!, $groupId: String!) {
      move_item_to_group(item_id: $itemId, group_id: $groupId) { id }
    }
    """
    _gql(mutation, {"itemId": str(item_id), "groupId": group_id})


def is_shipped(item: dict) -> bool:
    name = item.get("name") or ""
    if name.strip().startswith("✅"):
        return True
    for cv in item.get("column_values") or []:
        if cv.get("id") == STATUS_COLUMN_ID and (cv.get("text") or "") in DONE_LABELS:
            return True
    return False


def run(board_id: int, dry_run: bool) -> int:
    moved = 0
    for item in fetch_items(board_id):
        group_id = (item.get("group") or {}).get("id")
        item_id = int(item["id"])
        if not is_shipped(item):
            continue
        if group_id == COMPLETED_GROUP_ID:
            continue
        if dry_run:
            print(f"[dry-run] move {item_id} ({item['name'][:50]}) -> Completed")
        else:
            move_item(item_id, COMPLETED_GROUP_ID)
            print(f"moved {item_id} -> Completed")
        moved += 1
    return moved


def main() -> None:
    parser = argparse.ArgumentParser(description="Move shipped Monday items to Completed group")
    parser.add_argument("--board-id", type=int, default=BOARD_ID)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    n = run(args.board_id, args.dry_run)
    print(f"Done. {n} item(s) {'would be ' if args.dry_run else ''}moved to Completed.")


if __name__ == "__main__":
    main()
