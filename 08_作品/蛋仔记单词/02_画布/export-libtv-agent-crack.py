# -*- coding: utf-8 -*-
"""Export LibTV Agent (TV Director) crack workflow nodes into a local method doc.

Input : 04_素材/libtv-agent-crack/*.json  (libtv node <id> raw output)
Output: 00_方案/60-蛋仔记单词-crack-LibTV-Agent工作流-v1.md

只读本地 JSON，不发网络请求，不建画布。
"""
import io
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
RAW = ROOT / "04_素材" / "libtv-agent-crack"
OUT = ROOT / "00_方案" / "60-蛋仔记单词-crack-LibTV-Agent工作流-v1.md"

CANVAS = "0d70eb6b1fe74562a632f798cfc02f4c"
SPACE = "14396686"

ASSETS = {
    "i-Qne6Qz3F3J": ("心易-标准", "角色锚（已生效，不生成）"),
    "i-2mrdVFsHBp": ("心易-眼睛参考", "眼部局部锚"),
    "i-7Z4rrw5Ebo": ("芽芽-4A-经典灰", "角色锚（已生效）"),
    "i-dGRTXvhM5L": ("芽芽-4B-暖杏", "备选配色，未使用"),
    "i-pEOy4U0OEL": ("R00-蛋仔身高比例", "只借身高比例，不借外观"),
    "i-cQt15GMnR9": ("品牌LOGO-金色V", "本片未使用（无载体）"),
}

ORDER = [
    ("i-22fgwhvt6atw", "A3"),
    ("i-8ejxytgzuau4", "A4"),
    ("i-8x45zzzbu9cs", "A5"),
    ("i-7syq75ug6ksx", "A6"),
    ("i-zrtckghshjar", "A7"),
    ("v-vqzpnk397xg7", "S1"),
]


def load(node_id):
    return json.loads((RAW / f"{node_id}.json").read_text(encoding="utf-8"))


def txt(prompt):
    if prompt is None:
        return "（无提示词）"
    if isinstance(prompt, list):
        return "\n".join(str(x) for x in prompt)
    return str(prompt)


