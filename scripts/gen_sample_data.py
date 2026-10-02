#!/usr/bin/env python3
"""esimsift demo-data generator.

Fills the site with 50 countries so templates can be judged at scale:
  - rewrites data/countries.toml (50 entries, JP keeps its real quirks/slug)
  - rewrites data/plans/*.toml  (5 providers x 50 countries; JP-Roami prices stay REAL)
  - writes 49 compare pages + 49 faq files (japan kept as hand-written exemplar)
  - copies 4 pool illustrations per country to static/img/countries/<slug>-0N.webp
  - copies site hero/og images

Deterministic: seeded by ISO, rerunning produces identical output.
All generated prices are plausible but SAMPLE - real collection pass comes later.
"""
import hashlib
import random
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
CONTENT = ROOT / "content" / "en" / "compare"
FAQS = DATA / "faqs"
POOL = ROOT / "static" / "img" / "esim"
IMG_OUT = ROOT / "static" / "img" / "countries"
SITE_IMG = ROOT / "static" / "img" / "site"

POOL_SIZE = 132
CHECKED_DATES = ["2026-09-24", "2026-09-25", "2026-09-26", "2026-09-27", "2026-09-28", "2026-09-29", "2026-09-30"]

A = "Asia"
E = "Europe"
AM = "Americas"
ME = "Africa & Middle East"
O = "Oceania"

