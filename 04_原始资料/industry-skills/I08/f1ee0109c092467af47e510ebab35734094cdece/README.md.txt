<p align="center">
  <img src="docs/showcase/intro.png" alt="flaw 一秒钟记一个单词首屏" width="44%" />
</p>

<p align="center">
  <a href="https://github.com/Mr-funny/hbg-douyin-one-second-word-video/actions/workflows/ci.yml"><img src="https://img.shields.io/github/actions/workflow/status/Mr-funny/hbg-douyin-one-second-word-video/ci.yml?branch=main&style=flat-square&label=CI" alt="CI" /></a>
  <img src="https://img.shields.io/badge/Agent%20Skill-SKILL.md-8b5cf6?style=flat-square" alt="Agent Skill" />
  <img src="https://img.shields.io/badge/Video-1080%C3%971920-166534?style=flat-square" alt="1080x1920" />
  <img src="https://img.shields.io/badge/TTS-Edge-0f766e?style=flat-square" alt="Edge TTS" />
  <img src="https://img.shields.io/badge/Visuals-Code%20Only-f59e0b?style=flat-square" alt="Code only" />
</p>

<p align="center">
  把一个英文单词做成<strong>可复刻、可精确同步、可批量生产</strong>的抖音“一秒钟记一个单词”视频。<br />
  <strong>不使用 Qwen · 不使用图片/视频生成模型 · Edge TTS · HTML/CSS/SVG/GSAP · 最终 MP4 质检</strong>
</p>

## ⚡ 一句话安装进 Agent

把下面这段话直接发给 Codex、Claude Code 或其他支持 `SKILL.md` 的 Agent：

```text
请从 https://github.com/Mr-funny/hbg-douyin-one-second-word-video 安装
douyin-one-second-word-video skill。

请自动识别当前 Agent 的全局 skills 目录；若存在旧版本，请先备份再更新。
安装后检查 SKILL.md、agents、references 和 scripts 是否完整，并校验 Python 与 Shell 脚本。

验证完成后，告诉我如何使用 $douyin-one-second-word-video
为一个英文单词制作 Edge TTS 驱动的 9:16 抖音助记视频。
```

安装完成后可以直接说：

```text
使用 $douyin-one-second-word-video 制作 flaw：瑕疵，缺陷。
尽可能拆成两个以上发音块，用中文助记组成自然小故事，按 Edge TTS 真实边界同步动画。
```

## 🎞️ 真实成片结构

以下图片全部来自最终编码的 `flaw` MP4，而不是设计稿或生成式概念图。

| 首屏：单词 + 音标 + 释义 | 中文读到时才出现助记字 |
|:---:|:---:|
| <img src="docs/showcase/intro.png" width="360" alt="flaw 首屏" /> | <img src="docs/showcase/mnemonic.png" width="360" alt="佛落助记" /> |
| 发音块真正拼成完整单词 | 自然语义桥接与读音注释 |
| <img src="docs/showcase/assembly.png" width="360" alt="flaw 组装" /> | <img src="docs/showcase/example.png" width="360" alt="flaw 例句" /> |
| 最终四次强化并保留音标 | 完整视频接触表 |
| <img src="docs/showcase/final.png" width="360" alt="flaw 末帧" /> | <img src="docs/showcase/contact-sheet.jpg" width="360" alt="flaw 全片接触表" /> |

## 它固化了哪些容易做错的细节

| 常见偏差 | Skill 的硬约束 |
|---|---|
| 首屏先把谐音梗亮出来 | 第 0 帧只显示单词、音标、释义，不泄露中文助记 |
| 把英文拆块逐个念出来 | 英文块只用于视觉映射，旁白只读中文助记字 |
| 中文助记字提前全部出现 | 逐个对齐 Edge TTS 的中文 `WordBoundary` 再显示 |
| 单音节词直接做成一个谐音 | 先比较至少两种发音块拆法，尽可能构成两段或三段故事素材 |
| 把发音块误称为音节 | 明确称为 sound chunks / 发音块，不伪造语言学结论 |
| 拆完后单词中间仍有缝 | 复用同一组元素完成无缝组装，并保留完整单词停留帧 |
| 例句只是“谐音 + 释义”硬拼 | 用具体动作或物体建立自然的因果桥接 |
| 源网页正常就直接交付 | 对编码后的 MP4 再检查黑帧、音频、分辨率、帧率和 faststart |

## 工作流

```mermaid
flowchart LR
    A["输入一个英文单词"] --> B["比较 2–3 种发音块拆法"]
    B --> C["写自然中文助记故事"]
    C --> D["生成连续 Edge TTS"]
    D --> E["提取真实词边界"]
    E --> F["HTML / CSS / SVG / GSAP 动画"]
    F --> G["HyperFrames 渲染"]
    G --> H["最终编码 MP4 QA"]
```

标准旁白结构：

```text
一秒钟记一个单词，今天要记的是 <word>，<meaning>。
<中文助记单元>。
窍门：<助记故事>！你看，<自然例子>！
所以，<word>！<word>！<word>！<word>！<meaning>。
```

## `flaw` 实测

- 发音块：`f` + `law`
- 中文映射：佛 + 落
- 助记故事：佛落了
- 语义桥接：佛像落地裂出一道缝，这就是瑕疵、缺陷
- 成片：1080×1920、24 fps、18.208 秒、437 帧
- 编码：H.264 / yuv420p、AAC stereo / 48 kHz、faststart
- 音频：约 -20.4 LUFS，True Peak 约 -6.6 dBFS
- 检查：无黑帧，并逐帧确认组装、注释括号与末帧音标

## 安装

### Codex

```bash
curl -fsSL https://raw.githubusercontent.com/Mr-funny/hbg-douyin-one-second-word-video/main/install.sh | sh
```

默认安装到 `${CODEX_HOME:-$HOME/.codex}/skills/douyin-one-second-word-video`。

### Claude Code

```bash
curl -fsSL https://raw.githubusercontent.com/Mr-funny/hbg-douyin-one-second-word-video/main/install.sh | sh -s -- --claude
```

### 手动安装

```bash
git clone https://github.com/Mr-funny/hbg-douyin-one-second-word-video.git
mkdir -p ~/.codex/skills/douyin-one-second-word-video
cp SKILL.md ~/.codex/skills/douyin-one-second-word-video/
cp -R agents references scripts ~/.codex/skills/douyin-one-second-word-video/
```

运行依赖：Node.js、HyperFrames CLI、FFmpeg、Python 3 和 `edge-tts`。

```bash
python -m pip install edge-tts
```

## 单独使用脚本

生成连续旁白、48 kHz 双声道 WAV 和词边界清单：

```bash
python scripts/generate_edge_tts.py \
  --text "一秒钟记一个单词，今天要记的是 flaw，瑕疵，缺陷。佛，落。" \
  --out-dir assets/audio
```

检查最终成片：

```bash
bash scripts/final_media_qa.sh renders/final.mp4 qa/final
```

## 仓库结构

```text
├── SKILL.md
├── agents/openai.yaml
├── references/proven-structure.md
├── scripts/
│   ├── generate_edge_tts.py
│   └── final_media_qa.sh
├── docs/showcase/
├── install.sh
├── ARTICLE.md
└── ARTICLE-FROM-SOUND-TO-STORY.md
```

进一步阅读：

- [从复刻参考视频到开源 Skill：完整制作过程与设计取舍](ARTICLE.md)
- [从声音拆分、中文故事到确定性动画：单词记忆系统复盘](ARTICLE-FROM-SOUND-TO-STORY.md)

## License

[MIT](LICENSE)
