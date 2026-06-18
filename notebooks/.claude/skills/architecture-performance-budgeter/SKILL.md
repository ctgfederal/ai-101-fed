---
name: performance-budgeter
description: Define, track, and enforce performance budgets for applications to ensure consistent user experience and system reliability.
version: 1.0.0
---

# Performance Budgeter Skill

## Purpose
Define, track, and enforce performance budgets for applications to ensure consistent user experience and system reliability.

## Inputs
- **Scope**: api, frontend, database, all
- **Action**: define, check, update, report
- **Metrics**: Specific performance metrics to work with

## Output
- Performance budget definitions
- Compliance reports
- Violation alerts
- Optimization recommendations

## Budget Structure

File: `architecture/performance-budgets.json`

```json
{
  "api": {
    "responseTime": {
      "p50": "100ms",
      "p95": "300ms",
      "p99": "500ms",
      "max": "2s"
    },
    "throughput": {
      "requestsPerSecond": 1000,
      "concurrentConnections": 500
    },
    "payload": {
      "maxRequestSize": "1MB",
      "maxResponseSize": "5MB"
    },
    "errors": {
      "maxErrorRate": "0.1%"
    }
  },
  "frontend": {
    "loading": {
      "maxBundleSize": "200KB",
      "maxInitialLoadTime": "2s",
      "maxFirstContentfulPaint": "1s",
      "maxTimeToInteractive": "3s",
      "maxLargestContentfulPaint": "2.5s"
    },
    "runtime": {
      "maxMainThreadBlockingTime": "200ms",
      "maxCumulativeLayoutShift": 0.1
    },
    "resources": {
      "maxImageSize": "100KB",
      "maxFontSize": "50KB",
      "maxCSSSize": "50KB",
      "maxJSSize": "200KB"
    }
  },
  "database": {
    "queries": {
      "maxQueryTime": "50ms",
      "maxSlowQueryPercent": "1%"
    },
    "connections": {
      "maxPoolSize": 20,
      "maxIdleTime": "10m"
    },
    "storage": {
      "maxDiskIOPS": 1000,
      "maxMemoryUsage": "2GB"
    }
  }
}
```

## Budget Definitions

### API Budgets

**Response Time Budgets**:
- p50 (median): 50% of requests
- p95: 95% of requests
- p99: 99% of requests
- max: No request should exceed

**Throughput Budgets**:
- Requests per second capacity
- Concurrent connection limit

**Payload Budgets**:
- Request size limits
- Response size limits

### Frontend Budgets

**Core Web Vitals**:
- LCP (Largest Contentful Paint): < 2.5s
- FID (First Input Delay): < 100ms
- CLS (Cumulative Layout Shift): < 0.1

**Loading Performance**:
- Bundle size budgets
- Initial load time
- Time to Interactive

**Resource Budgets**:
- Images, fonts, CSS, JS sizes

### Database Budgets

**Query Performance**:
- Average query time
- Slow query threshold
- Query timeout

**Connection Management**:
- Pool size
- Connection timeout
- Idle timeout

## Budget Check Process

### Step 1: Load Budgets
Read from `architecture/performance-budgets.json`

### Step 2: Collect Metrics
Gather actual performance data:
- From monitoring systems
- From test results
- From profiling

### Step 3: Compare Against Budgets
For each metric:
- Check if within budget
- Calculate variance
- Identify violations

### Step 4: Generate Report

```markdown
# Performance Budget Report

## Summary
- ✅ Within Budget: 18 metrics
- ⚠️ Warning (90-100%): 4 metrics
- ❌ Over Budget: 2 metrics

## Critical Violations

### API Response Time - p95
**Budget**: 300ms
**Actual**: 450ms
**Variance**: +50% (150ms over)
**Status**: ❌ VIOLATION

**Impact**: Degraded user experience on 5% of requests

**Recommendations**:
1. Add database query index on users.email
2. Implement response caching
3. Optimize data serialization

**Related**:
- Query: `getUserProfile` averaging 250ms
- Database: Missing index TD-008

---

### Frontend Bundle Size
**Budget**: 200KB
**Actual**: 285KB
**Variance**: +42.5% (85KB over)
**Status**: ❌ VIOLATION

**Impact**: Slower initial load, especially on mobile

**Breakdown**:
- Main bundle: 180KB (90KB budget)
- Vendor bundle: 105KB (110KB budget)

**Recommendations**:
1. Code splitting for large components
2. Tree-shake unused lodash methods
3. Lazy load charting library

---

## Warnings (Near Budget)

### API Response Time - p99
**Budget**: 500ms
**Actual**: 475ms
**Variance**: 95% of budget
**Status**: ⚠️ WARNING

Close to budget limit. Monitor closely.

---

## Compliant Metrics

✅ API p50 response time: 85ms (budget: 100ms)
✅ Database query time: 32ms avg (budget: 50ms)
✅ Frontend FCP: 0.9s (budget: 1s)
✅ LCP: 2.1s (budget: 2.5s)
```

## Budget Enforcement

### During Development
- Warn when approaching budget
- Block if significantly over budget
- Suggest optimizations

### During Code Review
- Check impact on budgets
- Require optimization plan if over
- Track budget trends

### In CI/CD
- Run budget checks in pipeline
- Fail build if critical budgets violated
- Generate performance reports

## Budget Adjustment

Budgets should be reviewed quarterly:

```markdown
## Budget Review: Q4 2025

**Current Budgets**: Set Q3 2025
**Performance Trends**: Improving
**User Feedback**: Positive

**Proposed Changes**:
1. Tighten API p95: 300ms → 250ms
   Rationale: Consistently under 250ms for 2 months

2. Increase frontend bundle: 200KB → 220KB
   Rationale: New features justify +10% increase

3. Maintain database budgets
   Rationale: Currently optimal

**Approval**: Principal Engineer
**Effective**: 2025-11-01
```

## Optimization Strategies

### API Performance
- Add caching layers
- Optimize database queries
- Use connection pooling
- Implement rate limiting
- Add CDN for static content

### Frontend Performance
- Code splitting
- Lazy loading
- Image optimization
- Tree shaking
- Compression

### Database Performance
- Add indexes
- Query optimization
- Connection pooling
- Read replicas
- Caching layer

## Monitoring Integration

Performance budgets should integrate with:
- **Application Monitoring**: Real-time metrics
- **Synthetic Monitoring**: Automated checks
- **Real User Monitoring (RUM)**: Actual user experience
- **CI/CD Pipeline**: Pre-deployment checks

## Budget Templates

### New API Endpoint
```json
{
  "endpoint": "/api/users",
  "budgets": {
    "p50": "100ms",
    "p95": "300ms",
    "p99": "500ms",
    "throughput": 1000
  }
}
```

### New Frontend Page
```json
{
  "page": "/dashboard",
  "budgets": {
    "bundleSize": "200KB",
    "FCP": "1s",
    "LCP": "2.5s",
    "TTI": "3s"
  }
}
```

## Remember

Performance budgets are:
- ✅ Proactive (prevent problems)
- ✅ Measurable (objective metrics)
- ✅ Actionable (clear when violated)
- ✅ Living documents (adjust based on data)

Balance performance with feature velocity - budgets should enable quality, not block progress.
