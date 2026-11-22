#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日语语法复习归档 · 索引生成器

用法：把每天的复习页存成 YYYY-MM-DD.html 放在本目录下，然后运行
    python3 更新索引.py
即可重新生成 index.html。

不需要安装任何第三方库。
"""

import re
import sys
import html
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent
PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}\.html$")

WEEKDAYS = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]


def strip_tags(s: str) -> str:
    s = re.sub(r"<[^>]+>", "", s)
    return html.unescape(re.sub(r"\s+", " ", s)).strip()


def grab(text: str, pattern: str) -> str:
    m = re.search(pattern, text, re.S)
    return strip_tags(m.group(1)) if m else ""


def collect():
    items = []
    for p in ROOT.glob("*.html"):
        if not PATTERN.match(p.name):
            continue
        raw = p.read_text(encoding="utf-8", errors="ignore")
        title = grab(raw, r"<h1[^>]*>(.*?)</h1>") or "日语语法复习"
        sub = grab(raw, r'<div class="sub"[^>]*>(.*?)</div>')
        sections = len(re.findall(r"<section\b", raw))
        drills = len(re.findall(r"<details\b", raw))
        items.append({
            "date": p.stem,
            "file": p.name,
            "title": title,
            "sub": sub,
            "sections": sections,
            "drills": drills,
            "size": p.stat().st_size,
        })
    items.sort(key=lambda x: x["date"], reverse=True)
    return items


def weekday_of(date_str: str) -> str:
    try:
        return WEEKDAYS[datetime.strptime(date_str, "%Y-%m-%d").weekday()]
    except ValueError:
        return ""


def render(items) -> str:
    if items:
        cards = []
        for it in items:
            meta = []
            if it["sections"]:
                meta.append(f"{it['sections']} 节")
            if it["drills"]:
                meta.append(f"{it['drills']} 道自测")
            meta.append(f"{it['size'] / 1024:.0f} KB")
            meta_str = " · ".join(meta)
            sub = f'<div class="topic">{html.escape(it["sub"])}</div>' if it["sub"] else ""
            cards.append(f"""
      <a class="row" href="{html.escape(it['file'])}">
        <div class="date">
          <span class="d">{it['date']}</span>
          <span class="w">{weekday_of(it['date'])}</span>
        </div>
        <div class="body">
          <div class="name">{html.escape(it['title'])}</div>
          {sub}
          <div class="meta">{meta_str}</div>
        </div>
        <div class="arrow">→</div>
      </a>""")
        body = f'<div class="list">{"".join(cards)}\n    </div>'
    else:
        body = '<div class="empty">还没有归档。把当天的复习页存成 <code>YYYY-MM-DD.html</code> 放进本文件夹即可。</div>'

    total = len(items)
    latest = items[0] if items else None
    latest_hint = ""
    if latest:
        latest_hint = f'<a class="jump" href="{html.escape(latest["file"])}">直接看最近一份（{latest["date"]}）→</a>'

    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>日语语法复习 · 归档目录</title>
<style>
  :root{{
    --ink:#23201c; --ink-2:#5b544c; --ink-3:#8a8177;
    --line:#ddd7cd; --bg:#f7f5f1; --card:#fffdfa;
    --accent:#2f6b63; --accent-soft:#e8f0ee;
  }}
  *{{box-sizing:border-box;}}
  body{{
    margin:0; padding:44px 20px 90px; background:var(--bg); color:var(--ink);
    font-family:-apple-system,BlinkMacSystemFont,"PingFang SC","Hiragino Sans","Noto Sans JP",system-ui,sans-serif;
    font-size:15px; line-height:1.75; -webkit-font-smoothing:antialiased;
  }}
  .wrap{{max-width:780px;margin:0 auto;}}
  header{{padding-bottom:20px;margin-bottom:26px;border-bottom:2px solid var(--ink);}}
  h1{{margin:0 0 8px;font-size:26px;font-weight:700;letter-spacing:.5px;}}
  .sub{{color:var(--ink-3);font-size:13.5px;}}
  .summary{{
    display:flex;align-items:center;gap:14px;flex-wrap:wrap;
    background:var(--accent-soft);border-left:3px solid var(--accent);
    padding:11px 16px;border-radius:0 4px 4px 0;margin-bottom:22px;font-size:14px;
  }}
  .summary b{{color:var(--accent);font-size:17px;}}
  .jump{{margin-left:auto;color:var(--accent);text-decoration:none;font-weight:600;font-size:13.5px;}}
  .jump:hover{{text-decoration:underline;}}
  .list{{display:flex;flex-direction:column;gap:9px;}}
  .row{{
    display:flex;align-items:center;gap:16px;
    background:var(--card);border:1px solid var(--line);border-radius:6px;
    padding:15px 18px;text-decoration:none;color:inherit;
    transition:border-color .15s, transform .15s;
  }}
  .row:hover{{border-color:var(--accent);transform:translateX(2px);}}
  .date{{flex:0 0 96px;text-align:center;border-right:1px solid var(--line);padding-right:14px;}}
  .date .d{{display:block;font-family:"SF Mono",Menlo,monospace;font-size:14.5px;font-weight:700;letter-spacing:.3px;}}
  .date .w{{display:block;font-size:12px;color:var(--ink-3);margin-top:1px;}}
  .body{{flex:1 1 auto;min-width:0;}}
  .name{{font-size:15.5px;font-weight:600;line-height:1.5;}}
  .topic{{font-size:13px;color:var(--ink-2);margin-top:3px;}}
  .meta{{font-size:12.5px;color:var(--ink-3);margin-top:4px;font-variant-numeric:tabular-nums;}}
  .arrow{{flex:0 0 auto;color:var(--ink-3);font-size:16px;}}
  .row:hover .arrow{{color:var(--accent);}}
  .empty{{padding:34px;text-align:center;color:var(--ink-3);background:var(--card);border:1px dashed var(--line);border-radius:6px;}}
  code{{background:#f0ede6;padding:1px 5px;border-radius:3px;font-family:"SF Mono",Menlo,monospace;font-size:13px;}}
  footer{{margin-top:38px;padding-top:16px;border-top:1px solid var(--line);color:var(--ink-3);font-size:12.5px;}}
  @media (max-width:640px){{
    body{{padding:26px 14px 56px;}}
    h1{{font-size:22px;letter-spacing:0;}}
    .sub{{font-size:12px;word-break:break-word;}}
    .summary{{padding:10px 12px;font-size:13px;gap:8px;}}
    .summary b{{font-size:15px;}}
    .jump{{margin-left:0;font-size:12.5px;}}
    .row{{padding:12px 13px;gap:11px;}}
    .date{{flex:0 0 auto;padding-right:9px;}}
    .date .d{{font-size:12.5px;white-space:nowrap;}}
    .date .w{{font-size:11.5px;}}
    .name{{font-size:14.5px;}}
    .topic{{font-size:12.5px;}}
    .meta{{font-size:12px;}}
  }}

  @media print{{body{{background:#fff;padding:0;}}.row{{break-inside:avoid;}}.jump{{display:none;}}}}
</style>
</head>
<body>
<div class="wrap">
  <header>
    <h1>日语语法复习 · 归档</h1>
    <div class="sub">每天一份，按日期倒序 · 文件夹：~/Documents/日语语法</div>
  </header>

  <div class="summary">
    <span>已归档 <b>{total}</b> 份</span>
    {latest_hint}
  </div>

  {body}

  <footer>
    新增一天的流程：把复习页存成 <code>YYYY-MM-DD.html</code> 放进本文件夹 → 在本目录运行 <code>python3 更新索引.py</code>。<br>
    索引生成于 {now}
  </footer>
</div>
</body>
</html>
"""


def main():
    items = collect()
    out = ROOT / "index.html"
    new = render(items)

    # 内容没变就不重写（时间戳那行不算变化），避免 git 里留下无意义的空提交
    if out.exists():
        strip = lambda s: re.sub(r"索引生成于 [0-9:\- ]+", "", s)
        if strip(out.read_text(encoding="utf-8")) == strip(new):
            print(f"index.html 无变化（收录 {len(items)} 份）")
            return 0

    out.write_text(new, encoding="utf-8")
    print(f"已生成 {out}")
    print(f"收录 {len(items)} 份：" + ("、".join(i["date"] for i in items) if items else "无"))


if __name__ == "__main__":
    sys.exit(main())
