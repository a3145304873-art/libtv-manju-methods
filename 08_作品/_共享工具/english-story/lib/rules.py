# -*- coding: utf-8 -*-
"""规则目录：把踩过的坑固化成可执行的检查条目。

分层：
  G* 故事层（story.json：词、谐音、义接、时间、道具、台词、卡尾、评分）
  P* prompt 层（角色锁、手、道具、状态、字幕、字数、时长）
  C* 画布层（节点/边/组/引用/首帧/尾帧/顺序）
  A* 资产层（复用、URL、不重复生成）

level: ERROR 阻断交付 / WARN 可交付但会出错片 / INFO 提示
case: 出处（文档名 §节），只写名字，避免链接随目录变动失效。
"""

RULES = {}


def _rule(rid, level, title, fix, case):
    RULES[rid] = {"id": rid, "level": level, "title": title, "fix": fix, "case": case}


# ---------------- 故事层 ----------------
_rule("G01", "ERROR", "词条不完整", "补齐 word.spelling / ipa / zh / meaning", "31-谐音故事智能体 §三.1")
_rule("G02", "ERROR", "谐音不是自然话", "填 hook.line / who_says / why_natural（≥10 字），说明谁在什么场景真会说", "31 §三.1")
_rule("G03", "ERROR", "义接不成立", "meaning_link 取 object/consequence/function，并写 why_meaning（≥8 字）", "31 §三.2")
_rule("G04", "ERROR", "时间轴不合 profile", "beats 从 0 连续到 screen.end，拍数/时长形状按 profile", "32-pest-15s §一")
_rule("G05", "ERROR", "道具超限或缺首帧", "道具 ≤ profile.max_props，每件 first_frame=true 且有 form/at", "31 §三.3")
_rule("G06", "ERROR", "角色台词越界", "心易只能说咔啵（咔/啵/？）；旁白只在旁白字段；其他人不说话", "23-玩梗英语 §三")
_rule("G07", "ERROR", "咔啵带括号释义", "只写拟声，动作写括号外；模型会把括号里的字念出来", "23 §三 · 27-无补救 §四")
_rule("G08", "ERROR", "黄蛋讲解释", "解释只归旁白；黄蛋只说反应短句", "23 §三")
_rule("G09", "ERROR", "黄蛋没说出单词", "至少一句台词含目标词（meme20 要求）", "23 §五点三")
_rule("G10", "ERROR", "旁白不合格", "narration.text 要点名单词与词义，voice 声明独立声线，in_video=true", "23 §三 · 27 §四")
_rule("G11", "ERROR", "卡尾不是三行", "card 只含 word/zh/meaning 三行，不加小字/标语/副标题", "31 §三.7 · 32 §三")
_rule("G12", "ERROR", "评分不足", "四项各 0–25，总分 ≥80 才允许 build", "31 §五")
_rule("G13", "ERROR", "做了补救", "continuity.no_rescue=true；心易不拿吃的回来解决问题", "27 §一/§四")
_rule("G14", "WARN", "说了下一个词", "转场靠走位/尾帧，不靠口头预告", "24-转场不报词 §二")
_rule("G15", "ERROR", "场景没由梗决定", "填 scene.name / why（为什么这个场景能让字面动作成立）", "23 §二 · 25-场景选择")
_rule("G16", "ERROR", "字幕越界或对不上台词", "字幕落在画面段内，文本是某句台词的子串", "32 §四")
_rule("G17", "ERROR", "出现画面文字字段", "视频内无字：删 on_screen_text/bubble_text，字幕只进 SRT", "23 §三 · 26 §一")
_rule("G18", "WARN", "心易是背景板", "心易至少 2 个主动作/情绪点", "23 §三 · 心易不是背景板")
_rule("G19", "WARN", "单词拼写不规范", "统一小写；短语保留空格；音标用 /…/", "31 §四")
_rule("G20", "ERROR", "字段类型不对", "按 schema 手册修正类型（数字/字符串/数组）", "本插件 schema")
_rule("G21", "ERROR", "没有局势转折", "story.turn 填 at/before/after/why：第 3–5 拍之间局势要变化，不是同类出丑的重复", "34-设计 §十三 故事性门禁 v2.1")
_rule("G22", "ERROR", "没有小愿望/小落差", "story.stakes 填 want/cost：一个具体的小愿望＋一个小落差（不要求对抗：面子/一口吃的/重摞一次都算），都要画面可拍", "35-无厘头小插曲结构 · 34-设计 §十三")
_rule("G23", "WARN", "疑似对抗框架", "出现赌/押/赔/罚/输赢等词：确认这是无厘头小插曲而不是赌局；强度上限＝微微的不顺", "35-无厘头小插曲结构 §三/§五")
_rule("G24", "ERROR", "缺收尾锚点句", "卡在视频里时 story.signoff 必填：speaker＋text（含目标词与“你记住了吗”），这是系列记忆锚点", "35-无厘头小插曲结构 §七 · 用户 2026-11-03")

