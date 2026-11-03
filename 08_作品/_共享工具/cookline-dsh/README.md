# cookline-dsh · DSH Host 插件

> 2026-11-03｜v0.1.0｜状态：**已装在本机 DSH（profile `desktop`），工具已注册**
> 把 [cookline](../cookline/README.md) 的 CLI 包成 6 个 Agent 工具；Host-only，无界面，不导入、不派发。

## 装了什么

| 工具 | 作用 |
|---|---|
| `cookline_check` | 校验菜谱卡，默认 strict（WARN 也算不合格） |
| `cookline_build` | 出 `.monet` / runlist / 边车 / SRT |
| `cookline_gate` | 分镜闸门：`status` / `approve` / `runlist` |
| `cookline_doctor` | 审计 `.monet` 接线、字数、负向词、参考图、手改 |
| `cookline_new` | 按骨架起新菜谱卡 |
| `cookline_migrate` | 旧卡迁 v2 做兼容审计 |

插件 id `cookline`，包名 `@local/cookline-dsh`，装法是**本地目录链接**：

```
E:\libtv漫剧\08_作品\_共享工具\cookline-dsh  ←link←  profile desktop/node_modules
```

改这个目录的代码后，DSH 的本地链接不需要重新拷贝；但**替换已安装包**（改 package/依赖）通常要重启 Harness 才会加载新的 JS 模块代。

## 它怎么找到 cookline

调用时按顺序：

1. 工具参数 `root`（方法库根目录，包含 `08_作品` 的那一层）；
2. 从当前会话工作区向上，找 `08_作品/_共享工具/cookline/run.py`；
3. 从当前目录向上，若目录名本身是 `cookline`，也接受 `run.py`。

找不到会直接报错并说明找过哪里，不会静默跑错目录。

Python：Windows 先试 `py -3`，再试 `python`；其他平台试 `python3`。可用环境变量 `COOKLINE_PYTHON` 指定。

## 安装 / 卸载

安装（在 DSH 里由 Plugin Manager 或 Agent 调 `plugin_manager`）：

```
plugin_manager action=install_bundle target="E:\libtv漫剧\08_作品\_共享工具\cookline-dsh"
```

停用 / 移除：

```
plugin_manager action=set_bundle target="@local/cookline-dsh" enabled=false
plugin_manager action=remove_bundle target="@local/cookline-dsh"
```

停用只影响本 profile，不删方法库文件。

## 已验证

- `install_bundle` 返回 `application: applied`；
- `Tool` inspect 能看到 `cookline_check` / `build` / `gate` / `doctor` / `new` / `migrate`；
- 实际调用：
  - `cookline_check` 自测卡 → `0 ERROR / 0 WARN / 2 HUMAN；通过`；
  - `cookline_build` → 33 节点 / 44 边 / 7 组，四条视频 1659/1625/1712/1705 字；
  - `cookline_doctor` → `0 ERROR / 0 WARN`；
  - `cookline_gate status` → 四级 PENDING；
  - `cookline_gate approve assets` → 签核成功；`runlist storyboard` 被拒并返回 exit 1，说明闸门顺序生效。
- 图标与 `locale/zh.json`、`locale/en.json` 已随包提供；**Plugin Manager 里的实际渲染未在浏览器里看过**，只验证了资源存在且 SVG 可读。

## 边界

- Host-only：没有面板、按钮或页面；不会出现在聊天侧栏之外。
- 工具只跑 `cookline/run.py`，不调用生成模型、不导入 Monet、不派发、不删除。
- 方法库路径是外部依赖；换机器要同时带 `08_作品/_共享工具/cookline` 和这个包。
- 标题/描述/图标是本地原创；没有外部素材授权问题。
