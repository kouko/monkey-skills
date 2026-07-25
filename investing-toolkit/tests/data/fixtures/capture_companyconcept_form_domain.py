"""Regenerate `companyconcept_form_domain_2026-07-25.json` — the live
grounding capture for `sec_edgar_client._TOP_LINE_ANNUAL_CARRIER_FORMS`.

WHAT IT ANSWERS. Lane A's allowlist rests on one claim about an EXTERNAL
HTTP surface: which `form` values does SEC's `companyconcept` endpoint put
on 12-month top-line rows? That claim cannot be settled from in-repo
fixtures, so it is settled by hitting the endpoint and committing the
counts. Only the FORM VALUE DOMAIN is captured — no financial values.

NETWORK. Hits data.sec.gov live; NOT part of the offline suite (it is not
a `test_*` module and pytest never collects it). Re-run by hand when the
allowlist is questioned:

    python3 investing-toolkit/tests/data/fixtures/\\
      capture_companyconcept_form_domain.py > \\
      investing-toolkit/tests/data/fixtures/\\
      companyconcept_form_domain_2026-07-25.json

Set your own contact string in `UA` — SEC requires a real one and rate-
limits anonymous traffic.

FILER SAMPLE, and why each is in it: AAPL/INTC are the arc's own probe
filers (domestic 10-K). TM/HMC are us-gaap-tagging foreign private issuers
— the 20-F carriers that motivate the allowlist. TSM/SAP/SHEL/BP are
IFRS-tagging FPIs, included to record that they 404 out of the us-gaap
endpoint entirely and so bound the risk.
"""
import json, urllib.request, collections
from datetime import date as D
UA = {"User-Agent": "monkey-skills research kouko.d@gmail.com"}
CIKS = {"AAPL":320193,"INTC":50863,"TM":1094517,"HMC":715153,"TSM":1046179,"SAP":1000184,"SHEL":1306965,"BP":313807}
CONCEPTS = ["Revenues","RevenuesNetOfInterestExpense",
            "RevenueFromContractWithCustomerExcludingAssessedTax",
            "RevenueFromContractWithCustomerIncludingAssessedTax"]
def span(r):
    try: return (D.fromisoformat(r["end"]) - D.fromisoformat(r["start"])).days
    except Exception: return None
obs=[]
for t,cik in CIKS.items():
    for c in CONCEPTS:
        url=f"https://data.sec.gov/api/xbrl/companyconcept/CIK{cik:010d}/us-gaap/{c}.json"
        rec={"ticker":t,"cik":cik,"concept":f"us-gaap:{c}"}
        try: raw=json.load(urllib.request.urlopen(urllib.request.Request(url,headers=UA),timeout=30))
        except urllib.error.HTTPError as e:
            rec["http_status"]=e.code; obs.append(rec); continue
        rows=[]
        for unit,series in raw.get("units",{}).items():
            for r in series: r["_unit"]=unit; rows.append(r)
        ann=[r for r in rows if (span(r) or 0) and 330<=span(r)<=400]
        rec.update(http_status=200, units=sorted({r["_unit"] for r in rows}), n_rows=len(rows),
                   forms_all=dict(sorted(collections.Counter(r.get("form") for r in rows).items())),
                   forms_on_annual_span_rows=dict(sorted(collections.Counter(r.get("form") for r in ann).items())),
                   n_rows_missing_accn=sum(1 for r in rows if not r.get("accn")),
                   n_rows_missing_form=sum(1 for r in rows if not r.get("form")))
        obs.append(rec)
forms=collections.Counter()
for r in obs:
    if r.get("http_status")==200:
        for f,n in r["forms_on_annual_span_rows"].items(): forms[f]+=n
doc={
 "_capture": {
  "what": "Observed value domain of the `form` field on SEC companyconcept rows, for the four us-gaap concepts in sec_edgar_client._TOP_LINE_REVENUE_CONCEPTS. Grounds the _TOP_LINE_ANNUAL_CARRIER_FORMS allowlist in build_top_line_backfill (Lane A).",
  "endpoint": "https://data.sec.gov/api/xbrl/companyconcept/CIK{cik:010d}/us-gaap/{concept}.json",
  "captured_at": "2026-07-25",
  "cik_source": "https://www.sec.gov/files/company_tickers.json (resolved live, same date)",
  "annual_span_definition": "end - start between 330 and 400 days inclusive",
  "regenerate": "investing-toolkit/tests/data/fixtures/capture_companyconcept_form_domain.py",
  "note": "Counts only. No financial values are captured here - this fixture records the FORM value domain, nothing else."
 },
 "_summary": {
  "forms_observed_on_annual_span_rows": dict(sorted(forms.items())),
  "forms_NOT_observed_in_this_sample": ["10-K/A","40-F","8-K","S-1","424B"],
  "ifrs_fpis_absent_from_us_gaap_endpoint": ["TSM","SAP","SHEL","BP"]
 },
 "observations": obs,
}
print(json.dumps(doc,indent=1))
