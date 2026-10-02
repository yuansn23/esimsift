#!/usr/bin/env python3
"""Append [ISO.info] (cities + per-carrier strong/weak) blocks to data/carriers.toml.
Idempotent: refuses to append twice (checks for a marker)."""
from pathlib import Path

CITIES = {
    "AE": ["Dubai", "Abu Dhabi", "Sharjah"],
    "AR": ["Buenos Aires", "Cordoba", "Rosario"],
    "AT": ["Vienna", "Graz", "Salzburg"],
    "AU": ["Sydney", "Melbourne", "Brisbane", "Perth"],
    "BE": ["Brussels", "Antwerp", "Ghent"],
    "BR": ["Sao Paulo", "Rio de Janeiro", "Brasilia"],
    "CA": ["Toronto", "Vancouver", "Montreal", "Calgary"],
    "CH": ["Zurich", "Geneva", "Basel"],
    "CN": ["Beijing", "Shanghai", "Guangzhou", "Shenzhen"],
    "CO": ["Bogota", "Medellin", "Cartagena"],
    "CR": ["San Jose", "Liberia", "Limon"],
    "CZ": ["Prague", "Brno", "Ostrava"],
    "DE": ["Berlin", "Munich", "Hamburg", "Frankfurt"],
    "EG": ["Cairo", "Alexandria", "Sharm El Sheikh"],
    "ES": ["Madrid", "Barcelona", "Valencia", "Seville"],
    "FJ": ["Suva", "Nadi", "Lautoka"],
    "FR": ["Paris", "Marseille", "Lyon", "Nice"],
    "GB": ["London", "Manchester", "Birmingham", "Edinburgh"],
    "GE": ["Tbilisi", "Batumi", "Kutaisi"],
    "GR": ["Athens", "Thessaloniki", "Heraklion"],
    "HK": ["Central", "Kowloon", "Sha Tin"],
    "HR": ["Zagreb", "Split", "Dubrovnik"],
    "ID": ["Jakarta", "Surabaya", "Denpasar (Bali)"],
    "IE": ["Dublin", "Cork", "Galway"],
    "IL": ["Tel Aviv", "Jerusalem", "Haifa"],
    "IN": ["Mumbai", "Delhi", "Bangalore", "Chennai"],
    "IS": ["Reykjavik", "Akureyri", "Keflavik"],
    "IT": ["Rome", "Milan", "Naples", "Florence"],
    "JP": ["Tokyo", "Osaka", "Kyoto", "Fukuoka"],
    "KE": ["Nairobi", "Mombasa", "Kisumu"],
    "KR": ["Seoul", "Busan", "Incheon"],
    "MA": ["Casablanca", "Marrakesh", "Rabat"],
    "MO": ["Macau Peninsula", "Cotai", "Taipa"],
    "MX": ["Mexico City", "Cancun", "Guadalajara", "Monterrey"],
    "MY": ["Kuala Lumpur", "George Town", "Johor Bahru"],
    "NL": ["Amsterdam", "Rotterdam", "The Hague"],
    "NZ": ["Auckland", "Wellington", "Christchurch", "Queenstown"],
    "PE": ["Lima", "Cusco", "Arequipa"],
    "PH": ["Manila", "Cebu City", "Davao City"],
    "PL": ["Warsaw", "Krakow", "Gdansk"],
    "PT": ["Lisbon", "Porto", "Faro (Algarve)"],
    "QA": ["Doha", "Al Rayyan", "Al Wakrah"],
    "SA": ["Riyadh", "Jeddah", "Dammam"],
    "SG": ["Orchard Road", "Marina Bay", "Changi"],
    "TH": ["Bangkok", "Chiang Mai", "Phuket", "Pattaya"],
    "TR": ["Istanbul", "Ankara", "Izmir", "Antalya"],
    "TW": ["Taipei", "Kaohsiung", "Taichung"],
    "US": ["New York", "Los Angeles", "Chicago", "Miami"],
    "VN": ["Hanoi", "Ho Chi Minh City", "Da Nang"],
    "ZA": ["Johannesburg", "Cape Town", "Durban"],
}

