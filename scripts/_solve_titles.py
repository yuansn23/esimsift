import tomllib, glob, os, sys
from collections import Counter

plans = {}
for f in glob.glob('data/plans/*.toml'):
    with open(f, 'rb') as fh:
        plans[os.path.basename(f)[:-5]] = tomllib.load(fh)
with open('data/countries.toml', 'rb') as fh:
    countries = tomllib.load(fh)
with open('data/carriers.toml', 'rb') as fh:
    carriers = tomllib.load(fh)

stats = {}
for iso in countries:
    c = countries[iso]
    if not isinstance(c, dict) or 'name' not in c:
        continue
    name = c['name']
    minprice = minpergb = minunl = None
    has5g = False
    for pk, pdata in plans.items():
        cc = pdata.get(iso)
        if not cc:
            continue
        for p in cc.get('plans', []):
            pr = float(p['price']); gb = float(p.get('gb', 0))
            if minprice is None or pr < minprice:
                minprice = pr
            if gb > 0:
                if minpergb is None or pr / gb < minpergb:
                    minpergb = pr / gb
            else:
                if minunl is None or pr < minunl:
                    minunl = pr
    cp = carriers.get(iso)
    if cp:
        for prof in cp.get('profiles', []):
            if '5G' in prof.get('tech', ''):
                has5g = True
    stats[iso] = dict(name=name, pg=minpergb, ul=minunl, mp=minprice, g5=has5g)

YEAR = 2026
f2 = lambda x: '%.2f' % x
tech = lambda c: '5G' if c['g5'] else '4G'

def all_segments(c):
    t = tech(c)
    pg, ul, mp = c['pg'], c['ul'], c['mp']
    X = f2(pg) if pg else None
    Y = f2(ul) if ul else None
    Z = f2(mp) if mp else None
    segs = []
    def add(bucket, s):
        if s:
            segs.append((bucket, s))
    for s in [('Cheapest %s Data From $%s/GB' % (t, X)), ('Cheap %s Data From $%s/GB' % (t, X)),
              ('Cheap %s Travel Data From $%s/GB' % (t, X)), ('Cheapest %s Travel Data From $%s/GB' % (t, X)),
              ('Cheap %s Data Plan From $%s/GB' % (t, X)), ('%s Travel Data From $%s/GB' % (t, X)),
              ('Cheap %s Data' % t), ('Cheapest %s Data' % t), ('Cheap %s' % t)]:
        add('cheap', s)
    for s in [('Cheap %s Travel Data' % t), ('%s Travel Data Plans' % t), ('%s Travel Data' % t)]:
        add('travelcheap', s)
    for s in [('Unlimited %s From $%s' % (t, Y)), ('Unlimited %s Data From $%s' % (t, Y)),
              ('Cheap Unlimited Data From $%s' % Y), ('Unlimited Data From $%s' % Y),
              ('Unlimited %s' % t), 'Unlimited Data']:
        add('unlimited', s)
    for s in [('%s Data for Tourists From $%s/GB' % (t, X)), ('Cheap %s for Tourists From $%s/GB' % (t, X)),
              ('Unlimited %s for Tourists From $%s' % (t, Y)),
              '%s Travel Data for Tourists' % t, '%s Travel Data for Travelers' % t, '%s Travel Data for Visitors' % t,
              'Cheap %s Data for Tourists' % t, 'Cheap %s Data for Travelers' % t, 'Cheap %s Data for Visitors' % t,
              'Unlimited Data for Tourists', 'Unlimited Data for Travelers', 'Unlimited Data for Visitors',
              '%s Data for Tourists' % t, '%s Data for Travelers' % t, '%s Data for Visitors' % t,
              'Cheap %s for Tourists' % t, 'Cheap %s for Travelers' % t, 'Cheap %s for Visitors' % t,
              'Unlimited %s for Tourists' % t, 'Unlimited %s for Travelers' % t,
              '%s for Tourists' % t, '%s for Travelers' % t, '%s for Visitors' % t,
              'For Tourists']:
        add('tourists', s)
    for s in [('%s No Roaming From $%s/GB' % (t, X)), ('Cheap %s No Roaming From $%s/GB' % (t, X)),
              ('No Roaming %s Data From $%s/GB' % (t, X)), 'Unlimited %s No Roaming' % t,
              'Cheap %s No Roaming' % t, '%s No Roaming' % t, 'No Roaming']:
        add('noroam', s)
    for s in [('%s Data Plan From $%s/GB' % (t, X)), ('%s Internet From $%s/GB' % (t, X)),
              '%s Data Plan for Tourists' % t, '%s Data Plan' % t, '%s Internet' % t]:
        add('dataplan', s)
    for s in [('Prepaid %s Data From $%s/GB' % (t, X)), 'Prepaid %s Data Plan' % t,
              'Prepaid %s Data' % t, 'Prepaid %s Internet' % t]:
        add('prepaid', s)
    for s in [('Value %s Data From $%s/GB' % (t, X)), ('Value %s Data' % t), ('Value %s' % t)]:
        add('value', s)
    for s in [('Compare Cheap %s From $%s' % (t, Z)), ('Buy Cheap %s From $%s' % (t, Z)),
              'Buy Cheap %s Data Plans' % t, 'Compare Cheap %s Data Plans' % t,
              'Compare %s Prices' % t, 'Buy %s Data Plans' % t]:
        add('compare', s)
    return segs