# iso, name, slug, region, price level (JP=1.00), featured, weight, carriers, neighbors, kyc_note, quirks
C = [
 ("JP","Japan","japan",A,1.00,True,1,["NTT Docomo","SoftBank","KDDI"],["KR","TW","HK"],False,None),  # quirks set below
 ("US","United States","united-states",AM,1.20,True,2,["T-Mobile","AT&T","Verizon"],["CA","MX"],False,
  ["Verizon joined travel eSIM support late - most plans still run T-Mobile or AT&T, fine in cities, thinner in national parks.",
   "US 'unlimited' travel plans typically throttle after 2-5 GB per day; the fair-use fine print matters more here than anywhere."]),
 ("GB","United Kingdom","united-kingdom",E,1.15,True,3,["EE","Vodafone","O2","Three"],["IE","FR"],False,
  ["EE consistently wins UK rural coverage tests; Three is cheapest but thins out in the Highlands.",
   "UK 'unlimited' tourist plans from Three throttle video to 1080p - fine on a phone, annoying if you hotspot a laptop."]),
 ("FR","France","france",E,1.05,True,4,["Orange","SFR","Bouygues"],["GB","BE","CH","IT","ES"],False,
  ["Free is famously cheap but uneven in Provence; Orange remains the coverage king for the countryside.",
   "Orange Holiday packages are strong value at CDG - buy the eSIM online first to skip the counter queue."]),
 ("IT","Italy","italy",E,1.00,True,5,["TIM","Vodafone","WindTre"],["FR","CH","AT"],False,
  ["TIM still owns rural Italy; WindTre-based budget eSIMs can struggle in Umbrian hill towns.",
   "Italian law caps tourist SIM validity at 90 days - irrelevant for travel eSIMs, which expire with the plan anyway."]),
 ("TH","Thailand","thailand",A,0.80,True,6,["AIS","True Move","DTAC"],["MY","VN"],False,
  ["Airport SIM counters at Suvarnabhumi run 24/7 with aggressive tourist pricing - the rare case where physical SIMs compete on the spot.",
   "True and DTAC merged networks; most eSIMs land on the combined grid, making 'network choice' marketing mostly moot."]),
 ("KR","South Korea","south-korea",A,1.00,True,7,["SK Telecom","KT","LG U+"],["JP","TW"],False,
  ["Korean carrier apps often demand a local ARS verification - travel eSIMs sidestep this with pre-registered profiles.",
   "KT and SK both cap tourist plans at LTE despite the 5G rollout; check whether your plan lists 5G before paying extra."]),
 ("SG","Singapore","singapore",A,1.05,True,8,["Singtel","StarHub","M1"],["MY","ID"],False,
  ["Tourist SIMs are strong value but physical-only at Changi counters; eSIMs win on convenience for 1 AM arrivals.",
   "All three Singapore networks are excellent - the cheapest eSIM here rarely costs you coverage."]),
 ("ES","Spain","spain",E,1.00,True,9,["Movistar","Vodafone","Orange","Yoigo"],["PT","FR"],False,
  ["Movistar covers the coasts and islands best; Yoigo-based cheap plans roam onto it anyway.",
   "Spanish law requires ID for local SIMs; travel eSIMs skip the passport scan entirely."]),
 ("DE","Germany","germany",E,1.05,True,10,["Telekom","Vodafone","O2"],["FR","CH","AT","NL","BE","PL","CZ"],False,
  ["Telekom's network is the coverage benchmark; O2-based eSIMs save money but fade outside cities.",
   "German prepaid law requires ID for local SIMs - travel eSIMs skip the Ausweis check."]),
 ("AU","Australia","australia",O,1.15,True,11,["Telstra","Optus","Vodafone"],["NZ"],False,
  ["Telstra is the outback lifeline - Optus covers 98.5% of the population but a fraction of the land; a Telstra-based eSIM matters off the coast.",
   "Australian 'unlimited' tourist eSIMs always carry a daily speed cap after 2-3 GB."]),
 ("TW","Taiwan","taiwan",A,0.95,False,12,["Chunghwa Telecom","Taiwan Mobile","FarEasTone"],["JP","HK"],False,
  ["Taiwan's tourist SIMs are cheap but airport-counter-only; online eSIM prices are close enough that skipping the queue usually wins.",
   "FarEasTone tourist cards throttle after a daily cap; Airalo plans run full speed until the bucket empties."]),
 ("HK","Hong Kong","hong-kong",A,1.00,False,13,["CSL","3HK","SmarTone"],["TW","MO","CN"],False,
  ["Hong Kong is one market where local prepaid SIMs genuinely beat eSIMs on price - but require physical pickup at convenience stores.",
   "CSL runs the densest metro coverage; most travel eSIMs ride the same network, so cheap plans rarely cost you signal."]),
 ("MO","Macao","macao",A,1.00,False,14,["CTM","3 Macau","China Telecom"],["HK","CN"],False,
  ["Macao packs three networks into a tiny area - coverage differences are negligible; buy on price.",
   "Many Hong Kong eSIMs include Macao at no extra cost; check regional plans before buying a single-country one."]),
 ("MY","Malaysia","malaysia",A,0.80,False,15,["Maxis","Celcom","DiGi"],["TH","SG","ID"],False,
  ["Malaysian tourist SIMs need passport registration at a counter; eSIMs skip the paperwork entirely.",
   "DiGi's rural coverage lags Maxis and Celcom - if Borneo is on the itinerary, check which network your eSIM uses."]),
 ("VN","Vietnam","vietnam",A,0.80,False,16,["Viettel","Vinaphone","Mobifone"],["TH"],True,
  ["Vietnam requires passport registration for every SIM including eSIMs - expect a quick ID upload during purchase.",
   "Viettel is the only network that reliably covers Ha Long Bay and northern mountain routes; most travel eSIMs default to it."]),
 ("ID","Indonesia","indonesia",A,0.78,False,17,["Telkomsel","Indosat","XL Axiata"],["SG","MY","PH"],True,
  ["Indonesia's islands make network choice decisive - Telkomsel dominates outside Java and Bali; cheap Indosat plans drop signal on Lombok.",
   "Indonesian law requires a passport upload for eSIM registration; providers handle it in-app."]),
 ("PH","Philippines","philippines",A,0.85,False,18,["Globe","Smart"],["ID"],True,
  ["Smart and Globe coverage outside Luzon is patchy and complementary - a dual-eSIM phone with one of each is the island-hopper's power move.",
   "Philippine SIM registration requires an ID selfie by law; eSIM purchases include the same step."]),
 ("IN","India","india",A,0.72,False,19,["Jio","Airtel"],["TH"],True,
  ["Indian rules require passport-linked registration even for travel eSIMs - Airalo and Saily handle it in-app in about two minutes.",
   "Jio's coverage dwarfs Airtel outside cities; most travel eSIMs ride Airtel - fine for the Golden Triangle, weaker in Ladakh."]),
 ("CN","China","china",A,0.85,False,20,["China Mobile","China Unicom","China Telecom"],["HK","MO","JP","KR"],True,
  ["Travel eSIMs for China route through Hong Kong gateways - they need no VPN for Google and WhatsApp, unlike local SIMs.",
   "China Unicom accepts foreign eSIMs most reliably; Telecom occasionally needs manual APN entry."]),
 ("PT","Portugal","portugal",E,0.95,False,21,["MEO","NOS","Vodafone"],["ES"],False,
  ["Mainland Portugal is easy for all networks; the Azores and Madeira favor MEO-based plans.",
   "Lisbon and Porto have 5G on every network; the price gap between them buys nothing in cities."]),
 ("NL","Netherlands","netherlands",E,1.10,False,22,["KPN","Vodafone","Odido"],["BE","DE"],False,
  ["The country is small and flat - all three networks are effectively equal; buy on price.",
   "Dutch consumer rules cap 'unlimited' throttling - one of the few places the label means something."]),
 ("BE","Belgium","belgium",E,1.10,False,23,["Proximus","Orange","Base"],["NL","FR","DE"],False,
  ["Coverage is a solved problem on all networks; the Brussels-Bruges train has Wi-Fi, so big buckets go unused.",
   "Belgian local prepaid requires ID; travel eSIMs skip it."]),
 ("CH","Switzerland","switzerland",E,1.45,False,24,["Swisscom","Sunrise","Salt"],["FR","DE","IT","AT"],False,
  ["Switzerland is NOT in EU roaming - EU eSIMs pay surcharges here; a Swiss-specific plan pays for itself in hours.",
   "Swiss data is Europe's most expensive; Swisscom's Alpine coverage is unmatched, and priced like it."]),
 ("AT","Austria","austria",E,1.15,False,25,["A1","Magenta","Drei"],["DE","CH","IT","CZ"],False,
  ["Alpine coverage belongs to A1; Magenta-based eSIMs dip in Tyrol valleys.",
   "Austrian local prepaid asks for registration; travel eSIMs arrive pre-registered."]),
 ("GR","Greece","greece",E,0.95,False,26,["Cosmote","Vodafone","Wind"],["TR"],False,
  ["Cosmote owns the islands; Vodafone-based budget eSIMs lose signal hopping between the Cyclades.",
   "July and August strain island towers - no plan choice fixes peak-season congestion."]),
 ("TR","Turkiye","turkiye",E,0.85,False,27,["Turkcell","Vodafone","Turk Telekom"],["GR"],True,
  ["Turkiye blocks some VPN protocols by default - travel eSIMs route internationally and sidestep the block.",
   "Turkcell tourist packages are decent value but airport-only; eSIM prices compete closely online."]),
 ("IE","Ireland","ireland",E,1.15,False,28,["Vodafone","Three","Eir"],["GB"],False,
  ["Three Ireland covers the west coast best; Vodafone wins the midlands.",
   "Rural signal follows the M8 - offline maps matter more than network choice on the Ring of Kerry."]),
 ("PL","Poland","poland",E,0.85,False,29,["Orange","Play","Plus","T-Mobile"],["DE","CZ"],False,
  ["Play grew from budget brand to coverage leader; all four networks are fine in cities.",
   "Krakow-to-Zakopane buses cross Play dead zones - Telkomsel-style network checks don't apply; just download offline maps."]),
 ("CZ","Czechia","czechia",E,0.90,False,30,["O2","T-Mobile","Vodafone"],["DE","PL","AT"],False,
  ["Prague is trivial for coverage; castle-heavy rural Bohemia favors T-Mobile.",
   "Czech local prepaid requires registration; travel eSIMs skip the paperwork."]),
 ("HR","Croatia","croatia",E,0.95,False,31,["Hrvatski Telekom","A1 Hrvatska"],[],False,
  ["The islands are Hrvatski Telekom territory; A1-based plans fade south of Split.",
   "Ferry routes switch towers mid-strait - expect a 30-second data pause between islands on any network."]),
 ("IS","Iceland","iceland",E,1.35,False,32,["Siminn","Vodafone","Noa"],[],False,
  ["The ring road is covered by all networks; highland F-roads have nothing - offline maps regardless of SIM.",
   "Icelandic data is expensive everywhere; there is no budget hack, only per-GB optimization."]),
 ("GE","Georgia","georgia",E,0.80,False,33,["Magti","Silknet","Beeline"],["TR"],False,
  ["Mountain regions belong to Magti; twin-SIM phones pair a Magti physical SIM with a travel eSIM for the best of both.",
   "Georgian eSIM registration is not required - one of Europe's easiest buys."]),
 ("CA","Canada","canada",AM,1.15,False,34,["Bell","Rogers","Telus"],["US"],False,
  ["The Big Three share networks - a 'discount' Telus eSIM often runs the same towers as Bell.",
   "Canadian data is among the world's priciest; carrier day-passes are almost always worse than a travel eSIM."]),
 ("MX","Mexico","mexico",AM,0.90,False,35,["Telcel","AT&T Mexico","Movistar"],["US"],True,
  ["Telcel is the only network that covers Chiapas and Oaxaca properly; AT&T-based eSIMs are city-strong, rural-thin.",
   "Mexican law requires CURP/ID registration for local SIMs; travel eSIMs skip the counter visit."]),
 ("BR","Brazil","brazil",AM,0.95,False,36,["Vivo","Claro","TIM"],["AR"],False,
  ["Vivo leads national coverage; TIM-based budget eSIMs struggle in Amazonas.",
   "Brazilian local prepaid asks for CPF - foreigners rarely have one; travel eSIMs avoid the problem entirely."]),
 ("AR","Argentina","argentina",AM,0.95,False,37,["Personal","Claro","Movistar"],["BR"],True,
  ["Buenos Aires is fine on every network; Patagonia belongs to Personal.",
   "Local SIM registration requires a DNI for residents; tourists need a passport walkthrough - eSIMs skip it all."]),
 ("CO","Colombia","colombia",AM,0.90,False,38,["Claro","Movistar","Tigo"],["PE"],False,
  ["Claro owns rural Colombia; coffee-region roads lose Movistar signal fast.",
   "Bogota to Cartagena flights make big buckets pointless - hotel Wi-Fi carries the heavy lifting."]),
 ("PE","Peru","peru",AM,0.90,False,39,["Claro","Movistar","Entel"],["CO"],False,
  ["Entel covers Cusco and Machu Picchu best; Claro wins Lima.",
   "Andean passes drop every network - offline maps matter more than plan choice on the Salkantay route."]),
 ("CR","Costa Rica","costa-rica",AM,0.95,False,40,["Kolbi","Claro","Movistar"],[],False,
  ["State-run Kolbi covers the jungles; Claro-based tourist eSIMs lose Osa Peninsula signal.",
   "Tourist SIM counters at SJO close by 22:00 - eSIMs activate on landing regardless."]),
 ("AE","United Arab Emirates","united-arab-emirates",ME,1.10,True,41,["Etisalat","du"],["SA","QA"],True,
  ["Both UAE networks are excellent - and both throttle VoIP apps; travel eSIMs that route internationally restore WhatsApp calls.",
   "UAE tourist SIMs require a passport scan at purchase; eSIMs keep it in-app."]),
 ("SA","Saudi Arabia","saudi-arabia",ME,1.10,False,42,["STC","Mobily","Zain"],["AE","QA","EG"],True,
  ["STC leads coverage on the Riyadh-Jeddah corridor and the Red Sea projects; Zain-based plans lag in AlUla.",
   "Saudi tourist eSIMs need passport details; providers verify in-app within minutes."]),
 ("QA","Qatar","qatar",ME,1.15,False,43,["Ooredoo","Vodafone Qatar"],["AE","SA"],False,
  ["Two networks, near-identical Doha coverage - buy on price.",
   "Stadium-district towers congest on event nights; no plan choice fixes that."]),
 ("IL","Israel","israel",ME,1.15,False,44,["Cellcom","Partner","Pelephone"],[],True,
  ["Israeli law requires ID for all SIMs; travel eSIMs for Israel are surprisingly scarce - check coverage lists before assuming your provider sells one.",
   "Jerusalem's Old City alleys favor Cellcom; Petah Tikva industrial zones are fine everywhere."]),
 ("EG","Egypt","egypt",ME,0.85,False,45,["Vodafone Egypt","Orange Egypt","Etisalat Misr"],["SA"],True,
  ["Vodafone covers the Nile valley and Red Sea coast; Sinai inland routes need Etisalat.",
   "Egyptian SIM registration requires passport photos at official stores - eSIMs cut the bureaucracy."]),
 ("MA","Morocco","morocco",ME,0.90,False,46,["Maroc Telecom","Orange Maroc","Inwi"],[],True,
  ["Maroc Telecom covers the Atlas trails and Sahara edge; Inwi-based plans end at Marrakech.",
   "Medina alleys in Fes kill signal on every network - offline maps first, data second."]),
 ("ZA","South Africa","south-africa",ME,0.95,False,47,["Vodacom","MTN","Telkom"],[],False,
  ["Vodacom and MTN split the country; Garden Route towns favor Vodacom.",
   "Load-shedding hits towers - no SIM choice fixes a power cut, but offline maps soften it."]),
 ("KE","Kenya","kenya",ME,0.85,False,48,["Safaricom","Airtel Kenya","Telkom Kenya"],[],True,
  ["Safaricom covers the Maasai Mara; Airtel-based eSIMs fade outside Nairobi and Mombasa.",
   "Kenyan SIM registration requires a passport in person - eSIMs handle it digitally."]),
 ("NZ","New Zealand","new-zealand",O,1.15,False,49,["Spark","One NZ","2degrees"],["AU"],False,
  ["Spark wins the South Island's west coast; 2degrees-based budget plans fade in Fiordland.",
   "Milford Sound has no coverage on any network - download before the drive."]),
 ("FJ","Fiji","fiji",O,1.10,False,50,["Vodafone Fiji","Digicel Fiji"],["AU","NZ"],False,
  ["Vodafone covers the Mamanucas; Digicel wins the outer islands - inter-island ferries switch networks mid-strait.",
   "Resort Wi-Fi is metered and slow; an eSIM with a modest bucket beats the hotel's rates."]),
]

