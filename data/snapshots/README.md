# Precomputed snapshots

Store ticker-keyed, versioned snapshots here (for example `INFY/financial_snapshot.json`).
A snapshot should include `ticker`, `as_of`, `source_manifest`, and content hashes for all source documents.
Read snapshot first; fall back to a live provider path for any NSE/BSE ticker with available data.
