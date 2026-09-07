# Feature Separation Guidelines

This document helps the agent decide whether a user request should be treated as a
**new feature** (create a new `docs/<feature>/spec.md`) or an **update to an existing
feature** (modify an existing spec).

## Core Principle

A feature is a **user-facing capability** that delivers a distinct value or enables a
specific user goal. The boundary between features is drawn around **user intent**, not
technical implementation.

## Decision Framework

| Guideline | New Feature | Update to Existing |
|-----------|-------------|-------------------|
| **User goal** | Different outcome or capability | Same outcome, refined or extended |
| **Primary actor** | Different user role or persona | Same actor |
| **Interaction pattern** | Fundamentally different flow | Same flow, new option or variation |
| **Scope** | Something the existing feature never claimed to cover | Within the original intent, just deeper |

## Detailed Rules

### Rule 1: Same Goal, New Method → Update

If the user wants the same end result but through a different means, update the existing spec.

- Existing: "User can log in with email and password"
- New request: "User can log in with Google"
- **Verdict:** Update. Same goal (authentication), new method.

### Rule 2: Same Flow, Different Actor → New Feature

If the interaction pattern is similar but the actor and value delivered are different,
it's a new feature.

- Existing: "User can reset their own password"
- New request: "Admin can reset any user's password"
- **Verdict:** New feature. Different actor (admin vs user), different goal
  (management vs self-service).

### Rule 3: Extension vs Refinement

- **Extension:** Adding something completely new to an existing flow → Update the spec
  - Example: "Users can now attach images to their posts" → Update `create-post` spec

- **Refinement:** Improving or changing how an existing flow works → Update the spec
  - Example: "Password reset emails should expire after 1 hour instead of 24" → Update `user-password-reset` spec

### Rule 4: New Capability, No Overlap → New Feature

If the request describes something the user can do that doesn't fit under any
existing spec's scope, create a new one.

- Existing: "User can create and edit blog posts"
- New request: "Readers can subscribe to email notifications for new posts"
- **Verdict:** New feature. Different actor (reader vs author), different goal
  (subscription vs content creation).

### Rule 5: Bundled Requests → Ask

If a user request contains multiple capabilities that span different features,
ask the user if they want separate specs or a single combined one.

- Example: "Users should be able to reset their password and also enable 2FA"
- **Verdict:** These are two distinct features (`user-password-reset` and `two-factor-authentication`).
  Propose splitting them.

## Examples Table

| Existing Feature | New Request | Verdict | Reason |
|------------------|-------------|---------|--------|
| User registration with email | User registration with phone number | Update | Same goal, new method |
| User can post text updates | User can post photo updates | Update | Same flow, new content type |
| User can edit their profile | Admin can edit any profile | New feature | Different actor, different goal |
| User can search by keyword | User can filter by date range | Update | Same search feature, new filter option |
| User can bookmark items | User can share bookmarks with friends | Update | Extends existing bookmark capability |
| User can view their orders | Admin can view all orders | New feature | Different actor, different intent |
| Dark mode toggle | System follows OS theme setting | Update | Same feature (theme preference), new behavior |
| Push notifications | In-app notification center | New feature | Different interaction model, different user goal |

## Edge Cases

### Minor UX Tweaks

Small changes to wording, layout, or behavior that don't change the user's goal
should be treated as updates.

- "Change the 'Submit' button to say 'Publish'" → Update existing feature spec

### Platform Parity

Bringing an existing feature to a new platform (e.g., web → mobile app) can be
either an update or a new feature depending on whether the interaction model
changes significantly.

- Same interaction: Update spec with a note about platform
- Different interaction: Consider a new feature spec

### Settings / Configuration

Adding a new user preference or setting is usually an update to the relevant
feature, unless it's a global settings area that spans multiple features.

- "Add a toggle to disable animations" → Update the feature that has animations
- "Create a settings page for all notification preferences" → New feature (`notification-preferences`)

## When in Doubt

If you are uncertain whether a request is an update or a new feature:

1. Identify the closest existing spec
2. Present your reasoning to the user
3. Ask: "Should I update `<existing>` or create a new spec?"
