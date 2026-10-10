# -*- coding: utf-8 -*-
"""批 E 通用库：把德语正文写入 `content/de/compare/<slug>.md`（50 国家页）。

铁律（与仓库既有纪律一致）：
  · 一律 **bytes 读写**，改完复核 `CRLF == 0`；
  · 只做三件事：① `seo.description` 的数字/品牌**现算刷新**、② `TODO(de)` 注释统一为
    分层发布措辞（与 `/de/networks/*.md` 同款）、③ 正文写入。其余字段（title/iso/weight）**一字不动**；
  · `seo.description` 的数字与品牌**一律现算**（`.buildlog/compare_de_facts.json`），
    **不抄英语、不抄旧德语** —— 旧德语是 8 品牌时期快照，数字与品牌都已过期；
  · 自检：正文段数、短代码对齐、F 禁词、禁单位（`Mbps/Kbps/Gbps`）、CRLF=0。

用法（由分册脚本调用）：
    from _compare_de_lib import apply_country
    apply_country("argentina", [p1, p2, p3])
"""
from __future__ import annotations

import importlib.util
import json
import pathlib
import re
import sys
import tomllib

ROOT = pathlib.Path(__file__).resolve().parents[1]
DE = ROOT / "content" / "de" / "compare"
EN = ROOT / "content" / "en" / "compare"
FACTS = ROOT / ".buildlog" / "compare_de_facts.json"

# 品牌显示名：唯一真源 = data/providers.toml（不抄第二份）
PROVIDER_NAMES: dict[str, str] = {
    k: v["name"]
    for k, v in tomllib.loads((ROOT / "data" / "providers.toml").read_text(encoding="utf-8")).items()
}


def _load_guard_module():
    """动态加载 verify_de_text.py，取判据常量（单一真源，避免抄第二份清单）。"""
    p = ROOT / "scripts" / "verify_de_text.py"
    spec = importlib.util.spec_from_file_location("_vdtext", p)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["_vdtext"] = mod
    spec.loader.exec_module(mod)
    return mod


_G = _load_guard_module()
F_WORDS: list[str] = list(_G.F_FORBIDDEN_WORDS)
F_PHRASES: list[str] = list(_G.F_FORBIDDEN_PHRASES)
UNIT_BAD: tuple[str, ...] = tuple(_G.UNIT_BAD)

TODO_OLD_HEAD = "# TODO(de)：正文待翻译。"
TODO_NEW = "# TODO(de)：分层发布 —— 全站德语译文解禁（D9 那一轮）时删掉上面这行。"

_facts_cache: dict | None = None


def facts(slug: str) -> dict:
    global _facts_cache
    if _facts_cache is None:
        _facts_cache = json.loads(FACTS.read_text(encoding="utf-8"))
    for v in _facts_cache.values():
        if v["slug"] == slug:
            return v
    raise KeyError(f"facts 里没有 {slug}")


def _desc_tokens(slug: str, provider_name: dict) -> tuple[str, str, str, str]:
    """返回 (total, prov_n, brand, price) 的新值字符串。"""
    f = facts(slug)
    ce = f["cheapest_entry"]
    return (str(f["total_plans"]), str(f["provider_count"]),
            provider_name[ce["brand"]], f"${ce['price']:.2f}")


def _strip_shortcodes(s: str) -> str:
    """挖掉短代码再扫禁词。

    ★ 判据 F 扫的是**产物可见文本**，短代码到那时已经渲染成数字，所以 F 本身安全。
      这里是源文本层的**额外加固**：不挖掉 `{{< count-countries >}}`，
      里面的 `countries` 会撞 F 禁词表 —— 那是假红，不是真缺陷。
    """
    return re.sub(r"\{\{<[^>]*>\}\}", " ", s)


def _check_body(slug: str, body: str, en_body: str) -> list[str]:
    errs: list[str] = []
    paras = [p for p in body.strip().split("\n\n") if p.strip()]
    en_paras = [p for p in en_body.strip().split("\n\n") if p.strip()]
    if len(paras) != len(en_paras):
        errs.append(f"段数 {len(paras)} != 英语 {len(en_paras)}")
    if re.search(r"^#", body, re.M):
        errs.append("正文含标题行（国家页正文应为纯散文）")
    # 短代码对齐
    sc_de = sorted(re.findall(r"\{\{<[^>]*>\}\}", body))
    sc_en = sorted(re.findall(r"\{\{<[^>]*>\}\}", en_body))
    if sc_de != sc_en:
        errs.append(f"短代码不一致 德语={sc_de} 英语={sc_en}")
    # F 禁词 / 禁单位（挖掉短代码后扫）
    plain = _strip_shortcodes(body)
    for w in F_WORDS:
        m = re.search(r"(?<![A-Za-zÀ-ÿ])%s(?![A-Za-zÀ-ÿ])" % re.escape(w), plain)
        if m:
            errs.append(f"F 禁词 {w!r}: …{plain[max(0,m.start()-40):m.end()+40]}…")
    for ph in F_PHRASES:
        if ph in plain:
            errs.append(f"F 禁短语 {ph!r}")
    for u in UNIT_BAD:
        if re.search(r"(?<![A-Za-z])" + u + r"(?![A-Za-z])", plain):
            errs.append(f"禁单位 {u} → 应为 {u[:-1]}it/s")
    # 站内链必须 /de/ 前缀
    for href in re.findall(r"\]\((/[^)]*)\)", body):
        if not href.startswith("/de/"):
            errs.append(f"站内链缺 /de/ 前缀: {href}")
    return errs


