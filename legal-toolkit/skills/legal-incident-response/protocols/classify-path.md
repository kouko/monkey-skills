# Protocol — classify-path

The Step 0 classifier for legal-incident-response. Auto-classifies user's free-text incident description into one of 3 paths (pii-breach / authority-letter / contract-breach). User confirms before pipeline dispatches.

## Input

- `description` (str): user's free-text incident description, e.g., "今天早上發現有 8000 筆客戶資料被異常存取"

## Pipeline

### Step 0.1: Run deterministic keyword scan

```bash
python3 legal-toolkit/skills/legal-incident-response/scripts/classify_path.py \
  "<description>" \
  legal-toolkit/skills/legal-incident-response/assets/path-classifier-keywords.yml
```

Output JSON: `{"matched_paths": [...], "signals": {"pii-breach": [...], ...}}`.

### Step 0.2: LLM confidence judgement

Read the description full text + Step 0.1 signals output. Determine:

- **inferred_type**: which of (pii-breach / authority-letter / contract-breach) is the PRIMARY path
- **confidence**: HIGH / MEDIUM / LOW
- **rationale**: 1-2 sentences explaining why

Confidence rubric:

| Signals | Description match | Confidence |
|---|---|---|
| ≥ 3 keywords matched for 1 path, none for others | clear narrative fit | HIGH |
| ≥ 2 keywords matched + clear context fit | likely fit | MEDIUM |
| 1 keyword matched OR multi-path keywords | ambiguous | LOW |
| 0 keywords matched | description out-of-scope | (escalate; ASK user clarification) |

If `matched_paths` is empty: emit `inferred_type=null` + `confidence=NONE` and ASK user "請問這個事件比較像：(1) 個資外洩 (2) 主管機關函覆 (3) 合約違約？或您能再多描述一些細節？"

### Step 0.3: Confirm with user

Present to user:

```
事件分類：{{inferred_type_zh}}（{{inferred_type_en}}）
信心度：{{confidence}}
匹配關鍵字：{{signals[inferred_type]}}
判斷理由：{{rationale}}

請確認：
- 按 Enter 繼續走 {{inferred_type_zh}} 流程
- 輸入 1 / 2 / 3 切換 path（1=個資外洩 / 2=主管機關函覆 / 3=合約違約）
- 輸入 'q' 取消
```

If user confirms: proceed to Step 1 LOAD_PROFILE (in main pipeline). If user overrides: re-run classify-path with the override + continue.

### Step 0.4: Edge case — multi-path detection

If `matched_paths` ≥ 2 (e.g., "金管會來函說有客戶資料外洩，7 日內說明" matches both authority-letter + pii-breach):

- inferred_type = primary path (typically the OUTER trigger — here authority-letter, because 函 來文 deadline is the URGENT axis; pii-breach analysis runs INSIDE the 函覆 prep)
- LLM mentions secondary path in rationale: "本事件同時涉及 PII-breach 內容；可先走 authority-letter path（外部 deadline 緊），同 session 後續可再跑 pii-breach path 詳處 PDPC 通報"
- Confidence MEDIUM (not HIGH due to ambiguity)

## Output

JSON snippet returned to main pipeline:

```json
{
  "inferred_type": "authority-letter",
  "confidence": "MEDIUM",
  "signals_matched": ["金管會", "函", "日內", "客戶資料"],
  "rationale": "...",
  "secondary_path_hint": "pii-breach"
}
```

Main pipeline reads `inferred_type` for dispatch.
