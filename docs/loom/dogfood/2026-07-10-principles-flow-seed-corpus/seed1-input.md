# Replay seed 1 — B2B incident-response war-room dashboard (synthetic)

Feed §Seed to §Headless / seeded mode as run-input; every bullet = user-stated verbatim.

## Seed

- **Idea**: 我想做一個 B2B SaaS 的 incident response 戰情室 dashboard，讓 on-call 工程師在生產事故發生時，一眼看到相關 service 健康度、alert 關聯與 runbook。目標客群是 50-500 人的中大型工程團隊。
- **Q1 task**: 只做「事故發生當下的即時戰情室視圖」——alert aggregation + service health + runbook 連結
- **Scope-out**: postmortem 撰寫、SLA 報表、on-call 排班（下游/其他產品）
- **Q2 user**: on-call 值班工程師（非 SRE 主管，非管理層）
- **Q3 quality pick**: 資訊即時性（秒級更新）＞ 資訊密度（一頁看全貌）＞ 客製化彈性
- **Q4 success**: MTTA（acknowledge 時間）縮短 30%（事故前後 30 天均值比較）
- **Q5 why-new**: 現有工具（Grafana/Datadog）需人工拼裝面板，無「事故當下」預組版面
- **Q6 languages**: 僅英文介面（企業客戶皆用英文 stack）
- **Q7 money**: 年約企業授權，第一年目標簽 10 個 logo；MVP 要在 8 週內上線給種子客戶看
- **Q8 lifecycle**: 一次事故 view session 15 分鐘到 4 小時；結束後進 archive，不主動刪除
- **Product canon**: HEART（Google）＋ MoSCoW（8 週 MVP 範圍協商）
- **Design stance**: 資訊密度優先於美觀留白，深色模式為主（值班室常態環境）
- **Design canon**: Interaction = Nielsen's 10 Usability Heuristics + IBM Carbon；Visual = Swiss / International Typographic Style
- **Eng stances**: 打磨優先度=先求穩定不出事故（打磨次要）／可逆性=能快速 rollback 優先／隱私=不留存客戶生產環境實際數據內容只留 metadata／升級胃口=架構決策要工程主管參與事前討論／測試嚴謹度=alert 關聯邏輯需 property-based test 覆蓋
- **Tech-stack**: TypeScript + React 前端；Go 後端；PostgreSQL + Redis
- **Eng canon**: 混合 Layered/N-Tier（資料流分層）＋ Hexagonal/Ports & Adapters（alert source adapter 需可替換）；不採 Microservices（團隊規模不到）
