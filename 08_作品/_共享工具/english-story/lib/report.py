# -*- coding: utf-8 -*-
"""校验报告：Markdown 给人看，JSON 给下一次迭代做基线。"""
import json
from datetime import datetime, timedelta, timezone

TZ = timezone(timedelta(hours=8))
LEVEL_ORDER = {"ERROR": 0, "WARN": 1, "INFO": 2}
LEVEL_CN = {"ERROR": "阻断", "WARN": "警告", "INFO": "提示"}


def summary_line(result):
    return (f"{result.status} | ERROR {result.count('ERROR')} / "
            f"WARN {result.count('WARN')} / INFO {result.count('INFO')}")


def _sorted(findings):
    return sorted(findings, key=lambda f: (LEVEL_ORDER.get(f.level, 9), f.rule))


def render_markdown(results, title, meta=None):
    lines = [f"# {title}", ""]
    lines.append(f"> 生成时间：{datetime.now(TZ).replace(microsecond=0).isoformat()}｜"
                 f"插件：english-story（英语故事画布）")
    if meta:
        for key, value in meta.items():
            lines.append(f"> {key}：{value}")
    lines.append("")

    for result in results:
        lines.append(f"## {result.subject}")
        lines.append("")
        lines.append(f"**{summary_line(result)}**")
        lines.append("")
        findings = _sorted(result.findings)
        if not findings:
            lines.append("无问题。")
            lines.append("")
            continue
        lines.append("| 级别 | 规则 | 检查项 | 位置 | 实际 | 修复 | 出处 |")
        lines.append("|---|---|---|---|---|---|---|")
        for f in findings:
            lines.append(
                f"| {LEVEL_CN.get(f.level, f.level)} | {f.rule} | {f.title} | {f.where or '-'} | "
                f"{f.message.replace('|', '/')} | {f.fix.replace('|', '/')} | {f.case} |")
        lines.append("")

    lines.append("## 判定")
    lines.append("")
    errors = sum(r.count("ERROR") for r in results)
    warns = sum(r.count("WARN") for r in results)
    if errors:
        lines.append(f"- 有 {errors} 个阻断项：**不得交付/导入**，先按“修复”列改。")
    elif warns:
        lines.append(f"- 无阻断项，{warns} 个警告：可交付，但逐条确认后再导入。")
    else:
        lines.append("- 全绿：可交付。")
    lines.append("")
    return "\n".join(lines)


def render_json(results, meta=None):
    return {
        "generated_at": datetime.now(TZ).replace(microsecond=0).isoformat(),
        "meta": meta or {},
        "results": [
            {
                "subject": r.subject,
                "status": r.status,
                "counts": {lv: r.count(lv) for lv in ("ERROR", "WARN", "INFO")},
                "findings": [f.as_dict() for f in _sorted(r.findings)],
            }
            for r in results
        ],
    }


def write_report(path_prefix, results, title, meta=None):
    from pathlib import Path

    prefix = Path(path_prefix)
    prefix.parent.mkdir(parents=True, exist_ok=True)
    prefix.with_suffix(".report.md").write_text(
        render_markdown(results, title, meta), encoding="utf-8")
    prefix.with_suffix(".report.json").write_text(
        json.dumps(render_json(results, meta), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return prefix.with_suffix(".report.md"), prefix.with_suffix(".report.json")
