import json, shutil
from pathlib import Path
src=Path(r"E:\libtv漫剧\08_作品\蛋仔记单词\02_画布\EP02-like-capybara-bubble-text-v1.monet")
out=Path(r"E:\libtv漫剧\08_作品\蛋仔记单词\02_画布\EP02-like-capybara-bubble-text-v2.monet")
d=json.loads(src.read_text(encoding="utf-8")); c=d["canvas"]
for n in c["nodes"]:
    lab=n["meta"].get("label","")
    if lab.startswith("【待生成】K_A"):
        mp=n["params"]["model_params"]
        mp["prompt"]=mp["prompt"].replace(
            "在画面左1/3，站在石桌旁，头顶橘子；她头右上浮一个白色3D对话气泡",
            "在画面左1/3，从石桌后探出半个身子，头顶橘子；她头右上浮一个白色3D对话气泡"
        ).replace(
            "尾巴指向她；心易嘴巴闭合",
            "尾巴指向她，气泡像“啵”地弹出来；心易嘴巴闭合"
        )
    if lab.startswith("【待生成】V1"):
        mp=n["params"]["model_params"]
        old="""0–2 秒：黄蛋：“like 是‘像’。一个词加 like，就是‘像它一样’。”
2–2.8 秒：心易：“咔啵？”（升调、歪头；气泡文字保持 `rocklike` / `是什么意思？`）黄蛋看气泡。
2.8–5.2 秒：黄蛋：“rocklike？rock 是石头——rocklike 就是像石头一样，坚固的！”黄蛋拍石桌；心易点头。
5.2–6 秒：黄蛋：“真不错！snakelike——”心易转头；镜尾硬切。"""
        new="""0–1.2 秒：心易从石桌后探出半个身子，气泡文字 `rocklike` / `是什么意思？` 像“啵”地弹出；黄蛋转头看气泡。
1.2–3.2 秒：黄蛋：“好问题！like 是‘像’。一个词加 like，就是‘像它一样’。”
3.2–5.4 秒：黄蛋：“rock 是石头——rocklike 就是像石头一样，坚固的！”黄蛋拍石桌；心易点头。
5.4–6 秒：黄蛋：“真不错！snakelike——”心易转头；镜尾硬切。"""
        assert old in mp["prompt"], "V1 old block not found"
        mp["prompt"]=mp["prompt"].replace(old,new)
c["name"]="蛋仔记单词 · -like 三词样片「水豚心易·气泡文字版」v2 · 15s（问题先出）"
out.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding="utf-8")
shutil.copyfile(out,Path.home()/"Downloads"/out.name)
print("wrote",out)
print("K_A",next(len(n["params"]["model_params"]["prompt"]) for n in c["nodes"] if n["meta"].get("label","").startswith("【待生成】K_A")))
print("V1",next(len(n["params"]["model_params"]["prompt"]) for n in c["nodes"] if n["meta"].get("label","").startswith("【待生成】V1")))
