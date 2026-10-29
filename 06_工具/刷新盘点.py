"""从来源清单中的兼容 LibTV 快照重算盘点，不访问网络，不触发生成。"""
from pathlib import Path
from collections import Counter
import json

ROOT = Path(__file__).resolve().parents[1]


def inspect(path):
    doc = json.loads(path.read_text(encoding="utf-8-sig"))
    if "nodeDetails" in doc:
        nodes = list(doc["nodeDetails"].values())
    elif isinstance(doc.get("nodes"), list):
        nodes = doc["nodes"]
    else:
        raise ValueError(f"不兼容的快照结构: {path}")
    ids = {n["nodeKey"] for n in nodes}
    if len(ids) != len(nodes):
        raise ValueError(f"节点ID重复: {path}")
    types, prompts, actions, refs, models = (Counter() for _ in range(5))
    pairs, missing_members, missing_inputs = set(), set(), set()
    for node in nodes:
        data = node["data"]
        params = data.get("params") or {}
        kind = data.get("type", "unknown")
        types[kind] += 1
        actions[data.get("action", kind)] += 1
        if str(params.get("prompt") or "").strip():
            prompts[kind] += 1
        if data.get("action") == "video_generate":
            models[params.get("model", "unknown")] += 1
        for field in ("imageList", "videoList", "audioList", "textList"):
            for item in params.get(field) or []:
                if isinstance(item, dict) and item.get("nodeId"):
                    source = item["nodeId"]
                    refs[field] += 1
                    pairs.add((source, node["nodeKey"]))
                    if source not in ids:
                        missing_inputs.add(source)
        if kind == "group":
            missing_members.update(set(data.get("childNodeIds", [])) - ids)
    edges = doc.get("project", {}).get("edges")
    edge_pairs = ({(e["source"], e["target"]) for e in edges}
                  if edges is not None else None)
    return {
        "node_count": len(nodes), "types": dict(types), "actions": dict(actions),
        "nonempty_prompt_by_type": dict(prompts), "video_model_labels": dict(models),
        "parameter_refs_by_field": dict(refs), "parameter_pairs": len(pairs),
        "cli_edge_count": len(edges) if edges is not None else None,
        "parameter_pairs_missing_edges": len(pairs - edge_pairs) if edge_pairs is not None else None,
        "edges_requiring_other_interpretation": len(edge_pairs - pairs) if edge_pairs is not None else None,
        "unresolved_group_members": sorted(missing_members),
        "unresolved_input_nodes": sorted(missing_inputs),
    }


def main():
    manifest = json.loads((ROOT / "source-manifest.json").read_text(encoding="utf-8"))
    cases = []
    for source in manifest["sources"]:
        if source["kind"] != "workflow":
            continue
        for file in source["files"]:
            if file["path"].endswith("/nodes.json"):
                cases.append({"id": source["id"], "name": source["name"],
                              "snapshot": file["path"], **inspect(ROOT / file["path"])})
    result = {
        "schema_version": 1,
        "scope": "compatible local archived LibTV JSON; no media review or generation",
        "totals": {
            "snapshot_cases": len(cases),
            "nodes": sum(c["node_count"] for c in cases),
            "video_nodes_with_prompt": sum(c["nonempty_prompt_by_type"].get("video", 0) for c in cases),
            "image_nodes_with_prompt": sum(c["nonempty_prompt_by_type"].get("image", 0) for c in cases),
        },
        "cases": cases,
    }
    (ROOT / "snapshot-inventory.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result["totals"], ensure_ascii=False))


if __name__ == "__main__":
    main()
