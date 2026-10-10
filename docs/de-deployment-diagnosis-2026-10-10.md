# 德语站「线上什么都没有」诊断（第八十轮 · 2026-10-10）

> 用户四问：① `https://www.esimsift.com/de/sitemap.xml` 里为什么没有德语其他页面？
> ② `robots.txt` 为什么没有 `de/sitemap.xml`？③ 底部/顶部菜单很多链接没有 `/de/`？④ 是否还存在其他类似问题？
>
> **本文件所有数字均为当场现算**，命令可复跑。改动仍未 `git commit`、未部署。

---

## 0. 一句话结论

**不是模板坏了，是「提交进 Git 的德语站根本不完整」。**

`content/de/` 在 **HEAD（= 线上正在跑的那个提交）只有 55 个文件**，其中 **54 个带 `noindex: true`**；而工作区有 **644 个**、且 noindex 已全部解禁。三个现象全部由这一个原因派生 —— 线上跑的是「德语只有首页」的旧形态，本地早就是「德语 644 页」的完整形态，只差**提交 + 部署**。

| | 线上（= HEAD 构建） | 本地工作区产物 |
|---|---|---|
| `content/de/` 页数 | **55**（54 个 noindex） | **644**（0 个 noindex） |
| `/de/sitemap.xml` 条目 | **1** | **644** |
| `robots.txt` 的 `Sitemap:` 行 | **1**（只有根） | **2**（根 + `/de/`） |
| de 首页 `<footer>` 里缺 `/de/` 的链接 | **20 条** | **0 条** |
| de 首页 `<header>` 里缺 `/de/` 的链接 | **10 条** | **2 条**（都是语言切换器，**理应**指英语） |
| 英语侧 `/sitemap.xml` 路径集合 | **644 条，与本地逐条一致（差集 0）** | **644 条** |

---

## 1. 决定性证据链：线上确实是 HEAD 的构建

| 判据 | 线上实测 | HEAD 的源码 | 一致？ |
|---|---|---|---|
| `/sitemap.xml` 条目 | **644** | `content/en/*.md` = **644** | ✅ |
| `/de/sitemap.xml` 条目 | **1** | `content/de/*.md` 55 个 − 54 个 noindex = **1** | ✅ |
| `robots.txt` 的 `Sitemap:` 行数 | **1** | `git show HEAD:layouts/robots.txt` → **1 行** | ✅ |
| `/compare/matchups/` 是否含 `ItemList` / `FAQPage` | **0 / 0** | `git show HEAD:…matchups.html` → **0 / 0** | ✅ |
| `/de/` 首页 footeren 里带 `/de/` 的链接 | 8 条（`/de/compare/united-states/`…`/de/guides/`、`/de/research/`） | 这 3 类德语页在 HEAD **正好存在** | ✅ |
| `/de/` 首页 footer 里不带 `/de/` 的链接 | 20 条（`/about/`、`/esim-providers/…`、`/compare/matchups/`…） | 这 20 类德语页在 HEAD **正好不存在** | ✅ |

⇒ **部署管线是好的**（push → 构建 → 上线），问题纯粹是 **HEAD 里没有那些德语页**。

---

## 2. 逐条答复

### ① `/de/sitemap.xml` 为什么只有 1 条 —— 德语页从未提交

```
content/de  :: HEAD = 55，工作区 = 644（差 +589）
   (根)              HEAD   1   工作区   7
   compare           HEAD  51   工作区 596
   esim-deals        HEAD   0   工作区   1
   esim-providers    HEAD   0   工作区  11
   guides            HEAD   1   工作区  11
   networks          HEAD   1   工作区  13
   research          HEAD   1   工作区   4
   tools             HEAD   0   工作区   1

德语「新增未提交」= 589   Counter({'compare': 545, 'networks': 12, 'esim-providers': 11,
                                  'guides': 10, '(根)': 6, 'research': 3,
                                  'esim-deals': 1, 'tools': 1})
德语「改过（删 noindex）」= 54
```

**两层叠加**才造成「1 条」：

1. `content/de/` 只有 55 个文件就已被提交（`/de/` 首页 + 54 个国家页占位 + 3 个 section `_index`）；
2. 这 54 个占位页 front matter 里都写着 `noindex: true`，而 `layouts/partials/sitemap-urls.html:36` 的判据是
   `{{- if not .Params.noindex -}}` ⇒ **noindex 页不进 sitemap**（设计如此，避免 GSC 报 *Submitted URL marked 'noindex'*）。

⇒ 55 − 54 = **1**（只剩 `/de/` 首页）。

**本地早已不是这个状态**：54 个 `noindex:` 行**已全部删除**（`git diff HEAD -- content/de | grep -c '^-noindex'` = **54**），
产物实测 **645 个德语 HTML 里 0 个带 robots meta**，`public/de/sitemap.xml` = **644 条**。
`content/en` 与 `content/de` 现在是 **644 : 644，页面型 636 : 636，零缺失**。