DETAIL = {
    "US": [
        ("Verizon", "The widest rural footprint - the safest pick for road trips, national parks and interstate driving.", "Mid-city and indoor speeds can trail T-Mobile in dense downtowns."),
        ("AT&T", "Consistent middle ground - strong in the South and Midwest, solid at stadiums and venues.", "The rural West still trails Verizon outside towns."),
        ("T-Mobile", "Fastest 5G in city centers and excellent indoor coverage in metros.", "Rural stretches between cities can drop to slower layers."),
    ],
    "GB": [
        ("EE", "The coverage and speed leader - best rural reach and the fastest 5G.", "Usually slightly pricier on consumer tariffs."),
        ("Vodafone", "Solid nationwide reach with strong indoor 5G in cities.", "A few notched spots in the Highlands and rural Wales."),
        ("O2", "Reliable urban coverage, strong in London.", "Rural and motorway speeds trail EE."),
        ("Three", "Generous unlimited tariffs and improving city 5G.", "Weakest rural coverage of the four - check before countryside trips."),
    ],
    "JP": [
        ("NTT Docomo", "The widest coverage in Japan - the safest network for rural areas, mountains and islands.", "Congestion can slow it at peak times in Tokyo."),
        ("KDDI", "Nationwide reach close to Docomo with fast city service.", "Slightly thinner in a few remote island areas."),
        ("SoftBank", "Fast urban 5G and solid metro coverage.", "Rural and mountain coverage trails Docomo."),
    ],
    "DE": [
        ("Telekom", "The benchmark network - best rural reach and the most consistent speeds.", "Plans tend to cost a little more."),
        ("Vodafone", "Strong city 5G and improving rural LTE.", "Villages in central Germany still favor Telekom."),
        ("O2", "Aggressive pricing and solid urban coverage.", "Rural coverage and indoor depth trail the big two."),
    ],
    "FR": [
        ("Orange", "The best network in France - the coverage leader in rural areas and on motorways.", "Typically the priciest consumer tariffs."),
        ("SFR", "Good urban speeds and solid bundles.", "Rural coverage trails Orange in the southwest and mountains."),
        ("Bouygues", "Reliable city coverage with improving 5G.", "A step behind Orange outside towns."),
    ],
    "IT": [
        ("TIM", "The coverage leader - safest for rural Italy, the Alps and small towns.", "Urban peak speeds can trail Vodafone."),
        ("Vodafone", "Fast city 5G, strong in Milan and the north.", "The rural south and mountains favor TIM."),
        ("WindTre", "Best-value tariffs with good urban coverage.", "The thinnest rural coverage of the three."),
    ],
    "ES": [
        ("Movistar", "The widest and fastest network in Spain - the safe pick everywhere including rural areas.", "Usually the most expensive."),
        ("Vodafone", "Strong city 5G and good motorway coverage.", "Small villages favor Movistar."),
        ("Orange", "Solid urban and coastal coverage.", "The rural interior trails Movistar."),
        ("Yoigo", "Cheapest tariffs with fast city 5G.", "The smallest footprint - weakest rural coverage."),
    ],
    "CA": [
        ("Bell", "Co-leading coverage with Telus - strong in the East and on remote routes.", "Plans are premium-priced."),
        ("Rogers", "Best urban density and strong around Toronto and the West.", "The far North and long rural highways favor Bell/Telus."),
        ("Telus", "Co-leader in the West with Bell, fast 5G in Vancouver and Calgary.", "Eastern coverage rides on the Bell network."),
    ],
    "AU": [
        ("Telstra", "The coverage benchmark - the only real option for the Outback and long rural drives.", "Pricier than rivals."),
        ("Optus", "Strong metros and good regional coverage, often cheaper.", "The remote interior favors Telstra."),
        ("Vodafone", "Cheap city plans with decent metro 5G.", "The weakest regional coverage - avoid for road trips."),
    ],
    "TH": [
        ("AIS", "The biggest network in Thailand - the best coverage including islands and the north.", "Slightly pricier."),
        ("True Move", "Fast 5G in Bangkok and strong urban coverage.", "Rural and island coverage trails AIS."),
        ("DTAC", "Good value with solid city coverage.", "The thinnest rural reach of the three."),
    ],
    "TR": [
        ("Turkcell", "The coverage and speed leader nationwide.", "Nothing major."),
        ("Vodafone", "Good urban coverage in Istanbul and along the coast.", "Rural Anatolia favors Turkcell."),
        ("Turk Telekom", "Improving fast and strong value in cities.", "Coverage still trails Turkcell outside metros."),
    ],
    "AE": [
        ("Etisalat", "The strongest network in the UAE - best indoor coverage in malls, towers and the metro.", "Nothing major."),
        ("du", "Excellent city coverage, often keener prices.", "A small step behind Etisalat indoors."),
    ],
    "MX": [
        ("Telcel", "The national leader - by far the best coverage outside the big cities.", "Nothing major."),
        ("AT&T Mexico", "Fast 4G/5G in cities and tourist zones.", "Rural coverage trails Telcel by a wide margin."),
        ("Movistar", "Cheap tariffs, fine in big cities.", "The smallest network - avoid for road trips."),
    ],
    "KR": [
        ("SK Telecom", "The largest network in Korea - fastest 5G and the best coverage.", "Nothing major."),
        ("KT", "A close second with excellent Seoul and metro coverage.", "Marginally thinner in remote areas."),
        ("LG U+", "Good value and fast urban 5G.", "A slightly smaller footprint."),
    ],
    "IN": [
        ("Jio", "The largest 5G network in India - the best coverage and generous unlimited offers.", "Peak-time congestion in dense areas."),
        ("Airtel", "Strong network quality and fast city 5G.", "Rural reach trails Jio slightly."),
    ],
    "SG": [
        ("Singtel", "The strongest and fastest network with full MRT coverage.", "Nothing major."),
        ("StarHub", "Close to Singtel in speed and coverage.", "Marginally behind indoors in some towers."),
        ("M1", "Good value with solid coverage.", "A slight step behind in deep-indoor spots."),
    ],
    "CH": [
        ("Swisscom", "The benchmark - the best Alpine and rural coverage, fastest everywhere.", "The priciest."),
        ("Sunrise", "Strong 5G and good mountain coverage.", "High valleys favor Swisscom."),
        ("Salt", "The cheapest plans, fine in cities.", "The smallest coverage footprint."),
    ],
    "NL": [
        ("KPN", "The quality leader - the best coverage including rural provinces.", "Slightly pricier."),
        ("Vodafone", "Strong urban 5G with good bundles.", "Marginally behind KPN outside cities."),
        ("Odido", "Aggressive pricing with solid city coverage.", "Indoor and rural depth trails KPN."),
    ],
}


