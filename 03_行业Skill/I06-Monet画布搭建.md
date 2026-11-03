# I06｜Monet 画布搭建方法

> 本库适配说明：这是**内部生产规范**（非外部行业文档），整理自 2026-10-21 起多支 Monet 画布的实建与返工记录及已核实脚本文件。用户已于 2026-10-29 明确：**后续画布搭建一律采用本格式**。文中模型名、字数上限、存储 URL、账号与 API 细节是平台事实记录，不是全库规则；换平台时只迁移工艺原则，按当前工具能力重新核对参数。作品资产、build 脚本与校验脚本本体留在作品工作区（见文末依赖），本库只存方法与指针。

原文：[原文/source.md.txt](../04_原始资料/industry-skills/I06/source.md.txt)｜整理日期 2026-10-29｜状态：生产验证中（多支画布实建＋返工记录＋硬校验脚本；成片级验收在各作品工作区另行记录）。

## 核心原则

**"能跑"必须同时等于"看得清、接得上"**：画布是用户直接操作的交付物。接线数据只在一处定义（build 脚本里 edges 从 `reference_images`/`first_frame` 派生生成，不手写两套），改完必跑硬校验。这是[新来源接入](../00_方法论/05-新来源接入.md)所述"运行入口"模式的完整落地样例。

## .monet 结构与接线工艺

- `.monet` 是纯 JSON（`schemaVersion:2, type:"monet.canvas"`），节点六类：`input-image / input-text / input-video / gen-image / gen-video / gen-audio`；脚本生成 ID 用 `md5(前缀+key)[:8]`，**一次交付多支画布必须换前缀**（加 A/B/集数），否则节点 ID 全撞。
- **合法边只有三类**（数据流方向）：参考图→生成节点；首帧图→视频；派生参考→关键帧（不直接接视频，多宫格会干扰构图）。
- **禁止边**：`video→video`（平台不吃）；视频→尾帧的"来源记录边"（截尾帧时自动生成，见到先删，来源写进节点名）；`audio→video`（声音母版只放后期组）。
- **引用双接入铁律**：prompt 写了 `{{node-x}}`，必须同时 ① 挂进下游 `reference_images`（首帧则 `first_frame_image`）② 存在 `x→下游` 的边。缺一边即"无效的引用块"，节点无法派发；build 脚本必须硬校验缺边即失败。
- **组＝依赖分层＝跑序**：整组运行并行组内节点，**组内绝不能有依赖边**；组名按"第 N 步"编号即运行顺序；要重跑的段单独成组供一键跑。

## 尾帧续接体系（每支片标配）

1. 每段一个尾帧节点 `T01…T(n-1)`，单独成组；**S01 首帧＝计划首帧 K01，S02 起首帧＝上一段 T**；K 系列降级为构图参考。
2. 跑法：S01→截末帧换 T01（占位图位）→S02→…；**上一段重跑后必须重截 T**，旧尾帧会把旧尺度/旧表情带进下一段。
3. **切点性质决定接法**：同空间同朝向连续动作才硬接尾帧；地点/方向变化用 match cut 或 0.2s 叠化。截尾帧先确认截到的是适用画面。
4. 占位图故意一眼可辨（场记板样式＋"替换之前不要派发下一段"），漏换时成片第一帧就是场记板；替换后引用 token 不变。
5. 接线≠生效：首帧字段改了必须重跑下游段（先试点一段）。

## prompt 工艺（进入 S3 的具体写法）

- 结构顺序：`【首帧锁定】→【引用图片说明】→ 角色/表情/尺度 → 动作（时间拍）→ 特效延续 → 声音 → 负向`；引用 token 写在每个分镜标题/时间拍之后，每段只留本段实际用图的图例行；整段叙述式才集中开头。
- 首帧槽挂了还必须在正文写【首帧锁定】行点名 `{{node-T}}` 并锁位置/朝向/大小/光线。
- 只有 `{{node-ID}}` 是真引用（渲染成 chip）；纯文本 `@某图` 无效；节点 ID 换画布会变，按节点名重取。
- 尺度不写物理尺寸，写画面占比＋锚点比例，并规定"画面只出现人的脚/手"；默认表情写进角色锁——首帧决定最终表情。

## 工程与批次纪律

- build 脚本模式：ID 生成器→节点工厂→prompt 常量（token 简写＋`link()` 统一替换并断言无 `{{node-node-` 双前缀）→组装→自检→双份输出（仓库＋Downloads，带版本号）。
- 交付前必跑独立校验脚本（9 条 E 检查＋11 条 W 检查，覆盖上述全部禁手）；有 ERROR 不得交付。
- 批次：先跑互不依赖的图像组→关键帧→逐段视频（S01→换 T01→S02…）→尾帧依赖段；**不要一键全跑**。重跑不删 URL（新增 take 留对比）；视频逐段确认、每段最多 2 抽。
- 修改已有画布：先备份→脚本改 JSON→模块列重排并**完全替换** groups→更新标签（`【待生成】/【保留】/【重跑·尾帧】/【待替换】/【备用】`）；平台打开中的项目不自动同步，改完关开项目且不保存内存旧版。
- 交付政策：默认只交 `.monet`；**2026-11-02 用户授权后**：首次导入用 `08_作品/_共享工具/monet_push.py` 新建画布；**返修默认用 `monet_sync.py` 在原 canvasId 上覆盖更新（先建版本快照，保留已有输出，只重跑改过的节点）**，不再新建重复画布；删除须点名 canvasId 并确认无产物。画布无回收站。

