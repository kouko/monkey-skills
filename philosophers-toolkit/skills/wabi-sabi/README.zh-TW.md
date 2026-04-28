# Wabi-Sabi Skill

[English](README.md) | [日本語](README.ja.md) | **繁體中文**

透過三個視角評估不完美，
判斷何時為「夠好」，並對抗 over-engineering 與完美主義。

## 三個視角

| Lens | 日文 | 核心提問 | 目的 |
|------|------|---------------|------|
| Wabi | 侘 | 不損及本質的前提下，能拿掉什麼？ | 簡素 |
| Sabi | 寂 | 哪些不完美承載了故事或增添了個性？ | 時間與使用的痕跡 |
| Incompleteness | 不完全の美 | 哪些未完成的元素邀請成長？ | 刻意不完整之美 |

## Method Type

Framework-driven 分析（依序套用三個獨立視角，
最後 synthesize 為「夠好」的判斷）。

## 套用至 Software / Product

| Lens | Over-engineering | Wabi-Sabi |
|------|-----------------|-----------|
| Wabi | 20 個沒人用的 feature | 5 個使用者每天都用的 feature |
| Wabi | 50 個 API endpoint | 10 個多用途 endpoint |
| Wabi | 3 層抽象 | 直接實作，需要時再抽象 |
| Sabi | 通用 500 錯誤 | 提供脈絡且有用的錯誤訊息 |
| Sabi | 突然 deprecate API | 漸進 deprecate 並附遷移指南 |
| Sabi | 過時 UI 全面重寫 | 保留使用者依賴的熟悉 UX pattern |
| Incompleteness | 預先準備所有未來需求 | 預留延伸點，實作之後再說 |
| Incompleteness | 一切內建到核心 | Core + plugin 架構 |
| Incompleteness | 100 欄位的 template | 最小 template + 使用者客製 |

## 關鍵區別：品質 vs 過度品質

| | 低品質（非 wabi-sabi） | 充足品質（wabi-sabi） | 過度品質（也非 wabi-sabi） |
|--|----------------------------|-------------------------------|----------------------------------|
| 定義 | 缺少必要功能 | 必要功能具備，非必要部分已移除 | 超越情境所需的打磨 |
| 範例 | 搜尋壞了 | 搜尋可用，沒有自動完成 | 為 5 名使用者做 ML-powered 推薦的搜尋 |
| 行動 | 修好它 | 出貨 | 砍掉它 |

## SKILL.md 中的範例

| 範例 | Domain | 關鍵洞見 |
|------|--------|----------|
| MVP 發布決策 | SaaS Product | 移除非核心 feature（Gantt、dashboard）、改善錯誤訊息、新增狀態自訂 |
| UI 打磨決策 | 內部工具 | 5 人的內部工具不需動畫或主題；改去修真正被抱怨的那一點 |

## 額外案例

更多範例見 `references/wabi-sabi-cases.md`：
API 設計簡化、技術債評估、文件 scope。

## 與其他 Skills 的關聯

| Skill | 關係 |
|-------|-------|
| design-team（Kansei Engineering） | wabi-sabi 告訴我們可以拿掉什麼；kansei 告訴我們情感共鳴必須留下什麼 |
| code-team（YAGNI） | Wabi（簡素）對應 YAGNI；Incompleteness 對應延伸點 |
| hegelian-dialectics | 當「出貨 vs 打磨」變成二選一時，dialectics 找出 synthesis；wabi-sabi 提供視角 |
