# FINN integration blockers

This list tracks verification blockers independently from implementation status.

## Prompt 4 — Results Card

- **Pending:** Real-PDF verification using official Infosys, TCS and Reliance filings.
- **Blocker:** The execution environment blocks outbound HTTPS access to the official company filing hosts and package index. Earlier checks also found no compatible PDF parser packages or corresponding wheels in the local environment/cache.
- **Impact:** Actual filing extraction, financial validation against source pages, persistence of an actual generated card and retrieval of that card through FastAPI have not been demonstrated.
- **Status:** Not complete. No fixture or mocked extraction is represented as live verification.

## Prompt 5 — Management Change Intelligence

- **Resolved:** The server on port 3000 was the FINN Next.js process (HTTP runtime stack referenced this workspace's `frontend/.next`; PID 3504 was Node). A production build had overwritten the shared output while that dev process was active, causing the `./611.js` chunk mismatch. The server was stopped with SIGINT, the sandbox denied direct recursive cache deletion, and the sole Next dev server then regenerated usable output during normal startup.
- **Verified:** Mobile browser check at 390 CSS pixels, no horizontal overflow, management cards, ticker filter, empty state and mobile navigation. Frontend typecheck and production build passed with no dev server running during build.
- **Current state:** One Next dev server runs on port 3000; backend verification server runs on port 8013. No second Next server is using `.next`.
- **Note:** Events are derived from existing stored announcements; this feature does not fetch exchange announcements independently.
## Prompt 6 ? Intelligent Brief

- **Verified:** Digest endpoint combines available announcement, anomaly, results-card, management-change and enriched-filing records; deterministic ranking, explanations, grouping, filters, pagination and demo provenance are covered by tests and live requests.
- **Verified:** Brief filters, refresh, expansion, empty/error handling and company-research navigation were exercised in the browser. At 390, 768 and 1440 CSS pixels, document width did not exceed viewport width. Fresh 390px screenshot: `artifacts/brief-mobile-390.png`.
- **Checks:** Backend suite 132 passed; frontend typecheck passed; production build passed after stopping the dev server; related API regression routes returned HTTP 200. One dev server was restarted after the build.
- **Limitations:** Demo feed is fixture-backed and marked DEMO. Prompt 4's real filing PDF extraction remains pending as recorded above.
