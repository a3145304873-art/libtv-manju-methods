# -*- coding: utf-8 -*-
"""一次性入库脚本：W12-W16（LibTV 社区萌宠画布五部）+ R04（剧本拼合）。运行后可删除。"""
import json, hashlib, io, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WF = ROOT / '04_原始资料/workflows'
RDIR = ROOT / '04_原始资料/format-references/R04'
RDIR.mkdir(parents=True, exist_ok=True)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def sha(b):
    return hashlib.sha256(b).hexdigest()

PROMPT_FILE = {
    'luzhirong_copy': 'tmp_luzhirong_prompts.txt',
    'nannan_copy': 'tmp_nannan_prompts.txt',
    'badog_copy': 'tmp_badog_prompts.txt',
    'guabi_full': 'tmp_guabi_full_prompts.txt',
    'lulu3_full': 'tmp_lulu3_full_prompts.txt',
}

WORKS = [
    dict(wid='W12', key='luzhirong_copy', name='逐日之茸｜机器人阿秃的毛茸茸之旅',
         tpl='28c31a68d1cc4fbc97d46f31d4eb75e2', copy='54cdab2840eb4212b18d8d9cc6a7d7fd',
         stages=['S0', 'S1'],
         ability='C04 母图/三视图锚定分支；C16 {{Mixed N}} 引用锚位与 mixed2video；C03 剧情简介+主角性格先行；新句式证据：材质转换节点（机器人变毛绒保留LCD）与风格统一修正节点（参考A B质感改C，不改色相构图不增元素）',
         locators='模板 28c31a68…；本账号副本 canvas-54cdab28…；分段组：开头坠落/第二段刷河流接纳/第三段见树神/第四段茸夸父逐日(15s一镜到底)/第五段融入+海报；资产链 废图→设定→质感转换→三视图→风格统一→最终；坠落重拍生成1-5',
         gaps=['媒体成片未观看', '旁白音频节点文案未提取', '原作创作者归属未核（乌鸦卡夫卡，来自社区页自述）'],
         summary='五段寓言重构《夸父逐日》：机器人阿秃坠落毛绒星球→梳绒河相遇受惊→帮最小精灵理毛换信任→独眼树神→戏中戏创世神话（夸父追毛线球困卧，呼气成云、身化山脉、生出精灵）→金属接缝长绒毛融入。提示词九段式：参考图标签化/时长/剧情简介/主角性格/场景环境/按秒运镜/摄影参数(IMAX70mm柯达Vision3 C4D毛绒渲染)/光影色彩/逐动作音效清单+禁BGM。参考图纪律：主角阿秃参考挂全部20个视频节点。',
     ),
    dict(wid='W13', key='nannan_copy', name='《囡囡的毛绒梦境》治愈系原创3D定格动画',
         tpl='d82b1206a948414184d0d52cd42d7e64', copy='a35aa1f57721476781f660246193ebd4',
         stages=['S0', 'S1', 'S2'],
         ability='C16 引用锚位（Mixed 1-6 分段职责声明）；C06 逐镜景别/构图/运镜/位置四要素；C03 【关键约束（全片遵守）】负面物理与品位约束块逐段重复；新证据：声音材质化（过山车声全用绒布咯吱不用金属声）、逐镜写转场顺接、角色设计表排版模板（左头特写+右全身双视图黑圆遮脸）',
         locators='模板 d82b1206…；本账号副本 canvas-a35aa1f5…；组：角色设计/音色确认+片头旁白/背景音乐生成/第一至六段【分镜+视频】/社媒封面设计；关键节点：毛毡奇幻坠落(15s10镜)/毛毡初遇·捂眼偷瞄与回握(12s)/咕咪跟我来(15s7镜)/过山车卡丁车碰碰车/鬼屋两段/病房苏醒(4镜22s)',
         gaps=['媒体成片未观看', '片头旁白具体文案未持久化（音频节点仅存音色参考与生成词）', '水印保护图未取原图', '台词仅一句"放马过来吧"入档'],
         summary='六幕治愈闭环：植物人女孩→毛毡梦境坠落→小兽捂眼偷瞄与第一次触碰→小兽带路→游乐园补偿（旋转木马失落与安慰/过山车/卡丁车/碰碰车，台词"放马过来吧"）→鬼屋=恐惧具象化→开门走入白光→病房主观视角苏醒父女重逢。BGM 双面设计（《鬼妈妈》式可爱藏暗涌65BPM C小调）+片头父女合唱。角色身份标识=小兽双眼不对称（每镜必须保持）。',
     ),
    dict(wid='W14', key='badog_copy', name='糟糕！我的兄弟真的变成狗了！',
         tpl='b8aa664d2451425c92e33d08473760a4', copy='26ee96a7ff004f7bbac8096437dc33bb',
         stages=['S0', 'S1', 'S2', 'S3'],
         ability='C04 双形态角色资产（阿波人形态/阿柴有项圈无项圈两版）；C06 场景多角度资产（客厅俯视/侧视/反打）；C03 台词逐字保留+双角色音色固定设定（25-30岁嘴欠损友声线全描述）；新证据：宫格分镜切格（宫格高清1-1/1-2/1-3→编号镜头）、动作匹配硬切（放杯下伏切卫生间）',
         locators='模板 b8aa664d…；本账号副本 canvas-26ee96a7…；场次 P1卧室打游戏(20s)/P2大排档醉酒卫生间发誓(15s)/P2-B清晨我怎么和狗一样(16s)/P3-A接受现实亲兄弟认证(30s)/P3-B谁才是狗(28s)/P5-A宠物医院绝育了吧(30s)/P6公园长椅赚狗粮(30s)/P7哪边是五(30s)/P7-B站着挣钱(30s,让子弹飞致敬)',
         gaps=['P4 场次无独立提示词节点（可能并入或未保存）', '视频成片未观看', '阿嘉音色仅写"严格参考参考音频"未存设定文'],
         summary='人狗身份互换台词喜剧：黑柴阿波戴电竞耳机打游戏吵醒阿嘉→大排档毒誓"再喝酒我就是狗"字面应验→兄弟关系照旧运转（豆包豆包假如你兄弟变成狗/确定了这就是我亲兄弟）→"累成狗/单身狗/傻狗"段子→宠物医院绝育误会→短视频创业对话（五五分账哪边是五：摇头看耳朵能不能扇到脸）→《让子弹飞》站着挣钱改编（紫菜蛋花汤不要菜花不要汤）。台词是主角，画面是段子配图。',
     ),
    dict(wid='W15', key='guabi_full', name='呱比闯入毛茸茸世界1',
         tpl='13f97dd808664ec4b72a190bc4ea94a5', copy='0297a2aedf8f4f48acf1d0e46f62c8f3',
         stages=['S0', 'S1'],
         ability='C03 剧本/角色卡存文本节点扛内容+视频节点超短提示词（"呱比，场景，声线参考，不要BGM，画面流畅"）；新证据：同一梗概并行生成三个脚本选优（5镜20s/8镜30s/7镜详细）、黑屏委屈拟音彩蛋收尾、微表情演技+逐拟声音效的脚本粒度',
         locators='模板 13f97dd8…；本账号副本 canvas-0297a2ae…；Group1=EP1门(18s六镜《呱比的奇妙之门》+黑屏"呱比…"回音)；Group2/3/4=EP2鳄鱼三版本（20s骑马狂想曲5镜/30s天降呱比8镜/详细7镜）；文本节点含呱比角色卡（18cm/舌头外耷/猫系动作/盲目乐观/拟音幼童+小奶狗混合声位）',
         gaps=['文本节点产出未持久化于副本（脚本原文从只读创作过程页 9611 字全文抓取，见 06_工具/tmp_guabi_page_full.txt）', '7个视频节点输出未观看', '原作创作者归属未核（Muertu木二土，社区页自述）'],
         summary='EP1：呱比触碰毛茸茸巨门→纹路注光→世界材质变绒毛（子弹时间环绕）→树根缠身拖入门→黑屏委屈音。EP2：天降鳄鱼鼻→蹭脸未察觉身后睁眼→骑马幻想框→被甩飞（多普勒惨叫/BOING弹射）。方法论：梗概→多版本脚本选优→角色图+场景图+声线为输入→超短视频提示词。',
     ),
    dict(wid='W16', key='lulu3_full', name='噜噜毛茸茸的工作日常3',
         tpl='7e3feaeeb17a42f88f088638bc992fd0', copy='d9653caa0eca4e3aa751252e875bcd58',
         stages=['S0', 'S1', 'S2', 'S3'],
         ability='C04 母图锁定句（噜噜原母图锁定唯一成年噜噜：约40厘米圆胖苔藓身体黑亮眼睛头顶蕨叶与小蘑菇原竹编背篓原长木柄单头滚刷）；C16 mixed2video 样片模式；新证据：节点名=分镜卡（秒数+剧情+版本号）、单镜重拍 V4→V8、角色数量中途重铸（C01六改五去中间大圆团保留梨形）、上集场景定稿复用（S03上集定稿复用）、每集童趣大字海报 V1-V4',
         locators='模板 7e3feaee…；本账号副本 canvas-d9653caa…；组：分镜/角色变体资产/场景/正片/角色资产/海报/草稿/截图；场次 L01出工走散(28s)/L01B补拍(10s)/L02牵藤带队(6s×5版)/L03小帮手就位(23s)/L03A围身(15s×5版V4-V8)/L03B示范合作(10s)/L04成果(21s)/L05按摩落虫斗鸡眼(20s)',
         gaps=['媒体成片未观看', '海报生成词未逐条入档', '音频节点仅 A01 声线参考入档'],
         summary='第三集工作日常：带五只宝宝出工→走散乱跑叹气→牵藤带队（比例反复锁定，圆胖宝宝顶2cm毛毛虫）→工作区被围→拿刷示范排队合作→宝宝把所有东西刷上苔藓→仰卧按摩收尾毛毛虫落身斗鸡眼定格。提示词体系与本库 08_作品 噜噜画布完全同源（同一港式奇幻风格句与母图锁定句式），为本方画布方法的行业同源实证。',
     ),
]