def main():
    lines = []
    w = lines.append
    w("# 蛋仔记单词 · crack · LibTV Agent 工作流 v1")
    w("")
    w("> 2026-11-04｜状态：**Agent 原稿 + v2 修正已落盘；本地 .monet 已建（v1）**｜画布：LibTV `%s`（工作区 `%s`）" % (CANVAS, SPACE))
    w("> 来源：LibTV Agent（BETA）/ TV Director，对话里让它按「蛋仔记单词」竖屏 15–20s 搭工作流。")
    w("> 成本：首轮 4 + 建节点 5 + 修正轮 1 = **10 积分**（92 → 82）。**只建节点，未生成任何素材**。")
    w("> 原始节点 JSON：`04_素材/libtv-agent-crack/<nodeId>.json`（`libtv node <id>` 原样保存）。")
    w("")
    w("## 一、它选的故事")
    w("")
    w("单词 **crack**（裂开）。剧情：芽芽剥白煮蛋 → 递给心易 → 心易一捏「咔啵」蛋壳裂开 → 心易僵住 → 芽芽把羽冠伏下去，说唯一一句关键句。")
    w("")
    w("| 成片时间 | 内容 | 词是否出现 |")
    w("| --- | --- | --- |")
    w("| 0–8s | 芽芽剥蛋壳 → 递给心易 → 心易一捏「咔啵」裂开 → 僵住，芽芽羽冠炸起 | 无词、不报词 |")
    w("| 8–13s | 心易捂眼片塌肩 → 芽芽先看裂缝再看心易 → 羽冠一节节伏下、腮斑退色、钩喙碰手背 | 仍无词 |")
    w("| 13.0s | 芽芽：「别难过啦——是你捏得太用力，它才会 crack。」 | **首现＝正好 2/3** |")
    w("| 17–19.5s | 片尾卡：无文字干净底板定格，下半部留白给后期压词条 | — |")
    w("")
    w("合计 19.5s；镜一 8s、镜二 9s（台词 4.0s＋不重叠动作 5.0s）、片尾卡 2.5s。")
    w("")
    w("## 二、画布结构与引用关系")
    w("")
    w("```text")
    w("既有资产（已生效，不生成）")
    w("  i-Qne6Qz3F3J 心易-标准 ───────┐")
    w("  i-2mrdVFsHBp 心易-眼睛参考 ───┤")
    w("  i-7Z4rrw5Ebo 芽芽-4A-经典灰 ──┼─→ A6 镜头一·首帧 → S1 镜头一视频 8s")
    w("  i-pEOy4U0OEL R00-身高比例 ────┤")
    w("  A3 厨房料理台 ────────────────┤")
    w("  A4 白煮蛋·完整 ───────────────┘")
    w("                                 └─→ A5 白煮蛋·开裂 → A7 片尾卡·底板")
    w("S1 生效后抽最后一帧 → A8 镜头一·尾帧（待派生）→ S2 镜头二 9s（待建）→ COMP 19.5s（待建）")
    w("```")
    w("")
    w("Agent 的原话：**A8 必须从 S1 实际产物抽帧，不能伪造 key**，所以 A8/S2/合成没有建。")
    w("")
    w("## 三、逐节点（原样摘录）")
    w("")
    for node_id, tag in ORDER:
        d = load(node_id)
        data = d.get("data", {})
        p = data.get("params", {}) or {}
        w("### %s %s" % (tag, d.get("name", "")))
        w("")
        w("- nodeKey：`%s`｜type：`%s`｜action：`%s`" % (node_id, data.get("type"), data.get("action")))
        meta = {k: p.get(k) for k in ("model", "modeType", "ratio", "duration", "count") if p.get(k) is not None}
        w("- 生成参数：`%s`" % json.dumps(meta, ensure_ascii=False))
        refs = p.get("imageList") or []
        if refs:
            w("- 引用图：%s" % "、".join(str(x.get("label")) for x in refs))
        w("")
        w("```text")
        w(txt(p.get("prompt")))
        w("```")
        w("")
    w("## 四、它的提示词结构（值得抄的部分）")
    w("")
    w("1. **引用即定义**：每个节点开头逐个 `{{Node <id>}} 用于……`，把「这张图负责什么」写死，末尾统一一句「各人物的外貌、动作和站位不互相交换」。")
    w("2. **阶段制**：一个镜头内部拆【阶段一/二/三/四】，每阶段都是「承接上一阶段：…→ 动作 → 结束时：…」，等于把逐拍表写进单条提示词，防模型跳步。")
    w("3. **道具状态锚**：同一次开裂由 A5 一张图承载，S1/A7/S2 三处都引用它——裂缝形状不会每镜乱变。")
    w("4. **不采用背景**：引用浅灰底道具图/白底角色图时，逐张写「不采用其白色/灰色背景」。")
    w("5. **片尾卡主动不烧字**：做成无文字底板，文字交后期——和我们「画面内不生成任何字幕」一致。")
    w("6. **账本先行**：先写锚点集/分镜表/总表三份创作文本，再建节点，建完回填状态。")
    w("")
    w("## 五、和现有做法的差异 / 风险")
    w("")
    w("| 项 | Agent 版 | 我们的 EP01（canvas-faa4c52514） |")
    w("| --- | --- | --- |")
    w("| 镜头数 | 2 镜＋片尾卡 | 2 镜＋尾卡 |")
    w("| 尾帧链 | S1 抽帧 → A8 → S2 首帧（同思路） | K_A/T_A 手挂 |")
    w("| 关键句位置 | 13.0s（2/3） | 中段因果句 |")
    w("| 道具锚 | A4→A5 派生，三处复用 | 盒/菜单/店标分件 |")
    w("| 风险 1 | 首次生成的角色描述是「白色蛋形」，**必须喂资产否则造错人** | — |")
    w("| 风险 2 | 视频模型选 `wanx3.0`（Wan 3.0），不是我们常用的 Seedance | — |")
    w("| 风险 3 | 心易腮红：图偏粉橘，Agent 按文本写「橘色」并声明「以图为准」 | 规范写橘色 |")
    w("")
    w("## 六、缺口")
    w("")
    w("- S2 / A8 / COMP **未建**（等 S1 实际跑出尾帧）。")
    w("- 全部节点 **未生成**：A3/A4/A5/A6/A7（图）、S1（视频）。")
    w("- 本地 `.monet` **未建**：需把上面 6 个节点＋后续 3 个节点转成本地画布格式才能用 monet 工具链跑。")
    w("- SRT 已给：`00:06,300–00:06,900 咔啵`、`00:13,000–00:17,000 别难过啦——是你捏得太用力，它才会 crack。`")
    w("")
    w("## 七、下一步（待定）")
    w("")
    w("1. 让 Agent 继续跑 S1 前的图（A3/A4/A5/A6/A7），拿真尾帧补 A8/S2（花积分，需授权）；")
    w("2. 或按本文件在本地建 `.monet`，用我们自己的 monet 脚本跑，Agent 只当结构参考；")
    w("3. 或只把它当提示词范本，套回 EP01/EP02 现有画布。")
    w("")
    w("## 八、v2 修正（2026-11-04 同日晚）")
    w("")
    w("Agent 原稿有 3 处必改 + 3 处建议，已让它改完，实测节点提示词已更新：")
    w("")
    w("| # | 问题 | 改后 |")
    w("| --- | --- | --- |")
    w("| 1 | A6 首帧心易已入场，S1 阶段二又「探进半个身子」，入场演两次 | A6 改为「心易已在芽芽右侧站定」，S1 阶段二改为「承接…心易伸出的短手」，全文 `探进半个身子` 0 次 |")
    w("| 2 | S1 全无负向（settings 无 negative 字段） | 补【禁止出现】段：多手、字幕/文字/水印、心易黑瞳/瞳孔/高光/眨眼、换机位/换光、角色互换 |")
    w("| 3 | 阶段四「微推至近景」违反心易锁眼 | 改「中近景…不给心易的脸部与眼睛做特写」 |")
    w("| 4 | 镜一 8s 塞 4 拍 | A6 起手改为「已剥开一半」 |")
    w("| 5 | 「捂住纯白眼片」易演成捂眼特写 | 未在 S1 出现（该动作在未建的 S2） |")
    w("| 6 | A7「台前」有歧义 | 改「并排坐在原木料理台的台面上」 |")
    w("")
    w("**残留**：S1 阶段一仍写「捧着完整的白煮蛋低头剥壳」，与 A6「已剥开一半」矛盾——在本地抄版里已改。")
    w("")
    w("## 九、本地抄版 v1（纯净复刻，已导入 Monet）")
    w("")
    w("- 文件：`02_画布/crack-LibTV-Agent抄版-v1.monet`（13 节点 / 28 边 / 6 组；`检查画布接线.py` **0 ERROR / 0 WARNING**）")
    w("- Monet：**canvas-b82450b75b「蛋仔记单词 · crack一捏就裂 · Agent复刻 v1」**（导入回读 13/28/6 一致；**未生成**）")
    w("- 构建脚本：`02_画布/build-crack-agent.py`（读本目录 JSON 转录；改一处重跑即可）")
    w("- **提示词逐段字符比对**：A3/A4/A5/A6/A7/S1 六段归一化后**一字不差**（仅 `{{Node i-…}}` → `{{node-…}}`）；S2 为本地补写，是唯一非照抄节点。")
    w("- 连线：LibTV 21 条 vs 本地去掉 T_A/S2 后 21 条，**逐对集合相等**。")
    w("- 本地增补（非照抄）：`T_A` 尾帧占位、`S2`、`S0` 说明、6 个分组；素材节点只放被引用的 4 张（4B/LOGO 未引用，未放）。")
    w("- 模型：图 `gpt-image-2`、视频 `seedance-2.0-mini`（Agent 原稿为 `lib-image-2.5-s` / `wanx3.0`）。")
    w("- 跑序：A3＋A4 → A5＋A6 → S1 → 用 S1 最后一帧替换 `T_A` → S2 → A7 → 合成 19.5s。")
    w("")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print("written:", OUT)
    print("bytes:", OUT.stat().st_size)


if __name__ == "__main__":
    main()
