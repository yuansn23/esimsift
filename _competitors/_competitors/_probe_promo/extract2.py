# -*- coding: utf-8 -*-
"""Extract *visible text* + visible code-like tokens from saved HTML, with context windows.
Works on rendered (Playwright) HTML and static HTML alike."""
import os, re, html, sys

OUT = os.path.dirname(os.path.abspath(__file__))

KW = re.compile(
    r'(promo ?code|coupon|discount|use code|[A-Z0-9]{4,14}\s*[-–]\s*\d{1,2}%|'
    r'\d{1,2}\s*%\s*off|voucher|refer(?:ral)?|invite|welcome (?:gift|offer)|'
    r'free trial|first (?:purchase|order)|student|military|new user|sign ?up (?:bonus|offer)|'
    r'BOGO|buy \d+ get)', re.I)


def visible_text(t):
    t = re.sub(r'<script[\s\S]*?</script>', ' ', t, flags=re.I)
    t = re.sub(r'<style[\s\S]*?</style>', ' ', t, flags=re.I)
    t = re.sub(r'<noscript[\s\S]*?</noscript>', ' ', t, flags=re.I)
    t = re.sub(r'<[^>]+>', ' ', t)
    return html.unescape(re.sub(r'\s+', ' ', t)).strip()


def run(fn, width=110):
    p = os.path.join(OUT, fn)
    if not os.path.exists(p):
        print('MISSING', fn); return
    raw = open(p, encoding='utf-8', errors='ignore').read()
    txt = visible_text(raw)
    # code-like tokens near code words in the RAW (they may sit in JSON)
    raw2 = raw.replace('\\"', '"').replace('\\u0026', '&').replace('\\/', '/')
    print('=' * 90)
    print(fn, 'raw=%d visible=%d' % (len(raw), len(txt)))
    seen = set()
    for m in KW.finditer(txt):
        s = max(0, m.start() - width)
        e = min(len(txt), m.end() + width)
        frag = txt[s:e].strip()
        k = frag[:80]
        if k in seen:
            continue
        seen.add(k)
        print('   T>', frag[:240])
    # JSON-side code tokens
    jc = re.findall(r'(?:promoCode|promo_code|couponCode|coupon|code)"\s*:\s*"([A-Za-z0-9_\-]{3,20})"', raw2)
    jc = [c for c in jc if not re.match(r'^\$|undefined|null', c)]
    if jc:
        print('   JSON_CODES:', sorted(set(jc)))
    # discount fields
    for f in ('discountPercent', 'discountPercentage', 'discount', 'discountValue'):
        for m in list(re.finditer(f + r'"\s*:\s*([0-9.]+)', raw2))[:4]:
            print('   JSON_%s = %s' % (f, m.group(1)))


if __name__ == '__main__':
    for f in (sys.argv[1:] or sorted(x for x in os.listdir(OUT) if x.endswith('.html'))):
        run(f)
