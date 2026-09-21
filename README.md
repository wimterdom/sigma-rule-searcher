# Sigma 規則搜尋器

搜尋、篩選、一鍵複製與線上編輯 [SigmaHQ](https://github.com/SigmaHQ/sigma) 的全部偵測規則。
純靜態網頁，規則庫在使用者瀏覽器中以 IndexedDB 快取，之後開啟不需重新下載。

線上網址：<https://wimterdom.github.io/sigma-rule-searcher/>

## 功能

- 全文搜尋標題、描述、標籤、作者與 YAML 內容，支援 `level:high`、`tag:t1059`、`product:windows`、`field:CommandLine`、`-排除字`、`"完整片語"` 等語法
- 依規則來源、嚴重等級、狀態、ATT&CK 戰術、logsource 產品／類別／服務篩選
- 一鍵複製規則、收藏規則、連結至 ATT&CK 與 GitHub 原始檔
- 內建 YAML 編輯器：即時 Sigma 規格檢查、與原始規則比對差異、產生新 UUID、更新 modified 日期、草稿自動保存
- 日間／夜間模式，手機可用

## 檔案結構

| 路徑 | 說明 |
|---|---|
| `index.html` | 網頁本體（CSS/JS 皆內嵌，僅由 cdnjs 載入 CodeMirror 與 js-yaml） |
| `data/rules.json` | 全部 Sigma 規則（中繼資料＋原始 YAML） |
| `data/version.json` | 版本戳記，網頁先讀它決定要不要重新下載規則庫 |
| `build_db.py` | 由 SigmaHQ repo 產生上述兩個 JSON |
| `.github/workflows/update-sigma-rules.yml` | 每週自動更新規則庫 |

收錄資料夾：`rules`、`rules-emerging-threats`、`rules-threat-hunting`、`rules-compliance`、`rules-placeholder`、`rules-dfir`、`deprecated`、`unsupported`。

## 首次部署

```bash
# 1. 在 GitHub 上建立空的 repo：sigma-rule-searcher（Public）
# 2. 在本資料夾內執行
git init -b main
git add .
git commit -m "feat: Sigma 規則搜尋器"
git remote add origin https://github.com/wimterdom/sigma-rule-searcher.git
git push -u origin main
```

接著到 GitHub 的 **Settings → Pages**，Source 選 **Deploy from a branch**，分支選 `main`、資料夾選 `/ (root)`，存檔後約一分鐘即可開啟上方網址。

## 手動更新規則庫

到 **Actions → Update Sigma rules → Run workflow** 即可立即執行；
或在本機執行：

```bash
git clone --depth 1 https://github.com/SigmaHQ/sigma.git /tmp/sigma
pip install pyyaml
python3 build_db.py /tmp/sigma data/rules.json
git commit -am "chore: 更新 Sigma 規則庫" && git push
```

## 自動更新

`update-sigma-rules.yml` 每週日 16:00 UTC（台北時間週一 00:00）執行：
先比對 SigmaHQ 最新 commit，與 `data/version.json` 相同就跳過，不同才重建並 commit。
GitHub Pages 會在 commit 後自動重新發佈。

規則版權屬 SigmaHQ 專案（Detection Rule License）。
