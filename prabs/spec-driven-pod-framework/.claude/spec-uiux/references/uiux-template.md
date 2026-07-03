# UI/UX Design Specification
**Program:** {Program Name}
**Program ID:** {PRG-ID}
**Last Updated:** {Date}
**Version:** {N}
**Applies To:** All features and pods in this program

---

## Design Tokens

### Color Palette
```
Primary:     {#hex}  — Main brand color; CTAs, active states
Secondary:   {#hex}  — Supporting actions, highlights
Neutral-50:  {#hex}  — Page backgrounds
Neutral-100: {#hex}  — Card backgrounds, input fills
Neutral-300: {#hex}  — Borders, dividers
Neutral-600: {#hex}  — Secondary text
Neutral-900: {#hex}  — Primary text

Semantic:
  Success:   {#hex}  — Confirmations, positive states
  Warning:   {#hex}  — Cautions, pending states
  Error:     {#hex}  — Errors, destructive actions
  Info:      {#hex}  — Informational messages

Dark mode overrides:
  Background: {#hex}
  Surface:    {#hex}
  Text:       {#hex}
```

**Contrast Requirements (WCAG AA):**
- Normal text: ≥ 4.5:1 against background
- Large text (≥18px bold or ≥24px): ≥ 3:1
- UI components and state indicators: ≥ 3:1

### Typography
| Token | Font Family | Weight | Size | Line Height | Usage |
|-------|------------|--------|------|-------------|-------|
| heading-xl | {Inter / SF Pro} | 700 | 32px | 1.2 | Page titles |
| heading-lg | {Inter} | 700 | 24px | 1.3 | Section titles |
| heading-md | {Inter} | 600 | 20px | 1.4 | Card titles |
| body-lg | {Inter} | 400 | 16px | 1.5 | Body copy |
| body-md | {Inter} | 400 | 14px | 1.5 | Secondary copy |
| body-sm | {Inter} | 400 | 12px | 1.4 | Captions, labels |
| mono | {JetBrains Mono} | 400 | 13px | 1.4 | Code, amounts |

### Spacing Scale (base 4px)
```
space-1:  4px    space-5:  20px
space-2:  8px    space-6:  24px
space-3:  12px   space-8:  32px
space-4:  16px   space-12: 48px
                 space-16: 64px
```

### Border Radius
```
radius-sm:   4px   — Inputs, small chips
radius-md:   8px   — Cards, modals
radius-lg:   12px  — Bottom sheets, large cards
radius-full: 9999px — Pills, avatars, badges
```

### Elevation (Shadows)
```
elevation-0: none               — Flat surfaces
elevation-1: 0 1px 3px rgba(0,0,0,0.08)   — Cards, inputs
elevation-2: 0 4px 12px rgba(0,0,0,0.12)  — Dropdowns, popovers
elevation-3: 0 8px 24px rgba(0,0,0,0.16)  — Modals, bottom sheets
```

---

## Component Library

### Button
**Variants:** `primary` | `secondary` | `ghost` | `destructive` | `link`
**Sizes:** `sm` (32px h) | `md` (44px h) | `lg` (52px h)
**States:** default | hover | active/pressed | loading | disabled

| Variant | Background | Text | Border | Use Case |
|---------|-----------|------|--------|----------|
| primary | Primary | White | None | Main CTA (one per screen) |
| secondary | Transparent | Primary | Primary | Secondary actions |
| ghost | Transparent | Neutral-600 | None | Tertiary, low emphasis |
| destructive | Error | White | None | Delete, cancel, irreversible |

**Rules:**
- Minimum touch target: 48×48px (padding compensates if visual is smaller)
- Loading state: replace label with spinner; disable pointer events
- Full-width on mobile screens ≤375px wide

---

### Text Input
**States:** default | focused | filled | error | disabled
**Variants:** single-line | multiline (textarea) | search | password

```
Height:     44px (single-line)
Padding:    12px horizontal
Border:     1px Neutral-300 → Primary (focused) → Error (error state)
Background: Neutral-100 → White (focused)
Label:      Floating label pattern (animates up on focus/fill)
```

**Error display:** Error message below field in Error color; icon prefix in field

---

### Form
- All form fields use consistent 24px vertical gap between fields
- Required fields marked with asterisk in label; screen reader reads "required"
- Inline validation: validate on blur (not on keystroke) to reduce noise
- Submit button disabled until required fields are valid

---

### Navigation — Bottom Tab Bar (Mobile)
- 4–5 items max; icon + label
- Active state: Primary color icon + label; inactive: Neutral-400
- Height: 56px + safe area inset
- Badge support (notification count) on icons

---

### Modal / Dialog
- Centered on tablet/desktop; bottom sheet on mobile (≤768px)
- Backdrop: 40% opacity black; taps close modal unless `persistent`
- Max width: 480px on desktop
- Focus trapped within modal; restore focus on close
- `role="dialog"` + `aria-modal="true"` + `aria-labelledby`