JP_QUIRKS = [
  "Japanese law requires passport verification for local prepaid SIM cards (SoftBank, Docomo, KDDI) - travel eSIMs bypass this entirely.",
  "SoftBank's own tourist SIM can only be activated 09:00-21:00 JST; travel eSIMs activate 24/7, which matters for late-night arrivals at Narita or Haneda.",
  "Pocket WiFi rental is Japan's classic connectivity option. It wins for groups of 3 or more, but a solo traveler almost always pays less with an eSIM.",
]

# Roami JP 真实价格（保留，勿改）
ROAMI_JP_REAL = {
    "checked": "2026-09-28",
    "plans": [
        ("1GB / 7 Days", 1, 7, "data", 1.99, ""),
        ("3GB / 7 Days", 3, 7, "data", 3.99, ""),
        ("5GB / 7 Days", 5, 7, "data", 5.99, ""),
        ("10GB / 7 Days", 10, 7, "data", 9.99, ""),
        ("20GB / 7 Days", 20, 7, "data", 16.99, ""),
        ("Unlimited / 7 Days", 0, 7, "unlimited", 18.99, "Soft cap 2GB/day at full speed, then throttled"),
        ("3GB / 15 Days", 3, 15, "data", 4.99, ""),
        ("5GB / 15 Days", 5, 15, "data", 6.99, ""),
        ("10GB / 15 Days", 10, 15, "data", 10.99, ""),
        ("20GB / 15 Days", 20, 15, "data", 17.99, ""),
        ("30GB / 15 Days", 30, 15, "data", 25.99, ""),
        ("Unlimited / 15 Days", 0, 15, "unlimited", 42.99, "Soft cap 2GB/day at full speed, then throttled"),
        ("3GB / 30 Days", 3, 30, "data", 5.99, ""),
        ("5GB / 30 Days", 5, 30, "data", 7.99, ""),
        ("10GB / 30 Days", 10, 30, "data", 11.99, ""),
        ("20GB / 30 Days", 20, 30, "data", 20.99, ""),
        ("30GB / 30 Days", 30, 30, "data", 25.99, ""),
        ("50GB / 30 Days", 50, 30, "data", 37.99, ""),
        ("Unlimited / 30 Days", 0, 30, "unlimited", 71.99, "Soft cap 2GB/day at full speed, then throttled"),
    ],
}