### ② `robots.txt` 为什么没有 `de/sitemap.xml`

```diff
- HEAD（= 线上）:              Sitemap: {{ .Site.BaseURL }}sitemap.xml          ← 只有 1 行
+ 工作区（未提交）:            Sitemap: {{ .Site.BaseURL }}sitemap.xml
+                             Sitemap: {{ .Site.BaseURL }}de/sitemap.xml       ← 第 2 行是后来加的
```

内容本身没问题，**只是这一行还没提交**。

> ⚠ 另外：本地 `public/robots.txt` 现在写的是 `Sitemap: http://localhost:1313/…` —— 见 §4。

### ③ footer / header 为什么很多链接没有 `/de/` —— `lang-href.html` 的三层兜底

`layouts/partials/lang-href.html` 是「语言感知的安全版 `relLangURL`」，**三层兜底**：

| 层 | 条件 | 返回值 | 德语页上的结果 |
|---|---|---|---|
| 1 | 当前语言（de）有该页 | `.RelPermalink` | `/de/about/` ✅ |
| 2 | **别的语言**有该页 | 那个语言的 `.RelPermalink` | **`/about/`（英语 URL，没有 `/de/`）** ⚠ |
| 3 | 谁都没有 | `relURL(原路径)` | `/about/` |

所以「德语页缺失」不会变成 404，而是**静默退化成英语 URL** —— 这正好是你看到的形态：
线上德语站只有首页有内容 ⇒ 页脚/导航里 30 条指向「德语侧还没建」的链接全部退化成英语路径。

**本地实测（644 个德语页齐全）**：德语页里指回英语路径的站内链接 **只有语言切换器**：
645 × `/`（锚文本 `en`）+ 每页 1 条指向对应英语页的 `English` —— 两者**本来就该指英语**。
`<header>`/`<footer>` 里真正越界的链接 = **0**。守卫 `scripts/_de_link_leak_audit.py` 也全绿：

```
[规模] de 页 645
[1] ★ 语言泄漏（HTML，硬判据）：0 处 / 0 页
[2] ★ 畸形 href（硬判据）：0 处 / 0 页
[3] ★ 非 HTML 产物语言泄漏（硬判据）：0 处 / 0 个文件
[结论] 全绿
```

⇒ **这三个现象是同一个原因的三个投影**，不是三处独立 bug。

### ④ 是否还有其他类似问题 —— 已全量扫过，另有 1 个真问题（在本地，不在线上）

| 面 | 判据 | 结果 |
|---|---|---|
| 德语页 → 英语路径的站内链接（全站、全链接、不限 header/footer） | 逐页提取 `<a href>`，剔除外链/资源/锚点 | **646 种 / 1290 处，100% 是语言切换器**；越界 **0** |
| `_de_link_leak_audit.py` [1][2][3] | 语言泄漏 / 畸形 href / 非 HTML 产物 | **0 / 0 / 0** |
| `check_hreflang.py` | 自指、互指、noindex 页不发、目标存在 | **OK：1291 页 / 3864 tags / 1288 页** |
| 德语页 `<html lang>` | 645 页 | `lang="de"` **645/645** |
| 德语页 `canonical` / `og:url` 路径 | 645 页 | `/de/…` **645/645** |
| `content/en` vs `content/de` 页数 | 页面型 | **636 : 636，零缺失** |
| **本地 `public/` 是否可上线** | `check_dates.py` 断言 A | **✗ 1315 个文件含 `localhost` ‹真问题，见 §4›** |

**结论：SEO 面没有其他同类泄漏。** 唯一的真问题在本地产物（§4）。

---

## 3. 最小修复路径（一步到位）

**三个现象共用同一个修复动作：把德语站提交并推送。**

```bash
cd D:/esimsift/esimsift
git add -A                      # 589 个新德语页 + 54 个改过的 + layouts/ + i18n/ + data/ + docs/
git status --short | wc -l      # 复核规模
git commit -m "de: 全量德语站（644 页）+ robots de sitemap + 导航收窄"
git push origin main            # 触发部署
```

> `.gitignore` 已排除 `.buildlog/`、`public/`、`_competitors/`、`_net_results/`、`docs/internal/`、`__pycache__/`，
> 不会被误提交（四类目录的 `git ls-files` 计数均为 **0**）。

**部署后按这 4 条复核（各一条命令）**：

```bash
curl -s https://www.esimsift.com/de/sitemap.xml | grep -c '<loc>'          # 期望 644
curl -s https://www.esimsift.com/robots.txt    | grep -ci '^Sitemap:'      # 期望 2
curl -s https://www.esimsift.com/de/ | grep -o 'href="/de/about/"' | wc -l # 期望 ≥1
curl -sI https://www.esimsift.com/de/compare/france/ | head -1             # 期望 200
```

