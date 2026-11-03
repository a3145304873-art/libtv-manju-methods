import json, shutil
from pathlib import Path
from datetime import datetime, timedelta, timezone
p=Path(r"E:\libtv漫剧\08_作品\蛋仔记单词\02_画布\EP02-like-capybara-tail-v5-nopupil.monet")
d=json.loads(p.read_text(encoding="utf-8")); c=d["canvas"]
changed=[]
for n in c["nodes"]:
    lab=n["meta"].get("label","")
    if n["type"]!="gen-video": continue
    mp=n["params"]["model_params"]; t=mp["prompt"]
    if "V1" in lab:
        old="9.2–10 秒：黄蛋：“snakelike——”两人转身朝花坛走；镜尾停在花坛入口。"
        new="9.2–10 秒：黄蛋只做“走”的手势，**不报下一个词**；两人转身朝花坛走；镜尾停在花坛入口。"
        assert old in t, "V1 line not found"
        mp["prompt"]=t.replace(old,new)
        n["meta"]["label"]="【待生成·无瞳锁眼】V1 · 10s · 开头3气泡＋rocklike＋心易夸＋走向花坛（不报词）"
        changed.append("V1")
    elif "V2" in lab:
        old="4.4–5.4 秒：黄蛋：“doglike——”两人转身朝狗窝走；镜尾停在狗窝入口。"
        new="4.4–5.4 秒：黄蛋只做“走”的手势，**不报下一个词**（不要说 doglike）；两人转身朝狗窝走；镜尾停在狗窝入口。"
        assert old in t, "V2 line not found"
        mp["prompt"]=t.replace(old,new)
        n["meta"]["label"]="【待生成·无瞳锁眼】V2 · 6s · snakelike＋心易夸＋走向狗窝（不报词）"
        changed.append("V2")
c["name"]="蛋仔记单词 · -like 三词样片「水豚心易＋毛绒黄蛋·无瞳锁眼·不报词」v6 · 23s"
out=Path(r"E:\libtv漫剧\08_作品\蛋仔记单词\02_画布\EP02-like-capybara-tail-v6-nospoiler.monet")
out.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding="utf-8")
shutil.copyfile(out,Path.home()/"Downloads"/out.name)
print("changed",changed,"->",out)