# 品牌阶梯（基准价，level=1）；实际价 = 基准 × level，.99 取整
ROAMI_LADDER = [
    ("1GB / 7 Days",1,7,"data",1.99,""),("3GB / 7 Days",3,7,"data",3.99,""),("5GB / 7 Days",5,7,"data",5.99,""),
    ("10GB / 7 Days",10,7,"data",9.99,""),("20GB / 7 Days",20,7,"data",16.99,""),
    ("Unlimited / 7 Days",0,7,"unlimited",18.99,"Soft cap 2GB/day at full speed, then throttled"),
    ("3GB / 15 Days",3,15,"data",4.99,""),("5GB / 15 Days",5,15,"data",6.99,""),("10GB / 15 Days",10,15,"data",10.99,""),
    ("20GB / 15 Days",20,15,"data",17.99,""),("30GB / 15 Days",30,15,"data",25.99,""),
    ("Unlimited / 15 Days",0,15,"unlimited",42.99,"Soft cap 2GB/day at full speed, then throttled"),
    ("3GB / 30 Days",3,30,"data",5.99,""),("5GB / 30 Days",5,30,"data",7.99,""),("10GB / 30 Days",10,30,"data",11.99,""),
    ("20GB / 30 Days",20,30,"data",20.99,""),("30GB / 30 Days",30,30,"data",25.99,""),("50GB / 30 Days",50,30,"data",37.99,""),
    ("Unlimited / 30 Days",0,30,"unlimited",71.99,"Soft cap 2GB/day at full speed, then throttled"),
]
AIRALO_LADDER = [
    ("1GB / 7 Days",1,7,"data",2.49,""),("2GB / 7 Days",2,7,"data",3.99,""),("3GB / 7 Days",3,7,"data",4.99,""),
    ("5GB / 7 Days",5,7,"data",6.99,""),("10GB / 7 Days",10,7,"data",10.99,""),("20GB / 7 Days",20,7,"data",16.99,""),
    ("10GB / 30 Days",10,30,"data",13.99,""),("20GB / 30 Days",20,30,"data",23.99,""),
]
SAILY_LADDER = [
    ("1GB / 7 Days",1,7,"data",2.19,""),("3GB / 7 Days",3,7,"data",4.19,""),("5GB / 7 Days",5,7,"data",5.99,""),
    ("10GB / 7 Days",10,7,"data",9.99,""),("20GB / 7 Days",20,7,"data",16.99,""),
    ("5GB / 30 Days",5,30,"data",7.99,""),("10GB / 30 Days",10,30,"data",12.99,""),("20GB / 30 Days",20,30,"data",20.99,""),
]
NOMAD_LADDER = [
    ("1GB / 7 Days",1,7,"data",2.39,""),("3GB / 7 Days",3,7,"data",4.49,""),("5GB / 7 Days",5,7,"data",6.49,""),
    ("10GB / 7 Days",10,7,"data",10.99,""),("15GB / 7 Days",15,7,"data",14.99,""),
    ("10GB / 15 Days",10,15,"data",11.99,""),("20GB / 15 Days",20,15,"data",18.99,""),
    ("10GB / 30 Days",10,30,"data",12.99,""),("20GB / 30 Days",20,30,"data",21.99,""),
    ("Unlimited / 30 Days",0,30,"unlimited",37.99,"3GB/day high-speed cap, then 3G speeds"),
]
FUP_POOL = [
    "Full speed for the first 2GB each day, then 512kbps",
    "1.5GB/day high-speed cap, then 3G speeds",
    "No published cap; throttling reported above 3GB/day",
]


