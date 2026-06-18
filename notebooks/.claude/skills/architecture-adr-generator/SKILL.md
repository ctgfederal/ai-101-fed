---
name: adr-generator
description: Generate Architecture Decision Records (ADRs) that document significant technical decisions with context, rationale, alternatives, and consequences.
version: 1.0.0
---

# ADR Generator Skill

## Purpose
Generate Architecture Decision Records (ADRs) that document significant technical decisions with context, rationale, alternatives, and consequences.

## Inputs
- **Decision Title**: Short title describing the decision
- **Decision Context**: Background and situation driving the decision
- **Decision Made**: The specific choice that was made
- **Alternatives**: Other options that were considered
- **Rationale**: Why this decision was made
- **Consequences**: Impact of the decision (positive, negative, neutral)

## Output
Creates a formatted ADR markdown file with:
- Unique ADR number (sequential)
- Proper status and metadata
- Complete decision documentation
- Links to related decisions

## ADR Numbering

ADRs are numbered sequentially starting from 001:
- Read `architecture/adrs/README.md` to find next number
- If README doesn't exist, start with ADR-001
- Format: `ADR-{number}` where number is zero-padded to 3 digits

## ADR Template Structure

```markdown
# ADR-{number}: {Title}

**Status**: [Proposed | Accepted | Deprecated | Superseded by ADR-XXX]
**Date**: {YYYY-MM-DD}
**Deciders**: [Who made this decision]
**Tags**: [relevant, tags, here]

## Context

What is the technical issue we're trying to solve? What factors are driving this decision?

- Business requirement: ...
- Technical constraint: ...
- Current situation: ...
- Timeline considerations: ...

## Decision

We will [use/implement/adopt] {solution}.

[Clear statement of what was decided]

## Rationale

Why did we choose this approach?

1. **Primary Reason**: Detailed explanation
2. **Secondary Reason**: Detailed explanation
3. **Additional Consideration**: Detailed explanation

## Alternatives Considered

### Alternative 1: {Name}
**Description**: Brief description of the alternative

**Pros**:
- Advantage 1
- Advantage 2

**Cons**:
- Disadvantage 1
- Disadvantage 2

**Why Rejected**: Clear explanation of why this wasn't chosen

### Alternative 2: {Name}
[Same structure as Alternative 1]

### Alternative 3: {Name}
[Same structure as Alternative 1]

## Consequences

### Positive Consequences
- What becomes easier or better?
- What new capabilities does this enable?
- What problems does this solve?

### Negative Consequences
- What becomes harder or requires more work?
- What new constraints does this introduce?
- What technical debt might this create?

### Neutral Consequences
- What changes without clear benefit or cost?
- What remains the same?

## Implementation Notes

**Migration Plan** (if applicable):
- Steps to migrate from old approach
- Timeline for migration
- Backward compatibility considerations

**Dependencies**:
- Libraries or tools required
- Other ADRs this depends on
- External factors

**Risks**:
- Potential issues to watch for
- Mitigation strategies

## Related Decisions

- ADR-XXX: Related decision title
- ADR-YYY: Another related decision

## Additional Resources

For detailed examples and templates, see [REFERENCE.md](./REFERENCE.md).
