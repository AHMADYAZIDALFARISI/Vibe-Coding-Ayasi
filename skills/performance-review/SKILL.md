---
name: performance-review
description: Find avoidable performance cost in a change. Use when a change adds dependencies, renders lists or media, adds network calls or database queries, or when the user reports slowness. Measures first and recommends the simplest fix that matches real load.
---

# Performance Review

Measure before recommending. Do not add caching, queues, or services for load the project does not have.

## Checks

1. New dependencies: size and whether the platform already covers the need.
2. Network: requests per user action, duplicated fetches, payload size.
3. Database: queries inside loops, missing indexes on filtered or joined columns, unbounded `SELECT *` on growing tables.
4. Rendering: work repeated on every render, layout shift from late-loading content, large unoptimized images.
5. Web pages: run Lighthouse or the browser performance panel when available and record LCP, CLS, and INP. Targets per web.dev: LCP 2.5 s or less, CLS 0.1 or less, INP 200 ms or less.

## Output

List each finding with the measurement, the cost, and the fix. Mark estimates as estimates.