def money(x: float) -> float:
    return float(f"{max(1, round(x))}.99")


def rng_for(iso: str) -> random.Random:
    return random.Random(int(hashlib.md5(iso.encode()).hexdigest()[:8], 16))


def holafly_plans(level: float, rng: random.Random):
    per_day = 3.90 * (level ** 0.6)
    fup = rng.choice(FUP_POOL)
    out = []
    for days in (5, 10, 15, 20, 30, 60):
        out.append((f"Unlimited / {days} Days", 0, days, "unlimited", money(per_day * days), fup))
    return out


def scale(ladder, level):
    return [(n, gb, d, t, money(p * level), f) for (n, gb, d, t, p, f) in ladder]


def build_stats(iso: str, level: float) -> dict:
    """Mirror of country-stats.html: per-country computed facts for prose/FAQ."""
    rng = rng_for(iso)
    provs = {
        "roami": ROAMI_JP_REAL["plans"] if iso == "JP" else scale(ROAMI_LADDER, level),
        "airalo": scale(AIRALO_LADDER, level * 1.10),
        "holafly": holafly_plans(level, rng),
        "saily": scale(SAILY_LADDER, level * 0.95),
        "nomad": scale(NOMAD_LADDER, level),
    }
    rows = []
    for pk, plans in provs.items():
        for (n, gb, d, t, p, f) in plans:
            rows.append({"k": pk, "name": n, "gb": gb, "days": d, "type": t,
                         "price": p, "perDay": p / d, "perGB": (p / gb) if gb else 9e5, "fup": f})
    cheapest = min(rows, key=lambda r: r["price"])
    value = min((r for r in rows if r["gb"] > 0), key=lambda r: r["perGB"])
    unl = sorted((r for r in rows if r["gb"] == 0), key=lambda r: r["price"])
    hol = min((r for r in rows if r["k"] == "holafly"), key=lambda r: r["perDay"])
    return {"provs": provs, "rows": rows, "cheapest": cheapest, "value": value, "unl": unl, "hol": hol, "rng": rng}


