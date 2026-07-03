# UI/UX Design Specification
**Program:** Mobile-First Checkout Experience
**Program ID:** PRG-MFCE-001
**Last Updated:** June 2026
**Version:** 1.0
**Applies To:** All checkout features and pods in this program

---

## Design Tokens

### Color Palette
```
Primary:        #1A56DB  — Main CTA color; active states; focus rings
Primary-hover:  #1C47C0  — Pressed/hovered primary actions
Primary-light:  #EBF5FF  — Primary tint for selected states
Secondary:      #6875F5  — Supporting actions; progress indicators
Neutral-50:     #F9FAFB  — Page background
Neutral-100:    #F3F4F6  — Card surfaces; input fill backgrounds
Neutral-200:    #E5E7EB  — Dividers; skeleton screen base
Neutral-300:    #D1D5DB  — Input borders (default); step connector lines
Neutral-400:    #9CA3AF  — Placeholder text; inactive step icons
Neutral-600:    #4B5563  — Secondary text; inactive labels
Neutral-900:    #111827  — Primary text; headings

Semantic:
  Success:  #0E9F6E  — Order confirmed; payment authorized
  Warning:  #E3A008  — Session expiry warning (12-min countdown)
  Error:    #E02424  — Payment failed; field validation errors
  Info:     #3F83F8  — Informational banners; autocomplete hint text

Dark mode (OLED-optimised — program.md design highlight):
  Background:     #0A0A0A  — OLED true black (zero battery draw on OLED panels)
  Surface:        #1C1C1E  — Card and input surface
  Surface-raised: #2C2C2E  — Dropdowns; autocomplete suggestions
  Border:         #3A3A3C  — Input borders; dividers
  Text:           #F2F2F7  — Primary text
  Text-secondary: #8E8E93  — Secondary text; placeholders
```