# ---------------- prompt 层 ----------------
_rule("P01", "ERROR", "缺心易锁眼正向句", "写白圆眼片/中心无瞳孔/细深棕圈/全程睁开/不眨眼", "26-无瞳孔锁死 §一/§二")
_rule("P02", "ERROR", "负向泛化误伤黄蛋", "负向里的瞳孔/眼珠只写“心易的…”，不写裸词", "26 §三")
_rule("P03", "ERROR", "手没锁", "正向写“只有两只短手”，负向写多余手臂/第三只手/多双手", "AGENTS.md 视频自检 §2")
_rule("P04", "ERROR", "首帧没点名", "视频 prompt 必须含【首帧锁定】并写 {{node-K}}", "I06 prompt 工艺")
_rule("P05", "WARN", "道具凭空出现", "prompt 提到的道具必须在 props 里，且首帧就在画面", "AGENTS.md 自检 §3")
_rule("P06", "ERROR", "重复了已发生的场景状态", "场景已点着火/已开灯就不能再写生火/开灯/放水", "AGENTS.md 自检 §1")
_rule("P07", "ERROR", "没写不生成文字", "负向必须含“不生成任何文字/字幕/气泡”", "AGENTS.md 自检 §4")
_rule("P08", "WARN", "prompt 过长", "≤1900 字符（Vidu 硬上限 2000）", "I06 平台事实")
_rule("P09", "ERROR", "时长不是整数或超范围", "duration = 本段拍数总长，3–15 整数", "I06 平台事实")
_rule("P10", "ERROR", "咔啵带括号进 prompt", "prompt 里也只写拟声", "23 §三 · 27 §四")
_rule("P11", "ERROR", "旁白声线没声明", "写明画外旁白是独立声线、不是黄蛋/心易", "27 §四")
_rule("P12", "WARN", "挂参未点名 / 点名未挂参", "引用双接入；正文 token 与 reference_images 一一对应", "I06 引用双接入")
_rule("P13", "ERROR", "道具图带词", "道具图 prompt 不写目标词/谐音/词义；模型会把字烧进白底图", "AGENTS.md 视频自检 §4")
_rule("P14", "ERROR", "分镜图第一格缺道具/站位", "第一格必须点名全部道具与两人站位；否则视频首帧会缺东西", "AGENTS.md 分镜图闸门")

# ---------------- 画布层 ----------------
_rule("C01", "ERROR", "节点 ID 重复", "换 prefix 或检查 id 生成", "I06 工程纪律")
_rule("C02", "ERROR", "边端点不存在", "按节点 id 重建边", "I06 合法边")
_rule("C03", "ERROR", "引用节点不存在", "prompt 里的 {{node-x}} 必须对应真实节点", "检查画布接线 E1")
_rule("C04", "ERROR", "引用双接入缺失", "token ↔ reference_images/first_frame ↔ 边，三者齐", "I06 引用双接入铁律")
_rule("C05", "ERROR", "被引用的空节点", "input-image 没有 outputs（没传图），先补图或换节点", "检查画布接线 E6")
_rule("C06", "ERROR", "禁止边", "video→video、audio→video、视频→尾帧来源边都不许", "I06 禁止边")
_rule("C07", "ERROR", "组内有依赖边", "整组并行；把依赖拆到不同组", "I06 组＝依赖分层")
_rule("C08", "WARN", "重复边", "同 source→target 只留一条", "检查画布接线 W10")
_rule("C09", "ERROR", "prompt 超平台上限", "压到 1900 以内", "检查画布接线 E7")
_rule("C10", "ERROR", "挂了音频引用", "reference_audios 恒空；声音母版只放后期组", "I06 平台事实")
_rule("C11", "ERROR", "duration 非法", "3–16 整数（本插件按 profile 取 3–15）", "检查画布接线 E9")
_rule("C12", "WARN", "首帧挂参但正文没点名", "补【首帧锁定】行，否则模型重新构图", "检查画布接线 W1")
_rule("C13", "WARN", "挂参但正文没点名", "补 token 或摘掉挂参", "检查画布接线 W2")
_rule("C14", "WARN", "尾帧形状不对", "尾帧节点应单入单出，出线指向下一段", "检查画布接线 W7")
_rule("C15", "WARN", "纯文本 @ 引用", "@图 不算引用，必须用 {{node-x}}", "检查画布接线 W11")
_rule("C16", "ERROR", "mainOutputId 不命中 outputs", "导入会丢节点；空输出置 null，有输出指向第一个", "共享工具 README §push")
_rule("C17", "INFO", "组顺序不明确", "组名按“00/01/02…”或“第 N 步”编号即跑序", "I06 组＝跑序")
_rule("C18", "ERROR", "资产 URL 非法", "必须 http(s) storage URL；不许 base64/dataURI", "I06 参考图规则")
_rule("C19", "WARN", "组框没盖住节点", "重算 bounds，否则画布上框歪", "检查画布接线 W8")
_rule("C20", "ERROR", "缺分镜图闸门", "每段视频生成前先出 0/5/10s 三格分镜图；第一格含全部道具与站位", "AGENTS.md 分镜图闸门 2026-11-03")

# ---------------- 资产层 ----------------
_rule("A01", "ERROR", "复用资产没有 URL", "在 assets.json 登记 URL，或改成新建节点", "26 §四")
_rule("A02", "WARN", "重复生成已有资产", "已生成资产用 input-image 引用，不重建 gen 节点", "26 §四")
_rule("A03", "ERROR", "新资产没写理由", "新场景/道具/首帧必须在 story 里说明为什么不能复用", "26 §四")
_rule("A04", "ERROR", "资产引用为空", "input-image 必须有 outputs[0].value", "26 §四")


def rule(rid):
    return RULES[rid]


def level_of(rid):
    return RULES[rid]["level"]