---

## 4. ★ 另一处真问题：本地 `public/` 被 `localhost` 污染（1315 个文件）

| 项 | 实测 |
|---|---|
| `public/` 里含 `localhost` 的文件 | **1315**（细分：`.html` 1291 / `.xml` 19 / `.txt` 3 / `.json` 2） |
| 这些文件的 mtime | **10-10 22:19–22:21**（在最后一次 `npm run build` **之后**） |
| 直接后果 | `public/sitemap.xml` 的 644 个 `<loc>` 全是 `http://localhost:1313/…`；`public/robots.txt` 写成 `Sitemap: http://localhost:1313/sitemap.xml` |

守卫已明确报出来（`python -X utf8 scripts/check_dates.py`）：

```
[A] 1315 个产物含 localhost —— 本地 hugo server 的 baseURL 泄漏进了 public/
    （重新跑 npm run build 即可修复）：
      · 404.html · catalog.json · index.html · index.xml · llms.txt · robots.txt · sitemap.xml …
[A] sitemap <loc> 与 baseURL 不同源：http://localhost:1313/guides/best-europe-esim/
```

**成因**：手敲了 `hugo server`（不带 `--renderToMemory`）。它会用 `http://localhost:1313/` 覆盖 baseURL **并把整站写进 `public/`**。
这正是 `hugo.toml` 里那段长注释 + 项目红线 9 记过的老坑（此前已污染两次）。

**处置**：本轮已重跑 `npm run build` 恢复（见 §5 复核）。

**纪律重申**：预览一律 `npm run dev`（脚本自带 `--renderToMemory`，**绝不写 `public/`**）；
一旦手敲过 `hugo server`，**必须**再跑一次 `npm run build` 并 `--diff` 确认逐字节回基线。

---

## 5. 本轮复核（构建后实测）

| 判据 | 结果 |
|---|---|
| `npm run build` 退出码 | **`BUILD_EXIT=0`**（hugo `Total in 284855 ms`；`check:output` **12 项全绿**） |
| `public/` 含 `localhost` 的文件数 | **0**（构建前 1315） |
| `public/de/sitemap.xml` 条目 | **644**，主机 **全部 `https://www.esimsift.com`** |
| `public/robots.txt` 的 `Sitemap:` 行 | **2** 行（`/sitemap.xml` + `/de/sitemap.xml`，均 https） |
| `verify_no_regression --diff` | **变更 0 / 新增 0 / 删除 0** —— 与基线（`2026-10-10T14:02:33Z`）**1291 页逐字节相同** ⇒ 重建**精确还原**了第七十九轮验证过的状态 |
| `_de_link_leak_audit.py` | **[1][2][3] = 0 / 0 / 0** |
| `check_hreflang.py` | **OK：1291 页 / 3864 tags / 1288 页** |
| 德语页 `<html lang>` / `canonical` / `og:url` | **645/645** `de` / `/de/…` / `/de/…` |

### ★ 另一条独立证据：英语侧「本地 == 线上」逐条一致

把线上 `/sitemap.xml` **落盘后**解析，与本地重建的 `public/sitemap.xml` 比路径集合：

```
线上根 sitemap 路径 = 644   本地 = 644
差集：本地有线上无 = 0      线上有本地无 = 0
⇒ 英语侧逐条一致 ? True
```

⇒ 线上跑的**就是 HEAD 的构建**，英语侧已是最新 —— 德语侧独缺，正是「德语页未提交」。

---

## 6. 附带发现（未擅自改）

**563 个德语内容文件的 front matter 里留着已经过期的 TODO 注释**：

```yaml
# TODO(de)：正文已德语化。D9 解禁时统一删掉上面 noindex 行。
```

而「上面那行」**早就删掉了**（54 个 `noindex:` 行已全部移除）。注释本身是 YAML 注释、**不进产物**，
所以对读者与 SEO **零影响**，但它会误导后来人（指向一行不存在的东西）。
清理 = 563 个文件各删 1 行、产物**逐字节不变**。

**要不要清？** 你说一声即可（也可留到下次数据生成脚本统一重写时顺带清掉）。

---

## 7. 需要你确认的三件事

1. **提交 + 推送**：这是本轮四问的唯一修复动作（我不代提交 —— 按你的明令）。
2. **`public/` 污染**：确认你**不是**用「上传 `public/` 目录」的方式部署（线上 canonical 是 `https://www.esimsift.com/…`，
   说明部署走的是 Git 构建；但如果哪天改成上传目录，脏的 `public/` 会直接毁站）。
3. **563 条过期 TODO 注释**：清 / 不清。