**Contrast Requirements (WCAG 2.1 AA):**
- Normal text (< 18px / < 14px bold): minimum 4.5:1 against background
- Large text (≥ 18px regular or ≥ 14px bold): minimum 3:1
- UI components (input borders, focus rings, step indicators): minimum 3:1
- Never use Neutral-400 (#9CA3AF) for body text on Neutral-50 — contrast is 2.9:1 (fails AA)

### Typography
System font stack for mobile performance (no web font download on 4G connections):

| Token | Font Family | Weight | Size | Line Height | Usage |
|-------|------------|--------|------|-------------|-------|
| heading-xl | -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif | 700 | 28px | 1.2 | Page title ("Checkout") |
| heading-lg | same stack | 700 | 22px | 1.3 | Section titles ("Shipping Address") |
| heading-md | same stack | 600 | 18px | 1.4 | Card titles; step labels |
| body-lg | same stack | 400 | 16px | 1.5 | Primary body; form labels |
| body-md | same stack | 400 | 14px | 1.5 | Secondary copy; helper text |
| body-sm | same stack | 400 | 12px | 1.4 | Captions; badge text |
| label-strong | same stack | 600 | 14px | 1.4 | Input labels; summary row labels |
| mono | "SF Mono", "Fira Code", "Courier New", monospace | 500 | 14px | 1.4 | Order totals; card last-4 display |

**Note:** System fonts render instantly with no layout shift — critical for the LCP < 1.5s NFR. Do not substitute web fonts without re-validating the LCP target.

### Spacing Scale (base 4px)
```
space-1:  4px   — Icon gap; badge padding
space-2:  8px   — Inline element gap; tight stacking
space-3:  12px  — Input horizontal padding; button padding (sm)
space-4:  16px  — Standard section padding; form field gap
space-5:  20px  — Card internal padding
space-6:  24px  — Inter-section gap; list item height complement
space-8:  32px  — Major section gap
space-10: 40px  — Above-fold breathe room
space-12: 48px  — Minimum touch target dimension
space-16: 64px  — Bottom safe area clearance; sticky header height
```

### Border Radius
```
radius-sm:   6px    — Input fields; small chips; badge
radius-md:   10px   — Standard cards; buttons
radius-lg:   16px   — Bottom sheets; modal cards; payment method cards
radius-xl:   20px   — Order summary sticky card (visually prominent)
radius-full: 9999px — Pills; avatar; step connector dot
```

### Elevation (Shadows)
```
elevation-0: none
  Used: flat in-line elements; dividers

elevation-1: 0 1px 3px rgba(0,0,0,0.08), 0 1px 2px rgba(0,0,0,0.04)
  Used: standard cards; selected payment method card

elevation-2: 0 4px 12px rgba(0,0,0,0.10), 0 2px 4px rgba(0,0,0,0.06)
  Used: sticky order summary header; autocomplete dropdown; sticky bottom CTA

elevation-3: 0 10px 30px rgba(0,0,0,0.18), 0 4px 8px rgba(0,0,0,0.08)
  Used: session expiry modal; bottom sheet entry
```

**Dark mode elevation:** Replace shadow with subtle border (1px solid Surface-raised) — shadows are invisible on dark surfaces.

---

## Component Library

### Button
**Variants:** primary | secondary | ghost | destructive | wallet-apple-pay | wallet-google-pay
**Sizes:** sm (36px h) | md (44px h) | lg (56px h)
**States:** default | hover | active/pressed | loading | disabled

| Variant | Background | Text | Border | Min Height | Use Case |
|---------|-----------|------|--------|-----------|----------|
| primary | #1A56DB | White | None | 56px (checkout CTA) | "Place Order", "Confirm & Pay" — one per screen |
| secondary | Transparent | #1A56DB | 1.5px #1A56DB | 44px | "Edit", "Change address" |
| ghost | Transparent | Neutral-600 | None | 44px | Tertiary actions; "Cancel" |
| destructive | #E02424 | White | None | 44px | Remove saved payment method |
| wallet-apple-pay | #000000 | White | None | 56px | Apple Pay — must use Apple-provided button component; no custom styling |
| wallet-google-pay | #FFFFFF | #3C4043 | 1px #DADCE0 | 56px | Google Pay — must use Google-provided button component; no custom styling |

**Rules:**
- Minimum touch target: 48×48px — use padding to reach target when visual height is smaller (WCAG 2.5.5)
- Loading state: replace label with 20px spinner (Neutral-400 on light, Neutral-600 on dark); disable pointer events; aria-busy="true" + aria-label="Loading"
- Full-width on screens ≤ 480px; max-width 480px on wider screens
- Primary button is always the last element before the safe-area inset on mobile (sticky bottom bar)
- Wallet buttons (Apple Pay / Google Pay) must be rendered via @stripe/react-stripe-js PaymentRequestButton — never re-styled or custom-built
- Spacing between adjacent buttons: minimum space-2 (8px)

---

### Text Input
**States:** default | focused | filled | error | disabled
**Variants:** standard | search | password | address (see Address Autocomplete below)

```
Height:        44px (single-line)
Padding:       12px horizontal, 10px vertical
Border:        1.5px Neutral-300 (default)
               1.5px #1A56DB (focused)
               1.5px #E02424 (error)
               1.5px Neutral-200 (disabled)
Background:    Neutral-100 (default/filled)
               White (focused)
               Neutral-50 (disabled, 50% opacity)
Border-radius: radius-sm (6px)
Label:         Floating label — 16px body-lg above field; animates to 12px body-sm floating
               at top-left on focus or when value is present
```

**Error display:** Error message (body-sm, #E02424) immediately below field; left-aligned; role="alert" for screen readers; error icon prefix inside field right-side.

**Disabled:** opacity: 0.5; cursor: not-allowed; do not convey disabled state by color alone (pattern or opacity required — WCAG 1.4.1).

---

### Address Autocomplete Input
*Checkout-specific component — extends Text Input.*
**Trigger:** API call debounced 300ms after each keystroke; fires when ≥ 3 characters entered.

```
Input behavior:   Standard Text Input (address variant)
Dropdown:         elevation-2; radius-md; max 5 suggestion rows
Suggestion row:   48px height; 16px left padding; body-md text; Neutral-900 primary line,
                  Neutral-600 secondary line (city, state, postal)
Active row:       Primary-light (#EBF5FF) background; no border change
Loading state:    Spinner (16px) replaces chevron icon while API call in flight
Empty state:      Single row: "No suggestions — enter address manually" (Neutral-600)
```

**Keyboard navigation:**
- ↓ / ↑ arrows move through suggestions; Enter selects; Escape closes dropdown
- aria-haspopup="listbox", aria-autocomplete="list", aria-expanded
- Each suggestion row: role="option", aria-selected
- Dropdown: role="listbox", aria-label="Address suggestions"

**Fallback behavior (BR-031):** When geocoding API is unavailable, input renders as a standard Text Input with no dropdown; is_validated flag set to false; no user-visible error shown.

---

### Form
- Vertical gap between fields: space-6 (24px)
- Required fields: asterisk (*) appended to label in Neutral-600; aria-required="true" on input
- Inline validation: validate **on blur** (not on keystroke) — reduces noise for fast mobile typists
- Submit button disabled until all required fields pass Zod validation
- On submit attempt with errors: focus first invalid field; scroll it into view; announce error count via aria-live="polite"
- Field groups (e.g., city + state + postal on one row): 2-column grid at ≥ 375px; 1-column below

---

### Payment Method Selector
*Checkout-specific component.*
**Appearance:** Radio-group of visual cards. Wallet methods appear first (program.md: "wallet-first payment tray").

```
Card height:     72px (wallet methods: 56px — wallet button fills card)
Border:          1.5px Neutral-300 (unselected)
                 2px #1A56DB (selected)
Border-radius:   radius-lg (16px)
Background:      White (unselected); Primary-light (selected)
Elevation:       elevation-0 (unselected); elevation-1 (selected)
```

**Order of options:**
1. Apple Pay (shown only when available on device / browser — Stripe PaymentRequest API detects)
2. Google Pay (same detection logic)
3. Saved cards (one row per PaymentMethodToken; last-4 + card brand icon + expiry)
4. "Add new card" (opens Stripe CardElement inline — no modal)

**Stripe Element integration:** Card number input uses CardElement from @stripe/react-stripe-js; styled via Stripe's appearance API to match this spec's font and color tokens. Never render a custom card input.

**States:**
- role="radiogroup" on container; role="radio" + aria-checked on each card
- Selected card announces: "Visa ending 4242, selected" to screen readers
- Unavailable method (e.g., Apple Pay not supported): card hidden entirely — do not show disabled state

---

### Order Summary Card
*Checkout-specific component.*
**Behavior:** Sticky at top of the single-page checkout scroll view; collapses to show total only when user scrolls down > 80px; expands on tap.

```
Expanded height:  auto (grows with line items)
Collapsed height: 56px (shows item count + total only)
Background:       White (light) / Surface (#1C1C1E) (dark)
Border-radius:    radius-xl (20px) bottom corners only when sticky at top
Elevation:        elevation-2 when sticky; elevation-0 when inline (top of page before scroll)
Padding:          space-5 (20px) horizontal; space-4 (16px) vertical
```

**Content (expanded):**
- Line items: product name (body-md, truncated at 1 line) + price (mono, right-aligned)
- Divider
- Subtotal, Shipping, Total rows — Total in heading-md + mono, bold
- Currency formatted per Customer.locale (e.g., ¥1,234 for ja-JP; €12.34 for de-DE; $42.00 for en-US)

**Accessibility:** aria-expanded on collapse toggle; aria-label="Order summary" on section.

---

### Checkout Step Progress Indicator
*Checkout-specific component. Visual only — not navigable (single-page scroll model).*

```
Layout:    Horizontal, 4 steps: Identity → Shipping → Payment → Review
Height:    44px (visual area)
Step dot:  20px circle — Neutral-300 (pending), Primary (active), Success checkmark (complete)
Connector: 1px line, Neutral-300 (pending or active), Success (complete)
Label:     body-sm below dot — Neutral-400 (pending), Neutral-900 (active), Neutral-600 (complete)
```

**Accessibility:** aria-label="Checkout progress" on container; current step: aria-current="step"; announce step changes with aria-live="polite" region that reads "Step {N} of 4: {Step Name}".

---

### Session Expiry Warning Modal
*Checkout-specific component. Appears at 12-minute inactivity mark (design.md: "client-side countdown shown at 12 minutes").*

**Trigger:** Client-side timer fires at 12 min; modal appears with 3-min countdown.
**Persistence:** Cannot be closed by backdrop tap or Escape key — customer must tap "Continue Shopping" or let it expire.

```
Type:       Centered modal on all viewport sizes (exception to bottom-sheet-on-mobile rule —
            session expiry is urgent and requires deliberate action)
Width:      min(calc(100vw - 32px), 400px)
Backdrop:   rgba(0,0,0,0.6)
Heading:    "Your session is about to expire" (heading-md)
Body:       "You have {N:00} minutes to complete your checkout before your cart is cleared."
            Countdown updates every second; live region with aria-live="assertive"
CTA:        Primary button "Continue Shopping" (extends session)
            Ghost button "Start Over" (clears and restarts)
```

**Accessibility:** role="alertdialog", aria-modal="true", aria-labelledby, aria-describedby; focus trapped; "Continue Shopping" receives initial focus; countdown announced every 60 seconds (not every second — prevents screen reader spam).

---

### Toast / Snackbar
**Position:** Bottom-center on mobile (≤ 768px); top-right on desktop
**Auto-dismiss:** 4s for success/info; persistent for error (requires explicit dismiss)
**Variants:** success | error | warning | info
**Max visible:** 1 at a time; queue subsequent toasts

| Variant | Icon | Background | Checkout use case |
|---------|------|-----------|-------------------|
| success | Check circle | #0E9F6E | Order confirmed |
| error | X circle | #E02424 | Payment failed (persistent) |
| warning | Alert triangle | #E3A008 | Session expiring (first alert before modal) |
| info | Info circle | #3F83F8 | Autocomplete API unavailable (silent fallback) |

**Accessibility:** role="status" (success/info/warning); role="alert" (error); aria-live="polite" / aria-live="assertive" (error).

---

### Loading States
- **Spinner:** 24px; stroke-width 2px; Primary color; used for payment processing (SUBMITTING step) and button loading state
- **Skeleton screen:** Used for initial checkout load; mirrors exact layout of Order Summary Card + form fields; animated shimmer using CSS @keyframes; aria-hidden="true" on skeleton; aria-busy="true" on container
- **Progress indicator:** Indeterminate linear progress bar (Primary color, 3px height) pinned to top of viewport during step transitions
- **Rule:** Loading state must appear within 100ms of action; never show a blank screen

**Skeleton checkout shape:**
```
[——————————————————] ← Order Summary Card skeleton (120px)
[————————————] [——] ← Step indicator
[————] ← Label
[——————————————————] ← Input field (44px)
[——————————————————] ← Input field (44px)
[————] ← Label
[——————————————————] ← Input field (44px)
```

---

### Empty States
Applies when a customer has no saved addresses or payment methods:
- **No saved addresses:** "No saved addresses — enter your address below" + address form opens immediately (no additional tap)
- **No saved payment methods:** Stripe CardElement shown directly; no empty state message (wallet options still available)
- **Order history (if shown):** "No orders yet — your confirmed orders will appear here" + CTA back to shop

---

## Motion System

### Philosophy
Functional and fast — transitions confirm state changes without adding perceived latency. Checkout is a task flow, not a marketing surface; motion should reduce cognitive load, not entertain. All motion must respect prefers-reduced-motion: reduce.

### Duration Scale
```
duration-instant:  0ms    — disabled-state changes; immediate feedback
duration-fast:     100ms  — button press; checkbox; toggle; tap feedback
duration-normal:   200ms  — input focus/blur; dropdown open; step dot state change
duration-moderate: 300ms  — page-level transitions; sticky header appearance
duration-slow:     400ms  — modal/bottom sheet entry; order summary expand/collapse
```

### Easing Curves
```
ease-standard: cubic-bezier(0.4, 0.0, 0.2, 1)   — Most component state transitions
ease-decel:    cubic-bezier(0.0, 0.0, 0.2, 1)   — Elements entering viewport
ease-accel:    cubic-bezier(0.4, 0.0, 1.0, 1.0) — Elements leaving viewport
ease-spring:   cubic-bezier(0.34, 1.56, 0.64, 1) — Checkout step completion (celebratory)
```

### Standard Transitions
| Interaction | Duration | Easing | Transform / Property |
|-------------|---------|--------|---------------------|
| Button press | 100ms | ease-standard | scale(0.97) |
| Input focus | 200ms | ease-standard | border-color + box-shadow |
| Autocomplete dropdown open | 200ms | ease-decel | opacity 0→1 + 	ranslateY(-4px→0) |
| Autocomplete row hover | 100ms | ease-standard | background-color |
| Payment card select | 200ms | ease-standard | border-color + box-shadow + background |
| Order summary collapse | 300ms | ease-standard | max-height + opacity |
| Order summary sticky appear | 200ms | ease-decel | 	ranslateY(-8px→0) + opacity 0→1 |
| Step progress completion | 400ms | ease-spring | step dot scale + color |
| Toast enter | 200ms | ease-decel | 	ranslateY(16px→0) + opacity 0→1 |
| Toast exit | 150ms | ease-accel | opacity 1→0 |
| Session modal enter | 350ms | ease-decel | scale(0.95→1) + opacity 0→1 |
| Page step transition | 300ms | ease-standard | opacity fade cross |

**Reduced motion fallback:** All transforms removed; duration-fast (100ms) opacity-only transitions used instead.

---

## Layout System

### Grid
- **Mobile (< 480px):** 4-column grid; 16px gutters; 16px side margins
- **Mobile-large (480–767px):** 4-column grid; 20px gutters; 20px side margins
- **Tablet (768–1023px):** 8-column grid; 24px gutters; 24px margins
- **Desktop (≥ 1024px):** 12-column grid; checkout content centered; max-width 560px

**Checkout layout rule:** Checkout is always a single-column layout regardless of viewport. On desktop, the checkout column is centered at max-width 560px. No two-column layout for checkout — reduces cognitive load and keeps CTA above fold.

### Breakpoints (Tailwind tokens)
```
sm:  480px   — Mobile-large (larger phones, landscape)
md:  768px   — Tablet
lg:  1024px  — Desktop
```

### Touch Targets
- **Minimum:** 48×48px for all interactive elements (WCAG 2.5.5; Apple HIG)
- **Buttons:** Visual height 44px minimum; 4px padding added to reach 48px tap area
- **Form inputs:** 44px height; full-width tap area
- **Autocomplete suggestion rows:** 48px height
- **Payment method cards:** 56-72px height — comfortably tappable
- **Adjacent targets minimum gap:** 8px (space-2) between any two tappable elements

### Safe Areas (iOS / Android)
- Bottom-fixed CTAs ("Place Order" sticky bar): padding-bottom: env(safe-area-inset-bottom, 16px)
- Top navigation / step indicator: padding-top: env(safe-area-inset-top, 0px)
- Order summary sticky: accounts for status bar height via safe area inset
- React Native: use useSafeAreaInsets() hook from eact-native-safe-area-context

---

## Accessibility Standards

**Compliance target:** WCAG 2.1 AA — enforced at lint time (eslint-plugin-jsx-a11y) and test time (@testing-library/react accessibility queries).

| Requirement | Implementation |
|-------------|---------------|
| Color contrast | ≥ 4.5:1 for body text; ≥ 3:1 for large text and UI components; never Neutral-400 on Neutral-50 for text |
| Focus indicators | 2px solid #1A56DB outline + 2px transparent offset; outline-offset: 2px; never outline: none without an equivalent custom visible style |
| Focus order | Logical DOM order matches visual order; no 	abIndex > 0 |
| ARIA labels | All icon-only buttons: aria-label; all form inputs: associated <label>; Stripe Elements: aria-label applied via Stripe appearance API |
| Live regions | aria-live="polite" on toast (success/info/warning); aria-live="assertive" on error toast, payment failed message, and session expiry countdown |
| Modal focus trap | Focus cycles within open dialog; returns to trigger element on close; Radix UI Dialog component handles this natively |
| Heading hierarchy | One <h1> per page ("Checkout"); section headings use <h2>; step labels use <h3> |
| Checkout step announcement | aria-live="polite" region announces step changes: "Now on step {N} of 4: {Name}" |
| Stripe Elements | Card input announced as "Credit or debit card number"; accessible via keyboard; managed by Stripe SDK |
| Images / icons | Decorative icons: aria-hidden="true"; informative icons (payment brand logos): alt="Visa" etc. |
| Motion | All CSS transitions guarded by @media (prefers-reduced-motion: reduce) — durations set to 0ms or opacity-only |

### Screen Reader Patterns (Checkout-Specific)
- **Payment method selection:** role="radiogroup" + aria-label="Payment method"; each option announces as "Apple Pay, radio button, 1 of 4" etc.
- **Order summary amounts:** Wrap in <span aria-label="Total: $42.00">$42.00</span> — prevents screen readers from reading "$" as "dollar sign"
- **Address autocomplete:** Announce suggestion count on dropdown open: "5 address suggestions available. Use up and down arrows to navigate."
- **Session countdown:** Read every 60 seconds (not every second) via aria-live="assertive" region; prevent spam

### Internationalisation (i18n)
- **Currency display:** Use Intl.NumberFormat with Customer.locale and Order.currency (ISO 4217)
  - en-US + USD: $42.00
  - de-DE + EUR: 42,00 €
  - ja-JP + JPY: ¥4,200
- **Address format:** Country-specific field ordering and label names; postal_code label becomes "Postcode" (GB), "PLZ" (DE), "郵便番号" (JP)
- **Date format:** Use Intl.DateTimeFormat for delivery estimates and order dates
- **RTL:** Not required for initial launch; all component CSS uses logical properties (margin-inline-start not margin-left) to support future RTL without rework

---

## Iconography

- **Icon set:** Lucide Icons — consistent 1.5px stroke width; tree-shakeable; React-native compatible via lucide-react-native
- **Default size:** 20px
- **Small size:** 16px (inline with body-sm text; badges)
- **Large size:** 24px (section header icons; empty state illustrations)
- **Color:** Inherits current text color (currentColor) by default; never hard-coded hex in icon component
- **Touch target:** Icon-only interactive elements wrapped in a 48×48px tap area (button or pressable) — the icon itself is 20px centered within the tap area
- **Payment brand icons:** Use official SVG assets from Stripe's React library (@stripe/react-stripe-js) — do not substitute with Lucide icons for payment brands (Visa, Mastercard, Apple Pay, Google Pay)

**Checkout-specific icon usage:**
| Icon | Lucide name | Usage |
|------|------------|-------|
| Check circle | CheckCircle | Order confirmed; completed step |
| Alert circle | AlertCircle | Payment failed; validation error prefix |
| Clock | Clock | Session expiry warning |
| ChevronDown | ChevronDown | Order summary expand/collapse |
| MapPin | MapPin | Shipping address section header |
| CreditCard | CreditCard | Payment section header |
| Lock | Lock | PCI trust badge near payment section |
| ArrowRight | ArrowRight | "Place Order" button trailing icon |

---

## Copy & Tone

**Voice:** Friendly, direct, and reassuring. Checkout is stressful — copy should reduce anxiety, not add ceremony. Short sentences. Active voice. Plain language.

### Label Patterns
| Context | Pattern | Example |
|---------|---------|---------|
| Primary CTAs | Verb + noun | "Place Order", "Confirm & Pay", "Continue to Payment" |
| Secondary actions | Verb or short phrase | "Edit", "Change", "Remove" |
| Loading copy | Present progressive | "Processing payment…", "Verifying address…" |
| Session warning | Direct + time remaining | "Your session expires in 2 minutes" |
| Step labels | Noun only | "Identity", "Shipping", "Payment", "Review" |

### Error Messages
Format: [What happened] — [What to do]
- Payment declined: "Card declined — try a different card or use Apple Pay"
- Authorization timeout: "Payment timed out — please try again"
- Address not found: "Address not recognized — check the postcode and try again"
- Session expired: "Your session expired — start a new checkout"
- Field required: "Required" (inline below field, not "This field is required")
- Invalid card: "Check your card number — it doesn't look right"

### Tone Rules
- Never say "Error" or "Failed" as standalone labels — always explain what happened
- Never say "Please" in error messages — it implies the user made a mistake
- Use "your" not "the" for customer-owned items ("your address", not "the address")
- Currency amounts always use mono font token; never spell out ("$42.00" not "42 dollars")
- Empty states: positive framing ("No saved addresses yet" not "You have no addresses")

---

## [AS-IS] UI & UX
<!-- Routing: [AS-IS UI] -->
<!-- Populated by: doc-extraction (wireframe docs, screen specs, UX flows, style guides, UI descriptions) -->
<!-- DO NOT edit manually — use doc-extraction skill only -->
<!-- Note: existing sections above are TO-BE design; this section captures current-state from customer docs -->

> **PLACEHOLDER — PENDING CUSTOMER INPUT**
> No UI/UX documentation has been ingested. Run doc-extraction with wireframe specifications,
> screen description documents, workflow diagrams, or design system references to populate.

### Identified Screens
<!-- Expected: existing screens/views — name, purpose, primary user role, primary actions -->
<!-- Entry format: [Source: <doc name>, <page/section>] [AS-IS UI] <screen description> -->

> PLACEHOLDER — no screen inventory available yet.

<!-- APPEND BELOW THIS LINE -->

### User Workflows
<!-- Expected: key task flows step-by-step as described in source documents -->
<!-- Per workflow: name | actor | trigger | numbered steps | outcome -->

> PLACEHOLDER — no workflow documentation available yet.

<!-- APPEND BELOW THIS LINE -->

### Design Patterns Observed
<!-- Expected: color palette, typography, navigation model, component patterns, design system name/version -->

> PLACEHOLDER — no design pattern documentation available yet.

<!-- APPEND BELOW THIS LINE -->

### Accessibility & Compliance Notes
<!-- Expected: stated accessibility standards (WCAG level), compliance-related UI constraints, localisation -->

> PLACEHOLDER — no accessibility or compliance UI requirements documented yet.

<!-- APPEND BELOW THIS LINE -->

---

## Changelog

| Date | Version | Author | Summary |
|------|---------|--------|---------|
| Jun 2026 | 1.0 | Sarah Chen | Initial version — derived from program.md PRG-MFCE-001 and design.md v1.0 |
| 2026-06-01 | 1.1 | doc-extraction scaffold | Added [AS-IS] UI & UX routing section with sub-sections — all PLACEHOLDER pending document ingestion |
| 2026-06-01 | 1.2 | design-setup scaffold | Added [TO-BE] UI/UX Design session output section — PLACEHOLDER pending design session |

<!-- ============================================================ -->
<!-- DESIGN-SETUP SKILL OUTPUT — DO NOT EDIT MANUALLY             -->
<!-- Populated by design-setup Phase 3, Domain 5                  -->
<!-- ============================================================ -->

## [TO-BE] UI/UX Design — Design Session Output
<!-- Routing: design-setup Phase 3, Domain 5 — UI/UX Design Direction -->
<!-- Populated by: design-setup skill during structured session -->
<!-- AS-IS sections above are preserved and never overwritten -->

> **PLACEHOLDER — PENDING DESIGN REVIEW**
> No design session has been completed. Run `/design-setup` Domain 5 to populate.

### Design System
- **Component library:** [DESIGN DECISION PENDING] — Options: Material UI / Ant Design / Tailwind / Radix / custom
- **Brand guidelines:** [DESIGN DECISION PENDING] — reference link or N/A
- **Design tokens location:** [DESIGN DECISION PENDING] — Figma / Storybook / config file / TBD

<!-- OVERWRITE AFTER DESIGN SESSION -->

### Primary Personas & Devices
| Persona | Primary Device | Secondary Device | Key Tasks |
|---------|---------------|-----------------|-----------|
| PLACEHOLDER | [DESIGN DECISION PENDING] | — | PENDING DESIGN SESSION |

<!-- REPLACE TABLE AFTER DESIGN SESSION -->

### Navigation Model
> PLACEHOLDER — [DESIGN DECISION PENDING]
> Options: sidebar / top nav / tab-based / wizard-stepped / dashboard / other

<!-- OVERWRITE AFTER DESIGN SESSION -->

### Accessibility
- **Standard:** [DESIGN DECISION PENDING] — Options: WCAG 2.1 AA / WCAG 2.1 AAA / Section 508
- **Testing approach:** [DESIGN DECISION PENDING] — Options: automated / manual / both

<!-- OVERWRITE AFTER DESIGN SESSION -->

### Internationalization
- **i18n required:** [DESIGN DECISION PENDING]
- **Target locales:** [DESIGN DECISION PENDING]
- **RTL support:** [DESIGN DECISION PENDING]

<!-- OVERWRITE AFTER DESIGN SESSION -->

### Key Screen Inventory (TO-BE)
> PLACEHOLDER — [To be elaborated in Sprint 0 detailed design]
> Screen inventory is defined after feature requirements are confirmed and user journey is fully mapped.

| Screen | Purpose | Primary Actions | Persona |
|--------|---------|----------------|---------|
| PLACEHOLDER | PENDING DESIGN SESSION | — | — |

<!-- REPLACE TABLE IN SPRINT 0 -->