PROV_NAMES = {"roami": "Roami", "airalo": "Airalo", "holafly": "Holafly", "saily": "Saily", "nomad": "Nomad"}


def analysis_paras(iso: str, name: str, st: dict, carriers: list, quirk0: str) -> list:
    ch, val, unl = st["cheapest"], st["value"], st["unl"]
    rng = st["rng"]
    p1_open = rng.choice([
        f"{name}'s eSIM market splits cleanly into two pricing models.",
        f"Scan the {name} table and two pricing philosophies emerge.",
        f"Prices for {name} cluster into two distinct camps.",
    ])
    holoday = st["hol"]["perDay"]
    p1 = (f"{p1_open} Metered plans — {PROV_NAMES[ch['k']]} down to ${ch['price']:.2f} for {ch['gb']}GB — "
          f"charge for a data bucket, while Holafly sells a single shape: unlimited data billed at roughly ${holoday:.2f}/day. "
          f"On pure $/GB, {PROV_NAMES[val['k']]} wins outright: {val['name']} works out to ${val['perGB']:.2f}/GB, the best rate of the {len(st['rows'])} plans we track.")
    p2 = (f"The crossover point decides it. At ${holoday:.2f}/day, two weeks of Holafly runs ${unl[0]['price'] * 14 / unl[0]['days']:.0f}+, "
          f"while a 20GB bucket from the same table covers a heavy two-week trip for less. Light users — maps, messaging, the odd lookup — "
          f"can stop at a 3-5GB bucket and stay in single digits. "
          f"Rule of thumb for {name}: under a week and Wi-Fi at the hotel, buy the smallest bucket; remote work or hotspot sharing pushes every metered plan toward the unlimited tier.")
    p3 = (f"Network-wise, {name} runs on {', '.join(carriers[:2] + carriers[2:])} — coverage differences between them matter more than price differences between providers. "
          f"{quirk0.split(' - ')[0].rstrip('.')}. "
          f"Check the fair-use column before buying any 'unlimited' label, and re-check this page before your trip: prices move.")
    return [p1, p2, p3]


def faq_list(iso: str, name: str, st: dict, kyc, carriers: list, neighbors: list) -> list:
    ch, val, unl, hol = st["cheapest"], st["value"], st["unl"], st["hol"]
    kyc_a = ("Yes. Local law requires passport-linked registration even for travel eSIMs, but the big providers verify in-app in a couple of minutes."
             if kyc else
             f"No. {name} does not force ID checks on travel eSIMs - local SIM rules differ, but the plans on this page ship pre-registered.")
    return [
        (f"What is the cheapest eSIM for {name}?",
         f"{PROV_NAMES[ch['k']]} - the {ch['name']} at ${ch['price']:.2f} (${ch['perDay']:.2f}/day) is the cheapest plan we track. "
         f"That buys {ch['gb']}GB over {ch['days']} days: enough for maps and messaging if your hotel has Wi-Fi."),
        (f"Is unlimited eSIM data in {name} actually unlimited?",
         f"Not quite. All {len(unl)} 'unlimited' plans here apply fair-use policies - the cheapest, {PROV_NAMES[unl[0]['k']]} at ${unl[0]['price']:.2f} "
         f"(${unl[0]['perDay']:.2f}/day), carries: {unl[0]['fup'] or 'a daily high-speed cap'}. Treat them as big-but-capped plans and compare the caps."),
        (f"Airalo or Holafly for {name}?",
         f"Different animals. Airalo sells metered buckets - its best rate here is competitive per GB - while Holafly only sells unlimited-by-day "
         f"(${hol['perDay']:.2f}/day at its cheapest tier). Short light trip: Airalo-style buckets win. Heavy data or hotspot sharing: Holafly's flat rate caps your downside."),
        (f"Do I need ID verification for a {name} eSIM?",
         kyc_a),
        (f"Which networks do {name} eSIMs use?",
         f"Plans on this page run on {', '.join(carriers)}. Differences matter mostly outside the big cities - the network column in the main table shows which carrier each plan rides."),
        (f"Can one eSIM cover {name}{(' and ' + neighbors[0]) if neighbors else ''}?",
         (f"Regional Asia/continental plans from Airalo and Nomad bundle {name} with neighbors - usually worse $/GB than single-country plans, but cheaper than two separate eSIMs. "
          if neighbors else
          f"No single-country plan here bundles neighbors - regional plans from Airalo and Nomad cover multi-stop trips, usually at a $/GB premium. ")
         + "For a two-country trip, compare one regional plan against two country-specific ones in the tables before buying."),
    ]


def toml_str(s: str) -> str:
    return '"' + s.replace('\\', '').replace('"', "'") + '"'


