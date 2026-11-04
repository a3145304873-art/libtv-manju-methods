---
name: english-story-canvas
description: 把英语单词/词根做成蛋仔记单词的英语故事画布：故事校验、建 .monet、画布与 prompt 门禁、字幕与卡尾。用户说“英语故事”“谐音故事”“玩梗英语”“词族”“pest/morose 这类单词视频”“建英语画布”时使用。
---

# 玩梗学单词短剧画布（english-story-canvas）

插件本体在 `08_作品/_共享工具/english-story/`。这个 Skill 只负责路由与门禁，不重复代码。

## 什么时候用

- 新词要做英语玩梗短剧（15s 单卡或 20s V1+V2）；自然谐音是优先候选之一，不是每集必备；
- 已有 `story.json` 要校验/建画布/复检；
- 画布改完要确认没有接线或 prompt 坑。

## 必读（按顺序，只读需要的）

1. [心易·跨项目角色规范](../../../08_作品/_共享角色/心易/README.md)：全局无台词约束；
2. [插件 README](../../../08_作品/_共享工具/english-story/README.md)：用法、profile、产物、边界；
3. [设计 v2](../../../08_作品/蛋仔记单词/00_方案/34-英语故事画布插件-设计-v2.md)：为什么这么切、规则怎么分层、哪些是待拍板；
4. [邪修英语拆解与规范迭代](../../../08_作品/蛋仔记单词/00_方案/37-邪修英语拆解与规范迭代-v1.md)：B站长课与外部 Skill 的迁移边界；
5. [I08 外部 Skill 适配卡](../../../03_行业Skill/I08-单词助记短视频Skill.md)：候选比较、义桥、真实 TTS 边界和成片 QA；
6. [R03 邵氏武侠英语样片](../../../07_格式参考/R03-邵氏武侠英语样片.md)：用户点名该风格时作为可选表现型，不自动覆盖现有 profile；
7. `lib/rules.py`：规则 ID/级别/修复/出处（不要凭记忆改规则）。

## 标准动作

**优先用已安装的插件工具**（`@local/english-story`，已装进当前 profile）：

- `english_story_brief { word, meaning, zh?, ipa?, scene?, profile? }` → 任务书；`zh` 是本集中文谐音/联想短句，留空由创作者按梗决定
- `english_story_validate { story }` → 故事层门禁
- `english_story_build { story, prefix?, outDir?, copyTo? }` → `.monet`＋SRT＋报告
- `english_story_check { canvas, story? }` → 画布门禁

工具不可用时的 CLI 兜底：

```powershell
cd "E:\libtv漫剧\08_作品\_共享工具\english-story"

py -3 cli.py brief    --word <词> --meaning <词义> [--zh <记忆钩子>] [--scene <场景>]
py -3 cli.py validate --story stories/<id>.json
py -3 cli.py build    --story stories/<id>.json
py -3 cli.py check    --canvas out/<id>.monet --story stories/<id>.json
py -3 -m unittest discover -s tests
```

- 有 ERROR：不得交付/导入，按报告“修复”列改；
- 新建 schema 3 故事：目标是“玩梗学单词”，比较至少两种不同记忆梗并说明读音/词形怎样连接准确词义、选中梗落在哪个拍点。自然谐音优先；词形/拼写联想、双关、多义、词族或语义场景也可选。与目标词记忆无关的纯笑料不能当主梗；不写成课堂讲解。历史稿兼容；
- 只有 WARN：逐条确认后再导入；
- 全绿：交 `.monet`，导入仍要用户点头。

## 硬边界

- 模型只写 `story.json`；**不要让模型直接写 `.monet` 或手改 prompt**——prompt 由 `lib/prompts.py` 统一生成。
- 不生成图片/视频、不导入、不删除、不派发；需要时说清要哪一步并等用户明确授权。
- 不合并 15s 与 20s 的规则：结构、旁白、词出现位置相反，按 profile 分流。
- 心易是固定无台词角色，只能发“咔啵”；不能给她写人话、内心独白或借旁白代言。用动作和表情设计她的参与；旁白若存在，必须是独立声线。
- 复用资产先登 `assets.json`；已生成的图不要重建 gen 节点。
- 分镜图闸门（2026-11-03）：先出 G1 三格（0/5/10s），第一格含全部道具与站位，确认后再跑 K_A/V1。
- 返修同步沿用同一 `prefix`，否则节点 ID 变了、已有输出对不上。

## 交稿话术

报告路径、节点/边/组数、ERROR/WARN 数、哪些是本次新生成、哪些是复用、还没做什么（未导入/未生成）。
