import json

FP = "C:/Users/Nicol/MAS/n8n-workflows/hh-insurance/qualification-router.json"
wf = json.load(open(FP, encoding="utf-8"))

def enroll_node(node_id, name, track_value, prefix, position_y):
    props_expr = (
        "={{ { hh_insurance_track: \"" + track_value + "\", "
        + "hh_insurance_" + prefix + "_step: 0, "
        + "hh_insurance_" + prefix + "_state: \"active\", "
        + "hh_insurance_" + prefix + "_enrolled_at: $now.toISO(), "
        + "hh_insurance_classification_confidence: $json.confidence, "
        + "hh_insurance_classification_reasoning: $json.reasoning } }}"
    )
    return {
        "parameters": {
            "assignments": {
                "assignments": [
                    {"id": "ce", "name": "contact_email", "value": "={{ $node[\"When Called\"].json.contact_email }}", "type": "string"},
                    {"id": "props", "name": "properties", "value": props_expr, "type": "object"},
                ]
            },
            "options": {},
        },
        "id": node_id,
        "name": name,
        "type": "n8n-nodes-base.set",
        "typeVersion": 3.4,
        "position": [860, position_y],
    }

triage_props = (
    "={{ { hh_insurance_track: \"NEEDS_TRIAGE\", "
    + "hh_insurance_triage_state: \"awaiting_nick\", "
    + "hh_insurance_triage_flagged_at: $now.toISO(), "
    + "hh_insurance_classification_confidence: $json.confidence || 0, "
    + "hh_insurance_classification_reasoning: $json.reasoning || \"bentley_unavailable_or_unknown\", "
    + "hh_insurance_raw_track: $json.track || \"unknown\" } }}"
)

triage_node = {
    "parameters": {
        "assignments": {
            "assignments": [
                {"id": "ce", "name": "contact_email", "value": "={{ $node[\"When Called\"].json.contact_email }}", "type": "string"},
                {"id": "props", "name": "properties", "value": triage_props, "type": "object"},
            ]
        },
        "options": {},
    },
    "id": "enroll-triage",
    "name": "Enroll: Low Confidence Triage",
    "type": "n8n-nodes-base.set",
    "typeVersion": 3.4,
    "position": [860, 920],
    "notes": "Fires when Bentley confidence < 0.6 OR Bentley HTTP failed OR track unrecognized. Contact lands in HubSpot tagged for manual review. n8n-monitor skill surfaces to Nick via Monday.",
}

apply_node = {
    "parameters": {"workflowId": "lib-update-hubspot-contact", "workflowInputs": {"value": "={{ $json }}"}},
    "id": "apply-update",
    "name": "Apply HubSpot Update",
    "type": "n8n-nodes-base.executeWorkflow",
    "typeVersion": 1.2,
    "position": [1100, 600],
}

result_node = {
    "parameters": {
        "assignments": {
            "assignments": [
                {"id": "seq", "name": "router", "value": "hh-insurance--qualification-router", "type": "string"},
                {"id": "track", "name": "track", "value": "={{ $node[\"Bentley: Classify Lead\"].json.track || \"triage\" }}", "type": "string"},
                {"id": "cid", "name": "contact_id", "value": "={{ $node[\"When Called\"].json.contact_id }}", "type": "string"},
                {"id": "ts", "name": "routed_at", "value": "={{ $now.toISO() }}", "type": "string"},
            ]
        },
        "options": {},
    },
    "id": "result",
    "name": "Router Result",
    "type": "n8n-nodes-base.set",
    "typeVersion": 3.4,
    "position": [1340, 600],
}

new_nodes = [
    enroll_node("enroll-yp", "Enroll: Young Parent", "young-parent", "young_parent", 200),
    enroll_node("enroll-wb", "Enroll: Wealth Building", "wealth-building", "wealth_building", 320),
    enroll_node("enroll-t2i", "Enroll: Term to IUL", "term-to-IUL", "term_to_iul", 440),
    enroll_node("enroll-urg", "Enroll: Urgent No Coverage", "urgent-no-coverage", "urgent", 560),
    enroll_node("enroll-bo", "Enroll: Business Owner", "business-owner", "business_owner", 680),
    enroll_node("enroll-re", "Enroll: Re-engage", "re-engage", "re_engage", 800),
    triage_node,
    apply_node,
    result_node,
]
wf["nodes"].extend(new_nodes)

wf["connections"]["When Called"] = {"main": [[{"node": "Bentley: Classify Lead", "type": "main", "index": 0}]]}
wf["connections"]["Bentley: Classify Lead"] = {"main": [[{"node": "Route by Track", "type": "main", "index": 0}]]}
wf["connections"]["Route by Track"] = {
    "main": [
        [{"node": "Enroll: Low Confidence Triage", "type": "main", "index": 0}],
        [{"node": "Enroll: Young Parent", "type": "main", "index": 0}],
        [{"node": "Enroll: Wealth Building", "type": "main", "index": 0}],
        [{"node": "Enroll: Term to IUL", "type": "main", "index": 0}],
        [{"node": "Enroll: Urgent No Coverage", "type": "main", "index": 0}],
        [{"node": "Enroll: Business Owner", "type": "main", "index": 0}],
        [{"node": "Enroll: Re-engage", "type": "main", "index": 0}],
        [{"node": "Enroll: Low Confidence Triage", "type": "main", "index": 0}],
    ]
}
for n in ["Enroll: Young Parent", "Enroll: Wealth Building", "Enroll: Term to IUL", "Enroll: Urgent No Coverage", "Enroll: Business Owner", "Enroll: Re-engage", "Enroll: Low Confidence Triage"]:
    wf["connections"][n] = {"main": [[{"node": "Apply HubSpot Update", "type": "main", "index": 0}]]}
wf["connections"]["Apply HubSpot Update"] = {"main": [[{"node": "Router Result", "type": "main", "index": 0}]]}

wf["active"] = False
wf["settings"] = {"executionOrder": "v1"}
wf["tags"] = [{"name": "router"}, {"name": "business-hh-insurance"}, {"name": "ai-call"}]
wf["versionId"] = "1"
wf["id"] = "hh-insurance--qualification-router"
if "_truncation_marker" in wf:
    del wf["_truncation_marker"]

with open(FP, "w", encoding="utf-8") as f:
    json.dump(wf, f, indent=2, ensure_ascii=False)
with open(FP, "r", encoding="utf-8") as f:
    wf2 = json.load(f)
print("qualification-router.json OK -", len(wf2["nodes"]), "nodes,", len(wf2["connections"]), "connection groups")
