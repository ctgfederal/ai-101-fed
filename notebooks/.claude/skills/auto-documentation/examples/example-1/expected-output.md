---
title: "Admins can edit any user post; non-admins only their own"
category: business-rule
date: 2026-05-08
tags:
  - authorization
  - permissions
  - admin
  - user-posts
scope: "UserPostController#update"
source: "pair session with @alex on 2026-05-08 reviewing PR for USR-014"
---

# Admins can edit any user post; non-admins only their own

## Description

Authorization rule for edits on `UserPost`. Admins (role=admin) may edit any post regardless of ownership. Non-admins may only edit posts where `post.user_id == current_user.id`. The reject path returns 403, never 404, so post existence is not leaked.

## Why

Mirrors the business policy from the moderation runbook. Without this rule, non-admins could escalate by editing other users' posts, and admins would be over-restricted by a strict ownership check.

## Examples

```ruby
# allowed: admin can always edit; non-admin only their own
current_user.admin? || post.user_id == current_user.id
```

Reject path:

```ruby
raise Pundit::NotAuthorizedError unless current_user.admin? || post.user_id == current_user.id
# → controller renders 403, never 404
```

## Related

- `business-rule/2026-04-12-admin-elevation-policy.md` — how admins are granted
- `technical-pattern/2026-03-01-pundit-policy-conventions.md` — policy class layout
