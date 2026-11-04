---
name: manju-laoli
description: >-
  漫剧老李 Short-Drama Director Suite V7.4.26（上游开源，MIT）的本地安装入口：1 总控 + 12 子技能，覆盖赛道分流、剧本、资产、分镜、三大打戏引擎、投喂与质检。用在需要仙侠/玄幻打戏、大招与终结技、剑阵法相、打戏分镜与 Seedance 投喂提示词的场合；用户提到漫剧老李、打戏引擎、大招范式、玄幻大招、万剑归宗、法相、剑阵、终结技、投喂闸门时使用。
---

# 漫剧老李套装（本地安装）

上游：`lixiaoxiao9888-create/manju-laoli-skill`，commit `6f16955`（2026-10-21），MIT。
安装范围与排除项见 [来源记录](README-来源.md)。这里只做路由，不复制上游正文。

## 先读哪份

| 要做的事 | 读 |
|---|---|
| 全流程（先问六道锁再动手） | [总控](short-drama-director/SKILL.md) |
| **仙侠/玄幻大招、终结技、剑阵、法相** | [玄幻仙侠引擎](sd-xuanhuan-engine/SKILL.md) |
| 通用打戏、群战 | [通用打戏引擎](sd-combat-engine/SKILL.md) |
| 真人写实格斗 | [写实打戏引擎](sd-real-engine/SKILL.md) |
| 文戏分镜、故事板 | [分镜引擎](sd-storyboard-engine/SKILL.md) |
| 资产锁定与连续性 | [资产引擎](sd-asset-engine/SKILL.md) |
| 投喂闸门与格式 | [投喂引擎](sd-feed-engine/SKILL.md) |
| 成片质检与声音 | [质检引擎](sd-qc-engine/SKILL.md) |

## 写大招时按这个顺序取

1. [漫剧大招范式](short-drama-director/references/anime-ultimate-vfx-paradigm.md)：15 秒三段式、去水五律、双色缠绕、双属性对冲、绝杀收尾。
2. [三档与终结技体系](sd-combat-engine/references/tier-and-finisher-system.md)：R1/R2/R3 定档、终结技三幕、大招运镜 11 模式 A~K。
3. [大招·阵法法相参考库](sd-combat-engine/references/ultimate-array-library.md)：五套符文剑阵、法相五段式。
4. [玄幻特效体系](sd-xuanhuan-engine/references/xuanhuan-elements-vfx.md) 与 [大场面尺度](sd-xuanhuan-engine/references/grand-scale-domains.md)：13 类三层复合元素、尺度四件套、画面几何九要素（原文标注「大招必写」）。
5. [收束协议](sd-xuanhuan-engine/references/core-combat-laws.md)：A 遗物定场 / B 抛飞隔离 / C 光粒湮灭 / D 纯打斗硬切——防「天坑炸完、对手在坑上凭空刷出」。

## 使用边界

- 上游是**规则文档**，自述来自实战复盘，不是运行证据；本地未跑过它的 `scripts/` 机检，也未做过生成验证。
- 总控强制「六道前置锁未指定就停下问用户」，与本库「每个制作阶段先确认参考」是两套闸门；同时启用时以用户已确认的参考包为准，不重复追问同一决定。
- 子技能之间靠同级目录互相引用（如玄幻引擎读通用打戏的护栏）。**不要单独搬走某一个子目录**，否则跨引擎引用断链。