def prefix(name):
    return 'Best %s eSIM %d: ' % (name, YEAR)

cand = {}
for iso, s in stats.items():
    pre = prefix(s['name'])
    out = []
    for bucket, seg in all_segments(s):
        title = pre + seg
        if 48 <= len(title) <= 54:
            out.append((title, seg, bucket))
    cand[iso] = out

seg_usage = Counter()
assign = {}

def reserve(bucket, n):
    got = 0
    unassigned = [i for i in stats if i not in assign]
    while got < n and unassigned:
        choices = [(i, [p for p in cand[i] if p[2] == bucket]) for i in unassigned]
        choices = [(i, o) for i, o in choices if o]
        if not choices:
            break
        choices.sort(key=lambda io: len(io[1]))
        iso, opts = choices[0]
        opts = sorted(opts, key=lambda p: (seg_usage[p[1]], 0 if '$' in p[1] else 1, len(p[1])))
        title, seg, b = opts[0]
        assign[iso] = (title, seg, b)
        seg_usage[seg] += 1
        got += 1
        unassigned.remove(iso)

reserve('tourists', 6)
reserve('prepaid', 2)
reserve('travelcheap', 2)

targets = {'cheap': 7, 'unlimited': 8, 'tourists': 6, 'noroam': 8,
           'dataplan': 7, 'value': 5, 'compare': 6, 'prepaid': 2, 'travelcheap': 2}
bucket_usage = Counter(b for _, _, b in assign.values())
order = sorted([i for i in stats if i not in assign],
               key=lambda i: (-len(stats[i]['name']), stats[i]['name']))
for iso in order:
    opts = cand[iso]
    opts = sorted(opts, key=lambda p: (seg_usage[p[1]],
                                        0 if bucket_usage[p[2]] < targets.get(p[2], 0) else 1,
                                        0 if '$' in p[1] else 1,
                                        bucket_usage[p[2]], len(p[1])))
    title, seg, bucket = opts[0]
    assign[iso] = (title, seg, bucket)
    seg_usage[seg] += 1
    bucket_usage[bucket] += 1

dups = [s for s, n in seg_usage.items() if n > 1]
print('unique segments: %d/50, dup: %d' % (len(seg_usage), len(dups)))
for s in dups:
    print('  DUP x%d %s -> %s' % (seg_usage[s], s, [stats[i]['name'] for i in stats if assign[i][1] == s]))

print()
for iso in sorted(stats, key=lambda i: stats[i]['name']):
    title, seg, bucket = assign[iso]
    print('%-22s [%2d] %-10s %s' % (stats[iso]['name'], len(title), bucket, title))
print()
print('bucket distribution:', dict(bucket_usage))

buckets = ['Travel', 'Data Plan', 'Best', '5G', 'Cheap', 'Unlimited',
           'Tourists', 'No Roaming', 'Value', 'Buy', 'Compare', 'Prepaid', 'Internet']
allb = Counter()
for iso in stats:
    tt = assign[iso][0]
    for k in buckets:
        if k.lower() in tt.lower():
            allb[k] += 1
print('keyword coverage:', dict(allb))

if '--write' in sys.argv:
    with open('data/titlesegments.toml', 'w', encoding='utf-8') as fh:
        for iso in sorted(assign):
            fh.write('[%s]\ntitle = "%s"\n' % (iso, assign[iso][0]))
    print('\nWROTE data/titlesegments.toml')