manifest_path = ROOT / 'source-manifest.json'
m = json.loads(manifest_path.read_text(encoding='utf-8'))
existing_ids = {s['id'] for s in m['sources']}
assert not ({w['wid'] for w in WORKS} & existing_ids), 'ID 冲突'

capture = ('API-direct read-only（POST /api/canvas/project/list|project/detail，token 来自本机 CLI 凭据，浏览器注入 cookie 只读创作过程页）；'
           '副本经网页端「复制项目」落入本账号工作区后读取（2026-11-09/10）')

for w in WORKS:
    d = ROOT / '06_工具/tmp_canvases' / (w['key'] + '.json')
    wdir = WF / w['wid']
    wdir.mkdir(exist_ok=True)
    raw = d.read_bytes()
    (wdir / 'nodes.json').write_bytes(raw)
    pt = ROOT / '06_工具' / PROMPT_FILE[w['key']]
    prompts = pt.read_text(encoding='utf-8')
    dj = json.loads(raw.decode('utf-8'))
    data = dj.get('data') or {}
    nodes = data.get('nodeList') or []
    conns = data.get('connectionList') or []
    doc = (
        f'# 《{w["name"]}》LibTV 画布提示词与制作关系拆解（入库副本）\n\n'
        f'画布（本账号副本）UUID：`{w["copy"]}`　社区模板：`{w["tpl"]}`　入库日期：2026-11-10　'
        f'节点：{len(nodes)}　连线：{len(conns)}\n\n'
        '> 来源：LibTV 社区「创作精选」作品，经网页端「复制项目」落入本账号工作区后，'
        '用画布 API 只读读取全部节点参数（nodes.json 为完整快照，含 params/url/状态）。'
        '提示词原样复制节点 data.params.prompt；空提示词节点不反推。媒体成片未观看，任务状态不代表视觉验收。'
        '故事层拼合与跨作品公式见 R04《萌宠标杆完整剧本拼合与故事公式》。\n\n'
        f'## 快速结论\n\n{w["summary"]}\n\n'
        f'## 制作要点（归纳自节点名与提示词）\n\n'
        f'- 能力锚：{w["ability"]}\n'
        f'- 关键定位：{w["locators"]}\n\n'
        f'## 全部可读提示词（逐节点原文）\n\n{prompts}\n'
    )
    docb = doc.encode('utf-8')
    docname = f'{w["name"]}-副本_LibTV提示词与制作关系拆解_2026-11-10.md.txt'
    (wdir / docname).write_bytes(docb)
    entry = {
        'id': w['wid'], 'kind': 'workflow', 'name': w['name'],
        'stable_id': 'libtv:' + w['tpl'],
        'stages': w['stages'], 'ability_notes': w['ability'], 'locators': w['locators'],
        'gaps': w['gaps'],
        'evidence': {'structure': 'snapshot', 'media_review': 'not_performed',
                     'reproduction': 'not_performed', 'capture': capture},
        'intake_date': '2026-11-10',
        'files': [
            {'path': f'04_原始资料/workflows/{w["wid"]}/nodes.json', 'sha256': sha(raw), 'bytes': len(raw),
             'source_relative': f'LibTV 画布 API 快照 {w["copy"]}（社区模板 {w["tpl"]}，复制副本读取）'},
            {'path': f'04_原始资料/workflows/{w["wid"]}/{docname}', 'sha256': sha(docb), 'bytes': len(docb),
             'source_relative': '本库自同源快照生成的逐节点提示词拆解'},
        ],
    }
    m['sources'].append(entry)
    print(w['wid'], 'ok', len(nodes), '节点, 拆解', len(docb), 'B')

