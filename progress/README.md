# MultiLinguinal Application — Project Progress & Handoff

> **Purpose:** This file is the shared project checkpoint for continuing development across separate ChatGPT conversations without losing decisions, completed work, pending functionality, or the next implementation step.
>
> **Repository:** `vivekkhillar/MultiLinguinal_Application`  
> **Branch:** `main`  
> **Last updated:** 2026-11-15

---

## 1. How to use this checkpoint

At the beginning of a new project discussion:
1. Read this file first.
2. Confirm the current task against the latest code in the repository.
3. Continue from the **Immediate next step** below; do not re-implement completed work without a reason.
4. Treat implementation status and test status separately. Never mark a task complete unless the code and relevant tests have been checked.

At the end of each meaningful implementation/review:
1. Update the relevant roadmap status.
2. Record important design decisions and any changed assumptions.
3. Record tests actually run and their reported results.
4. Update blockers and the immediate next step.
5. Commit the updated checkpoint to this file.

**Working style:** Implement and review one logical step/file at a time. The developer writes the code; review the latest repository version when asked to “check now”. Do not push code changes unless explicitly requested. Never inspect or expose secrets in `.env` files.

---

## 2. Current project status

**Current phase:** Phase 1 — Core Application Foundation  
**Current roadmap step:** Step 8 — Authentication & Authorization  
**Current substep:** Step 8.6 — Authentication Service (not yet implemented)

### Authentication progress

| Substep | Work | Status |
|---|---|---|
| 8.1 | Password utility | Complete |
| 8.2 | Authentication configuration | Complete |
| 8.3 | JWT utility | Complete — 6 tests reported passing |
| 8.4 | Session-token utility | Complete — 18 tests reported passing |
| 8.5.1 | UserRepository | Complete — 10 tests passed (2026-11-15) |
| 8.5.2 | SessionRepository | Complete — 14 tests reported passing |
| 8.6 | AuthenticationService | Pending — next |
| 8.7+ | Authentication API routes and integration | Pending |

### Repository work already completed

- `UserRepository` is the persistence layer for user records. It owns database operations such as `create()`, `get_by_id()`, and `get_by_email()`.
- `SessionRepository` is the persistence layer for session records. Its reviewed operations include lookup, create, activity update, revoke, and token rotation.
- Repositories do database access; they do not expose HTTP endpoints or own registration/login business rules.
- Repository methods use the injected SQLAlchemy async session. Transaction commit/rollback is managed by the database/session lifecycle, not arbitrarily inside each repository method.

---

## 3. Locked architecture decisions

### Layering

Use this separation consistently:

```text
React frontend
    |
    v
FastAPI Router / API
    |
    v
Service (business rules)
    |
    v
Repository (database operations)
    |
    v
PostgreSQL
```

- **Router/API:** HTTP request parsing, validation integration, status codes, response/cookie handling.
- **Service:** business rules and orchestration.
- **Repository:** SQL/database persistence.
- **Utilities:** reusable password, JWT, and opaque-token functions.

Do not put SQL directly in services or business logic in repositories.

### User creation and profile updates

- Registration is orchestrated by `AuthenticationService.register()`.
- The service checks for an existing email, hashes the password, and calls `UserRepository.create()`.
- `UserRepository.create()` performs the actual insert.
- Profile functionality will later use a separate `UserService.update_profile()` and a new `UserRepository.update()` method. Reuse the same UserRepository; do not create a second repository just for profile updates.
- Profile updates must allowlist editable fields. Email changes and password changes may require separate verification/security flows.

### Authentication and session policy

- Access JWT lifetime: **15 minutes**.
- Opaque session/refresh token lifetime: **fixed 7 days** from session creation.
- No sliding expiry for the current design.
- Do not extend `expires_at` during refresh.
- Store only the SHA-256 hash of the opaque session token in `chat_app.user_sessions`; never store the raw token.
- The raw session token is returned to the client in a Secure, HttpOnly cookie (with appropriate SameSite and HTTPS settings for the deployment).
- JWT access token and opaque session token are different credentials and serve different purposes.
- Multiple active sessions per user are allowed (for example, separate laptop and mobile sessions).

### Login / refresh / logout flow

**Login**
1. Find user by email through UserRepository.
2. Verify submitted password against the stored password hash.
3. Create a short-lived access JWT.
4. Generate a random opaque session token and hash it.
5. Calculate fixed `expires_at = now + 7 days`.
6. Create the session through SessionRepository.
7. Return the access token and set the raw session token as an HttpOnly cookie.

**Refresh**
1. Read the opaque token from the cookie.
2. Hash it and look up the session by token hash.
3. Validate that the session exists, is ACTIVE, is not revoked, and has not expired.
4. Obtain the user identity from the matched database session; do not trust a client-supplied user_id.
5. Generate a new opaque token and hash, plus a new access JWT.
6. Call `SessionRepository.update_token()` with session_id, old hash, and new hash.
7. Only if the conditional DB update succeeds, set the new cookie and return the new access token.
8. Preserve the original `expires_at`; update activity only.

**Logout**
- Revoke the matching session in the database and clear the session cookie.

**Access-token revocation consideration**
- If protected routes only validate JWT signature and expiry, an already-issued access JWT may remain valid until it expires even after session revocation.
- A session_id claim plus an active-session check can be considered when implementing authorization, balancing immediate revocation against per-request database/cache checks.

