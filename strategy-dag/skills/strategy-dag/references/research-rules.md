# Research rules ／研究規則

When to answer inline, verify once, or spin up a standalone research
note — and the hard rule that keeps a plan's reasoning traceable back
to a source.

## When to do what

| Situation ／情況 | Action ／動作 | Where it lands ／落點 |
|---|---|---|
| Project docs already answer it ／專案內文件能回答 | Infer directly ／直接推論 | No extra record ／不需額外記錄 |
| One missing external fact needed to continue ／需要一個外部事實才能繼續 | Verify, at most ONE agent arm ／查證，最多一個臂 | **Must** write into the current note: one-line conclusion + source ／**必須**寫進當前筆記：一行結論＋出處 |
| Need to survey a topic ／需要盤點一個主題 | Standalone research note ／獨立研究筆記 | New file (e.g. via research-toolkit) ／新檔案 |
| User explicitly asks for research ／使用者明說要研究 | Standalone research note ／獨立研究筆記 | New file ／新檔案 |

## Hard rule ／硬規則

**Any external fact entering the reasoning must be findable in the docs.**
／**任何進入推論的外部事實，都必須在文件裡找得到出處。**
Verified in chat but not written down is not verified — the note is
the only record that survives the conversation. Do not rely on
"we discussed it earlier" as a citation.
／在對話裡驗過但沒寫進文件的，等於沒驗過。

## Agent-initiated search triggers

Four situations where the agent should search on its own, without
waiting to be asked:

1. Asserting something without a source ／斷言了一件沒有來源的事
2. A measurement result surprises ／量測結果出乎意料
3. About to make a judgment but missing a checkable fact ／要下判斷但缺一個可查事實
4. About to cite a name — a standard, paper, or number ／打算引用一個名字（標準、論文、數字）

> [!warning] Search triggers only catch cheap misses
> These triggers catch missing facts. They do not catch framework
> errors — being inside the wrong frame means nothing looks worth
> checking. The defense against a framework error is not search; it
> is the human gate question asked at every node boundary:
> 「這段推論建立在什麼假設上？你同意嗎？」
