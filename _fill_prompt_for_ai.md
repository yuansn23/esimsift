# 提示词（直接复制下面整段发给 AI）

```

你是 eSIM 行业数据助手。请帮我补齐一份「7 家 eSIM 品牌 × 50 国，各自连接哪些本地运营商」的清单。

品牌：airalo、saily、ubigi、holafly、yesim、alosim、roamic（共 7 家）。

【运营商名称约束 —— 最重要】
每个国家只能用下面列出的规范名，一个字都不能改，不得自造、不得翻译、不得用缩写或俗称：
AR Argentina = Personal, Claro, Movistar
AU Australia = Telstra, Optus, Vodafone
AT Austria = A1, Magenta, Drei
BE Belgium = Proximus, Orange, Base
BR Brazil = Vivo, Claro, TIM
CA Canada = Bell, Rogers, Telus
CN China = China Mobile, China Unicom, China Telecom
CO Colombia = Claro, Movistar, Tigo
CR Costa Rica = Kolbi, Claro, Movistar
HR Croatia = Hrvatski Telekom, A1 Hrvatska
CZ Czechia = O2, T-Mobile, Vodafone
EG Egypt = Vodafone Egypt, Orange Egypt, Etisalat Misr
FJ Fiji = Vodafone Fiji, Digicel Fiji
FR France = Orange, SFR, Bouygues
GE Georgia = Magti, Silknet, Beeline
DE Germany = Telekom, Vodafone, O2
GR Greece = Cosmote, Vodafone, Wind
HK Hong Kong = CSL, 3HK, SmarTone
IS Iceland = Siminn, Vodafone, Noa
IN India = Jio, Airtel
ID Indonesia = Telkomsel, Indosat, XL Axiata
IE Ireland = Vodafone, Three, Eir
IL Israel = Cellcom, Partner, Pelephone
IT Italy = TIM, Vodafone, WindTre
JP Japan = NTT Docomo, SoftBank, KDDI
KE Kenya = Safaricom, Airtel Kenya, Telkom Kenya
MO Macao = CTM, 3 Macau, China Telecom
MY Malaysia = Maxis, Celcom, DiGi
MX Mexico = Telcel, AT&T Mexico, Movistar
MA Morocco = Maroc Telecom, Orange Maroc, Inwi
NL Netherlands = KPN, Vodafone, Odido
NZ New Zealand = Spark, One NZ, 2degrees
PE Peru = Claro, Movistar, Entel
PH Philippines = Globe, Smart
PL Poland = Orange, Play, Plus, T-Mobile
PT Portugal = MEO, NOS, Vodafone
QA Qatar = Ooredoo, Vodafone Qatar
SA Saudi Arabia = STC, Mobily, Zain
SG Singapore = Singtel, StarHub, M1
ZA South Africa = Vodacom, MTN, Telkom
KR South Korea = SK Telecom, KT, LG U+
ES Spain = Movistar, Vodafone, Orange, Yoigo
CH Switzerland = Swisscom, Sunrise, Salt
TW Taiwan = Chunghwa Telecom, Taiwan Mobile, FarEasTone
TH Thailand = AIS, True Move, DTAC
TR Turkiye = Turkcell, Vodafone, Turk Telekom
AE United Arab Emirates = Etisalat, du
GB United Kingdom = EE, Vodafone, O2, Three
US United States = T-Mobile, AT&T, Verizon
VN Vietnam = Viettel, Vinaphone, Mobifone
【输出格式】
每个品牌一个区块，标题写 `### {品牌}`；区块内每国一行：`- {ISO} {国家名}: {运营商1;运营商2}`，多个用英文分号 `;` 分隔。
示例：
### airalo
- JP Japan: NTT Docomo;SoftBank
- US United States: T-Mobile;AT&T
- CN China: 
【纪律】
1. 只填你能核实的（优先查各品牌官网对应国家页的 host networks；查不到就依据可靠常识，但绝不能瞎猜）。
2. 拿不准的国家/品牌，整行留空（`- CN China: ` 冒号后什么都不写），严禁编造运营商名。
3. 全部 50 国 × 7 家都要输出，不确定的留空即可，不要省略行。
现在开始，输出完整清单。

```


（上面的规范名表共 50 国，已包含全部允许使用的运营商名。）
