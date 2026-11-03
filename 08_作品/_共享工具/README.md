# _共享工具 · 跨作品脚本

> 这里放**跨作品**的操作脚本，不放作品资产。当前三个：拉取（只读）、导入（新建）、同步（覆盖，保留输出）。
> 另有 [english-story](english-story/README.md)：英语故事画布插件（story → `.monet`，带 61 条门禁），已装为 DSH 插件（`@local/english-story`，4 个工具），不走 API、不导入。
> 另有 [cookline](cookline/README.md)：做菜短片生产线（菜谱卡 → 校验 → 分镜闸门 → `.monet`，带 30 条拦截），不走 API、不导入。
> 另有 [cookline-dsh](cookline-dsh/README.md)：上面这套的 DSH Host 插件（6 个 `cookline_*` 工具），已装在本机 profile `desktop`。

## monet_pull.py（只读）

**解决什么问题**：以前 Monet 里生成了图、有错漏，要手动导出再发过来重做。这个脚本直接从本机 Monet 账号拉画布状态和已经生成的结果，不用导出、不用截图。

```powershell
py -3 monet_pull.py --list
py -3 monet_pull.py --pull canvas-68731ad6dc --media images
py -3 monet_pull.py --pull "心易做菜" --media all --limit 20
```

- `--list`：列出账号里的画布（id、更新时间、名称）。
- `--pull`：按 id 或名称片段拉一支画布，写 `pulls/<canvasId>/`：
  - `canvas.json`：完整画布（节点、边、组、每个输出的 URL 与状态）；
  - `manifest.json`：输出清单（节点、类型、状态、URL、本地文件）；
  - `media/`：下载的图/视频（`--media images|all|none`）。
- `pulls/` 是**审查缓存**，可以随时删；不放进作品目录。

## monet_push.py（写入）

**解决什么问题**：画布改完不用手动拖进 Monet，直接建成一支新画布。

```powershell
py -3 monet_push.py --test "path\to\x.monet"        # 临时画布验证，自动删
py -3 monet_push.py --import "path\to\x.monet" --name "画布名"
py -3 monet_push.py --delete <canvasId>             # 只预览：显示名称/节点数，不删
py -3 monet_push.py --delete <canvasId> --yes       # 真删
```

流程（与桌面端导入一致）：

1. `POST /api/canvases {name}` → 新建空画布（返回 201）；
2. `PATCH /api/canvas/:id/actions` → `ADD_NODE` / `UPSERT_EDGE` / `UPSERT_GROUP`；
3. `GET /api/canvas/:id` → 回读校验；
4. 删除用 `DELETE /api/canvas/:id`（**单数** canvas；复数 `/api/canvases/:id` 会 404）。

已踩过的坑（写进脚本）：

- 节点/输出的 `createdAt`、`createdBy`、`updatedAt`、`updatedBy`，以及输出的 `taskSource`、`taskId`，**服务端不收**（422 extra_forbidden）；脚本会先剥掉。
- `POST /api/canvases` 成功返回 **201**，不是 200。
- 导入只写结构，**不花生成积分**。

验证记录（2026-11-02，用户确认「确实成功了」）：

- 测试画布：导入 3 节点 / 1 边 / 2 组 → 回读一致 → 删除；
- 正式：`EP01-等土豆熟-v1.monet` → **canvas-52e8cd58fa**，回读 20 节点 / 45 边 / 10 组，四条视频的 `duration=15`、`_reference_way=reference`、prompt 长度 1383/1340/1350/1515 全部保留；
- 同日重导：`EP01-等土豆熟-v1.monet` → **canvas-ea1f4018c4**，回读 20 节点 / 45 边 / 10 组，四条视频 `duration=15`、`_reference_way=reference`、prompt 1383/1340/1350/1515 保留。
- 注：旧画布 `canvas-52e8cd58fa` 随后由**用户本人删除**（2026-11-02 确认）；导入能力本身已由回读验证，需要时重导即可；
- 现有画布一张未动；临时画布已全部删除。
- 2026-11-02 补：`EP02-like-capybara-tail-v7-dog-inside.monet` → **canvas-b1064b1312**「蛋仔记单词 · 心易23s · 狗在窝里 v7 正式」，回读 **17 节点 / 26 边 / 7 组**。
- 同日修复：`mainOutputId` 必须命中本节点 `outputs`。空输出（V1/V2/V3）或旧指针（R02）会让整个节点 `ok:false`，回读只少节点、边还在，表现为“节点数不对 + 悬空边”。`clean_node()` 现在会：无 outputs → `mainOutputId=None`；有 outputs 但不匹配 → 指向第一个 output。

## monet_sync.py（覆盖同步，保留输出）

**解决什么问题**：用户报错/改需求时，不新建重复画布、不重跑已经生成的节点。先看已有输出能不能用，再在**同一个 canvasId** 上覆盖更新。

**默认返修流程**：

