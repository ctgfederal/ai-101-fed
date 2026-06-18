# Agent Selection Results

**Task**: Build a RegisterForm React component with RHF + Zod, wired to Supabase.
**Keywords**: react, form, frontend, component, validation
**Agents searched**: 159
**Matches returned**: 3

## Ranked Matches

| Agent | Score | Reason | Tools | Model |
|-------|-------|--------|-------|-------|
| react-specialist | 0.42 | name token match: 'react'; description token match: 'component' | vite, jest, typescript | sonnet |
| frontend-developer | 0.34 | name token match: 'frontend'; description substring match: 'component' | vite, npm, jest | sonnet |
| nextjs-developer | 0.20 | description token match: 'react'; description substring match: 'component' | next, vite, npm | sonnet |

## Recommended Primary

**Agent**: `react-specialist`
**Why**: Highest score; description targets advanced React patterns (hooks, performance), which matches a complex form component.

## Alternatives

- `frontend-developer` — pick this if the task were simpler or framework-agnostic.
- `nextjs-developer` — pick this if the form lived inside an App Router server boundary.

## Steering / Skill References

- `.claude/agents/react-specialist.md` — agent definition.
- `.claude/steering/tech.md` — project React conventions.
- Skill `ai-sdk-patterns` — relevant only if the form streams AI responses.

## Delegation Prompt

```
Use the Task tool with:
  subagent_type: react-specialist
  prompt: |
    Build the RegisterForm component per the task description. Use React Hook Form
    for state, Zod for validation, the existing useSupabaseClient hook for the API
    call. Mirror the structure of components/forms/LoginForm.tsx.
```
