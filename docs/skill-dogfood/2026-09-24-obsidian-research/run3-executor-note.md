---
title: Mac 本地 LLM 推論框架怎麼選——llama.cpp、MLX、Ollama 比較
type: research
date: 2026-09-24
tags:
  - local-llm
  - apple-silicon
  - llama-cpp
  - mlx
  - ollama
  - inference
status: completed
aliases:
  - Mac 本地 LLM 框架比較
  - llama.cpp vs MLX vs Ollama
source_count: 57
source_languages: [en, ja]
---

# Mac 本地 LLM 推論框架怎麼選——llama.cpp、MLX、Ollama 比較

> 📌 想先跑起來選 Ollama，要最快的單人生成速度或要在 Mac 上微調選 MLX（mlx-lm），要當穩定的 API 服務、長上下文或跨平台選 llama.cpp 的 `llama-server`——而且這三者不是互斥的，Ollama 本身現在就同時內建另外兩個引擎。

在同一台 Mac、同位元量化下，MLX 的生成速度通常是原生 llama.cpp 的 1.2–2 倍；網路上常見的「3 倍」多半是拿 MLX 跟 Ollama 比，而 Ollama 包裝層本身就會吃掉一截速度 [11][14]。反過來，llama.cpp 在 prompt 預處理（prefill）和超長上下文上常常不輸甚至勝出 [13][15]，功能最完整的伺服器也是它的 `llama-server` [19]。Ollama 最好上手，但預設上下文長度、截斷行為與 OpenAI 相容層的缺口是最常踩的坑 [5][24]。

## Table of Contents