# R04 剧本拼合
src = ROOT / '06_工具/萌宠标杆剧本拼合_20261109.md'
rb = src.read_bytes()
rpath = RDIR / '萌宠标杆完整剧本拼合与故事公式_2026-11-10.md'
rpath.write_bytes(rb)
m['sources'].append({
    'id': 'R04', 'kind': 'format_reference',
    'name': '萌宠标杆完整剧本拼合与故事公式（呱呱系/逐日之茸/囡囡/变狗/呱比闯入/噜噜日常3）',
    'stable_id': 'derived:2026-11-10:mengchong-benchmarks-script-reconstruction',
    'stages': ['S0', 'S1'],
    'ability_notes': '故事层跨源拼合：呱系追逐公式（误会开场/变形载具/第三方惩罚/反差收尾）、治愈闭环三变体、台词喜剧分场；六工程手法（尾帧接力/统一风格前缀/节点名分镜卡/状态变体资产/剧本即文本节点/海报必配）',
    'locators': '呱呱和辣条合集 BV1Wwnj6BEJo 逐帧；wuhu拆解 BV1JNn56ZEcv；三张图教程 BV1J8xq6BEqa；五画布副本 canvas-54cdab28/a35aa1f5/26ee96a7/0297a2ae/d9653caa',
    'gaps': ['呱呱系拍表来自逐帧观察非官方台本', '囡囡片头旁白原文缺失', '变狗P4场次缺'],
    'evidence': {'structure': 'derived_analysis', 'media_review': 'performed_partial', 'reproduction': 'not_performed',
                 'capture': 'BBDown 下载五样本（B站）+LibTV 五画布 API 全量提示词 + 创作过程页只读渲染'},
    'intake_date': '2026-11-10',
    'files': [{'path': '04_原始资料/format-references/R04/萌宠标杆完整剧本拼合与故事公式_2026-11-10.md',
               'sha256': sha(rb), 'bytes': len(rb),
               'source_relative': '本库衍生分析（源为 W12-W16 快照与 B 站样本观看记录）'}],
})
print('R04 ok', len(rb), 'B')

m['scope'] = m['scope'] + '；+2026-11-10 W12–W16 intake（LibTV 社区萌宠画布五部：网页复制副本后 API 全量提示词+结构快照）与 R04（六部标杆完整剧本拼合与故事公式，含呱呱系 B 站样本逐帧拆解）'
n_json = len(list((ROOT / '04_原始资料/workflows').glob('W*/nodes.json')))
m['counts']['workflow_sources'] = len([s for s in m['sources'] if s['kind'] == 'workflow'])
m['counts']['workflow_json_snapshots'] = n_json
m['counts']['format_reference_packages'] = len([s for s in m['sources'] if s['kind'] == 'format_reference'])
manifest_path.write_text(json.dumps(m, ensure_ascii=False, indent=1), encoding='utf-8')
print('manifest updated: sources =', len(m['sources']), '| counts =', m['counts'])
