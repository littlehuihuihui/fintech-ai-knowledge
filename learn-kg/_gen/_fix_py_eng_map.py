# -*- coding: utf-8 -*-
import json
from pathlib import Path

KG = Path(r"D:\cursor\数据学习平台\kg-data")
MIRRORS = [
    Path(r"D:\cursor\多行业数据平台\portfolio\pages\kg-data"),
    Path(r"D:\cursor\financial-data-portfolio-publish\pages\kg-data"),
]


def find(n, nid):
    if n.get("id") == nid:
        return n
    for c in n.get("children") or []:
        h = find(c, nid)
        if h:
            return h
    return None


def sync(name, tree):
    compact = json.dumps(tree, ensure_ascii=False, separators=(",", ":"))
    pretty = json.dumps(tree, ensure_ascii=False, indent=2)
    (KG / f"{name}.json").write_text(compact, encoding="utf-8")
    (Path(r"D:\cursor\数据学习平台\_gen\lessons") / f"{name}.json").write_text(
        pretty, encoding="utf-8"
    )
    hub = "hub-python.json"
    (KG / hub).write_text(compact, encoding="utf-8")
    emb = (
        'window.__KG_EMBEDDED = window.__KG_EMBEDDED || {};\n'
        f'window.__KG_EMBEDDED["{name}"]={compact}\n'
    )
    (KG / f"embed-{name}.js").write_text(emb, encoding="utf-8")
    for m in MIRRORS:
        if not m.exists():
            continue
        (m / f"{name}.json").write_text(compact, encoding="utf-8")
        (m / hub).write_text(compact, encoding="utf-8")
        (m / f"embed-{name}.js").write_text(emb, encoding="utf-8")


py = json.loads((KG / "python.json").read_text(encoding="utf-8"))
eng = find(py, "py-eng")
c = eng["content"]
row = "| 3 | 异常处理与日志 | ?? | 文件缺失、断连、脏 amount 时仍可定位可重跑。 |"
if "| 3 | 异常处理与日志 |" in c:
    print("already ok")
else:
    lines = c.splitlines()
    out = []
    inserted = False
    for line in lines:
        out.append(line)
        if (not inserted) and line.startswith("| 2 |") and ("可复现" in line or "复现" in line):
            out.append(row)
            inserted = True
    if not inserted:
        # dump lines with |
        for i, line in enumerate(lines):
            if line.startswith("|"):
                print(i, line)
        raise SystemExit("could not find row 2")
    text = "\n".join(out)
    if not text.endswith("\n"):
        text += "\n"
    text = text.replace("约 **2** 片", "约 **3** 片").replace("合计约 **2**", "合计约 **3**")
    eng["content"] = text
    sync("python", py)
    print("inserted row3")

eng2 = find(json.loads((KG / "python.json").read_text(encoding="utf-8")), "py-eng")
assert "| 3 | 异常处理与日志 |" in eng2["content"]
print("verified")
