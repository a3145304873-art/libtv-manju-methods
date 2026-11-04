# I08｜Douyin One-Second Word Video（英语单词助记视频）

状态：**研究候选**（2026-11-03）。蛋仔英语定位为“玩梗学单词”：用好玩的梗连接词形/读音与准确词义，不做课堂讲解。从外部 Skill 选择性借用多个候选比较、发音核验、TTS 对齐（按需）和成片 QA，不安装其渲染栈。

## 来源与证据

- 来源：[Mr-funny/hbg-douyin-one-second-word-video](https://github.com/Mr-funny/hbg-douyin-one-second-word-video)，MIT。固定 main commit `f1ee0109c092467af47e510ebab35734094cdece`；选定 SKILL、README、proven-structure、sound-to-story 文章和 LICENSE 副本见 [`04_原始资料/industry-skills/I08/`](../04_原始资料/industry-skills/I08/)；SHA-256 见 `source-manifest.json`。
- GitHub 页面记录 4 Stars、2 Forks；README 展示作者自制的 `flaw` 单词样片（18.208 秒）及编码/逐帧检查数据。关注度小，且核心媒体/结果是作者自报，不能当成独立市场或学习效果验证。
- 已读：Skill 与 README 全文、`references/proven-structure.md` 全文、`ARTICLE-FROM-SOUND-TO-STORY.md` 的发音块/自然义桥/渲染 QA 部分。未运行外部脚本、未使用 Edge TTS/HyperFrames 复现、未对作者成片做独立学习测试。

## 可迁移到英语模块的规则

| 外部方法 | 加入 `english-story` 的处理 |
|---|---|
| 至少比较两种发音/助记候选；自然度或辨音度不够时回退，不把发音块称作音节 | 比较自然谐音、词形/拼写、词族或语义场景；纯视觉梗只有在能帮助回想目标词义时才作为主梗 |
| 助记要经具体动作/物件自然抵达真实词义 | 每个候选明确“读音/词形怎样连接到准确词义”；音近、记忆联想、实际 IPA 和词义分开核对 |
| 按真实 TTS word boundary 对齐动态字幕 | 记录为可选渲染技术：当前 Monet 视频产线不使用 Edge TTS 时间边界，不把其 API 或 30–80ms 数值写成通用规范 |
| 对最终编码 MP4 抽帧、看声音/黑帧/字幕 | 作为生成后验收项；本模块生成画布与校验报告不等于成片通过 |

## 不迁移

深绿黑板风格、9:16/24fps、Edge TTS 小晓 +20%、固定旁白、四次重复、“所以”单独一拍、英文字母动画拼装、HTML/SVG/GSAP/HyperFrames 全链路，均是该 Skill 的单一账号模板，不作为蛋仔故事画布的通用门禁。

## 最小阅读路由

新词选题/故事前读本卡的创意候选比较段；需要做 TTS 字幕动画时再读 `proven-structure.md` 的时间边界章节；若当前成片使用 Monet 视频生成，则忽略外部 HyperFrames 构图/运动实现，只借用最终媒体 QA 原则。
