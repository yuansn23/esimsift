# 发布前检查清单

> 2026-10-07（第四十九轮）首次成文。被问「可以正式发布吗」时，照这张表跑一遍即可给结论。
> 部署方式：**手动上传 `public/`** —— `public/` 不在 git 里，仓库无任何 CI / 部署配置（PROJECT.md §16）。

---

## 0. 一条命令，但别用管道取退出码

```bash
npm run build     # stamp → build:css → validate → hugo → check:output（九项串在里面）
```

⚠️ `npm run build 2>&1 | tail -40` 之后拿到的 `$?` 是 **`tail` 的退出码**（第四十九轮体检时真的因此误判过一次）。
一律改成：

```bash
npm run build > "$TMP/esim_build.log" 2>&1; code=$?
tail -40 "$TMP/esim_build.log"; echo "EXIT=$code"
```

判断前面各项是否也过了，有个省事的推理：npm script 是 `&&` 串联，**最后一项跑到了就说明前面都没中断**。

---

## 1. 九项校验（`build` 内）

| 脚本 | 通过线 | 2026-10-07 实测 |
|:---|:---|:---|
| `validate.py` | 0 error / 0 warning | ✅ |
| `check_css_sync.py` | 模板 class 全部在编译 CSS 里 | ✅ 526 classes |
| `check_i18n.py` | en/de key 逐一对齐、模板无新增硬编码 | ✅ en 1145 key，引用 1128，未定义 0 |
| `hugo` | 构建成功 | ✅ 704 files / 702 pages |
| `check_output.py` | 无格式串泄漏 / 无模板残留 / JSON-LD 合法 | ✅ 4028 JSON-LD |
| `check_headings.py` | h2/h3 无 `, ; : — –` | ✅ bad 0 |
| `verify_provider_pages.py` | 品牌×国家子页 13 项 | ✅ 499/499 |
| `check_faq_facts.py` | FAQ 数字与 `data/plans` 对账 + R10/R11 反重复 | ✅ 499/499 |
| `check_dates.py` | 产物域名 + 日期口径 + sitemap 完整性 | ✅ 644 URL |
| `verify_no_regression.py` | A 标记隔离 / B 全站不变量 / C gb 哨兵 | ✅ |

## 2. `build` 之外的三项（上线前单独跑）

```bash
python -X utf8 scripts/check_links.py        # 全站死链
python -X utf8 scripts/audit_meta.py         # title/description 去重与长度
python -X utf8 scripts/verify_external_refs.py --data-only   # 外链与运营商 1:1（网络版可直接扫，但别进 build）
```

| 脚本 | 通过线 | 2026-10-07 实测 |
|:---|:---|:---|
| `check_links.py` | 坏链 0 | ✅ 187,316 href / 0 坏链 |
| `audit_meta.py` | 无重复；长度为 WARN 级 | ✅ EXIT=0（provider-sub title 47<48、德语页 desc 145–169>140 均为 WARN） |
| `verify_external_refs.py` | `--data-only` 无孤儿 | 按需 |

## 3. 产物卫生（直接 grep 断言）

```bash
grep -rl localhost public/ | wc -l                    # 应为 0（dev server 污染，见 PROJECT.md 红线）
grep -rl "SAMPLE\|TODO\|PLACEHOLDER" public/ | wc -l   # 见下：必须用大写精确匹配
find public -type d -name "*backup*" -o -type d -name ".workbuddy"   # 应为空
```

⚠️ **必须大小写敏感**。2026-10-07 首查用 `-i` 得到 105 个命中，**逐个看下去全是误报**：
`Speedtest samples`（正文里的普通词）、HTML 的 `placeholder=` 属性、小写 `todo`。大写精确匹配 = **0**。

## 4. 可索引性

```bash
grep -c "<loc>" public/sitemap.xml          # sitemap 声明的 URL 数
grep -rl "noindex" content/en/ | wc -l      # 英文站应为 0
grep -rl "draft" content/en/ | wc -l        # 应为 0
```

| 项 | 2026-10-07 状态 |
|:---|:---|
| 英文页 | 643 页，**无 `noindex` / 无 `draft`**，全部在 sitemap |
| 德语站 | 54 页 `noindex`（i18n 未完成，**设计如此**；`de/sitemap.xml` 只有 `/de/` 首页 1 条） |
| `robots.txt` | `Allow: /`，并单独放行 GPTBot / ClaudeBot / PerplexityBot 等 |

## 5. 内容层的「不实陈述」自查（一次性、但值得每次复查）

这两类问题 build 全绿也发现不了，只能靠读产物：

- **面向读者的待办 / 备忘**：编辑注释若写在 Markdown 正文（哪怕用 `_…_` 包着）会被渲染成可见文字。
  统一放 **front matter 注释**，且注释必须落在两个 `---` **之间**（写在外面会被当 Markdown 渲染成 `<h1>` → B 类不变量 FAIL，见 PROJECT.md 红线 59）。
- **文案里的断言要能对上它自己的口径**：第四十九轮发现 `#whobeats` 导语宣称"完全同规格"，
  而匹配判据的三条分支里只有一条真的查了天数 → 页面可见行 35.5% 不符。**判据不变而只改文案，等于把不实陈述写得更圆滑。**

## 6. 部署

```bash
rm -rf public && npm run build     # 干净产物（hugo 不清理旧页；--cleanDestinationDir 会慢 10 倍）
# 然后手动上传 public/ → esimsift.com
```

上线后：

1. GSC 提交 `sitemap.xml`
2. 确认 `llms.txt` / `catalog.json` 可达
3. GA4 核对 campaign（`compare-<slug>` / `vs-<a>-<b>` / `partner`）

---

## 附：本轮的 git 卫生

- 改动**未提交**时先说清楚：`git status --short | wc -l`
- 改完数据 / 模板后基线要重建：`scripts/verify_no_regression.py --diff docs/regression-manifest.json` 看变更面，
  逐条确认归因，再 `--write-manifest`
- `docs/regression-manifest.json` 与 `docs/checked-state.json` **都必须提交**
