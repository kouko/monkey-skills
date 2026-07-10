# Run-input seed — 線上預約排班 SaaS（full-stack web service）

- **Idea**: 我想做一個給美容院、診所這類小型店家用的線上預約排班 web 服務：顧客在網頁上自己挑時段預約，店家後台管理員工班表與服務項目，兩邊即時同步。
- **Q1 task**: 讓顧客不用打電話就完成預約，讓店家不用手抄本管理班表；核心任務是「時段庫存的即時正確性」——同一時段絕不能重複預約。
- **Q2 user**: 買的人是店家老闆（非技術背景）；用的人有兩種——店家員工（後台）與終端顧客（前台預約頁）。不做給連鎖集團的企業版。
- **Q3 quality pick**: 預約流程的順暢（顧客 30 秒內完成）＞後台功能深度＞視覺華麗度
- **Q4 success**: 顧客端預約完成率 ≥80%；重複預約事故 = 0
- **Q5 why-new**: 現有服務（SimplyBook 之類）對台灣小店家太貴太複雜，且 LINE 通知整合差
- **Q6 notifications**: 預約確認與提醒走 LINE Messaging API 與 email，簡訊之後再說
- **Q7 money**: 月費三檔（免費／基本 390／進階 990），預計 Q4 上線搶年底旺季
- **Q8 lifecycle**: 預約記錄保留多久還沒想清楚（法規要查），無法判斷；班表資料一年後可歸檔
- **Platform**: 響應式 web（顧客端手機為主），店家後台桌面瀏覽器為主
- **Product canon**: Working Backwards（先寫顧客新聞稿）
- **Design stance**: 顧客端要「長輩也會用」的簡單，後台照 Material Design 的做法走就好，無障礙至少要符合 WCAG 2.2 AA
- **Eng stances**（一次講完）: 快速迭代優先（先搶市場，之後再打磨）、決策偏可逆（能換就先用現成的）、雲端成本上限每月一萬台幣超過就降級功能、顧客個資只存必要欄位且預約完成後電話遮罩顯示、工程決策全委派給 agent 只看結果
- **SLA/uptime 目標**: 無法判斷，要先看第一批店家的營業時間分布
- **Tech-stack**: 前端用 React + TypeScript 做，後端我想用 FastAPI 配 PostgreSQL，整體照 12-Factor App 的慣例部署到雲端
