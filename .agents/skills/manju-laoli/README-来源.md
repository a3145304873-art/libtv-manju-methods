# 来源记录：漫剧老李套装

| 项 | 值 |
|---|---|
| 上游 | https://github.com/lixiaoxiao9888-create/manju-laoli-skill |
| 类型 | W（工作流案例 / Agent 技能套装），不是行业标准文档，也不是运行证据 |
| 版本 | README 自述 V7.4.26 |
| commit | `6f16955c57053d77ea0ffbdbbf3a7985a3e0080a` |
| commit 日期 | 2026-10-21 10:06:28 +0800 |
| 取用日期 | 2026-11-03 |
| 许可 | MIT（仓库根 LICENSE，Copyright (c) 2026 Short-Drama Director Suite contributors） |
| 安装位置 | `.agents/skills/manju-laoli/` |
| 文件数 | 165（13 个技能目录 + LICENSE + 本记录 + 路由 SKILL.md） |

## 导入范围

整仓 13 个技能目录同级导入（上游 README 要求「总控 + 12 子技能整体同级部署」）：
`short-drama-director`、`sd-decision-engine`、`sd-recon-engine`、`sd-script-engine`、`sd-overseas-engine`、`sd-jieshuo-engine`、`sd-asset-engine`、`sd-storyboard-engine`、`sd-combat-engine`、`sd-xuanhuan-engine`、`sd-real-engine`、`sd-feed-engine`、`sd-qc-engine`。

## 未导入及其原因

| 上游文件 | 处理 | 原因 |
|---|---|---|
| `README.md` | 未导入 | 落地页，非执行所需；其中 `README.en.md` 不存在、`mailto:` 链接会被本库导航校验判为失效链接 |
| `assets/dianzhong.png`、`assets/himadrama.png`、`assets/omniboard.jpg` | 未导入 | 方法层不放行制作媒体（`06_工具/检查方法库.py` 只对 `08_作品` 放行 png/jpg/mp4） |
| `.gitignore` | 未导入 | 无执行含义 |

## 已做的本地处理

- **换行统一为 LF**：上游 163 个文本文件为 CRLF，统一转换，避免本库 Skill 元数据校验（要求 `---\n` 开头）失败。内容未改一字。
- 新增 `SKILL.md`（路由入口）与本源记录，上游 13 个目录内正文未改动。

## 验证状态

| 项 | 状态 |
|---|---|
| 文件完整（13 目录 / 165 文件） | 已核对，与上游 `git ls-tree` 逐项比对 |
| 元数据（`---` + `name` + `description`） | 13 个 SKILL.md 全部通过 |
| 本库结构校验 `检查方法库.py` | 见交付说明 |
| 上游 `scripts/` 机检 | `validate_prompt.py --help` 与 `--self-test` 已于本机通过（`py -3`，无额外依赖）；其余脚本未逐个运行 |
| 用真实稿跑机检 | **未做**，没有拿本库的稿子过它的 C1~C33 |
| 生成效果 / 换主体迁移 | **未验证**。上游自述规则来自实战复盘，本库不据此宣称方法有效 |

## 入口提示

使用先读 [SKILL.md](SKILL.md)；写大招直接进 `sd-xuanhuan-engine/SKILL.md` 与 `short-drama-director/references/anime-ultimate-vfx-paradigm.md`。