def q(s: str) -> str:
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def main() -> None:
    p = Path(__file__).resolve().parents[1] / "data" / "carriers.toml"
    text = p.read_text(encoding="utf-8")
    if "[US.info]" in text:
        print("info blocks already present - nothing appended")
        return
    lines = [
        "",
        "# --- [ISO.info] major cities + per-carrier detail (added 2026-09-30) ---",
        "# cities = top metros every national network covers at full speed;",
        "# detail[].carrier must match the profile name; strong/weak are editorial",
        "# typicals (hedge wording), to be verified per market during P-A.",
        "",
    ]
    for iso in sorted(CITIES):
        lines.append(f"[{iso}.info]")
        lines.append("cities = [" + ", ".join(q(c) for c in CITIES[iso]) + "]")
        for carrier, strong, weak in DETAIL.get(iso, []):
            lines.append("")
            lines.append(f"[[{iso}.info.detail]]")
            lines.append(f"carrier = {q(carrier)}")
            lines.append(f"strong = {q(strong)}")
            lines.append(f"weak = {q(weak)}")
        lines.append("")
    with p.open("a", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines))
    print(f"appended: {len(CITIES)} country info blocks, "
          f"{sum(len(v) for v in DETAIL.values())} carrier detail entries")


if __name__ == "__main__":
    main()