def apply_country(slug: str, paragraphs: list[str], *, dry: bool = False) -> str:
    """写入一个国家页。返回 'applied' / 'skipped'。"""
    f = facts(slug)
    total, prov_n, brand, price = _desc_tokens(slug, PROVIDER_NAMES)

    path = DE / f"{slug}.md"
    en_path = EN / f"{slug}.md"
    raw = path.read_bytes()
    text = raw.decode("utf-8")
    en_text = en_path.read_text(encoding="utf-8")
    en_body = en_text.split("---\n", 2)[2]

    body_new = "\n\n".join(p.strip() for p in paragraphs).strip() + "\n"

    errs: list[str] = []
    if not text.startswith("---\n"):
        errs.append("front matter 起始异常")

    # ① seo.description 数字/品牌刷新
    pat = re.compile(r'(\n  description: "eSIM Sift vergleicht alle eSIM-Tarife für [^"]*?: )'
                     r'(\d+) echte Tarife von (\d+) Anbietern, günstigster ([A-Za-z]+) ab \$([\d.]+)')
    m = pat.search(text)
    if not m:
        errs.append("seo.description 形态未匹配")
    else:
        old = m.group(0)
        new = f"{m.group(1)}{total} echte Tarife von {prov_n} Anbietern, günstigster {brand} ab {price}"
        text = text.replace(old, new, 1)

    # ② TODO 注释统一
    if TODO_NEW in text:
        pass
    elif TODO_OLD_HEAD in text:
        blk = re.search(r"# TODO\(de\)：[^\n]*\n(?:#[^\n]*\n)*", text)
        if not blk:
            errs.append("TODO 块未匹配")
        else:
            text = text.replace(blk.group(0), TODO_NEW + "\n", 1)
    elif "noindex: true" in text:
        errs.append("有 noindex 但找不到 TODO 块")
    else:
        errs.append("缺 noindex/TODO")

    # ③ 正文
    parts = text.split("---\n", 2)
    head = "---\n" + parts[1]
    cur_body = parts[2]
    if cur_body.strip():
        if cur_body.strip() == body_new.strip():
            return "skipped"
        errs.append("正文已非空且与目标不符，拒绝覆盖")
    if "noindex: true" not in head:
        errs.append("front matter 缺 noindex（批 E 不应删它，D9 才删）")

    errs += _check_body(slug, body_new, en_body)
    if errs:
        raise SystemExit(f"[{slug}] 自检失败:\n  - " + "\n  - ".join(errs))

    new_text = head + "---\n\n" + body_new
    b2 = new_text.encode("utf-8")
    if b2.count(b"\r\n"):
        raise SystemExit(f"[{slug}] CRLF 污染: {b2.count(chr(13).encode()+chr(10).encode())}")
    if not dry:
        path.write_bytes(b2)
    return "applied"


def apply_hub(paragraphs: list[str], *, dry: bool = False) -> str:
    """写入 `content/de/compare/_index.md`（hub，6 个 h2 + 2 个短代码）。"""
    path = DE / "_index.md"
    en_path = EN / "_index.md"
    raw = path.read_bytes()
    text = raw.decode("utf-8")
    en_body = en_path.read_text(encoding="utf-8").split("---\n", 2)[2]
    body_new = "\n\n".join(p.strip() for p in paragraphs).strip() + "\n"

    errs: list[str] = []
    if TODO_NEW in text:
        pass
    elif "# TODO(de)：" in text:
        blk = re.search(r"# TODO\(de\)：[^\n]*\n(?:#[^\n]*\n)*", text)
        text = text.replace(blk.group(0), TODO_NEW + "\n", 1)
    else:
        errs.append("hub 缺 TODO 块")

    parts = text.split("---\n", 2)
    head = "---\n" + parts[1]
    cur_body = parts[2]
    if cur_body.strip():
        if cur_body.strip() == body_new.strip():
            return "skipped"
        errs.append("hub 正文已非空且与目标不符")

    # hub 正文自带 h2，段数判据换成 h2 数对齐
    en_h2 = len(re.findall(r"^## ", en_body, re.M))
    de_h2 = len(re.findall(r"^## ", body_new, re.M))
    if de_h2 != en_h2:
        errs.append(f"hub h2 数 {de_h2} != 英语 {en_h2}")
    sc_de = sorted(re.findall(r"\{\{<[^>]*>\}\}", body_new))
    sc_en = sorted(re.findall(r"\{\{<[^>]*>\}\}", en_body))
    if sc_de != sc_en:
        errs.append(f"hub 短代码不一致 德语={sc_de} 英语={sc_en}")
    plain = _strip_shortcodes(body_new)
    for w in F_WORDS:
        m = re.search(r"(?<![A-Za-zÀ-ÿ])%s(?![A-Za-zÀ-ÿ])" % re.escape(w), plain)
        if m:
            errs.append(f"F 禁词 {w!r}: …{plain[max(0,m.start()-40):m.end()+40]}…")
    for u in UNIT_BAD:
        if re.search(r"(?<![A-Za-z])" + u + r"(?![A-Za-z])", plain):
            errs.append(f"禁单位 {u}")
    if errs:
        raise SystemExit("hub 自检失败:\n  - " + "\n  - ".join(errs))

    new_text = head + "---\n\n" + body_new
    b2 = new_text.encode("utf-8")
    if b2.count(b"\r\n"):
        raise SystemExit("hub CRLF 污染")
    if not dry:
        path.write_bytes(b2)
    return "applied"
