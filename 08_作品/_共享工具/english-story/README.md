# english-story · 英语故事画布插件

> 2026-11-03｜状态：**可用（harmonic15 闭环已跑通）**
> 只做一件事：把「一个英语词 + 中文谐音」变成一支**可导入 Monet 的英语故事画布**，并把我们踩过的坑做成硬门禁。
> 设计说明见 [英语故事画布插件·设计 v2](../../蛋仔记单词/00_方案/34-英语故事画布插件-设计-v2.md)。

## 为什么是"垂直"的

- 只服务**英语单词/词族短故事**（蛋仔记单词），不接中文漫剧、不做通用分镜；
- 角色、资产、眼睛锁、场景都**锁死**，不让人每次重选；
- 输出只有一种东西：`.monet` + SRT + 校验报告；不生成图片/视频、不导入、不派发；
- 所有判断都落成**规则 ID**（G/P/C/A 四层），每条都能追到一次真实翻车。

## 目录

```
english-story/
├── cli.py                 brief / validate / build / check / all
├── lib/
│   ├── rules.py           规则目录（61 条，含出处与修复）
│   ├── model.py           story/profile/资产载入
│   ├── check_story.py     G 层：故事层
│   ├── check_canvas.py    P/C/A 层：prompt、画布、资产
│   ├── prompts.py         角色锁、负向、逐拍、分镜图、卡面（只在这里写一次）
│   ├── builder.py         story.json → .monet + SRT
│   └── report.py          Markdown/JSON 报告
├── profiles/              harmonic15（已实现）、meme20（仅校验）
├── stories/               pest-15s.json（定稿样例）
├── assets.json            复用资产锁（URL/尺寸/来源画布）
├── tests/test_gates.py    32 个反例：门禁自测
└── out/                   .monet / .srt / report（产物，可重跑）
```

## DSH 插件（已安装，2026-11-03）

除了 CLI，这套能力已经装成当前 profile 的 Harness 插件：`@local/english-story`。Host-only bundle，**只注册工具，不走网络、不碰 Monet、不生成素材**；重启后仍生效。

源码在 [`../../../.plugins/english-story/`](../../../.plugins/english-story/index.js)：

```powershell
# 已执行，不必重跑
plugin_manager install_bundle target="E:\libtv漫剧\.plugins\english-story"
# 卸载
plugin_manager remove_bundle target="@local/english-story"
```

| 工具 | 作用 | 对应 CLI |
| --- | --- | --- |
| `english_story_brief` | 出故事任务书 | `cli.py brief` |
| `english_story_validate` | 查故事层（G 规则） | `cli.py validate` |
| `english_story_build` | 建 `.monet`＋SRT＋报告 | `cli.py build` |
| `english_story_check` | 复检画布（P/C/A 规则） | `cli.py check` |

工具参数示例：

```json
{ "story": "stories/pest-15s.json", "outDir": "out" }
```

配置在 `cordis.patch.yml`：`workspace`（CLI 目录）、`python`（`C:\Windows\py.exe`，必须带 `-3`，因为系统 `python` 是 2.7）。

已验证：4 个工具各调通一次（build 出 11 节点 / 17 边 / 7 组），中文输出正常。未验证：Plugin Manager 里的标题、描述和图标渲染（没有浏览器控制，只确认资源已导出）。

### 创作模式（preset，已安装）

另有一个 preset bundle `@local/dsh-english-story-preset`，在 GUI 的预设选择里显示为**「英语故事画布」**。选中后每轮只推进一个阶段：

| 阶段 | 动作 | 停点 |
| --- | --- | --- |
| S0 | 确认词/谐音/词义/场景 | 缺信息先问，不猜 |
| S1 | `english_story_brief` → 子代理并发出 3 版 story.json | — |
| S2 | 3 版并排成表 | **停下等你选**，不替你选 |
| S3 | `english_story_validate` | ERROR 清零才进下一步 |
| S4 | `english_story_build` | — |
| S5 | `english_story_check` | 有 ERROR 回 S4 |
| S6 | 交 `.monet`/SRT/报告 | 导入还是要你点头 |

配置：[`../../../.plugins/english-story-preset/cordis.patch.yml`](../../../.plugins/english-story-preset/cordis.patch.yml)。preset 只对**新会话**生效，当前已开的会话不会变。

为什么是 preset 而不是 workflow 工具：workflow 一次跑完、人插不进“选稿”；这条线必须在 S2 停一次、S3/S5 各设一道门，才挡得住以前“跳步建画布、验收走过场”的问题。

## 四步闭环

