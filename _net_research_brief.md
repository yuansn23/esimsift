# eSIM network-partner research brief (P0)

You are researching which **mobile network operator (MNO)** each eSIM brand actually runs on, per country, for the eSIM Sift comparison site.

## Why
The site compares 8 eSIM brands across 50 countries. The one missing data field is `networks` — which real carrier each brand's eSIM rides on in a given country. This is the transparency differentiator (competitors don't show it). It MUST be real, not guessed.

## Input data
Read this file (UTF-8 JSON): `D:\HUGO test\29.1_windows-amd64\hugo_0.159.1_windows-amd64\esimsift\_net_agent_input.json`

It lists 50 countries as `{"iso","name","slug","carriers":[...]}`. The `carriers` array is the **canonical set of MNO names** for that country (e.g. JP -> ["NTT Docomo","SoftBank","KDDI"]).

## Your assigned brands
See your task prompt (the agent tells you which brands).

## Research method
For EACH assigned brand, find which MNO(s) the brand uses in EACH of the 50 countries. Use WebSearch and WebFetch. Best sources, in order of trust:
1. The brand's own official coverage / "supported networks" page (e.g. Airalo country page, Ubigi coverage page, Saily coverage, Holafly coverage, the brand's FAQ).
2. A well-known comparison site that lists the network per country (eSIMDB, esims.io) — only when it agrees with the brand's own page.

Roami = roamiapp.com. Roamic = roamic.com (different company — do not confuse).

## HARD RULES — do not fabricate
1. Only record a network you actually saw published for that brand + that country. Never infer from neighbouring countries, never reuse one country's answer for another.
2. The network name you record MUST match one of the names in that country's `carriers` array (case-insensitive, ignore punctuation/whitespace). E.g. if the brand says "Vodafone" and carriers has "Vodafone" -> ok. If the brand uses a network NOT in the `carriers` array, do NOT add it to `networks`; instead put a note in `notes`.
3. If you cannot find a verified network for a country, LEAVE IT OUT entirely. Empty is correct and safe. Do not fill to look complete.
4. Record the one source URL you relied on per brand in `source_url` (and per-country URLs in `sources` if they differ).

## Output
Write ONE JSON file per brand to:
`D:\HUGO test\29.1_windows-amd64\hugo_0.159.1_windows-amd64\esimsift\_net_results\<brand>.json`

Schema (use the brand's lowercase key: airalo, saily, ubigi, holafly, yesim, alosim, roami, roamic):
```json
{
  "brand": "airalo",
  "source_url": "https://www.airalo.com/coverage",
  "networks": { "JP": ["NTT Docomo","SoftBank"], "US": ["T-Mobile"] },
  "notes": { "GB": "brand lists 'EE' and 'O2'; only 'EE' is in carriers" },
  "sources": { "JP": "https://...", "US": "https://..." }
}
```
- `networks`: iso -> array of matched carrier names (only names present in that country's `carriers`).
- `notes`: iso -> string, only where something needs explaining.
- `sources`: optional iso -> URL.

Use the Write tool (UTF-8) to write these files. Then reply with a short summary: per brand, how many of the 50 countries you filled, and the brand's source_url.
