# think-orbit

> 單人使用的思考與規劃夥伴——把一段討論轉成透明的思考鏈：每個節點一個 markdown 檔、帶過時傳播的假設檔、靜默的機械式關卡、以及可重新產生的 DAG 視圖。決策只是其中一種結尾，不是唯一的結尾。

[English](README.md) | [日本語](README.ja.md) | **繁體中文**

**版本**：0.1.1
**所屬**：[monkey-skills](https://github.com/kouko/monkey-skills)
**授權**：MIT
**狀態**：Part 1 — 預發佈版。核心對話協定尚未實作（將於 Task 11 完成）。

## 使用方式

說「幫我想 X」／「規劃 X」／「我要決定 X」（或 "help me think through X"、"plan X"、"help me decide X"），入口 skill `using-think-orbit` 會把你帶進 `thinking-session`，agent 會問幾個問題，邊聊邊把推理寫進 markdown 檔案，並重新產生你隨時可讀的 DAG 視圖。一次坐下可以停在一個未解的問題或一份計畫骨架，那也是完整的紀錄。

## 安裝

```bash
/plugin marketplace add kouko/monkey-skills
/plugin install think-orbit@monkey-skills
```

**執行需求**：安裝了 PyYAML 的 Python 3（`pip install pyyaml`）— 閘門與 DAG 腳本靠它執行。
