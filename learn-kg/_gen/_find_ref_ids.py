# -*- coding: utf-8 -*-
import json
from pathlib import Path

KG = Path(r"D:\cursor\数据学习平台\kg-data")


def walk(n, acc=None):
    acc = acc if acc is not None else []
    acc.append((n.get("id"), n.get("title")))
    for c in n.get("children") or []:
        walk(c, acc)
    return acc


for name in ("dwh", "etl"):
    t = json.loads((KG / f"{name}.json").read_text(encoding="utf-8"))
    print("====", name)
    for i, tit in walk(t):
        if any(
            k in (tit or "") or k in (i or "")
            for k in (
                "对账",
                "层级",
                "分层",
                "增量",
                "分区",
                "质检",
                "校验",
                "dbt",
                "选型",
                "加工",
            )
        ):
            print(i, "|", tit)