```powershell
cd "E:\libtv漫剧\08_作品\_共享工具\english-story"

# 1) 出任务书（喂给模型/子代理，硬规则全在里面）
py -3 cli.py brief --word pest --zh 拍死它 --meaning 害虫 --scene 夏夜小院石桌

# 2) 模型交回 story.json 后，先只查故事
py -3 cli.py validate --story stories/pest-15s.json

# 3) 全绿再建画布（会自动再跑一遍画布门禁）
py -3 cli.py build --story stories/pest-15s.json --copy-to "$env:USERPROFILE\Downloads"

# 4) 手改过画布，单独复检
py -3 cli.py check --canvas out/pest-15s.monet --story stories/pest-15s.json
```

退出码：`0` 干净 / `1` 只有 WARN / `2` 有 ERROR（不得交付）。

产物：

- `out/<id>.monet`：导入用画布（只交这个，不自动导入）；
- `out/<id>.srt`：字幕，后期加，视频内无字；
- `out/<id>.report.md` / `.json`：逐条校验结果，能直接贴进任务记录。

## profile（结构档）

| profile | 结构 | 状态 | 用在哪 |
| --- | --- | --- | --- |
| `harmonic15` | 15s＝6 拍（3+2+2+2+2+1）覆盖 0–12s ＋ 单卡 12–15s；无 T_A、无 V2、无旁白；含 G1 三格分镜闸门。卡尾默认后期叠；`card.in_video: true` 时内嵌 V1（15s，KC→V1 连线，负向改“除卡尾静帧外无字”） | **implemented** | [pest 15s 定稿](../../蛋仔记单词/00_方案/32-pest-15s最终版-v1.md)（后期叠）、ambition v4-a（内嵌） |
| `meme20` | 20s＝V1 8s ＋ T_A ＋ V2 9s ＋ 单卡 3s；旁白在 V2 视频内 | validate-only | [玩梗英语标准模板](../../蛋仔记单词/00_方案/23-玩梗英语-标准模板-v1.md) |

> 两档不是"合并规则"，而是**分流**：例如"黄蛋必须说出单词"只在 meme20 生效；harmonic15 的词只出现在卡尾。把两套规则混在一起就是之前反复改稿的根源。

## 三层门禁

| 层 | 管什么 | 例子 |
| --- | --- | --- |
| **G 故事层** | 词/谐音/义接证据、时间形状、道具首帧、台词归属、卡尾三行、评分 | 心易说人话、黄蛋讲解释、卡尾加小字、字幕越界 |
| **P prompt 层** | 角色锁、负向范围、手、道具、场景状态、字幕禁写、字数、时长 | 负向泛化"瞳孔"误伤黄蛋、没写两只短手、首帧没点名 |
| **C 画布层** | 节点/边/组、引用双接入、禁止边、mainOutputId、组框重叠、分镜图闸门 | token 挂了没接线、video→video、组内有依赖边、缺 G1 三格分镜 |
| **A 资产层** | 复用、URL、不重复生成 | 已生成的图又建 gen 节点、base64 URL |

规则全表在 [lib/rules.py](lib/rules.py)，每条带 `case`（出处文档）与 `fix`（怎么改）。报告按规则 ID 出，不写"感觉不对"。

## 门禁自测

```powershell
py -3 -m unittest discover -s tests -v
```

32 个反例（改台词、改时长、去 token、去手锁、加禁用边、坏 URL、缺转折、缺赌注、赌局框架…）必须逐个被对应规则抓住。
只跑样例不算证据——**反例被抓住**才算。现在是 **32 个**（另含缺分镜图、分镜第一格缺道具、道具图带词、缺转折/缺赌注/赌局框架预警）。

## 和现有工具的关系

| 工具 | 关系 |
| --- | --- |
| `../monet_push.py` | 首次导入；本插件只产 `.monet`，导入要人点头 |
| `../monet_sync.py` | 返修同步；**必须沿用同一个 prefix**（节点 ID 不变，输出才对得上） |
| `../monet_pull.py` | 先拉已有画布，判断哪些资产能复用，再改 `assets.json` |
| `检查画布接线.py`（外部） | 老脚本 9E/11W；本插件的 C 层与其等价并已交叉验证（0 ERROR / 0 WARNING） |

## 边界

- 不生成图片/视频、不导入、不删除、不派发；这些仍要每次明确授权。
- 不存账号凭据；`assets.json` 只存 storage URL。
- 不把 `out/` 当资产库：需要复用的图，先登记进 `assets.json`。
- 新场景/新角色/新画风不在本插件范围内——那是方向层的事。

## 已跑通的证据（2026-11-03）

- `pest-15s`：story 层 0/0/0，画布层 0/0/0；11 节点 / 17 边 / 7 组；
- 外部 `检查画布接线.py`：0 ERROR / 0 WARNING；
- 32 个门禁反例全过；
- 产物：[pest-15s.monet](out/pest-15s.monet)、[pest-15s.srt](out/pest-15s.srt)、[校验报告](out/pest-15s.report.md)。
- 未做：未导入 Monet、未生成任何节点（等用户点头）。
