---
description: "Tsundoku 積読 — turn your owned-but-unread e-book pile into actionable agent skills. Routes to kobo-auth / kobo-library / book-extract / book-distill based on intent (login / search / convert / distill)."
---

You are entering the tsundoku plugin. Based on the user's request, route to the
appropriate skill:

- **Setting up Kobo login / re-authenticating / importing credentials**
  → use `tsundoku:kobo-auth`
- **Searching the user's Kobo library / downloading EPUBs**
  → use `tsundoku:kobo-library`
- **Converting an EPUB to chunked Markdown**
  → use `tsundoku:book-extract`
- **Distilling a book into atomic agent skills (RIA-TV++ pipeline)**
  → use `tsundoku:book-distill`

If the user's intent is ambiguous or asks for an overview, briefly describe
the 4-stage pipeline (login → search/download → extract → distill) and ask
which step they want to start with. The natural sequence is:

```
kobo-auth → kobo-library → book-extract → book-distill
(once)      (daily)         (per book)     (per book)
```

For the very first time using tsundoku, recommend starting with `kobo-auth`
unless the user already has Kobo credentials they want to import.
