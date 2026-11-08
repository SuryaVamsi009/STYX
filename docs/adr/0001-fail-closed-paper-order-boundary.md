# Fail closed on paper-order isolation

Because broker credentials may be order-capable and Analyzer Mode's isolation is **UNVERIFIED** until checked against the installed version, Gate 0 uses route-specific proof rather than assuming Analyzer Mode is a sandbox. The gate requires version-matched documentation, a pre-order configuration and active-route audit, a virtual order record, a route-specific guard against real-broker order paths, and a read-only broker-side order-book check; missing or ambiguous evidence blocks the test, with no route fallback.
