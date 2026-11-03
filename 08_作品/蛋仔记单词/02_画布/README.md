# 02_画布

build 脚本与导出的 `.monet`。按 [I06 Monet 画布搭建方法](../../../03_行业Skill/I06-Monet画布搭建.md) 执行（用户 2026-10-29 已确认画布格式）。

## 文件约定

```
02_画布/
├── build-EP01-morose.py         ID 生成、节点工厂、prompt 常量、组装、自检、双份输出（现行 EP01）
├── EP01-morose-v1.monet         脚本产物，不手改（12 节点 / 22 边 / 8 组，含 G01 四宫格）
├── build-capybara-nospoiler.py           水豚心易＋毛绒黄蛋·不报词 v6 脚本（现行样片）
├── build-morose-meme.py                   玩梗样片 morose v2 脚本（旧）
├── EP01-morose-meme-v2.monet              旧版（11 节点 / 23 边 / 7 组）
├── build-morose-v3.py                     玩梗样片 morose v3（锁眼＋T_A）脚本
├── EP01-morose-meme-v3.monet              旧版（12 节点 / 21 边 / 7 组）
├── build-morose-v4.py                     玩梗样片 morose v4（旁白＋三卡尾）脚本
├── EP01-morose-meme-v4.monet              旧版（13 节点 / 21 边 / 7 组）
├── build-morose-v5.py                     玩梗样片 morose v5（黄蛋说话）脚本
├── EP01-morose-meme-v5.monet              旧版（13 节点 / 21 边 / 7 组）
├── build-morose-v6.py                     玩梗样片 morose v6（院子版，单卡尾）脚本
├── EP01-morose-meme-v6.monet              院子版（13 节点 / 21 边 / 7 组）
├── build-morose-restaurant.py             玩梗样片 morose 小饭馆版 v1 脚本
├── EP01-morose-restaurant-v1.monet        小饭馆版 v1（14 节点 / 21 边 / 7 组）
├── build-morose-restaurant-v2-eye-lock.py 小饭馆版 v2·心易无瞳孔锁眼脚本
├── EP01-morose-restaurant-v2-eye-lock.monet v2（14 节点 / 21 边 / 7 组）
├── build-morose-restaurant-v3-order-first.py 小饭馆版 v3·点单后才拿盒脚本
├── EP01-morose-restaurant-v3-order-first.monet v3（14 节点 / 20 边 / 7 组）
├── build-morose-restaurant-v4-closed-box.py 小饭馆版 v4·关盒递出脚本
├── EP01-morose-restaurant-v4-closed-box.monet v4（15 节点 / 21 边 / 7 组）
├── build-morose-restaurant-v5-clean.py 小饭馆版 v5·无释义/单词/桌面脚本
├── EP01-morose-restaurant-v5-clean.monet v5（15 节点 / 21 边 / 7 组）
├── build-morose-restaurant-v6-final.py 小饭馆版 v6·无补救/旁白收/单卡脚本
├── EP01-morose-restaurant-v6-final-story.monet v6（14 节点 / 20 边 / 7 组）
├── build-morose-v7-ai-card.py 小饭馆版 v7·AI单卡尾脚本
├── EP01-morose-restaurant-v7-ai-card.monet v7（15 节点 / 20 边 / 7 组）
├── build-morose-v9-invideo-narration.py 小饭馆版 v9·视频内旁白脚本
├── EP01-morose-restaurant-v9-invideo-narration.monet v9（15 节点 / 20 边 / 8 组）
├── build-morose-v10-long.py 小饭馆版 v10·24s 脚本
├── EP01-morose-restaurant-v10-long.monet 脚本产物，不手改（15 节点 / 20 边 / 8 组）
├── build-capybara-bubble-text-v2.py       上一版：单气泡问题先出
├── build-capybara-bubble-text.py          上一版：文字气泡 v1
├── EP02-like-capybara-tail-v7-dog-inside.monet 脚本产物，不手改（17 节点 / 26 边 / 7 组）
├── build-capybara-bubble.py               上一版：浮动气泡只放 ?
├── build-EP02-like-yard-pilot.py          三词样片「蛋仔的小院」脚本（上一版）
├── EP02-like-yard-pilot-user-v3.monet     基于用户已生成 A01–A04 的修改版（16 节点 / 37 边 / 8 组）
├── EP02-like-yard-pilot-v3.monet          干净重排版（16 节点 / 44 边 / 8 组；备查）
├── _归档-dataURI-作废/          v2 内嵌 data URI（URL 过长，作废）
│   └── EP02-like-yard-pilot-v2.monet
├── _归档-旧心易-作废/           旧粉蛋心易版（作废）
│   └── EP02-like-yard-pilot-v1.monet
├── _归档-远甩-作废/            三词样片「蛋仔的日常」远甩版（作废）
│   └── EP02-like-daily-pilot-v1.monet
├── _归档-照相馆-作废/           三词样片「模仿照相馆」（用户否掉，作废）
│   ├── build-EP02-like-photostudio-pilot.py
│   └── EP02-like-photostudio-pilot-v1.monet
├── build-EP02-like.py           v3 连续运镜脚本（作废，留对照）
├── _归档-慢运镜-作废/           v3 慢运镜版（作废）
│   └── EP02-like-family-v3.monet
├── _归档-硬切-作废/             v2 硬切版（作废）
│   └── EP02-like-family-v2.monet
├── _归档-连续镜头-作废/         v1 静止版（作废）
│   └── EP02-like-family-v1.monet
├── _归档-拼词-作废/             2026-10-29 用户否掉“拼词”方向，不再交付
│   ├── build-EP02-compound.py
│   ├── EP02-compound-animals-v1.monet
│   └── EP02-compound-animals-v2.monet
├── build-EP01-agony-v2.py       候选脚本（暂停，留对照）
├── EP01-agony-v2.monet          候选画布（暂停，不作交付）
├── build-EP01-agony.py          旧大蒜版脚本（v1 已取代，留对照）
├── EP01-agony-v1.monet          旧大蒜版画布（不作交付）
├── (EP03-bail-v1.monet)        待建
└── _归档-词义反转-作废/          2026-10-29 试错方向，不再交付
    ├── build_twist.py
    ├── 蛋仔记单词-EP01-watch-反转剧-2x23s-v1.monet
    └── 蛋仔记单词-EP02-crush-反转剧-2x23s-v1.monet
```