### SessionRepository.update_token() reviewed behavior

The reviewed implementation:
- Requires `session_id`, `old_token_hash`, and `new_token_hash`.
- Updates the token hash only when session_id and old hash match, status is ACTIVE, and `expires_at > CURRENT_TIMESTAMP`.
- Updates `last_activity_at`.
- Does not change `expires_at`.
- Returns the updated row or `None` when no row matches.

The SessionRepository and its tests were reviewed on 2026-11-14. The user reported **14 tests passed**. Recheck the latest branch before relying on this as the current code state.

---

## 4. Authentication API plan

The intended public endpoints are:

| Method | Endpoint | Responsibility | Status |
|---|---|---|---|
| POST | `/auth/register` | Register a new user | Pending |
| POST | `/auth/login` | Authenticate and create a session | Pending |
| POST | `/auth/refresh` | Rotate session token and issue a new access JWT | Pending |
| POST | `/auth/logout` | Revoke current session | Pending |

The JWT creation utility (for example, `create_access_token()`) is an internal backend utility, not a separate public API endpoint.

**Implementation order:** Build and test service methods first, then expose them through FastAPI router endpoints. Registration and login are service responsibilities; the API routes call those service methods.

---

## 5. Full Phase 1 roadmap

| # | Area | Status |
|---|---|---|
| 1 | Overall Project Architecture | Complete |
| 2 | Technology Stack & Project Structure | Complete |
| 3 | Frontend Architecture — React + TypeScript | Complete |
| 4 | Backend Architecture — FastAPI | Complete |
| 5 | AI / Language / Translation Architecture | Approved / locked |
| 6 | PostgreSQL Database Design & Implementation | Complete |
| 7 | Redis Architecture & Implementation | Core implementation/testing complete; production hardening deferred |
| 8 | Authentication & Authorization | **In progress** |
| 9 | User Profile & Language Preference | Pending |
| 10 | Language Configuration & Management | Pending |
| 11 | Chat Room & Group Chat Foundation | Pending |
| 12 | Message Management | Pending |
| 13 | WebSocket / Real-Time Communication | Pending |
| 14 | Local File / Media Storage | Pending |
| 15 | Encryption Architecture | Pending |
| 16 | Session Management & Account Lifecycle | Pending |
| 17 | Basic LangGraph Integration | Pending |
| 18 | Basic Agent / Tool / MCP Foundation | Pending |
| 19 | Dockerization — Local Development | Pending |
| 20 | Frontend + Backend Integration | Pending |
| 21 | Phase 1 Testing & Validation | Pending |
| 22 | Phase 1 Final Review & Lock | Pending |

A “complete” roadmap label means the planned core work was completed at the project level; it does not imply every production-hardening task is finished. Track deferred work explicitly.

---

## 6. Cross-cutting foundation notes

### Logging
- Logging foundation exists in `Backend/app/core/logging_config.py`.
- `Backend/app/core/lifespan.py` initializes logging before Redis/database connections.
- Logging tests were previously reported as 7 passing.
- Current logging setup is single-process oriented; revisit before multi-worker deployment.
- Logs are ignored by `.gitignore`.

### Application lifecycle
- Preserve the existing `LifeSpan` class and its established lifecycle design when making backend changes.

---

## 7. Immediate next step — do not skip

### Step 8.6: AuthenticationService

Before writing code, inspect the latest repository versions of:
- `UserRepository`
- `SessionRepository`
- Password utility
- JWT utility
- Session-token utility
- Existing service package structure and dependency-injection conventions

Then implement **one method first: `AuthenticationService.register()`**.

Expected responsibility:
1. Accept validated registration data.
2. Check whether the email is already registered using UserRepository.
3. Hash the password using the existing password utility.
4. Call `UserRepository.create()` with the actual fields supported by the current database schema.
5. Return a safe user representation; never return the password hash.
6. Handle duplicate-email and persistence errors consistently with the project's service/API error conventions.

Write focused service tests using the project's existing test patterns. Do not invent schema fields or duplicate existing utility functionality. Once registration is reviewed and tested, proceed to `login()`; do not start the API router prematurely.

**Important:** Inspect the actual current User model/table and repository signatures before finalizing the service method or its tests.

---

## 8. Review and progress-update checklist

Use this checklist at each implementation milestone:

- [ ] Confirm the current roadmap step and scope.
- [ ] Inspect the latest relevant code from `main`.
- [ ] Confirm the implementation follows API → service → repository → database layering.
- [ ] Check validation, error handling, security, and transaction behavior.
- [ ] Add/update unit tests and relevant integration tests.
- [ ] Run tests and record the exact user/tool-reported result.
- [ ] Review for regressions and unintended changes.
- [ ] Update this README with status, decisions, test results, and next action.
- [ ] Keep deferred production-hardening work visible.
- [ ] Do not mark unverified functionality as complete.

---

## 9. Change log

### 2026-11-15
- Established this file as the project-wide progress and conversation handoff checkpoint.
- Recorded current Authentication & Authorization status and the agreed repository/service/API separation.
- Recorded the fixed 7-day session expiry and 15-minute access JWT policy.
- Reviewed the latest UserRepository and test file; all **10 tests passed**, including duplicate username/email and omitted last_name cases.
- Marked Step 8.5.1 UserRepository complete and set the next task to inspect existing dependencies and implement `AuthenticationService.register()`.
