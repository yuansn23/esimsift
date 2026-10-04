# -*- coding: utf-8 -*-
"""第二十三轮 i18n 补丁（续）：修对比口径 + 加单价曲线。

为什么还要第二支补丁：
  1. 「最便宜无限流量对手比它便宜」原本写在**优点**列 —— 语义反了。
     改成：优点列只写真话（有无限档 / 日单价），把比价放回缺点列。
  2. 与最便宜**计量**套餐比价，对只卖无限流量的品牌是苹果比橘子
     （$4.00 买的是 1GB，不是 30 天无限）—— 这正是上轮修过的「假价」坑。
     只卖无限流量的品牌改用「无限 vs 无限」的日单价对比。
  3. 任何报价格的句子都要说清那笔钱买到多少数据，所以 l_gap 补 {{ .data }}。
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]

NEW = [
    # 无限 vs 无限：日单价对比（只在「对手的无限档更便宜」时出现）
    ("compare_provider__tradeoffs_l_unl",
     "The cheapest unlimited plan here is ${{ .price }} a day from {{ .rival }}",
     "Der günstigste Unlimited-Tarif hier kostet ${{ .price }} pro Tag und kommt von {{ .rival }}"),
    # 单价随天数递减 —— 同一品牌在短途和长途中是两副面孔，读者该看到这条曲线
    ("compare_provider__tradeoffs_w_curve",
     "Its daily rate drops from ${{ .short }} over {{ .shortdays }} days to ${{ .long }} over {{ .longdays }} days",
     "Der Tagespreis fällt von ${{ .short }} für {{ .shortdays }} Tage auf ${{ .long }} für {{ .longdays }} Tage"),
]

REWRITE = [
    # 优点列只留事实，去掉「对手更便宜」这半句
    ("compare_provider__tradeoffs_w_unl",
     "Unlimited data from ${{ .perday }} a day",
     "Unlimited-Daten ab ${{ .perday }} pro Tag"),
    # 报价格必须同时报「这笔钱买到多少」
    ("compare_provider__tradeoffs_l_gap",
     "On a {{ .days }}-day trip {{ .provider }}'s {{ .data }} plan costs ${{ .price }} against ${{ .mine }} here — ${{ .diff }} less",
     "Bei einer {{ .days }}-Tage-Reise kostet {{ .data }} von {{ .provider }} ${{ .price }} statt ${{ .mine }} — ${{ .diff }} weniger"),
]


def main() -> int:
    en = ROOT / "i18n" / "en.toml"
    de = ROOT / "i18n" / "de.toml"
    for path, pairs in ((en, [(k, e) for k, e, d in NEW]), (de, [(k, d) for k, e, d in NEW])):
        s = path.read_text(encoding="utf-8")
        if not s.endswith("\n"):
            s += "\n"
        add, n = ["\n# ── 第二十三轮（续）───────────────────────────────\n"], 0
        for key, val in pairs:
            if f"\n{key} = " in "\n" + s:
                print(f"  SKIP 已存在: {key}")
                continue
            add.append(f'{key} = "{val}"\n')
            n += 1
        path.write_text(s + "".join(add), encoding="utf-8", newline="\n")
        print(f"{path.name}: +{n}")

    for key, en_v, de_v in REWRITE:
        for path, val in ((en, en_v), (de, de_v)):
            lines = path.read_text(encoding="utf-8").split("\n")
            hit = False
            for i, ln in enumerate(lines):
                if ln.startswith(key + " = "):
                    lines[i] = f'{key} = "{val}"'
                    hit = True
                    break
            print(f"  改写 {key} in {path.name}: {'OK' if hit else 'MISS'}")
            path.write_text("\n".join(lines), encoding="utf-8", newline="\n")

    import tomllib
    ce = len(tomllib.loads(en.read_text(encoding="utf-8")))
    cd = len(tomllib.loads(de.read_text(encoding="utf-8")))
    print(f"key 总数 en={ce} de={cd} {'✓' if ce == cd else '✗'}")
    return 0 if ce == cd else 1


if __name__ == "__main__":
    sys.exit(main())
