# variance-target-action-template

[English](README.md) | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)

通用平衡迴路控制範本（目標 ↔ 變異 ↔ 行動 ↔ 實績），以及振盪情境下「無為」判斷的診斷工具。

## 何時使用

- KPI 在目標周圍振盪，振幅持續或逐漸放大。
- 每次介入都讓擺幅變得更大的「乒乓調整」狀態。
- 想把任何管理控制機制（配額、OKR、庫存規則、貨幣政策委員會、客戶成功劇本）建模為平衡迴路時。

## 如何啟動

```
/systems-thinking-toolkit:variance-action
```

## 你會得到

- 四節點平衡迴路診斷（target / actual / variance / action），明確標示變異方向與 S/O 連結符號。
- 考量回饋延遲的建議；當迴路本身正在收斂、或過度修正才是失敗模式時，會明確建議「不要行動」。
- 一份向上溝通用的理由說明，避免「節制」被誤讀為「怠惰」。

## 邊界

- 不適用於強化迴路（R 迴路）或真正在發散的系統 — 請改用 `loop-and-link-primitives`。
- 不適用於振盪本身就是目的（例如刻意設計的週期行為）、或偵測延遲實質為零的情境。
- 不適用於一次性、非重複的決策，因為根本沒有可振盪的回饋迴路。

## 更多

- 技能本體: [SKILL.md](SKILL.md)
- 出處: Dennis Sherwood, *Seeing the Forest for the Trees* (2002), Chapter 6（平衡迴路、時間延遲、振盪）; Chapter 10（每個槓桿的 B 迴路範本）。
