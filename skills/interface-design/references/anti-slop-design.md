# Anti-slop design checklist

Use after the UI renders. Each item names what to look for and the usual fix.

| Pattern | Why it hurts | Fix |
|---|---|---|
| Purple-to-blue hero gradient, glowing borders, glass cards | Signals template output; often lowers contrast | Remove, or keep one surface treatment tied to the brand |
| Every section is a 3-column card grid | Content types differ; the layout should too | Use lists for scan-heavy data, tables for comparisons, prose for explanation |
| Oversized display heading with vague copy ("Unleash your potential") | Pushes the task below the fold | State the product's job in plain words; size by hierarchy |
| Random icon next to every heading | Adds noise, no meaning | Keep icons only where they speed recognition |
| Invented numbers ("10k+ users", "99.9% uptime") | False claims | Use real data or remove |
| Fake loading via `setTimeout` | Lies about system state | Tie loading state to the real request |
| Optimistic UI with no rollback | Shows success that may not exist | Roll back and show the error, or wait for the server |
| Uniform 16px radius on everything | Flattens hierarchy | Use the project's radius scale; containers and controls can differ |
| Placeholder-only inputs | Label disappears while typing; fails WCAG 1.3.1/3.3.2 | Add a label |
| `user-scalable=no` or `maximum-scale=1` | Blocks zoom; fails WCAG 1.4.4 | Remove |
| Hover-only affordances | Invisible on touch and keyboard | Show controls on focus and on touch devices |

Source standards: WCAG 2.2 (w3.org/TR/WCAG22), WAI-ARIA Authoring Practices (w3.org/WAI/ARIA/apg).
