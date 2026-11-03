# 故事生成任务书 · 谐音故事 · 15s · 6 拍 + 单卡

> 输入：ambition / /æmˈbɪʃən/ / 谐音「俺必胜」/ 词义「野心」/ 场景：小院石桌
> 你只产出 **一个 story JSON**；不要写画布、不要生成图/视频、不要导入。

## 一、结构

- 6 拍，3+2+2+2+2+1 = 12s；卡尾 12–15s
- 道具 ≤ 3 件，第一帧全在画面里
- 单场景；不换景、不加第三个角色
- 卡尾只三行：`ambition` / `俺必胜` / `野心`，无小字

## 二、角色（硬规则）

- 黄蛋：毛绒版；只说反应短句；不讲解释、不讲词义。
- 心易：棕色水豚；只发“咔啵”（不许说人话、不许加括号释义）；不做补救。
- 本档没有旁白：词只在卡尾出现。
- 视频内无文字、无字幕、无气泡；字幕只进 SRT。

## 三、故事层门禁（违反即退回）

| 规则 | 检查项 | 修复 | 出处 |
|---|---|---|---|
| G01 | 词条不完整 | 补齐 word.spelling / ipa / zh / meaning | 31-谐音故事智能体 §三.1 |
| G02 | 谐音不是自然话 | 填 hook.line / who_says / why_natural（≥10 字），说明谁在什么场景真会说 | 31 §三.1 |
| G03 | 义接不成立 | meaning_link 取 object/consequence/function，并写 why_meaning（≥8 字） | 31 §三.2 |
| G04 | 时间轴不合 profile | beats 从 0 连续到 screen.end，拍数/时长形状按 profile | 32-pest-15s §一 |
| G05 | 道具超限或缺首帧 | 道具 ≤ profile.max_props，每件 first_frame=true 且有 form/at | 31 §三.3 |
| G06 | 角色台词越界 | 心易只能说咔啵（咔/啵/？）；旁白只在旁白字段；其他人不说话 | 23-玩梗英语 §三 |
| G07 | 咔啵带括号释义 | 只写拟声，动作写括号外；模型会把括号里的字念出来 | 23 §三 · 27-无补救 §四 |
| G08 | 黄蛋讲解释 | 解释只归旁白；黄蛋只说反应短句 | 23 §三 |
| G09 | 黄蛋没说出单词 | 至少一句台词含目标词（meme20 要求） | 23 §五点三 |
| G10 | 旁白不合格 | narration.text 要点名单词与词义，voice 声明独立声线，in_video=true | 23 §三 · 27 §四 |
| G11 | 卡尾不是三行 | card 只含 word/zh/meaning 三行，不加小字/标语/副标题 | 31 §三.7 · 32 §三 |
| G12 | 评分不足 | 四项各 0–25，总分 ≥80 才允许 build | 31 §五 |
| G13 | 做了补救 | continuity.no_rescue=true；心易不拿吃的回来解决问题 | 27 §一/§四 |
| G15 | 场景没由梗决定 | 填 scene.name / why（为什么这个场景能让字面动作成立） | 23 §二 · 25-场景选择 |
| G16 | 字幕越界或对不上台词 | 字幕落在画面段内，文本是某句台词的子串 | 32 §四 |
| G17 | 出现画面文字字段 | 视频内无字：删 on_screen_text/bubble_text，字幕只进 SRT | 23 §三 · 26 §一 |
| G20 | 字段类型不对 | 按 schema 手册修正类型（数字/字符串/数组） | 本插件 schema |
| G21 | 没有局势转折 | story.turn 填 at/before/after/why：第 3–5 拍之间局势要变化，不是同类出丑的重复 | 34-设计 §十三 故事性门禁 v2.1 |
| G22 | 没有小愿望/小落差 | story.stakes 填 want/cost：一个具体的小愿望＋一个小落差（不要求对抗：面子/一口吃的/重摞一次都算），都要画面可拍 | 35-无厘头小插曲结构 · 34-设计 §十三 |

## 四、评分（每项 0–25，总分 <80 不采用）

- natural 自然度：这句话在该场景真会说
- meaning 义接：字面对象/后果/作用能落到词义
- visual 画面：15s 内可拍、道具少、动作清楚
- character 人设：黄蛋努力笨拙、心易一下即中

## 五、输出模板

```json
{
  "schema": 1,
  "id": "ambition-harmonic15",
  "profile": "harmonic15",
  "status": "draft",
  "title": "ambition《俺必胜》",
  "word": {
    "spelling": "ambition",
    "ipa": "/æmˈbɪʃən/",
    "zh": "俺必胜",
    "meaning": "野心",
    "pos": "n."
  },
  "hook": {
    "line": "（那个人真会说的一句话，含谐音）",
    "who_says": "黄蛋",
    "why_natural": "（谁、在什么场景、为什么会这么说）",
    "meaning_link": "object|consequence|function",
    "why_meaning": "（字面怎么落到词义）"
  },
  "stakes": {
    "want": "（黄蛋这 12s 想要的具体目标，画面可拍）",
    "cost": "（出局的代价：输了丢什么，画面可拍）"
  },
  "turn": {
    "at": 3,
    "before": "（转折前局势）",
    "after": "（转折后局势）",
    "why": "（为什么意外且改变局势，不是同类出丑的重复，≥12 字）"
  },
  "scene": {
    "name": "小院石桌",
    "why": "（为什么这个场景让字面动作成立）",
    "asset": "A02"
  },
  "first_frame": {
    "composition": "（首帧构图：两人站位、每件道具 0.0s 在哪、触发物在哪）",
    "light": "（光线/时段/景别，如：夏夜暖黄院灯；中景全身）"
  },
  "props": [
    {
      "name": "（道具）",
      "form": "（形状/材质/不是什么）",
      "first_frame": true,
      "at": "（0.0s 在哪）"
    }
  ],
  "trigger": {
    "name": "（触发物）",
    "form": "（长什么样）",
    "at": "（0.0s 在哪）",
    "note": ""
  },
  "beats": [
    {
      "start": 0,
      "end": 3,
      "shot": "（景别）",
      "action": "（画面动作）",
      "speaker": "黄蛋",
      "line": "（台词）",
      "sfx": "（音效）"
    }
  ],
  "card": {
    "word": "ambition",
    "zh": "俺必胜",
    "meaning": "野心"
  },
  "subtitles": [
    {
      "start": 0.8,
      "end": 2.0,
      "text": "（台词子串）"
    }
  ],
  "scores": {
    "natural": 0,
    "meaning": 0,
    "visual": 0,
    "character": 0
  },
  "continuity": {
    "no_rescue": true,
    "no_spoiler_next": true,
    "scene_state": [
      "（0.0s 已经就位的状态）"
    ],
    "hands": "两只短手"
  },
  "negatives": [
    "（这条故事特有的负向）"
  ],
  "assets_why": {
    "A05": "新道具图",
    "K_A": "新首帧",
    "KC": "新卡"
  },
  "notes": []
}
```

## 六、交稿前自检

```powershell
py -3 cli.py validate --story stories/ambition-harmonic15.json
```

有 ERROR 就按报告改；全绿再交。
