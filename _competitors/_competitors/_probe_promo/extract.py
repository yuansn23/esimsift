# -*- coding: utf-8 -*-
"""Scan saved promo HTML for coupon/promo signals and dump plain text snippets."""
import os, re, html, sys, json

OUT = os.path.dirname(os.path.abspath(__file__))

CODE_HINT = re.compile(
    r'(?:use|apply|enter|code|coupon|promo)\s*(?:code)?\s*[:\-]?\s*["\u201c\u2018]?'
    r'([A-Z0-9][A-Z0-9_\-]{2,19})["\u201d\u2019]?', re.I)
PCT = re.compile(r'(\d{1,2})\s*%\s*(?:off|discount)', re.I)
CTX = re.compile(
    r'.{0,80}(?:promo ?code|coupon code|use code|discount code|voucher|% ?off|referral|refer a friend|invite).{0,120}',
    re.I)


def plain(t):
    t = re.sub(r'<script[\s\S]*?</script>', ' ', t, flags=re.I)
    t = re.sub(r'<style[\s\S]*?</style>', ' ', t, flags=re.I)
    t = re.sub(r'<[^>]+>', ' ', t)
    return html.unescape(re.sub(r'\s+', ' ', t)).strip()


def scan(fn):
    p = os.path.join(OUT, fn)
    if not os.path.exists(p):
        return None
    t = open(p, encoding='utf-8', errors='ignore').read()
    txt = plain(t)
    codes = {}
    for m in CODE_HINT.finditer(t):
        c = m.group(1).upper()
        if c in ('GB', 'OFF', 'SALE', 'FREE', 'ESIM', 'SIM', 'AND', 'THE', 'FOR', 'YOU', 'ALL', 'NEW', 'APP', 'IOS', 'USD', 'EUR', 'VPN', 'FAQ', 'OPT', 'OK', 'ID', 'PDF', 'PNG', 'SVG', 'API', 'HTML', 'CSS', 'JSON'):
            continue
        codes[c] = codes.get(c, 0) + 1
    pcts = sorted(set(int(x) for x in PCT.findall(txt + ' ' + t)))
    ctx = [re.sub(r'\s+', ' ', m.group(0)).strip() for m in CTX.finditer(txt)]
    return {'file': fn, 'len': len(t), 'codes': codes, 'pct_off': pcts, 'context': list(dict.fromkeys(ctx))[:14]}


if __name__ == '__main__':
    targets = sys.argv[1:] or sorted(f for f in os.listdir(OUT) if f.endswith('.html'))
    for f in targets:
        r = scan(f)
        if not r:
            continue
        print('=' * 78)
        print(f, 'len=%d' % r['len'])
        if r['codes']:
            print('  CODES:', r['codes'])
        if r['pct_off']:
            print('  PCT:', r['pct_off'])
        for c in r['context']:
            print('   >', c[:190])
