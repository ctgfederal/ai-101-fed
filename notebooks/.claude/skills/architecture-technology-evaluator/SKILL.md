---
name: technology-evaluator
description: Systematically evaluate new technologies, libraries, and tools for potential adoption in the codebase.
version: 1.0.0
---

# Technology Evaluator Skill

## Purpose
Systematically evaluate new technologies, libraries, and tools for potential adoption in the codebase.

## Inputs
- **Technology Name**: What to evaluate
- **Category**: library, framework, tool, service, language
- **Purpose**: What problem it would solve
- **Current Alternative**: What we use now (if applicable)

## Output
- Comprehensive evaluation report
- Recommendation (adopt, trial, assess, hold)
- Risk assessment
- Integration plan (if recommended)

## Evaluation Criteria

### 1. Technical Fit (Weight: 30%)
- Solves the specific problem well
- Performance characteristics
- Scalability
- Security posture
- Integration complexity

### 2. Maturity & Stability (Weight: 25%)
- Production-ready
- Version stability
- Breaking change frequency
- Deprecation risk
- Longevity indicators

### 3. Community & Support (Weight: 20%)
- Active development
- Community size
- Issue response time
- Documentation quality
- Commercial support available

### 4. Developer Experience (Weight: 15%)
- Learning curve
- API design
- Tool

ing support
- Debugging capabilities
- Error messages

### 5. Operational Considerations (Weight: 10%)
- Maintenance burden
- Monitoring/observability
- Deployment complexity
- Resource requirements
- Cost implications

## Evaluation Process

### Step 1: Research Phase
- Read official documentation
- Review GitHub/repository activity
- Check community forums/discussions
- Find production usage examples
- Identify known issues

### Step 2: Scoring Phase
Rate each criterion (1-5 scale):
```
5 = Excellent
4 = Good
3 = Acceptable
2 = Concerning
1 = Poor
```

Calculate weighted score:
```
Total Score =
  (Technical Fit × 0.30) +
  (Maturity × 0.25) +
  (Community × 0.20) +
  (Developer Experience × 0.15) +
  (Operational × 0.10)
```

### Step 3: Risk Assessment
Identify risks:
- Adoption risk (learning curve, migration effort)
- Technical risk (performance, bugs, limitations)
- Operational risk (maintenance, support, cost)
- Strategic risk (vendor lock-in, deprecation)

### Step 4: Recommendation
Based on total score:
- **4.0-5.0**: ADOPT (use for new projects)
- **3.0-3.9**: TRIAL (pilot in non-critical area)
- **2.0-2.9**: ASSESS (keep watching, not ready)
- **0.0-1.9**: HOLD (do not use)

## Evaluation Report Template