def write_countries_toml(by_iso):
    L = [
        "# ============================================================",
        "# 国家主数据 —— 单一事实源（ GENERATED by scripts/gen_sample_data.py ）",
        "#   - quirks 为逐国研究内容：量产前人工复核",
        "#   - slugs.roami 的深链规则当前为模式假设（<slug>-esim），上线前核对",
        "# ============================================================",
        "",
    ]
    for (_, name, slug, region, level, featured, weight, carriers, nbs, kyc, quirks) in sorted([c for c in C], key=lambda x: x[6]):
        iso = [c for c in C if c[2] == slug][0][0]
        qs = JP_QUIRKS if iso == "JP" else (quirks or [])
        L += [f"[{iso}]", f"name = {toml_str(name)}", f"slug = {toml_str(slug)}",
              f'flag = "img/flags/{iso.lower()}.svg"', f"region = {toml_str(region)}"]
        if featured:
            L.append("featured = true")
        L.append(f"neighbors = [{', '.join(toml_str(n) for n in nbs)}]")
        L.append("carriers = [" + ", ".join(toml_str(c) for c in carriers) + "]")
        if kyc is not None:
            L.append(f"kyc_required = {str(bool(kyc)).lower()}")
        imgs = [f"{slug}-0{i}.webp" for i in range(1, 5)]
        L.append("images = [" + ", ".join(toml_str(i) for i in imgs) + "]")
        if qs:
            L.append("quirks = [")
            L += [f"  {toml_str(q)}," for q in qs]
            L.append("]")
        L += ["", f"[{iso}.slugs]", f'roami = "{slug}-esim"', ""]
    (DATA / "countries.toml").write_text("\n".join(L), encoding="utf-8")


def write_plans(by_iso):
    header = "# ⚠ SAMPLE data (except JP-Roami) - generated placeholders, verify before launch\n"
    # roami
    L = [header]
    for (iso, name, slug, region, level, *_r) in C:
        st = build_stats(iso, level)
        rng = st["rng"]
        checked = "2026-09-28" if iso == "JP" else rng.choice(CHECKED_DATES)
        carriers = [c for c in C if c[0] == iso][0][7]
        L += [f"[{iso}]", f'checked = "{checked}"', "networks = [" + ", ".join(toml_str(c) for c in carriers) + "]", ""]
        rows = ROAMI_JP_REAL["plans"] if iso == "JP" else scale(ROAMI_LADDER, level)
        for (n, gb, d, t, p, f) in rows:
            L += [f'[[{iso}.plans]]', f"name = {toml_str(n)}", f"gb = {gb}", f"days = {d}",
                  f'type = "{t}"', f"price = {p:.2f}"]
            if f:
                L.append(f"fup_note = {toml_str(f)}")
            L.append("")
        L.append("")
    (DATA / "plans" / "roami.toml").write_text("\n".join(L), encoding="utf-8")

    for key, ladder, mult in (("airalo", AIRALO_LADDER, 1.10), ("saily", SAILY_LADDER, 0.95), ("nomad", NOMAD_LADDER, 1.0)):
        L = [header]
        for (iso, name, slug, region, level, *_r) in C:
            rng = rng_for(iso + key)
            checked = rng.choice(CHECKED_DATES)
            carriers = [c for c in C if c[0] == iso][0][7]
            L += [f"[{iso}]", f'checked = "{checked}"', "networks = [" + ", ".join(toml_str(c) for c in carriers) + "]", ""]
            for (n, gb, d, t, p, f) in scale(ladder, level * mult):
                L += [f"[[{iso}.plans]]", f"name = {toml_str(n)}", f"gb = {gb}", f"days = {d}",
                      f'type = "{t}"', f"price = {p:.2f}", ""]
            L.append("")
        (DATA / "plans" / f"{key}.toml").write_text("\n".join(L), encoding="utf-8")

    L = [header]
    for (iso, name, slug, region, level, *_r) in C:
        st = build_stats(iso, level)
        carriers = [c for c in C if c[0] == iso][0][7]
        L += [f"[{iso}]", f'checked = "{st["rng"].choice(CHECKED_DATES)}"',
              "networks = [" + ", ".join(toml_str(c) for c in carriers) + "]", ""]
        for (n, gb, d, t, p, f) in st["provs"]["holafly"]:
            L += [f"[[{iso}.plans]]", f"name = {toml_str(n)}", f"gb = {gb}", f"days = {d}",
                  f'type = "{t}"', f"price = {p:.2f}", f"fup_note = {toml_str(f)}", ""]
        L.append("")
    (DATA / "plans" / "holafly.toml").write_text("\n".join(L), encoding="utf-8")


def write_pages_and_faqs():
    for (iso, name, slug, region, level, featured, weight, carriers, nbs, kyc, quirks) in C:
        if iso == "JP":
            continue
        st = build_stats(iso, level)
        ch, val, unl = st["cheapest"], st["value"], st["unl"]
        desc = (f"Every {name} eSIM plan compared: {len(st['rows'])} plans from 5 providers ranked by $/GB and $/day, "
                f"with unlimited fair-use limits and {'/'.join(carriers[:2])} coverage decoded. From ${ch['price']:.2f}.")
        paras = analysis_paras(iso, name, st, carriers, (quirks or [""])[0])
        md = ["---", f'title: "{name} eSIM"', f"iso: {iso}", f"weight: {weight}",
              "seo:", f'  description: "{desc}"', "---", ""]
        md += [paras[0], "", paras[1], "", paras[2], ""]
        (CONTENT / f"{slug}.md").write_text("\n".join(md), encoding="utf-8")

        L = [f"# {name} FAQ - generated (review before launch)", ""]
        for q, a in faq_list(iso, name, st, kyc, carriers, [x[1] for x in C if x[0] in nbs]):
            L += ["[[faq]]", f"q = {toml_str(q)}", f"a = {toml_str(a)}", ""]
        (FAQS / f"{iso.lower()}.toml").write_text("\n".join(L), encoding="utf-8")


