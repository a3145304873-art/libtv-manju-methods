"""检查迁移边界、原文哈希、导航与索引；不能验证成片或外部附件。"""
from pathlib import Path
from argparse import ArgumentParser
import hashlib
import json
import re
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
MEDIA = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".mp4", ".mov", ".mp3", ".wav"}
# 用户 2026-10-29 指定的作品区：允许放资产、画布与成片。方法层（08_作品 以外）仍不得携带制作媒体。
WORKSPACE = ROOT / "08_作品"


def require(condition, detail):
    if not condition:
        raise ValueError(detail)


def without_fences(text):
    active = None
    out = []
    for line in text.splitlines():
        marker = re.match(r"^\s*(`{3,}|~{3,})", line)
        if marker:
            token = marker[1]
            if active is None:
                active = token
            elif token[0] == active[0] and len(token) >= len(active):
                active = None
            continue
        if active is None:
            out.append(line)
    return "\n".join(out)


def main(excluded_terms=()):
    (ROOT / "validation-report.json").write_text('{"status": "running"}\n', encoding="utf-8")
    manifest = json.loads((ROOT / "source-manifest.json").read_text(encoding="utf-8"))
    sources = manifest["sources"]
    ids = [s["id"] for s in sources]
    require(len(ids) == len(set(ids)), "来源 ID 重复")
    hashes = 0
    paths = set()
    for source in sources:
        for file in source["files"]:
            path = (ROOT / file["path"]).resolve()
            require(path.is_relative_to(ROOT), f"来源路径逃逸: {path}")
            require(path not in paths, f"来源文件重复注册: {path}")
            paths.add(path)
            require(path.is_file(), f"缺少原文: {path}")
            # 入库有两种哈希口径：多数按 CRLF→LF 归一化文本记录（与仓库 blob 一致），少数按原始字节（原文为 CRLF）。
            # 仓库统一存 LF，检出侧可能是 LF 或 CRLF，因此三种口径任一匹配即通过：
            # 当前字节、CRLF→LF 归一化、以及 LF→CRLF 还原（用于比对按原始 CRLF 字节记录的哈希）。
            data = path.read_bytes()
            variants = [data]
            if b"\r\n" in data:
                variants.append(data.replace(b"\r\n", b"\n"))
            else:
                variants.append(data.replace(b"\n", b"\r\n"))
            require(file["sha256"] in {hashlib.sha256(v).hexdigest() for v in variants}, f"原文哈希不符: {path}")
            hashes += 1
    links = 0
    # 工作区文档引用的制作媒体常留在媒体库/本机、按边界规则不入仓库；
    # 这类缺口逐条记录进验证报告保持可见，不静默放行，也不当作失败。
    workspace_media_links_outside_repo = []
    generated = []
    workspace_files = 0
    for path in ROOT.rglob("*"):
        if ".git" in path.parts or "__pycache__" in path.parts:
            continue
        require(not path.is_symlink(), f"方法库包含外部链接: {path}")
        if not path.is_file():
            continue
        in_workspace = WORKSPACE in path.parents
        if in_workspace:
            workspace_files += 1
        else:
            require(path.suffix.lower() not in MEDIA, f"不应携带制作媒体: {path}")
        require(path.name not in {"credentials.json", ".env"} and ".libtv" not in path.parts,
                f"不应携带账号配置: {path}")
        if path.suffix not in {".md", ".txt", ".json"}:
            continue
        text = path.read_text(encoding="utf-8-sig")
        # 检查内容文件；检查脚本本身包含排除词定义，不属于内容层。
        for word in excluded_terms:
            require(word not in text, f"发现旧项目内容词 {word}: {path}")
        if path.suffix == ".json":
            json.loads(text)
        if path.suffix != ".md":
            continue
        if not in_workspace:
            generated.append(path)
        for target in re.findall(r"(?<!!)\[[^\]]*\]\(([^)]+)\)", without_fences(text)):
            if re.match(r"^(?:https?://|#|app://)", target):
                continue
            local = unquote(target.strip("<>").split("#")[0])
            require(not re.match(r"^[a-zA-Z]:|^/", local), f"导航依赖绝对路径: {path}: {target}")
            resolved = (path.parent / local).resolve()
            require(resolved.is_relative_to(ROOT), f"链接逃逸: {path}: {target}")
            if not resolved.exists():
                in_ws = WORKSPACE in path.parents
                is_media = resolved.suffix.lower() in MEDIA
                require(in_ws and is_media, f"失效链接: {path}: {target}")
                workspace_media_links_outside_repo.append(
                    {"file": str(path.relative_to(ROOT)), "target": target})
            links += 1
    ability_text = (ROOT / "01_能力库/能力卡.md").read_text(encoding="utf-8")
    ability_ids = re.findall(r"^## (C\d+)｜", ability_text, re.M)
    require(len(ability_ids) == len(set(ability_ids)), "能力编号重复")
    stages = (ROOT / "00_方法论/01-阶段学习与确认.md").read_text(encoding="utf-8")
    require(all(f"| S{i} " in stages for i in range(7)), "阶段表不完整")
    skills = list((ROOT / ".agents/skills").glob("*/SKILL.md"))
    for path in skills:
        text = path.read_text(encoding="utf-8")
        require(text.startswith("---\n") and "\nname: " in text and "\ndescription: " in text,
                f"Skill 元数据不完整: {path}")
    inventory = json.loads((ROOT / "snapshot-inventory.json").read_text(encoding="utf-8"))
    result = {
        "status": "pass", "source_records": len(sources), "source_hashes_verified": hashes,
        "snapshot_totals": inventory["totals"], "generated_markdown_files": len(generated),
        "relative_links_verified": links, "ability_ids": ability_ids,
        "project_skill_entries": len(skills),
        "workspace_files": workspace_files,
        "workspace_media_links_outside_repo": workspace_media_links_outside_repo,
        "excluded_content_terms_checked": len(excluded_terms),
        "boundary": "method layer carries no production media; 08_作品 workspace allowed to carry assets/canvas/outputs; supplied excluded content terms, credentials, symlinks and external local navigation still rejected",
        "limitations": "engineering/package checks only; source media and method quality not evaluated; missing upstream attachments remain missing",
    }
    (ROOT / "validation-report.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--exclude-term", action="append", default=[], help="本次迁移需排除的内容词，可重复；不将具体旧项目词固化在方法库")
    args = parser.parse_args()
    try:
        main(args.exclude_term)
    except Exception as error:
        (ROOT / "validation-report.json").write_text(
            json.dumps({"status": "fail", "error": str(error)}, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8")
        raise
