---
id: SAN-527
title: NG0100 ExpressionChangedAfterItHasBeenCheckedError from live Quill editorContent getter (3 components)
type: bug-fix
status: done
linear: https://linear.app/sanchiconnect/issue/SAN-527
sentry:
  - SC-SAAS-FRONTEND-A8
repos: [frontend]
commit: sc-saas-frontend@0b862bb0 (branch ai_native_setup_vishali, pushed to origin)
created: 2026-08-26
updated: 2026-08-26
---

# SAN-527 — NG0100 from live Quill editorContent getter

## Root cause
`editorContent` in `ProgramOfficeIntroComponent`, `MentorIntroComponent`, and `IndividualProfileEditFormComponent` is a getter that reads live state directly off the Quill.js instance:

```ts
get editorContent() {
  return this.quillEditor?.quillEditor?.getText()
}
```

Each component's template reads this getter in several bindings (`[class.d-block]`, `[class.text-red]`, `*ngIf`, a remaining-character-count interpolation, and a `[disabled]` binding). Because it re-queries live, externally-mutable Quill state on every change-detection check rather than a stable Angular-tracked field, Angular's dev-mode `checkNoChanges()` verification pass can see a different value than the first pass — e.g. once the initial `briefDescription`/`longDescription` data finishes loading into the editor — producing `NG0100`.

Notably, every affected template already wires `(onContentChanged)="onAboutChange($event)"` on the `quill-editor`, but `onAboutChange(e) {}` was an empty no-op in all three components — clearly meant to keep a stable value in sync but never implemented.

## Fix
In all 3 files:
1. Replaced the `editorContent` getter with a plain field (`editorContent = ''`).
2. Implemented `onAboutChange(e)` to set `this.editorContent = e?.text || ''`.
3. Also set `this.editorContent` synchronously right after the initial data `patchValue()` call, so the UI reflects loaded data immediately rather than waiting on the editor's own change event.

## Blast radius
None for the working case — the same text length drives the same UI; the value is now read from a stable field instead of re-querying the live Quill instance on every check, which is what removes the two-pass mismatch. Diff is the identical shape in all 3 files (field declaration, handler body, one line after patchValue).

## Verification
`tsc --noEmit` clean across all 3 files. No test suite configured for this repo; type-check + code-review was the strongest verification available. Committed (`0b862bb0`) and confirmed pushed to `origin/ai_native_setup_vishali`. Not yet on the shared `ai_native_setup` branch or `main`.