---

### Toast / Snackbar
- Position: bottom-center on mobile; top-right on desktop
- Auto-dismiss: 4s (info/success); persistent (error — requires dismiss)
- Variants: `success` | `error` | `warning` | `info`
- Max 1 visible at a time; queue subsequent toasts

---

### Loading States
- **Spinner:** Used for indeterminate short waits (<3s)
- **Skeleton screen:** Used for initial page/section loads; mirrors layout shape
- **Progress bar:** Used for determinate multi-step operations
- **Rule:** Never show a blank screen; always show a loading state within 100ms of navigation

---

### Empty States
Every list or data surface must have a designed empty state:
- Illustration (simple, on-brand)
- Headline: what's missing
- Body: why it's empty or what to do
- CTA (if action can resolve the empty state)

---

## Motion System

### Duration Scale
```
duration-fast:   100ms  — Micro-interactions (button press, checkbox)
duration-normal: 200ms  — Component state changes (hover, focus)
duration-slow:   350ms  — Page transitions, modal entry/exit
duration-xslow:  500ms  — Onboarding, celebratory animations
```

### Easing Curves
```
ease-standard:  cubic-bezier(0.4, 0.0, 0.2, 1)   — Most transitions
ease-decel:     cubic-bezier(0.0, 0.0, 0.2, 1)   — Elements entering screen
ease-accel:     cubic-bezier(0.4, 0.0, 1, 1)     — Elements leaving screen
ease-spring:    cubic-bezier(0.34, 1.56, 0.64, 1) — Playful, bouncy interactions
```

### Standard Transitions
| Interaction | Duration | Easing | Transform |
|-------------|---------|--------|-----------|
| Button press | 100ms | ease-standard | scale(0.97) |
| Modal enter | 350ms | ease-decel | translateY(0) from translateY(100%) |
| Modal exit | 250ms | ease-accel | translateY(100%) |
| Page transition | 300ms | ease-standard | fade + slide (12px) |
| Toast enter | 200ms | ease-decel | translateY(0) from translateY(16px) |

**Accessibility:** All motion must respect `prefers-reduced-motion: reduce` — fall back to instant or opacity-only transitions.

---

## Layout System

### Grid
- **Mobile (< 768px):** 4-column grid, 16px gutters, 16px margins
- **Tablet (768–1023px):** 8-column grid, 24px gutters, 24px margins
- **Desktop (≥ 1024px):** 12-column grid, 24px gutters, 32px margins

### Touch Targets
- Minimum: 48×48px for all interactive elements
- Preferred: 44px height for inputs and buttons (with padding to reach 48px tap area)
- Spacing between adjacent targets: ≥ 8px

### Safe Areas (iOS/Android)
- Use `env(safe-area-inset-*)` for bottom nav, CTAs near screen edges
- Status bar area: 44px reserved on iOS notch devices

---

## Accessibility Standards

**Compliance target:** WCAG 2.1 AA

| Requirement | Implementation |
|-------------|---------------|
| Color contrast | ≥ 4.5:1 for normal text; ≥ 3:1 for large text and UI components |
| Focus indicators | 2px solid Primary color outline; never `outline: none` without custom style |
| Focus order | Logical DOM order; no tabindex > 0 |
| ARIA labels | All icon-only buttons have `aria-label`; form inputs have associated `<label>` |
| Live regions | `aria-live="polite"` on toast/status; `aria-live="assertive"` for errors |
| Modal focus trap | Focus cycles within open modal; returns to trigger on close |
| Headings | One `<h1>` per page; logical heading hierarchy |
| Images | Decorative: `alt=""`; Informative: descriptive alt text |

---

## Iconography

- **Icon set:** {Lucide / Heroicons / Material Icons} — {size: 20px default, 16px small, 24px large}
- **Stroke width:** 1.5px (consistent across set)
- **Color:** Inherits from parent text color by default; never hard-coded
- **Touch target:** Icon-only buttons wrapped in 44×44px touch area

---

## Copy & Tone

- **Voice:** {Friendly and direct / Professional / Casual} — consistent across all UI text
- **Button labels:** Verb-first, action-oriented ("Confirm Payment", not "OK")
- **Error messages:** Plain language; tell the user what happened and what to do ("Card declined — check your card details or try a different payment method")
- **Empty states:** Positive framing ("No orders yet — your confirmed orders will appear here")
- **Loading copy:** Present progressive ("Processing payment…", "Loading your cart…")
- **Placeholders:** Hint format, not label replacement ("e.g. 123 Main St")

---

## Changelog

| Date | Version | Author | Summary |
|------|---------|--------|---------|
| {Date} | 1.0 | {Name} | Initial version |