## 平台事实记录（非通用规则）

生图 `gpt-image-2` 1K/medium 16:9；视频模板锁 `vidu-q4-preview` 720p/3–16 整数秒/`generate_audio:true`（蛋仔记单词系列 2026-10-28 起、小蛋仔做菜板块 2026-10-29 起，均换 `seedance-2.0-mini`）；声音母版 `seed-audio-1.0` 只做后期；Vidu Q4 prompt 硬上限 2000 字符（目标 ≤1900）；`reference_audios` 恒空、prompt 无音频 token，音频引用块会整批派发失败；参考图禁止 base64，预置 Monet 存储 URL；storage 读公开可跨画布复用。换模型先查其 prompt 字数与时长限制。

## 本机 API 操作（2026-11-02 验证；非公开文档）

Monet 桌面端把登录态放在 `%APPDATA%\@monet\desktop-prod\auth.json`（`accessToken`＋`authUser`），后端 `https://backend.monet.dreammaker.netease.com`；带 `X-Access-Token` / `X-Auth-User` / `X-Aigw-App` / `X-Group-Id` 四个头即可调用。storage 下载另取 `POST /api/storage/token`，再带 `Authorization: Bearer`。

| 操作 | 接口 | 备注 |
|---|---|---|
| 列画布 | `GET /api/canvases` | 返回 id/name/updatedAt/totalCredits |
| 读画布 | `GET /api/canvas/:id` | nodes/edges/groups ＋ 每个输出的 URL/状态 |
| 新建 | `POST /api/canvases {name}` | **成功返回 201**，不是 200 |
| 写入结构 | `PATCH /api/canvas/:id/actions` | `ADD_NODE` / `PATCH_NODE` / `UPSERT_EDGE` / `UPSERT_GROUP` 等 |
| 运行节点 | `POST https://monet-runner-api.dreammaker.netease.com/nodes/generate` | body `{canvas_id,node_id,node_type,num,model_id,model_params}`；**model_params 删掉 watermark**，否则 422 |
| 删除 | `DELETE /api/canvas/:id` | **单数 canvas**；复数 `/api/canvases/:id` 会 404 |
| 下载输出 | storage URL ＋ `Authorization: Bearer <storage token>` | 裸 GET 会 401/405 |

写入的坑（pydantic `extra_forbidden`）：节点与输出里的 `createdAt/createdBy/updatedAt/updatedBy`、输出的 `taskSource/taskId` 服务端不收，要先剥掉。动作形状：`{id, type, timestamp, payload}`；`ADD_NODE.payload.node`、`PATCH_NODE.payload.{nodeId, patches}`、`UPSERT_EDGE.payload.edge`、`UPSERT_GROUP.payload.group`。

工具：`08_作品/_共享工具/monet_pull.py`（只读拉画布＋输出）、`monet_push.py`（`--test` / `--import` / `--delete`）。脚本运行时读本机 auth，不复制凭据、不打印 token。

2026-11-02 实测：临时画布 3 节点 / 1 边 / 2 组 → 回读一致 → 删除；整支《等土豆熟》→ `canvas-52e8cd58fa`，回读 20 节点 / 45 边 / 10 组，四条视频 `duration=15`、`_reference_way=reference`、prompt 长度 1383/1340/1350/1515 全部保留。用户确认「确实成功了」，随后由用户本人删除该画布；导入能力本身已由回读验证，重导即可。

**没做**：运行/派发（`PATCH actions` 保存 ＋ `POST /nodes/generate` ＋ `output-task-ids` 轮询）没有发过请求；要跑须单独授权，先在测试画布跑 1 张 1K 图确认扣费与回填。

## 采用状态与依赖

- **采用：confirmed**（2026-10-29，用户明确后续画布用此格式搭建）。按[阶段确认](../00_方法论/01-阶段学习与确认.md)规则记为用户直接指定；替换主参考或扩范围时重新确认。
- 原文完整性：SHA-256 `fc97ea8035a9bb2dba70350feb8c73abc6579160fb06b35f412bff02d77a37e7`（17,958 字节）。
- 外部工作区依赖（存在于作品工作区 `E:\漫剧项目\ai-drama\_共享\`，2026-10-29 核实存在；本库不复制本体）：`工具/检查画布接线.py`（交付前必跑）；`工作流研究/衍生方案-蛋仔游成都/画布分析/` 下 `尾帧接线规则.md`、`首尾帧引用写法.md`、`extract_tail_frames.py`、可导入模板 `蛋仔游城市-工作流模板-v1.monet`；`工作流研究/衍生方案-蛋仔记单词/脚本/build_ep01_ambulance.py`（build 范例）；`工作流研究/衍生方案-四小只/脚本/upload_refs.py`（参考图上传）。
- 2026-10-29 作品区迁移：蛋仔记单词的资产／画布／成片统一放 `E:\libtv漫剧\08_作品\蛋仔记单词\`（规范见 [08_作品/README.md](../08_作品/README.md)）；词义反转试做（watch／crush）已作废归档到其 `02_画布\_归档-词义反转-作废\`，谐音反转待建。
- 待验证：段间风格统一与 C14 风格语句在 Monet 格式下的组合用法未见实例；seedance-2.0-mini 全线替换后的 prompt 约束差异未入本库。
