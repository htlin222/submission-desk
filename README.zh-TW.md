# 📮 投稿決策台 Submission Desk

*「這篇到底要投哪?」—— 用算術回答,而不是凌晨三點的絕望。*

> English README: [README.md](README.md)

你把論文寫完了。恭喜你這位美麗的災難。接下來是沒人教過你的部分:選期刊,而且不要 (a) 志向遠大到花八個月蒐集拒稿信像在抓寶可夢,也不要 (b) 保守到指導教授露出「那個表情」。

投稿決策台把「要投哪?」從憑感覺擲筊,變成一套**可重現、無聊、卻無比站得住腳的流程**:硬性門檻 → 計分 → 排序梯隊。同樣輸入、同樣答案、每次都一樣。它對你的 h-index 沒有意見。

**[▶ 打開工具](https://submission-desk.pages.dev/zh-TW/)** · **[▶ English version](https://submission-desk.pages.dev/)**

不用 build、不用安裝、不追蹤、不需帳號,也沒有那種「我們重視您的隱私」但其實剛好相反的 cookie 橫幅。一個 HTML 檔、離線可用 —— 反正這種決定大多是在飛機上做的。

---

## 它到底做什麼(全部切成分頁,剛好塞進一張投影片)

1. **門檻** — 五個是非題。錯一項,那本期刊就在用影響因子迷惑你之前先被踢出去。沒得商量,像一位手拿評分表的保鑣。
2. **候選** — 一張可編輯的表:IF、接受率、契合度(1–5)、到首次決議週數、APC。兩種排序模式:*期望產出*(預設,成熟大人的選擇)與*平衡加權*(滑桿,給你需要「掌控感」的時候)。
3. **排序** — 排名梯隊,冠軍蓋上 `→ 投這本` 印章。那個印章非常療癒。老實說,一半的價值就在這。
4. **敏感度 · 權衡 · 模擬 · 對照** — 完整量化四件組:龍捲風圖、Pareto 權衡散點、固定種子的蒙地卡羅(「你的第一名是真的穩,還是只是運氣好?」),以及期望產出對平衡加權的 bump chart。專治簡報進行到第 15 分鐘有人舉手問「那這個有多敏感?」。
5. **流程 + 時程** — 八個固定投稿狀態,加一張可編輯甘特圖與「加一次被拒循環」開關,讓「衝一本高分刊」的真實代價用「週」而不是用樂觀來衡量。

## 你該記住的那一條公式

```
接受機率 = clamp( (接受率/100) × 契合係數 , 0.02 , 0.95 )    契合係數:0.5 0.75 1.0 1.3 1.6 對應契合 1–5
EIM      = 接受機率 × IF / (週數 / 4.345)
```

白話:純粹的影響因子會過度討好那些 (a) 不會收你、又 (b) 拖很久才說不的期刊。除以「到決議的時間」,就是禮貌地請這些期刊坐下。完整推導、參數出處、以及模型「其實在猜」的部分誠實清單:**[docs/METHOD.md](docs/METHOD.md)**。

## 這些是真的,還是你自己編的?

都有!而且 —— 難得地 —— 工具會告訴你哪個是哪個:

- **有真研究撐腰:**契合度優先(Rees 等 2022:重視契合度使首投命中勝算比約*翻倍*,OR 2.11),以及時間折現的期望值(Salinas 與 Munch 2015,他們正經推導出來的指標,被 `EIM` 厚著臉皮簡化)。
- **憑感覺,並在介面上老實標成 `未校準`:**契合係數、乘法形式、clamp 邊界、預設權重。看起來合理、內部一致、但未經校準。你若有能校準它們的資料,那就是這個 repo 能收到最棒的 PR。

證據支持的誠實一句話:**沿著影響因子往下投,損失的引用其實不多,但很花時間、也很傷首投命中率。** 反面證據與參考文獻都在 [docs/METHOD.md](docs/METHOD.md)。

## 執行方式(所謂「困難」的做法,其實不難)

```bash
git clone https://github.com/htlin222/submission-desk.git
cd submission-desk
open index.html        # macOS   ·   xdg-open (Linux)   ·   start (Windows)
```

瀏覽器對本機檔案很龜毛?

```bash
python3 -m http.server 8000   # → http://localhost:8000
```

## 部署你自己的一份 → Cloudflare Pages

這個 repo 內建一條 GitHub Actions 流水線,每次 push 到 `main` 就把網站發佈到 **Cloudflare Pages**。加兩個 repo secret 就上線:

| Secret | 去哪拿 |
|---|---|
| `CLOUDFLARE_API_TOKEN` | Cloudflare 後台 → My Profile → API Tokens → *Create Token* → **「Cloudflare Pages — Edit」**範本 |
| `CLOUDFLARE_ACCOUNT_ID` | Cloudflare 後台 → Workers & Pages → 右側欄的 Account ID |

流水線會在**第一次執行時自動建立 Pages 專案**,你完全不必碰後台的點擊迷宮。到 *Settings → Secrets and variables → Actions* 設好 secret,再重跑 workflow 即可。(同時也附了一份 GitHub Pages 的 workflow,給念舊的人。)

## 不靠猜也能填表

五欄裡有兩欄可以來自 Crossref,而不是你的想像力:

```bash
python3 tools/crossref_index.py --issn 1741-7015 2045-2322 --mailto you@uni.edu -o data/snapshots/mine.json
```

然後在工具裡按 **匯入 Crossref 快照**。本機讀取、不連網、不儲存。接受率、APC、契合度仍要手填,因為宇宙就是不肯讓它們變簡單。詳情:**[docs/CROSSREF.md](docs/CROSSREF.md)**。

## 引用 · 貢獻 · 授權

- **引用:**有一份 [CITATION.cff](CITATION.cff)(GitHub 會渲染出「Cite this repository」按鈕)。但任何實質論點,請直接引用*那些真正的論文* —— 工作是他們做的。
- **貢獻:**校準資料勝過一切。翻譯、領域預設值、無障礙修正都歡迎。請保持每個版本單檔、零相依。見 [CONTRIBUTING.md](CONTRIBUTING.md)。
- **授權:**[MIT](LICENSE)。想做什麼都行。我們不會寄 email 給你。

---

*不儲存、不傳輸任何資料。重新整理頁面就全部清空 —— 一塊小小的、私密的、學術版神奇畫板。*