- [[#一、先分清楚：三者不在同一層]]
- [[#二、速度：生成、預處理與 M5]]
- [[#三、功能：伺服器、多模態、微調]]
- [[#四、上手與維運：Ollama 的預設值陷阱]]
- [[#五、模型格式與量化]]
- [[#六、硬體：記憶體怎麼抓]]
- [[#七、決策矩陣]]
- [[#八、怎麼選]]
- [[#九、分歧、被推翻的說法與未解問題]]
- [[#十、研究方法與限制]]
- [[#十一、下一步]]
- [[#附錄：來源清單]]

---

## 一、先分清楚：三者不在同一層

一篇日文整理講得最乾淨：「GGUFとsafetensorsは主にモデル重み・推論ファイルの形式、MLXはApple silicon向けの機械学習framework、Ollamaはモデルを取得・実行・管理するruntimeの入口です」（GGUF 與 safetensors 是權重檔格式，MLX 是 Apple Silicon 的機器學習框架，Ollama 是下載、執行、管理模型的 runtime 入口）[48]。

| | 是什麼 | 在 Mac 上怎麼用 GPU | 模型格式 |
|---|---|---|---|
| **llama.cpp** | 純 C/C++ 推論引擎（底層是 ggml 張量庫），附 `llama-server` [51] | ARM NEON、Accelerate 與 Metal [51] | GGUF |
| **MLX**（+ mlx-lm） | Apple 的陣列運算框架；mlx-lm 是它上面的 LLM 套件 [52][22] | 陣列放在共享記憶體，CPU／GPU 之間不搬資料 [52] | safetensors（MLX 量化版） |
| **Ollama** | 模型管理＋伺服器的 runtime | 看模型格式，交給 llama.cpp 或 MLX [5] | 兩者皆可 |

**Ollama 的引擎演變**（這是 2026 年最大的變化）：

1. 早期直接依賴 llama.cpp 做模型支援 [6]。
2. 2025-05 推出自己的「new engine」，但底層仍是 GGML 張量庫 [6]。
3. 2026-03 的 v0.19 起，Apple Silicon 上可用 MLX 推論（preview）[2]。
4. 到 2026-09 的 v0.34.4，兩個引擎都還在並行更新（"Updated llama.cpp, MLX, and XGrammar."）[4]。原始碼裡的分流規則是**看模型格式**：safetensors 走 MLX，其餘走 llama.cpp [5]。實務上就是 `-mlx`、`-nvfp4` 結尾的 tag 走 MLX，一般 GGUF tag（例如 Q4_K_M）走 llama.cpp [5][16]——**更新 Ollama 不等於自動變成 MLX**。 — **信心度 High**（官方原始碼＋發行說明，第三方實測的 tag 用法一致）

另外兩個背景事實：LM Studio 從 0.3.4（2024-10）起就能在同一個 app 裡混用 llama.cpp 與 MLX 模型 [34]；GGML／llama.cpp 團隊在 2026-02-20 加入 Hugging Face，官方說專案維持開源、開發照舊 [31]。

## 二、速度：生成、預處理與 M5

### 先理解兩種速度

Apple 自己的說法：第一個 token（prefill，處理你輸入的 prompt）是**算力**瓶頸；之後逐字生成（decode）是**記憶體頻寬**瓶頸 [1]。所以：

- 生成速度幾乎跟著記憶體頻寬走。llama.cpp 社群長年累積的基準表也是這個規律：LLaMA 7B Q4_0 生成速度從 M1 Max 的 61 tok/s 到 M5 Max 的 120 tok/s [8]。 — **信心度 High**
- prompt 很長的用法（RAG、貼整份文件、coding agent）主要吃 prefill，看的是 GPU 算力與框架實作。

### MLX 對 llama.cpp：生成快，但沒有「3 倍」那麼誇張

| 測試 | 機器 | 模型 | MLX | llama.cpp | Ollama |
|---|---|---|--:|--:|--:|
| Kapetanovic [11] | M4 Max 128GB | Qwen3.5-35B-A3B | 121.3（Python API）／84.5（HTTP） | 68.8 | 40.3 |
| john-rocky [12] | M4 Max | Qwen 3.5 2B | 291.9 | 149.7 | — |
| john-rocky [12] | M4 Max | Gemma 4 E2B | 185.4 | 119.2 | — |
| famstack [13] | M1 Max | （4-bit vs Q4_K_M） | 57 | 29 | — |
| zephel01 [18] | M3 Max 64GB | Qwen3.6-35B-A3B（Chat 2K） | 163（mlx-lm） | — | 51（GGUF／llama.cpp 路徑） |

單位皆為生成 tok/s。讀法：

- **MLX 生成比原生 llama.cpp 快約 1.2–2 倍**，dense 小模型也有接近 2 倍的案例 [11][12][13]。學術比較（M2 Ultra）同樣結論是 MLX 持續生成吞吐量最高、Ollama 在吞吐與首字延遲上落後 [7]。 — **信心度 High**
- **「3 倍」是跟 Ollama 比出來的**：同一台機器上 Ollama（llama.cpp 路徑）只有原生 llama.cpp 的六成左右 [11]；一篇 AI 生成的整理文估計 Ollama 的 Go 包裝層吃掉約 50% 效能 [14]。 — **信心度 High**（兩份獨立實測方向一致；包裝層比例本身只有單一來源）
- **包裝方式也有差**：同一個 MLX，Python API 直接呼叫 121 tok/s，走 HTTP 伺服器只剩 84.5 [11]。你實際用的是「伺服器＋client」時，框架差距會被壓縮。
- 量化並不完全對等（例如 Kapetanovic 的 llama.cpp 用 Q4_K_XL，部分層升到 8–16 bit）[11]，所以倍數只能當大概。

### 預處理與長上下文：llama.cpp 常常不輸

- 短 prompt 的首字延遲，llama.cpp 反而較低（29 vs 42 ms）[12]。
- 8,500 token 的上下文，MLX 預處理花 49.4 秒、GGUF 37.8 秒，MLX 總時間有 94% 花在 prefill [13]。
- mlx-lm 的一個 issue 回報：M3 Ultra 上，30K 上下文時 MLX 生成 25 t/s、開 Flash Attention 的 llama.cpp 32 t/s；146K 時 5.95 vs 12.12 t/s [15]。這是單一使用者回報，維護者尚未重現。

— **信心度 Medium**（有反方說法，見〈九〉）。長 prompt 用途最好自己用實際工作量測一次。

### M5 世代：prefill 大躍進，但不是 MLX 獨享

- Apple：M5 的 GPU Neural Accelerator 讓 MLX 的首字延遲比 M4 快 3.33–4.06 倍；生成只快 19–27%，約等於記憶體頻寬的增幅（120→153 GB/s）；需要 macOS 26.2 以上 [1]。
- llama.cpp 在 2025-11-06 合併了 Metal 4 tensor API 支援 [9]，社群基準顯示 M5 Max 的 prefill（pp512）是 3219.99 tok/s，M4 Max 為 885.68，約 3.6 倍 [8]。
- 但**要看你用的 build**：LM Studio 內建的 llama.cpp runtime 2.21.0 在 M5 Max 上把 tensor API 關掉了，同機跑上游 llama.cpp 的 prefill 快 2–2.4 倍 [10]。

— **信心度 High**。換句話說，「M5 上只有 MLX 能拿到 prefill 加速」這種說法已經過時。

### Ollama 換 MLX 到底快多少

- Ollama 官方（M5 系列）：Qwen3.5-35B-A3B，v0.18（Q4_K_M, llama.cpp）→ v0.19（NVFP4, MLX）生成 58→112 tok/s、prefill 1,154→1,810 tok/s [2]。2026-06 的第二篇只說 NVFP4 比 q4_K_M 生成快約 20% [3]。
- 獨立實測（舊晶片）：M2 Max 32GB 上 Gemma 4 12B，MLX NVFP4 與 GGUF Q4_K_M 生成幾乎一樣（約 14.0 vs 13.7 tok/s），prefill 反而 GGUF 快約 1.4 倍 [16]；M4 Max 上 Gemma 4 26B 兩者生成同樣幾乎相同（41.4 vs 41.8）[17]；另一篇指出加速靠的是 NVFP4 模型，單純升級到 0.19 效果有限 [47]。

— **信心度 Medium**：在 M2–M4 上，官方的「接近 2 倍」重現不出來；但沒有人在 M5 上做過獨立對照，官方數字在 M5 上仍可能成立。

## 三、功能：伺服器、多模態、微調

| 功能 | llama.cpp（`llama-server`） | MLX（`mlx_lm.server` 等） | Ollama |
|---|---|---|---|
| OpenAI 相容 API | chat、responses、embeddings [19] | 「intended to be similar to」OpenAI chat API [20] | chat、completions、embeddings、responses [24] |
| Anthropic Messages API | 有 [19] | 本次未查到 | 本次未查 |
| 工具呼叫 | 幾乎任何模型，需 `--jinja` [19] | 有（程式碼支援，文件沒寫）[21] | 有，但不支援 `tool_choice` [24][5] |
| JSON schema 結構化輸出 | 有 [19] | 未見 [21] | 有（`format`／`response_format`）[53] |
| 多人並行 | continuous batching、multi-user [19] | 有 batching；開 `--kv-bits` 量化 KV cache 就退回一次一個 [20][21] | `OLLAMA_NUM_PARALLEL` 預設 1 [26] |
| 推測解碼（speculative decoding） | 有 [19] | 每次請求可指定 `draft_model` [20] | 本次未查 |
| 多模態 | 圖、音、影片輸入（libmtmd，需 `--mmproj`）[54] | mlx-vlm：視覺＋音訊／影片模型 [23] | new engine 為多模態而生 [6]；MLX 引擎上 gemma4 支援圖與音 [4] |
| 微調 | 本次未查 | LoRA 與全參數微調，支援量化模型 [22]；mlx-vlm 也能訓練 [23] | 不是它的用途 |
| 官方對正式環境的態度 | — | **明言不建議正式環境**，只有基本安全檢查 [20] | — |

幾點補充：

- **llama-server 是三者中最「服務級」的**：OpenAI 與 Anthropic 兩種 API、continuous batching、schema 約束、推測解碼都在同一個 binary 裡 [19]。日本的實務指南也說它「本番運用に向いています。依存関係が最小限」（適合正式運用、依賴最少），並提醒每多一個並行 slot 就多吃一份 KV cache 記憶體 [45]。
- **MLX 的強項在「玩模型」**：Hugging Face 上一行指令就能拉 mlx-community 的模型 [22]，還能在 Mac 上做 LoRA。實例：M2 Pro 32GB 的 Mac mini，7B 4-bit 模型 LoRA 1,000 次迭代約 20 分鐘，記憶體幾乎用滿但沒有 swap [38]。
- **Ollama 的文件落後程式碼**：OpenAI 相容頁面仍寫不支援 logprobs [24]，但程式碼 2025-11-11 就加上了 [25]。
- **新模型上架速度**：一篇 2026-09 的評測認為 Ollama 的模型庫較慢，也不一定有 Unsloth 的動態量化版本 [39]（意見）。

## 四、上手與維運：Ollama 的預設值陷阱

**上手難度**：Ollama 最簡單，日文比較文直說「一番の強みは導入の簡単さ」（最大強項是好安裝）；mlx-lm 是 `pip install mlx-lm`，適合熟悉 Python 的人 [46]。

**Ollama 最常踩的五個坑**（都已對照 2026-09 的原始碼）：

1. **預設上下文長度依 VRAM 分三級**：< 24 GiB 用 4k、24–48 GiB 用 32k、≥ 48 GiB 用 256k。這是 v0.15.5（2026-02-03）才改的 [27][5][50]；FAQ 頁面還停在「4096 tokens」[26]。 — **信心度 High**
2. **Mac 的「VRAM」其實是 Metal 可用上限**，32GB 的 Mac 只算到約 21.3 GiB [29]，所以**32GB Mac 預設只有 4k 上下文**，36GB 的 Mac（27 GiB [28]）才有 32k。這是查證時從原始碼與日誌推出來的，Ollama 文件沒有明寫 [5][28][29]。 — **信心度 Medium**
3. **超出上下文時會從對話前面丟訊息**，保留 system 訊息與最新一則，回應裡不會告訴你；可用 `truncate: false` 改成報錯 [5]。
4. **從 OpenAI 相容的 `/v1` 端點傳 `num_ctx` 沒用**，要用 Modelfile 或伺服器層級的 `OLLAMA_CONTEXT_LENGTH` [24][5]。接 coding agent 或 RAG 時，這條最容易讓模型「看不到」前面的內容。
5. **閒置 5 分鐘就卸載模型**（`OLLAMA_KEEP_ALIVE` 可改）；**並行預設是 1**，記憶體用量隨「並行數 × 上下文長度」放大 [26]。以前會自動在 4 和 1 之間選，2025-07 起固定為 1 [49]。

**同時開多套工具會爆記憶體**：有人在 64GB Mac 上同時開幾套工具，每套各吃約 22GB，結果當機 [18]。

**社群爭議（意見，供判斷用）**：r/LocalLLaMA 曾有一篇「Stop using Ollama」拿到 1,175 讚，主要批評 Ollama 沒有在 MIT 授權裡附上 llama.cpp 的版權聲明 [32]。查證時發現，要求在發行檔附上授權聲明的 issue 從 2024-03 開到現在仍未關閉 [33]。Ollama 在 2025–2026 年也加入了雲端託管模型等功能 [55]。在意「純本地、透明」的人會因此偏向直接用 llama.cpp。

## 五、模型格式與量化

- **GGUF（llama.cpp）**：k-quants 對不同張量用不同位元（quant mixtures），可用 imatrix 降低品質損失；Q4_K_M 約 4.9 bits/weight [35]。
- **MLX**：量化模式有 affine（2–8 bit）、mxfp4、mxfp8、nvfp4 [56]。預設的 affine 4-bit（group size 64）實際約 4.5 bits/weight [37]。mlx-lm 另有 DWQ、AWQ、GPTQ、dynamic 等學習式量化：dynamic 最快，DWQ 較花時間但「typically yields better results」[36]。
- **品質**：Ollama 宣稱 NVFP4 的品質損失約為 4-bit 的一半 [3]（廠商說法，**信心度 Medium**）。TensorFoundry 的看法是：在 Mac 上追速度就用 MLX 4-bit，想要更好的品質就升到 5 或 6 bit，不必糾結格式 [37]（意見）。
- **實務影響**：格式決定了你能用哪個引擎。同一個模型要在 MLX 和 llama.cpp 之間切換，就得各下載一份；在 Ollama 裡也是靠選 tag 決定引擎 [5]。

## 六、硬體：記憶體怎麼抓

**頻寬決定生成速度，容量決定能跑多大的模型。** 目前的 Apple 規格：

| 晶片 | 最大統一記憶體 | 記憶體頻寬 |
|---|--:|--:|
| M5 | — | 153 GB/s [1] |
| M5 Pro | 64GB | 307 GB/s [41] |
| M5 Max | 128GB | 最高 614 GB/s [41] |
| M5 Ultra（Mac Studio，2026-09-22 開賣） | 512GB | 1.2 TB/s [40] |

**模型實際吃多少記憶體**（Apple 用 MLX 量的）：Qwen3-8B 4-bit 5.61GB、Qwen3-14B 4-bit 9.16GB、GPT-OSS-20B 12.08GB、Qwen3-30B MoE 4-bit 17.31GB [1]。但檔案大小會低估執行時的需求：有人量到 `qwen3-coder:30b` 檔案 18GB、執行中用了 45GB，多出來的部分作者歸因於 Ollama 預設保留的約 26 萬 token 對話歷史（KV cache）[43]——這正是〈四〉講的 64GB 機器預設 256k 上下文 [5]。另一份日本實測（8／16／32GB 三台 Mac）的經驗法則是「占有 + 3GB が搭載メモリに収まれば完走する」（模型占用加 3GB 塞得進記憶體就跑得完）[44]。

**macOS 的 GPU 記憶體上限**：macOS 不會讓 GPU 用光全部記憶體。從日誌看，36GB 以下的 Mac 約 2/3，36GB 以上約 3/4 [28][29]。可以用 `sudo sysctl iogpu.wired_limit_mb=<MB>` 調高 [30]，重開機後會恢復原值 [30]。這個比例是從日誌推算的，Apple 沒有公開文件。 — **信心度 Medium**

**多台 Mac 串接**：macOS 26.2 起 Thunderbolt 5 支援 RDMA，MLX 可透過 Apple 的 JACCL 做分散式推論。WWDC26 示範用 4 台 M3 Ultra，Qwen 3.6 的生成速度接近單機的 3 倍 [42]。這是 MLX 目前獨有的路線。

**Ollama 的 MLX 路徑**：v0.19 部落格建議 32GB 以上 [2]，但程式碼裡並沒有強制檢查 [5]。但沒有門檻不代表跑得動：在 M4 32GB 上用 MLX 路徑載入 35B 模型，MLX runner 逾時失敗 [57]。

## 七、決策矩陣

評分：◎ 最強、○ 夠用、△ 有明顯限制。依據見前面各章。

| 標準 | llama.cpp | MLX（mlx-lm） | Ollama |
|---|:-:|:-:|:-:|
| 上手難度 | △（指令列、自己挑 GGUF） | ○（Python／pip） | ◎ |
| 單人生成速度 | ○ | ◎ | △（llama.cpp 路徑有包裝損耗） |
| 長 prompt／長上下文 | ◎ | ○ | ○（取決於走哪個引擎） |
| M5 prefill 加速 | ○（要用新版上游 build） | ◎ | ○（MLX tag 才有） |
| API 伺服器完整度 | ◎ | △（官方說不適合正式環境） | ○（缺 `tool_choice`） |
| 多人並行 | ◎ | ○ | △（預設 1） |
| 微調 | — | ◎ | — |
| 新模型取得 | ◎（GGUF 生態最大） | ◎（mlx-community） | ○ |
| 透明度／可控性 | ◎ | ◎ | △（預設值藏得深、授權爭議） |
| 跨平台（Linux／NVIDIA） | ◎ | △（僅 Apple Silicon） | ◎ |

## 八、怎麼選

| 你的情況 | 建議 |
|---|---|
| 第一次玩、想接 Open WebUI 或各種 app | **Ollama**。記得設 `OLLAMA_CONTEXT_LENGTH`；32GB 以上的 Mac 可以試 `-mlx`／`-nvfp4` tag |
| 一個人用、想要最快的回應、會寫 Python | **mlx-lm**；要圖片就加 mlx-vlm |
| 想在 Mac 上微調（LoRA） | **mlx-lm**，這是三者中唯一的選項 |
| 要當團隊或 agent 的後端（並行、工具呼叫、JSON schema、Anthropic API） | **llama.cpp `llama-server`** |
| 大量長 prompt（RAG、整份程式碼庫） | **llama.cpp**，或兩者用自己的資料實測 |
| 同一套設定也要跑在 Linux／NVIDIA | **llama.cpp**（或 Ollama） |
| 想要 GUI 又想兩個引擎都能用 | LM Studio；M5 使用者注意它內建的 llama.cpp runtime 可能沒開 tensor API [10] |

> [!tip] 最務實的組合
> 日常用 Ollama 或 LM Studio 當入口，遇到「速度不夠」再改用 mlx-lm，遇到「要當服務」再改用 llama-server。三者可以共存，但別同時把模型都載入記憶體 [18]。

**這些建議背後的假設**：

- 你用的是 Apple Silicon，而且主要是一個人在用；多人服務的情境才輪到 llama-server 的並行優勢。
- 速度數字來自 M1–M4 與廠商的 M5 測試；M5 Pro／Max／Ultra 的獨立實測還很少。
- Ollama 的版本變化很快（2026 年 3 月到 9 月從 0.19 到 0.34），預設值和引擎分流隨時可能改。

**事前驗屍（pre-mortem）**：如果一年後回頭看這份建議是錯的，最可能的原因是**Ollama 把 MLX 變成所有模型的預設路徑，並補齊伺服器功能**。到那時「Ollama 比較慢」這個主要缺點就消失了，它會變成大多數人的唯一答案。其次的可能是 llama.cpp 在 M5 上追平 MLX 的生成速度。

## 九、分歧、被推翻的說法與未解問題

**被推翻或過時**：

- ❌「用 `OLLAMA_MLX=1` 就能讓 Ollama 改走 MLX」：原始碼裡沒有這個變數，引擎是看模型格式決定的 [5]。一篇日文基準 [18] 就是用這個變數測「Ollama MLX」，所以它那組「Ollama+MLX」的數字其實很可能都跑在 llama.cpp 上，本筆記不採用。它的 mlx-lm 對 Ollama 標準 tag 的比較仍可用。
- ❌「32GB 以下的 Mac 會自動退回 llama.cpp」：程式碼沒有這個記憶體門檻，分流只看格式 [5]。32GB 只是官方建議 [2]。
- ❌「Ollama 的 MLX 在 v0.30 已脫離 preview」：只有一個第三方部落格這樣說，還誤引了發行說明；v0.30 的更新重點其實是 llama.cpp 那一側 [4]。官方至今沒有宣布 MLX 正式版。
- ❌「M5 的首字加速只有 MLX 拿得到」：上游 llama.cpp 已支援 Metal 4 tensor API [9][8]。
- ⚠️ Ollama FAQ 的「預設 4096 上下文」已過時 [26][27]；「並行數自動選 4 或 1」也已過時 [49]；OpenAI 相容頁面寫不支援 logprobs，也已過時 [24][25]。
- ⚠️「macOS 在 64GB 以下只給 GPU 2/3」：日誌顯示 36GB 的機器就已經是 3/4 [28]。

**來源之間的分歧**：

- **MLX 的長上下文 prefill**：mlx-lm issue [15] 與 famstack [13] 都說 MLX 較慢；一篇 SEO 色彩較重的部落格則說 MLX 0.22 的 adaptive flash attention 讓它在 32K 反而快 25%（只看到搜尋摘要，沒能打開頁面驗證，沒有列入來源）。版本不同，結論可能都對。
- **Ollama MLX 的增益**：官方在 M5 上量到接近 2 倍 [2]，獨立測試在 M2／M4 上幾乎沒差 [16][17]。兩者不矛盾，比較可能是晶片不同。
- **32GB 門檻到底是建議還是限制**：一篇 Qiita 實測在 M4 32GB 上載入 35B 模型逾時失敗 [57]，程式碼卻沒有強制門檻 [5]。兩者不衝突：沒有門檻，不代表跑得動。

**未解問題**：

- M5 Pro／Max／Ultra 上，MLX 與新版 llama.cpp 在相同位元下的獨立對照。
- NVFP4 與 Q4_K_M、MLX 4-bit 的困惑度（perplexity）比較。搜尋摘要有「Q4_K_M 的困惑度劣化比 MLX 4-bit 低 4.7 倍」的說法，但沒能找到原始數據。
- `mlx_lm.server` 的工具呼叫與 batching 目前只寫在程式碼裡，文件沒寫，行為可能還會變。

## 十、研究方法與限制

- **結構**：工具比較骨架（選項 → 評比標準 → 各標準分章 → 決策矩陣 → 建議）。
- **研究角度（5 個）**：①Apple Silicon 上的效能；②架構關係與模型格式；③功能與生態；④上手、維運與社群爭議；⑤時間與硬體。第 ⑤ 個是缺口檢查補上的，對應「時間」與「可行性」兩個盲點。
- **語言**：英文與日文都完整搜尋。英文 47 個來源、日文 10 個；日文來源以個人實測與實務文章為主。
- **查證**：挑 12 條關鍵事實說法，交給 4 個子代理去找反證；另外確認 1 條意見說法確實出自其來源。
  - 沒有一條被完全推翻。
  - 6 條需要部分修正：Ollama 的 MLX 狀態、MLX 與 llama.cpp 的速度倍數、預設上下文、並行預設值、macOS GPU 上限的分界、logprobs。
  - 途中另外推翻 3 條第三方說法：`OLLAMA_MLX=1`、「v0.30 MLX 已是正式版」、「M5 加速只有 MLX 有」。
- **引用核對**：由一個獨立子代理逐項核對約 110 項（數字、日期、比例、引文、歸屬、因果說法）。先對照來源資料，對不上的 4 項再打開原網頁確認，結果全部通過、0 項不符，所以沒有做任何修改。之後補上的 1 句（第〈六〉章 45GB 的成因）是依照核對時查到的原文寫的，已再對照一次。
- **來源偏差**：
  - 效能數字多來自個人部落格，量化設定常常不完全對等。
  - 有一個來源 [14] 自稱「100% AI 生成」，只用來輔助，不單獨支撐結論。
  - Ollama 與 Apple 的數字是廠商自測，信心度上限為 Medium。
- **時效**：本筆記反映 2026-09-24 的狀態。Ollama 大約每幾週就發一版；M5 Ultra 剛開賣，獨立評測預計幾週內出現；macOS 27 預計今年秋天推出，可能改變 Neural Accelerator 與 RDMA 的支援。**建議 2027 年初重看一次。**

## 十一、下一步

1. **先確認你的 Mac 記憶體與晶片**：記憶體決定能跑多大的模型，晶片世代決定 prefill 速度，然後照〈八〉的表挑工具。
2. **用 Ollama 的話，第一件事就是設定上下文長度**：例如 `launchctl setenv OLLAMA_CONTEXT_LENGTH 32768` 後重開 Ollama，32GB 以下的 Mac 尤其要做 [5][26]。
3. **用自己的工作量實測**：拿同一個模型的 MLX 4-bit 與 GGUF Q4_K_M，分別在 mlx-lm 和 llama-server 上用你真實的 prompt 長度量 prefill 和生成速度。短對話與長 RAG 的結論可能相反。
4. **要跑大模型又卡在記憶體**，可以考慮調高 `iogpu.wired_limit_mb`，但要留系統記憶體，而且重開機會還原 [30]。
5. **M5 使用者**：確認用的 llama.cpp 是支援 tensor API 的新版上游 build，不要用 app 內建的舊 runtime [9][10]。

## 附錄：來源清單

1. Exploring LLMs with MLX and the Neural Accelerators in the M5 GPU — Apple Machine Learning Research — https://machinelearning.apple.com/research/exploring-llms-mlx-m5 — en — accessed 2026-09-24
2. Ollama is now powered by MLX on Apple Silicon in preview — Ollama Blog — https://ollama.com/blog/mlx — en — accessed 2026-09-24
3. Ollama's highest performance on Apple Silicon yet with MLX — Ollama Blog — https://ollama.com/blog/mlx-performance — en — accessed 2026-09-24
4. Releases · ollama/ollama — GitHub — https://github.com/ollama/ollama/releases — en — accessed 2026-09-24
5. ollama/ollama 原始碼（server/images.go、server/sched.go、envconfig/config.go、server/routes.go、server/prompt.go、openai/openai.go、docs/context-length.mdx） — GitHub — https://github.com/ollama/ollama — en — accessed 2026-09-24
6. Ollama's new engine for multimodal models — Ollama Blog — https://ollama.com/blog/multimodal-models — en — accessed 2026-09-24
7. Production-Grade Local LLM Inference on Apple Silicon: A Comparative Study of MLX, MLC-LLM, Ollama, llama.cpp, and PyTorch MPS — arXiv — https://arxiv.org/abs/2511.05502 — en — accessed 2026-09-24
8. Performance of llama.cpp on Apple Silicon M-series (Discussion #4167) — ggml-org / GitHub — https://github.com/ggml-org/llama.cpp/discussions/4167 — en — accessed 2026-09-24
9. metal : initial Metal4 tensor API support (PR #16634) — ggml-org / GitHub — https://github.com/ggml-org/llama.cpp/pull/16634 — en — accessed 2026-09-24
10. LM Studio bug tracker issue #2040（M5 Max tensor API disabled） — lmstudio-ai / GitHub — https://github.com/lmstudio-ai/lmstudio-bug-tracker/issues/2040 — en — accessed 2026-09-24
11. Qwen3.5 on Apple Silicon benchmark — Ante Kapetanovic — https://antekapetanovic.com/blog/qwen3.5-apple-silicon-benchmark/ — en — accessed 2026-09-24
12. apple-silicon-llm-bench — john-rocky / GitHub — https://github.com/john-rocky/apple-silicon-llm-bench — en — accessed 2026-09-24
13. MLX vs GGUF on Apple Silicon — famstack.dev — https://famstack.dev/guides/mlx-vs-gguf-apple-silicon/ — en — accessed 2026-09-24
14. MLX vs llama.cpp on Apple Silicon: Benchmarks, M5 Neural Accelerators, and Why Ollama Switched — yage.ai — https://yage.ai/share/mlx-apple-silicon-en-20260331.html — en — accessed 2026-09-24
15. mlx-lm issue #763（long-context generation slower than llama.cpp） — ml-explore / GitHub — https://github.com/ml-explore/mlx-lm/issues/763 — en — accessed 2026-09-24
16. Apple MLX × Ollama deep dive — DevelopersIO（クラスメソッド） — https://dev.classmethod.jp/articles/apple-mlx-ollama-deep-dive/ — ja — accessed 2026-09-24
17. Local LLM benchmark on M4 Max (2026-05-10) — kyu.co — https://kyu.co/posts/local-llm-m4-max-benchmark-2026-05-10/ — en — accessed 2026-09-24
18. [2026年5月最新] Macでローカルで一番速いのは結局どれ？mlx-lm / vllm-mlx / oMLX / Ollama / LM Studio 徹底比較 — note.com（zephel01） — https://note.com/zephel01/n/ncf2b8b652c01 — ja — accessed 2026-09-24
19. llama.cpp server README — ggml-org / GitHub — https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md — en — accessed 2026-09-24
20. mlx-lm SERVER.md — ml-explore / GitHub — https://github.com/ml-explore/mlx-lm/blob/main/mlx_lm/SERVER.md — en — accessed 2026-09-24
21. mlx-lm server.py — ml-explore / GitHub — https://github.com/ml-explore/mlx-lm/blob/main/mlx_lm/server.py — en — accessed 2026-09-24
22. ml-explore/mlx-lm README — Apple / GitHub — https://github.com/ml-explore/mlx-lm — en — accessed 2026-09-24
23. Blaizzy/mlx-vlm README — GitHub — https://github.com/Blaizzy/mlx-vlm — en — accessed 2026-09-24
24. OpenAI compatibility — Ollama docs — https://docs.ollama.com/api/openai-compatibility — en — accessed 2026-09-24
25. server: add logprobs and top_logprobs support to Ollama's API (#12899) — ollama / GitHub — https://github.com/ollama/ollama/commit/59241c5bee60bc49e96589a7a7482f964fe7ffe0 — en — accessed 2026-09-24
26. FAQ — Ollama docs — https://docs.ollama.com/faq — en — accessed 2026-09-24
27. Use tiered VRAM-based default context length (PR #13946) — ollama / GitHub — https://github.com/ollama/ollama/pull/13946 — en — accessed 2026-09-24
28. ollama issue #2370（36GB M3 recommendedMaxWorkingSetSize） — ollama / GitHub — https://github.com/ollama/ollama/issues/2370 — en — accessed 2026-09-24
29. ollama issue #11686（32GB recommendedMaxWorkingSetSize） — ollama / GitHub — https://github.com/ollama/ollama/issues/11686 — en — accessed 2026-09-24
30. llama.cpp Discussion #2182（iogpu.wired_limit_mb） — ggml-org / GitHub — https://github.com/ggml-org/llama.cpp/discussions/2182 — en — accessed 2026-09-24
31. GGML and llama.cpp join Hugging Face — Hugging Face Blog — https://huggingface.co/blog/ngxson/ggml-and-llama-cpp-join-hugging-face — en — accessed 2026-09-24
32. 1,175 Redditors Just Told You to Stop Using Ollama — DEV Community（jamilxt） — https://dev.to/jamilxt/1175-redditors-just-told-you-to-stop-using-ollama-heres-why-local-ai-tooling-got-serious-2eia — en — accessed 2026-09-24
33. ollama doesn't distribute notice licenses in its release artifacts（issue #3185） — ollama / GitHub — https://github.com/ollama/ollama/issues/3185 — en — accessed 2026-09-24
34. LM Studio 0.3.4 ships with Apple MLX — LM Studio Blog — https://lmstudio.ai/blog/lmstudio-v0.3.4 — en — accessed 2026-09-24
35. llama.cpp tools/quantize README — ggml-org / GitHub — https://github.com/ggml-org/llama.cpp/blob/master/tools/quantize/README.md — en — accessed 2026-09-24
36. mlx-lm LEARNED_QUANTS.md — ml-explore / GitHub — https://github.com/ml-explore/mlx-lm/blob/main/mlx_lm/LEARNED_QUANTS.md — en — accessed 2026-09-24
37. MLX vs GGUF: How 4-bit Quantisation Really Works — TensorFoundry — https://tensorfoundry.io/blog/mlx-vs-gguf-quantisation — en — accessed 2026-09-24
38. メモリ32GBのMacでLLMファインチューニングを試す(MLX-LM LoRA) — o-84.com — https://o-84.com/article/llm-finetune-on-mac32gb/ — ja — accessed 2026-09-24
39. I tested Unsloth's new desktop app — XDA Developers — https://www.xda-developers.com/tested-unsloth-new-desktop-app/ — en — accessed 2026-09-24
40. Apple introduces new Mac Studio with M5 Max and M5 Ultra — Apple Newsroom — https://www.apple.com/newsroom/2026/08/apple-introduces-new-mac-studio-with-m5-max-and-m5-ultra/ — en — accessed 2026-09-24
41. Apple debuts M5 Pro and M5 Max — Apple Newsroom — https://www.apple.com/newsroom/2026/03/apple-debuts-m5-pro-and-m5-max-to-supercharge-the-most-demanding-pro-workflows/ — en — accessed 2026-09-24
42. Explore distributed inference and training with MLX（WWDC26 session 233） — Apple Developer — https://developer.apple.com/videos/play/wwdc2026/233/ — en — accessed 2026-09-24
43. Mac StudioでローカルLLMは動くのか｜64GBで実測したメモリの決め方 — スーログ — https://blog.skeg.jp/archives/2026/09/mac-studio-local-llm-memory.html — ja — accessed 2026-09-24
44. ローカルLLMに何GB必要か、Mac 3台で測った — Elcamy Tech Blog — https://blog.elcamy.com/articles/local-llm-ram-8-16-32gb — ja — accessed 2026-09-24
45. llama-serverの使い方｜ローカルLLMをOpenAI互換APIとして動かす実践ガイド — クリスタルメソッド — https://crystal-method.com/blog/llama-server/ — ja — accessed 2026-09-24
46. Mac MシリーズでローカルLLMを動かすなら Ollama / mlx-lm / vllm-mlx のどれを使うべきか — Qiita（engchina） — https://qiita.com/engchina/items/656833a334a99615205a — ja — accessed 2026-09-24
47. Ollama MLX on Apple Silicon — Zenn（takish） — https://zenn.dev/takish/articles/ollama-mlx-apple-silicon — ja — accessed 2026-09-24
48. GGUF・safetensors・MLX・Ollamaの違い — Local AI Compass — https://localaicompass.kawaii-girl.com/articles/gguf-vs-safetensors-mlx-ollama/ — ja — accessed 2026-09-24
49. Reduce default parallelism to 1 (PR #11330) — ollama / GitHub — https://github.com/ollama/ollama/pull/11330 — en — accessed 2026-09-24
50. Ollama's Default Context Length, and Why It Is Not the Number You Read — Multigrid — https://multigrid.ai/learn/ollama-default-context-limit — en — accessed 2026-09-24
51. ggml-org/llama.cpp README — GitHub — https://github.com/ggml-org/llama.cpp — en — accessed 2026-09-24
52. ml-explore/mlx README — Apple / GitHub — https://github.com/ml-explore/mlx — en — accessed 2026-09-24
53. Structured Outputs — Ollama docs — https://docs.ollama.com/capabilities/structured-outputs — en — accessed 2026-09-24
54. llama.cpp docs/multimodal.md — ggml-org / GitHub — https://github.com/ggml-org/llama.cpp/blob/master/docs/multimodal.md — en — accessed 2026-09-24
55. Ollama — Wikipedia — https://en.wikipedia.org/wiki/Ollama — en — accessed 2026-09-24
56. mlx.core.quantize — MLX documentation — https://ml-explore.github.io/mlx/build/html/python/_autosummary/mlx.core.quantize.html — en — accessed 2026-09-24
57. Ollama 0.19のMLX対応でApple Siliconのローカル推論が変わる — 速度比較と実測 — Qiita（takish） — https://qiita.com/takish/items/3e256b37d2c4b3d8d459 — ja — accessed 2026-09-24
