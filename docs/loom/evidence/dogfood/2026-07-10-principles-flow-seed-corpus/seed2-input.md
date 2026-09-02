# Replay seed 2 — bedtime-story audio app for preschoolers (synthetic)

Feed §Seed to §Headless / seeded mode as run-input; every bullet = user-stated verbatim.

## Seed

- **Idea**: 我想做一個手機版睡前故事語音 App，家長可以幫小孩選故事，App 用 AI 語音朗讀，也能錄自己的聲音當旁白，讓學齡前兒童每晚有固定的睡前儀式。
- **Q1 task**: 只做「故事播放 + 家長自訂/自錄旁白」
- **Scope-out**: 互動遊戲、識字教學、社群分享
- **Q2 user**: 3-6 歲兒童的家長（決策者是家長，使用情境是小孩）
- **Q3 quality pick**: 情感溫度（聲音要溫暖不生硬）＞ 內容豐富度 ＞ 功能多樣性
- **Q4 success**: 連續 7 天睡前使用率達 40%（首週留存指標）
- **Q5 why-new**: 現有有聲書 App 聲音是罐頭語調，無法客製化家長自己的聲音
- **Q6 languages**: 中文（繁體）為主，未來評估英文，暫不做日文
- **Q7 money**: 訂閱制，第一年不談具體定價數字，先看留存；先求 3 個月內上架 App Store 讓家長測試
- **Q8 lifecycle**: 一則故事 5-15 分鐘；播完自動淡出關閉螢幕（避免藍光影響入睡）
- **Product canon**: Kano Model（分層 must-be/delighter）＋ Jobs-to-be-Done（「哄睡儀式」任務框架）
- **Design stance**: 螢幕互動要「越少越好」——播放介面走低打擾、近乎無 UI 的設計，睡前不該有太多按鈕干擾；這種走向接近 Calm Technology 那套「注意力是稀缺資源」的思路
- **Design canon**: Interaction = Apple Human Interface Guidelines（iOS 優先平台）；Visual = Kenya Hara / MUJI「Emptiness」
- **Eng stances**: 打磨優先度=打磨優先（家長對品質敏感）／可逆性=無法判斷／隱私=小孩聲音錄音永遠不上傳雲端，只存裝置本機／升級胃口=無法判斷，暫時看 agent 自行決定
- **Tech-stack**: React Native + on-device TTS，雲端 TTS 僅在有網路時作為選配 fallback
- **Eng canon**: Local-First（錄音資料本機優先）