```markdown
# Technology Evaluation: {Technology Name}

**Date**: {YYYY-MM-DD}
**Evaluator**: Principal Engineer
**Category**: {library|framework|tool|service|language}
**Purpose**: {What problem does this solve}

## Executive Summary

{2-3 sentence summary of evaluation and recommendation}

**Recommendation**: [ADOPT | TRIAL | ASSESS | HOLD]
**Overall Score**: {X.X}/5.0

## Technology Overview

**Name**: {Full name}
**Version**: {Current stable version}
**License**: {License type}
**Repository**: {GitHub URL}
**Website**: {Official site}

**Description**: {What is this technology}

**Primary Use Case**: {What it's designed for}

**Current Alternative**: {What we use now, if any}

## Evaluation Scores

| Criterion | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| Technical Fit | {X}/5 | 30% | {X.XX} |
| Maturity & Stability | {X}/5 | 25% | {X.XX} |
| Community & Support | {X}/5 | 20% | {X.XX} |
| Developer Experience | {X}/5 | 15% | {X.XX} |
| Operational | {X}/5 | 10% | {X.XX} |
| **Total** | | | **{X.XX}/5.0** |

## Detailed Analysis

### Technical Fit ({X}/5)

**Strengths**:
- {Strength 1}
- {Strength 2}

**Weaknesses**:
- {Weakness 1}
- {Weakness 2}

**Performance Characteristics**:
- {Performance notes}

**Integration Complexity**: {Low|Medium|High}
- {Integration considerations}

### Maturity & Stability ({X}/5)

**Version History**:
- First release: {Date}
- Current version: {Version}
- Release frequency: {Frequency}

**Stability Indicators**:
- Breaking changes: {Frequency}
- Deprecation policy: {Policy}
- Backward compatibility: {Assessment}

**Production Usage**:
- {Company 1} uses it for {purpose}
- {Company 2} uses it for {purpose}

### Community & Support ({X}/5)

**Community Metrics**:
- GitHub stars: {Number}
- Contributors: {Number}
- Open issues: {Number}
- Issue response time: {Average}

**Documentation**: {Poor|Fair|Good|Excellent}
- {Documentation assessment}

**Commercial Support**: {Available|Not Available}

### Developer Experience ({X}/5)

**Learning Curve**: {Gentle|Moderate|Steep}
- {Learning assessment}

**API Design**: {Poor|Fair|Good|Excellent}
- {API quality notes}

**Tooling Support**:
- IDE support: {Level}
- Debugging: {Quality}
- Testing: {Support}

### Operational Considerations ({X}/5)

**Maintenance Burden**: {Low|Medium|High}
- {Maintenance notes}

**Resource Requirements**:
- Memory: {Requirements}
- CPU: {Requirements}
- Storage: {Requirements}

**Cost**: {Free|Freemium|Paid}
- {Cost details}

## Risk Assessment

### High Risks
- ❌ {Risk 1}
  - Mitigation: {How to mitigate}

### Medium Risks
- ⚠️ {Risk 2}
  - Mitigation: {How to mitigate}

### Low Risks
- ⚡ {Risk 3}
  - Mitigation: {How to mitigate}

## Comparison with Alternatives

| Criterion | {This Tech} | {Alternative 1} | {Alternative 2} |
|-----------|-------------|-----------------|-----------------|
| Technical Fit | {X}/5 | {X}/5 | {X}/5 |
| Maturity | {X}/5 | {X}/5 | {X}/5 |
| Community | {X}/5 | {X}/5 | {X}/5 |
| DX | {X}/5 | {X}/5 | {X}/5 |
| Operational | {X}/5 | {X}/5 | {X}/5 |
| **Total** | **{X.X}** | **{X.X}** | **{X.X}** |

**Winner**: {Technology name} - {Brief reason}

## Recommendation: {ADOPT|TRIAL|ASSESS|HOLD}

### Reasoning
{Detailed explanation of recommendation}

### Adoption Path (if ADOPT or TRIAL)

1. **Proof of Concept**
   - Build {specific thing} to validate
   - Timeline: {X weeks}
   - Success criteria: {Criteria}

2. **Pilot Project**
   - Use for {specific project}
   - Timeline: {X weeks}
   - Team: {Who}

3. **Full Adoption** (if pilot successful)
   - Migration plan: {Overview}
   - Training needed: {What}
   - Timeline: {X months}

### Next Steps

1. {Action 1}
2. {Action 2}
3. {Action 3}

## Related Decisions

- Related to ADR-XXX (if applicable)
- Impacts {feature/system}

## References

- [Official Documentation]({URL})
- [GitHub Repository]({URL})
- [Comparison Article]({URL})
- [Production Case Study]({URL})

---

**Evaluation Valid Until**: {Date} (re-evaluate yearly or when major version released)
```

## Example Evaluation

```markdown
# Technology Evaluation: Zod

**Date**: 2025-10-18
**Category**: library
**Purpose**: Runtime type validation and schema definition

## Executive Summary

Zod is a TypeScript-first schema validation library with excellent type inference. It provides runtime validation that stays in sync with TypeScript types, reducing duplication and potential bugs. Strong recommendation for adoption.

**Recommendation**: ADOPT
**Overall Score**: 4.2/5.0

## Evaluation Scores

| Criterion | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| Technical Fit | 5/5 | 30% | 1.50 |
| Maturity & Stability | 4/5 | 25% | 1.00 |
| Community & Support | 4/5 | 20% | 0.80 |
| Developer Experience | 5/5 | 15% | 0.75 |
| Operational | 3/5 | 10% | 0.30 |
| **Total** | | | **4.35/5.0** |

[... detailed analysis ...]

## Recommendation: ADOPT

### Reasoning
Zod provides excellent TypeScript integration with zero configuration. The type inference is superior to alternatives (Yup, Joi), and it's becoming the industry standard. Low operational overhead (pure TS library), and excellent developer experience.

### Adoption Path

1. **Proof of Concept** ✓ Complete
   - Validated in auth service
   - Reduced code by 30%
   - Caught 3 runtime bugs in testing

2. **Pilot Project**: User registration feature
   - Timeline: This sprint
   - Replace existing validation
   - Measure error rate improvement

3. **Full Adoption**
   - Migrate all API validation to Zod
   - Timeline: 2 sprints
   - Create Zod schemas library

### Next Steps

1. Create ADR documenting Zod adoption
2. Add Zod to tech radar (Adopt)
3. Create team training materials
```

## Tech Radar Integration

After evaluation, update `architecture/tech-radar.json`:

```json
{
  "rings": {
    "adopt": [
      {
        "name": "Zod",
        "category": "library",
        "added": "2025-10-18",
        "evaluation": "architecture/evaluations/zod-evaluation.md"
      }
    ],
    "trial": [],
    "assess": [],
    "hold": []
  }
}
```

## Remember

Technology evaluation is about:
- ✅ Making informed decisions
- ✅ Reducing risk
- ✅ Choosing sustainable solutions
- ✅ Balancing innovation with stability

Re-evaluate technologies yearly or when major versions release.
