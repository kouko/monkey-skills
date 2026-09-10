# loom-memory

> **一個選用、被動觸發的儲存庫記憶能力，帶 OKF v0.2 相容的儲存格式。**
> 它可以獨立安裝、獨立運作 —— 不依賴 `loom-code`、`loom-design` 或
> `loom-workflow` —— 而且這些 plugin 中的任何一個，或完全沒裝任何一個的
> 使用者，都能呼叫同一個公開的記憶 skill。

**Status**: v0.1.0 —— 首次發布即包含帶四個操作的公開記憶 skill、OKF
格式驗證器與索引產生器，以及一次性的舊格式遷移工具。詳見
[CHANGELOG.md](CHANGELOG.md)。
**Languages**: [English](README.md) | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)
**Repository**: [`monkey-skills`](https://github.com/kouko/monkey-skills) 的一部分

---

## 這是什麼

儲存庫知識 —— 學到的教訓、踩過的坑、值得不再重學一次的決策 —— 活得比
任何一次變更都久。loom-memory 就是這些知識住的地方：一個符合 Open
Knowledge Format（OKF）v0.2 規格的 Markdown 文件儲存庫，外加一個公開
skill，負責 recall（回想）、record（記錄）、reconcile（核對）、retire
（淘汰）裡面的條目。

這個能力是被動的：只有使用者明確要求記住、回想、核對或淘汰儲存庫知識，
或是 agent 自己判斷確實需要先前的儲存庫經驗時，才會動作。沒有任何 Loom
站會只因為走到那一站就呼叫它；它不存在也不會擋住 `loom-code`、
`loom-design` 或任何其他使用方 —— 沒有儲存庫或 recall 結果是空的，就是
正常的「沒有記憶」結果，不是失敗。

## 可獨立安裝

loom-memory 以自己的 plugin 發行。它的 skill、儲存模板與驗證器全部都在
這個 plugin 目錄內，而且它的 manifest 不宣告對 `loom-code`、
`loom-design` 或 `loom-workflow` 的任何必要依賴 —— 跟 `loom-design` 不同，
它不會去讀任何姊妹 plugin 的 contract package。`loom-code` 與
`loom-design` 同樣不宣告對它的依賴：彼此只透過帶 plugin 名的 skill 名稱
與專案自己的檔案相接，絕不碰別的 plugin 私有的 `hooks/`、`skills/`、
`scripts/` 路徑。

## OKF v0.2 相容儲存格式

這個 plugin 管理的儲存庫符合 OKF v0.2：每份非保留的 Markdown 文件都帶有
可解析的 YAML frontmatter，且 `type` 欄非空；存在的保留檔案 `index.md`
與 `log.md` 則遵守各自的保留結構。這個相容性代表任何理解 OKF 規格的
工具都能讀取與驗證這個儲存庫，不只是這個 plugin。

## 安裝

### Claude Code

```bash
claude plugin marketplace add https://github.com/kouko/monkey-skills.git
claude plugin install loom-memory@monkey-skills
claude plugin list | grep loom-memory     # 應該看到 enabled
```

loom-memory 自己裝、自己就能跑。`loom-code` 與 `loom-design` 永遠不是
必要條件 —— 它們只透過帶 plugin 名的 skill 名稱與專案自己的
`docs/loom/`（或等效）產物跟它相接。

### Codex CLI

用同樣方式安裝 Codex plugin；它自帶 `.codex-plugin/plugin.json`。

## 授權

MIT，作為 `monkey-skills` 的一部分。
