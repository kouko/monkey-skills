# Replay seed 4 — local-first vector sketchbook for illustrators (synthetic)

Feed §Seed to §Headless / seeded mode as run-input; every bullet = user-stated verbatim.

## Seed

- **Idea**: 我想做一個 macOS/Windows 桌面版向量繪圖筆記工具，給插畫師做快速草稿與版面構思，強調離線優先、檔案自己掌控，介面要像紙本速寫本一樣不打斷創作流。
- **Q1 task**: 只做「向量繪圖 + 圖層 + 本機檔案管理」
- **Scope-out**: 向量轉點陣批次輸出、團隊即時共編、素材市集
- **Q2 user**: 獨立接案插畫師/概念設計師（非團隊、非企業採購）
- **Q3 quality pick**: 創作流暢度（筆刷延遲低）＞ 檔案掌控權（本機可攜）＞ 功能廣度
- **Q4 success**: 筆刷延遲 <16ms（60fps 感知），離線可完整使用不需帳號登入
- **Q5 why-new**: 現有工具（Illustrator/Affinity）訂閱綁死或格式封閉，速寫用途太重
- **Q6 languages**: 介面英文＋繁中雙語，日文晚點看使用者需求
- **Q7 money**: 買斷制一次性付費，不訂閱；第一版先免費 beta 三個月收集回饋再開始賣
- **Q8 lifecycle**: 一個專案檔可能反覆開關數個月；不做雲端備份，使用者自己用 Git/Dropbox 這類工具備份（產品不管）
- **Product canon**: Jobs-to-be-Done（任務框架）＋ Blue Ocean Strategy（對 Illustrator/Affinity 飽和市場重畫價值曲線）
- **Design stance**: 介面要「安靜」，工具列預設收起、畫布佔滿全螢幕，靈感來自紙本速寫本的留白感；Interaction 走 Apple Human Interface Guidelines（原生桌面手感）混合 Norman's Design Principles（affordance 要讓筆刷工具一看就懂怎麼用，不用說明書）
- **Design canon**: Visual = Kenya Hara / MUJI「留白即邀請」的日式極簡
- **Eng stances**: 打磨優先度=打磨優先（筆刷手感是產品核心）／可逆性=檔案格式要開放可逆、不能鎖平台／隱私=完全不連網也能用，任何雲端功能都是選配非必要／升級胃口=無法判斷，先不談架構層級決策，之後再議
- **Tech-stack**: C++ 核心繪圖引擎（跨平台）＋ Qt 殼視窗層，檔案格式用開放 SVG 延伸格式
- **Eng canon**: Local-First（資料/檔案本機優先，可攜）＋ Vertical Slice Architecture（功能模組化，減少跨層改動）
