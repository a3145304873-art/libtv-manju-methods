---
name: english-story-canvas
description: 把英语单词/词根做成蛋仔记单词的英语故事画布：故事校验、建 .monet、画布与 prompt 门禁、字幕与卡尾。用户说“英语故事”“谐音故事”“玩梗英语”“词族”“pest/morose 这类单词视频”“建英语画布”时使用。
---

# 英语故事画布（english-story-canvas）

插件本体在 `08_作品/_共享工具/english-story/`。这个 Skill 只负责路由与门禁，不重复代码。

## 什么时候用

- 新词要出谐音故事（15s 单卡）或玩梗故事（20s V1+V2）；
- 已有 `story.json` 要校验/建画布/复检；
- 画布改完要确认没有接线或 prompt 坑。

## 必读（按顺序，只读需要的）

1. [插件 README](../../../08_作品/_共享工具/english-story/README.md)：用法、profile、产物、边界；
2. [设计 v2](../../../08_作品/蛋仔记单词/00_方案/34-英语故事画布插件-设计-v2.md)：为什么这么切、规则怎么分层、哪些是待拍板；
3. `lib/rules.py`：61 条规则的 ID/级别/修复/出处（不要凭记忆改规则）。

## 标准动作

**优先用已安装的插件工具**（`@local/english-story`，已装进当前 profile）：

- `english_story_brief { word, zh, meaning, ipa?, scene?, profile? }` → 任务书
- `english_story_validate { story }` → 故事层门禁
- `english_story_build { story, prefix?, outDir?, copyTo? }` → `.monet`＋SRT＋报告
- `english_story_check { canvas, story? }` → 画布门禁

工具不可用时的 CLI 兜底：

```powershell
cd "E:\libtv漫剧\08_作品\_共享工具\english-story"

py -3 cli.py brief    --word <词> --zh <谐音> --meaning <词义> [--scene <场景>]
py -3 cli.py validate --story stories/<id>.json
py -3 cli.py build    --story stories/<id>.json
py -3 cli.py check    --canvas out/<id>.monet --story stories/<id>.json
py -3 -m unittest discover -s tests
```

- 有 ERROR：不得交付/导入，按报告“修复”列改；
- 只有 WARN：逐条确认后再导入；
- 全绿：交 `.monet`，导入仍要用户点头。

## 硬边界

- 模型只写 `story.json`；**不要让模型直接写 `.monet` 或手改 prompt**——prompt 由 `lib/prompts.py` 统一生成。
- 不生成图片/视频、不导入、不删除、不派发；需要时说清要哪一步并等用户明确授权。
- 不合并 15s 与 20s 的规则：结构、旁白、词出现位置相反，按 profile 分流。
- 复用资产先登 `assets.json`；已生成的图不要重建 gen 节点。
- 分镜图闸门（2026-11-03）：先出 G1 三格（0/5/10s），第一格含全部道具与站位，确认后再跑 K_A/V1。
- 返修同步沿用同一 `prefix`，否则节点 ID 变了、已有输出对不上。

## 交稿话术

报告路径、节点/边/组数、ERROR/WARN 数、哪些是本次新生成、哪些是复用、还没做什么（未导入/未生成）。