- 一次交付多支画布必须换节点 ID 前缀（集数/版本），否则节点 ID 全撞。
- `edges` 从 `reference_images` / `first_frame_image` 派生生成，不手写两套。
- 输出双份：本目录 + `Downloads`，带版本号。
- 只交 `.monet` 由用户自行导入；不自动导入、不自动删除。

## 接线纪律

- **引用双接入**：prompt 写了 `{{node-x}}`，必须同时挂进下游 `reference_images`（首帧则 `first_frame_image`）并存在 `x→下游` 的边。
- **组＝依赖分层＝跑序**：组内不得有依赖边；组名按"第 N 步"编号。
- **禁止边**：`video→video`、`audio→video`、视频→尾帧的来源记录边。
- **T_A 铁律**：Part A 跑完必须截真实尾帧替换占位，替换前不派发 Part B。

## 交付前

```powershell
py -3 "E:\漫剧项目\ai-drama\_共享\工具\检查画布接线.py" <画布路径>
```

有 ERROR 不得交付。画布无回收站，删除前先查产物。

## 当前状态

- **EP01《morose＝没肉丝》已建（现行）**：`EP01-morose-v1.monet`，12 节点 / 22 边 / 8 组（含 G01 四宫格预演）；`检查画布接线.py` **0 ERROR / 0 WARNING**；套壳 B站 31s 3D 卡通；**未导入、未生成**。
- **玩梗样片 EP01《morose＝没肉丝》小饭馆版 v10（无补救／视频内旁白／24s）已建**：`EP01-morose-restaurant-v1.monet`，14 节点 / 21 边 / 7 组；1 词／20s（8＋9＋3）；小饭馆柜台点单→端盒到桌→没肉丝→心易后厨补救；黄蛋短句；旁白解释；心易只咔啵；R02E 锁眼＋T_A；单卡尾；复用 R01P/A05/R02/R02E；新 A06/A07/K_A/V1/V2；`检查画布接线.py` **0 ERROR / 0 WARNING**；**未导入、未生成**。
- **EP02《-like 家族》三词样片「水豚心易＋毛绒黄蛋·尾帧链·无瞳锁眼·不报词·狗在窝里」v7 已建**：`EP02-like-capybara-tail-v7-dog-inside.monet`，17 节点 / 26 边 / 7 组；rocklike／snakelike／doglike，6＋4＋5＝23s；心易＝棕色水豚，只发“咔啵”；黄蛋说话；白色浮动气泡（`rocklike` / `是什么意思？`）在视频里；A01–A04、KC 已生成保留；A05_R/S/D、K/V 待生成；`检查画布接线.py` **0 ERROR / 0 WARNING**；**未导入、未生成**。
- **上一版：三词样片「蛋仔的小院」v3（用户素材版）**：`EP02-like-yard-pilot-user-v3.monet`，16 节点 / 37 边 / 8 组；A01–A04 已生成保留；rocklike／snakelike／doglike，8＋8＋10s；一个小院三个角落（石桌/花坛/狗窝），人物在场景里，镜头短推/下摇指向对象；**心易用白色猫耳版（临时公网 URL，约 1 小时），心易提问、黄蛋回答**；`检查画布接线.py` **0 ERROR / 0 WARNING**；**未导入、未生成**。远甩/照相馆作废归档。
- **agony v2 候选暂停**：`EP01-agony-v2.monet`，12/21/8；“手机丢茶”动作待改，暂不导入。
- v1（大蒜照片版）已被取代，**不要导入**；脚本与画布留作对照。
- EP02（bail／ambition）待定，未建。
- 旧方向（watch／crush）已归档，**不要导入**。
- 九宫格／十二宫格暂不挂：本集是单场景 3 拍连续动作，多格图直接接视频会干扰构图；若做 A/B，另加 4 格预演，只派生 K_A，不直接接视频。