def distribute_images():
    IMG_OUT.mkdir(parents=True, exist_ok=True)
    SITE_IMG.mkdir(parents=True, exist_ok=True)
    pool = sorted(POOL.glob("travel-esim-illustration-*.webp"))
    assert len(pool) == POOL_SIZE, f"pool size {len(pool)} != {POOL_SIZE}"
    for i, (iso, name, slug, *_r) in enumerate(C):
        h = int(hashlib.md5(slug.encode()).hexdigest()[:6], 16)
        picks = [(h + off) % POOL_SIZE for off in (0, 31, 67, 103)]
        for j, p in enumerate(picks, 1):
            dst = IMG_OUT / f"{slug}-0{j}.webp"
            if not dst.exists():
                shutil.copy2(pool[p], dst)
    shutil.copy2(pool[(7) % POOL_SIZE], SITE_IMG / "home-hero.webp")
    shutil.copy2(pool[(41) % POOL_SIZE], SITE_IMG / "og-default.webp")


def write_provider_pages():
    """品牌×国家子页 content/en/compare/<slug>/<provider>.md — 正文为空，全部由模板层推导。
    描述数字直接读 data/plans/*.toml（刚由 write_plans 生成 / JP 为真实数据）→ 单一事实源。"""
    import tomllib
    plans = {f.stem: tomllib.loads(f.read_text(encoding="utf-8"))
             for f in sorted((DATA / "plans").glob("*.toml"))}
    # 品牌名单/名称从 plans 文件名 + providers.toml 解析（避免硬编码两份）
    prov_names = {}
    _key = None
    for line in (DATA / "providers.toml").read_text(encoding="utf-8").splitlines():
        if line.startswith("[") and line.endswith("]"):
            _key = line[1:-1]
        elif line.startswith("name = ") and _key:
            prov_names[_key] = line.split('"')[1]
    n_prov = len(plans)

    for (iso, name, slug, *_r) in C:
        # 每品牌最优 $/GB（无限量套餐按 +inf 排最后）→ 全场排名
        best = {}
        for pk, pdata in plans.items():
            c = pdata.get(iso)
            if not c:
                continue
            pgb = [pl["price"] / pl["gb"] for pl in c["plans"] if pl["gb"] > 0]
            best[pk] = min(pgb) if pgb else float("inf")
        ranked = sorted(best, key=lambda k: best[k])
        n_all = sum(len(pdata[iso]["plans"]) for pk, pdata in plans.items() if iso in pdata)

        for pk in sorted(plans):
            c = plans[pk].get(iso)
            if not c:
                continue
            my = c["plans"]
            pname = prov_names.get(pk, pk.title())
            from_price = min(pl["price"] for pl in my)
            metered = [pl for pl in my if pl["gb"] > 0]
            unl = [pl for pl in my if pl["gb"] == 0]
            rank = ranked.index(pk) + 1
            if metered:
                bpgb = min(pl["price"] / pl["gb"] for pl in metered)
                desc = (f"{pname} eSIM plans for {name}: {len(my)} plans from ${from_price:.2f}, "
                        f"best ${bpgb:.2f}/GB (#{rank} of {n_prov} providers), fair-use decoded — "
                        f"benchmarked against all {n_all} {name} eSIMs we track.")
            else:
                bday = min(pl["price"] / pl["days"] for pl in unl)
                desc = (f"{pname} eSIM for {name}: {len(my)} unlimited plans from ${bday:.2f}/day, "
                        f"fair-use caps decoded — benchmarked against all {n_all} {name} eSIMs we track.")
            md = ["---",
                  f'title: "{pname} {name} eSIM Plans & Prices"',
                  f"iso: {iso}",
                  f"provider: {pk}",
                  "layout: provider",
                  "seo:",
                  f'  description: "{desc}"',
                  "---", ""]
            d = CONTENT / slug
            d.mkdir(parents=True, exist_ok=True)
            (d / f"{pk}.md").write_text("\n".join(md), encoding="utf-8")
    n_sub = sum(1 for _ in CONTENT.glob("*/*.md"))
    print(f"OK: {n_sub} provider×country sub-pages written.")


def main():
    by_iso = {c[0]: c for c in C}
    assert len(C) == 50, f"{len(C)} countries, want 50"
    isos = {c[0] for c in C}
    for c in C:
        for n in c[8]:
            assert n in isos, f"{c[0]} neighbor {n} not in set"
    write_countries_toml(by_iso)
    write_plans(by_iso)
    write_pages_and_faqs()
    write_provider_pages()
    distribute_images()
    n_pages = len(list(CONTENT.glob('*.md'))) - 1  # minus _index
    print(f"OK: 50 countries in countries.toml, plans x5, {n_pages} compare pages, "
          f"{len(list(FAQS.glob('*.toml')))} faq files, images distributed.")


if __name__ == "__main__":
    main()
