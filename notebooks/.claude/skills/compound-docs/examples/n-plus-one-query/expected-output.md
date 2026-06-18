---
title: "N+1 query in brief generation"
category: performance-issues
date: 2026-02-14
tags: 
  - activerecord
  - rails
  - n+1
  - query-optimization
module: "BriefGenerator"
symptom: "Brief generation taking 12s for 50 records; SQL log shows one SELECT per record."
root_cause: "BriefGenerator.render iterated over briefs and accessed .author on each, triggering one query per row."
severity: high
---

# N+1 query in brief generation

## Symptom

Brief generation took ~12s for 50 records. SQL log showed one SELECT against `authors` per brief. Symptom reported by ops after a customer dashboard timed out.

## Investigation

1. **Tried**: profiled with `rack-mini-profiler` — **Result**: confirmed 50+ identical queries against `authors`, indicating N+1.
2. **Tried**: cached `briefs.first.author` in a local — **Result**: did not help (different objects per row).
3. **Tried**: `briefs.includes(:author)` — **Result**: render dropped to 0.3s, query count 51 → 2.

## Root Cause

ActiveRecord lazy-loads belongs_to associations. `BriefGenerator#render` iterated `briefs.each` and called `b.author.name` per row, triggering one query each. The fix is to eager-load via `includes`.

## Solution

```ruby
# app/services/brief_generator.rb
class BriefGenerator
  def render(brief_ids)
    Brief.where(id: brief_ids).includes(:author).map { |b| line(b) }
  end
end
```

## Verification

1. Reproduce with 50 briefs in dev: render time < 0.5s.
2. SQL log shows 2 queries: one for briefs, one for authors.
3. New test asserts query count: `expect { generator.render(ids) }.to make_database_queries(count: 2)`.

## Prevention

- Bullet gem in development to flag N+1 at request time.
- RSpec matcher `make_database_queries(count:)` on every index/list endpoint.
- Code-review checklist item: any `each + association.attr` requires `includes`.

## Related

- See `runtime-errors/2025-12-01-stale-author-cache.md` for the *opposite* mistake (eager-loading the wrong association).
