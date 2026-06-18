# Source conversation excerpt

User: brief generation is taking 12 seconds for 50 records. Production logs show one SELECT against authors per brief.
Assistant: profiled with rack-mini-profiler. Confirmed N+1 on briefs.author. Added .includes(:author) — render dropped to 0.3s. Query count went 51 -> 2. Added a Bullet test in CI.
