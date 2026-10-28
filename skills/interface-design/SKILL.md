---
name: interface-design
description: Design and build user interfaces that look deliberately made for the product, not generated from a template. Use when creating or changing any screen, component, form, dashboard, or landing page, and as the anti-AI-slop gate before UI work is delivered. Covers visual direction, hierarchy, states, responsive layout, and accessibility.
---

# Interface Design

## Before writing UI code

Write three lines:

```
USER TASK: <the one thing this screen must let the user do>
DIRECTION: <existing design language to preserve, or the chosen direction and why>
CONTENT: <real content source; no lorem ipsum, no invented numbers>
```

If the project already has a design language, extend it. Redesign only when asked.

## Build rules

- Layout follows content priority. The primary action is the most visible control on the screen.
- Use the project's spacing and type scale. If none exists, pick one scale and use only its steps.
- Every interactive element has hover, focus-visible, active, and disabled states. Focus must be visible without a mouse.
- Every async action has pending, success, and failure states. Failure text says what happened and what to do.
- Inputs have a visible or programmatic label. Placeholder text is not a label.
- Icon-only buttons have an accessible name that includes the object ("Delete 'Buy milk'", not "Delete").
- Touch targets are at least 24 by 24 CSS px (WCAG 2.2 SC 2.5.8); aim for 44 on mobile.
- Never disable browser zoom.
- Animations must explain a change of state. Respect `prefers-reduced-motion`.

## Anti-slop gate

Run `scripts/slop_scan.py <path>` for a first pass, then review by eye. The scanner flags candidates; it does not decide. Full checklist: [references/anti-slop-design.md](references/anti-slop-design.md).

Reject the UI if any of these hold:

1. A decorative element (gradient, glow, blob, glass panel) has no job a user would notice if it were removed.
2. Metrics, testimonials, logos, or activity feeds are invented.
3. A control looks interactive but does nothing, or reports success the server never confirmed.
4. Sections repeat the same card layout regardless of content type.
5. Spacing, radius, or color values appear that are not in the project's scale.
6. Text contrast is below 4.5:1 for body text or 3:1 for large text and UI boundaries.