1. `monet_pull.py --pull <canvasId> --media images`：拉画布和已生成图，判断哪些能用；
2. 改等菜卡/重建 `.monet`——**保持同一 PREFIX**，节点 ID 不变（换 PREFIX 等于换角色，输出对不上）；
3. `monet_sync.py --canvas <canvasId> --file <x.monet> --dry-run`：看 diff（保留 / 改参数 / 新增 / 删除）；
4. 去掉 `--dry-run` 执行：默认先建版本快照，再 PATCH；**已有输出原样保留，只重跑改过的节点**。

```powershell
py -3 monet_sync.py --canvas canvas-xxxx --file "path\x.monet" --dry-run
py -3 monet_sync.py --canvas canvas-xxxx --file "path\x.monet"
```

- `PATCH_NODE` 的 patches 形状是 `{op:"replace", path:"meta"|"params", value:...}`（漏 `op` 会 422）。
- 差异算法：同 ID 比 `meta/params/specialParams/config`，变了才 PATCH；新节点 ADD；旧节点 REMOVE；边/组 UPSERT/REMOVE。
- 版本快照走 `POST /api/canvas/:id/history {name}`；**版本名最多 20 字**（超了 400 INVALID_NAME）；`--no-version` 可跳过（不建议）。
- 默认**不同步节点坐标**（画布里的摆放可能是你手动调过的）；要连坐标一起覆盖加 `--with-meta`。
- `--labels-only`：只改节点标签（保留当前坐标与参数），用来把【必重跑】/【建议重跑】/【已生成·保留】标到画布上。

验证记录（2026-11-02）：临时画布 `canvas-44da2fab18` 先导入 3 节点 / 2 个输出，再用整支 EP01 同步——保留 2、改参数 1、新增 17；回读 20 节点 / 45 边 / 10 组，**A0/A0F 的输出 URL 原样保留**；测试画布已删除。

同日实测（正式画布）：给 `canvas-ea1f4018c4` 同步 v2（加 T1–T3 尾帧第二参考）——保留 17、改参数 3（V2–V4）、新增 3（T）、新增 3 边 / 1 组；回读 **23 节点 / 48 边 / 11 组**，原有 11 个输入输出未动。

随后撤回：整帧尾帧和 K 的开场构图打架（用户指出），v3 回到 K-only——改参数 3、删 3 节点 / 3 边 / 1 组；回读 **20 节点 / 45 边 / 10 组**；这次 `POST /api/canvas/:id/history` 返回 200（版本名改成 ≤20 字后）。

2026-11-02 再同步 v4（锅煮版）：逐帧看过已生成的 4 条视频后，改 17 个节点的 params（V3 土豆下锅、V4 浅黄热土豆/睁眼、V2 去削皮、全局眼睛与负向、S3 锅与水/柴堆、K4 改引 S4＋P4），边 45→44；回读 **20 节点 / 44 边 / 10 组**，**20 个已有输出全部保留**，版本快照 200。旧视频不删，重跑生成新 take 对比。

## 运行单个节点（需用户每次明确授权）

```powershell
POST https://monet-runner-api.dreammaker.netease.com/nodes/generate
body: {canvas_id, node_id, node_type, num, model_id, model_params}
```

- `model_params` 直接取画布里该节点的 `params.model_params`，但**要删掉 `watermark`**（服务端 422：Extra inputs are not permitted）；
- 成功返回 202 + `graph_run_id`；输出状态看画布详情里该节点的 `outputs[].status`；
- 2026-11-03 用户授权跑 V1/V2 验证通过；**以后每次运行前仍要用户明确说“跑”**。

## 删除画布

```powershell
py -3 monet_pull.py --list                          # 1. 拿 canvasId，核对名称
py -3 monet_pull.py --pull <canvasId> --media none  # 2.（可选）备份 canvas.json
py -3 monet_push.py --delete <canvasId>             # 3. 预览：显示名称/节点数，不删
py -3 monet_push.py --delete <canvasId> --yes       # 4. 真删
```

- 接口是 `DELETE /api/canvas/:id`（**单数** canvas）；画布无回收站，**删了不可恢复**。
- 删除路径已验证：2026-11-02 用户在桌面端手动删除过 `canvas-52e8cd58fa`；脚本删除在测试画布上验证过。
- 只删测试画布或明确废弃的版本；正式画布只新建版本，不删已采用的。
- id 不对会提示先去 `--list` 核对；不加 `--yes` 永远只预览。

## 还没做的：运行 / 派发

运行是另一条链（`PATCH actions` 保存 + `POST /nodes/generate` 派发 + `output-task-ids` 轮询），body schema 只从 bundle 里确认了大概，**没有派发过**。要跑需要单独授权：先测试画布跑 1 张 1K 图，确认扣费与回填，再谈批量。

## 边界

- 只读脚本只发 GET（另加取 storage token 的 POST）；导入脚本只新建画布，不覆盖现有画布。
- 凭据：运行时从 `%APPDATA%\@monet\desktop-prod\auth.json` 读；不复制、不写进仓库、不打印。
- 私有接口：`backend.monet.dreammaker.netease.com`，没有公开文档，平台升级可能变。
- `pulls/` 里是账号内容，按作品素材对待，不要外发。

## 已有的一次拉取

`pulls/canvas-68731ad6dc/`：2026-11-02 从「蛋仔记单词 · morose 小饭馆版 v4」拉的 12 张已生成图 + 画布 JSON。
