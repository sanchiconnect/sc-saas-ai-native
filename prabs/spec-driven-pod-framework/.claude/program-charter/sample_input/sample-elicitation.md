# Sample Elicitation Dialogue

This illustrates how the `program-charter` skill conducts its elicitation session.

---

**Claude:** I'll guide you through creating a Program Charter — the single source of truth for your program that all future feature work, sprints, and architecture decisions will reference. We'll work through this in five topic groups. Ready when you are.

Let's start with the foundation. Can you tell me:
1. What is this program called?
2. Who is the Program Lead?
3. What problem does it solve, and what does the current pain look like?

---

**User:** It's called "Mobile-First Checkout Experience". I'm Sarah Chen, the Program Lead. The problem is that our mobile checkout is slow and clunky — customers abandon their carts at 2x the desktop rate.

---

**Claude:** Got it. A few follow-up questions to sharpen the problem statement:
- Do you have a baseline conversion rate for mobile vs desktop?
- What's the primary friction point — payment entry, shipping, or something else?
- And roughly what's the business value of closing that gap?

---

**User:** Mobile conversion is 2.1% vs desktop at 4.3%. Payment entry is the biggest drop-off — it takes 90 seconds on average. We think fixing checkout could drive $2.8M in Year 1.

---

**Claude:** Excellent. Moving to scope and users — who are the primary user segments, and what's explicitly in vs out of scope for this program?

---

**User:** Target users are Gen Z and millennial mobile-first shoppers, plus international customers in APAC and EU. In scope: mobile checkout redesign, one-click payment, Apple Pay/Google Pay, address autocomplete. Out of scope: desktop redesign and post-purchase experience.

---

**Claude:** *(continues through Groups 3–5 in the same pattern)*

---

**Claude (pre-generation summary):**

Before I generate the charter, here's what I've captured. Please confirm or correct anything:

**Program:** Mobile-First Checkout Experience  
**Lead:** Sarah Chen  
**Goal:** Reduce mobile checkout time from 4.2 min → 1.8 min; lift conversion 2.1% → 3.5%  
**Business Impact:** $2.8M Year 1 incremental revenue  
**Users:** Mobile-first Gen Z/millennials, APAC/EU international customers  
**In Scope:** Checkout redesign, one-click payment, Apple/Google Pay, address autocomplete  
**Out of Scope:** Desktop redesign, post-purchase experience  
...

Does this look right? I'll generate `specs/program.md` and scaffold the folder structure once confirmed.
