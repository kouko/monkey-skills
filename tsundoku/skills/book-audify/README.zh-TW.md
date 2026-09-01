# book-audify

[English](README.md) | [日本語](README.ja.md) | **繁體中文**

> 把你擁有的電子書轉成個人有聲書——帶章節書籤的 `.m4b`,使用免費的
> Microsoft 神經語音(edge-tts)合成。

接收 `book-extract` 的逐章 Markdown,流程:
清理 → **驗證硬閘門** → 逐章 TTS → ffmpeg 合併 m4b。

- 清理會拿掉所有 TTS 會唸錯的東西(標記符號、腳註錨點、譯註、裝飾性章名),
  並跳過獻詞/致謝/版權頁;`validate_tts.py` 沒過就拒絕合成。
- 聲音與語速交給使用者決定——skill 會用同一段文字做 A/B 試聽,不空談偏好。
  習慣開 1.5 倍速聽的人,基準語速要放慢,倍速後才保得住抑揚頓挫。
- 原文書:逐章全文「為聽而譯」(一書一譯名表、專有名詞不夾英文),
  先翻一章試聽通過才翻全書。

依賴由 `scripts/install_deps.sh` 安裝:`edge-tts` 以隔離的 CLI 工具安裝
(`uv tool install edge-tts` 或 `pipx install edge-tts`,不用裸 `pip`),
`ffmpeg`/`ffprobe` 走 brew 或經 SHA256 驗證的 static build。

資料流提醒:edge-tts 是 Microsoft 線上朗讀服務的 client,合成時整本書的
全文會逐章上傳到 Microsoft。僅限個人使用自己擁有的書,請勿散布產出的音檔。
