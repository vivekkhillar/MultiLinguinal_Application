# MultiLinguinal Application — Project Progress & Handoff

> **Purpose:** Shared project checkpoint for continuing development across conversations.
>
> **Repository:** `vivekkhillar/MultiLinguinal_Application`  
> **Branch:** `main`  
> **Last updated:** 2026--11-22

---

## 1. How to use this checkpoint

At the beginning of each project discussion:
1. Read this file first.
2. Verify the current task against the latest repository code.
3. Continue from **Immediate next step**; do not repeat completed work without a reason.
4. Keep implementation status separate from test status.

After each meaningful milestone:
1. Update the roadmap and decisions.
2. Record only tests actually run and their reported results.
3. Update blockers and the immediate next step.
4. Commit the updated checkpoint.

**Working style:** Work one logical step at a time. The user implements code and asks for review. Fetch the latest GitHub files before every code review. Do not modify code unless explicitly requested. Never inspect or expose `.env` secrets.

---

## 2. Current project status

**Current phase:** Phase 1 — Core Application Foundation  
**Current roadmap step:** Step 8 — Authentication & Authorization  
**Current substep:** Step 8.9 — Authentication routes; registration route implemented, login route scaffolded.

### Authentication progress

| Substep | Work | Status |
|---|---|---|
| 8.1 | Password utility | Complete — 6 tests reported passing |
| 8.2 | Authentication configuration | Complete |
| 8.3 | JWT utility | Complete — 6 tests reported passing |
| 8.4 | Session-token utility | Complete — 18 tests reported passing |
| 8.5.1 | UserRepository read methods and create | Complete — 10 tests reported passing |
| 8.5.2 | SessionRepository | Complete — 14 tests reported passing |
| 8.6 | AuthenticationService.register() | Implemented and reviewed |
| 8.7 | Authentication request/response schemas | Implemented and reviewed |
| 8.8 | API dependencies | Implemented and reviewed |
| 8.9.1 | Register API route | Implemented and reviewed; manual API validation pending |
| 8.9.2 | Login API route | Scaffold exists; login service and endpoint behavior pending |
| 8.9.3 | Refresh API route | Pending |
| 8.9.4 | Logout API route | Pending |
| 8.10 | Centralized router registration | Implemented |
| 8.11 | Authentication API test suites | Pending — write after all four endpoints are implemented |

**Test-status note:** The test counts above are previously reported results. The latest GitHub review did not execute tests. Registration API manual validation has not yet been confirmed.

---

## 3. Current repository structure

Relevant backend structure (verify against `main` before making structural changes):

```text
Backend/app/
├── api/
│   ├── routers/
│   │   ├── health.py
│   │   └── authentication.py
│   ├── router.py
│   └── dependencies.py
├── core/
│   ├── exception.py
│   ├── logging_config.py
│   └── ...
├── repositories/
│   ├── session_repository.py
│   └── user_repository.py
├── schemas/
│   └── authentication.py
├── security/
│   ├── jwt.py
│   ├── password.py
│   └── session_token.py
├── services/
│   └── authentication_service.py
└── tests/
```

---

## 4. Locked architecture decisions

### Layering

```text
Frontend
   |
FastAPI Router
   |
Service (business logic)
   |
Repository (database operations)
   |
PostgreSQL
```

- **Router/API:** HTTP request parsing, dependency injection, status codes, response and cookie handling.
- **Service:** authentication rules and orchestration.
- **Repository:** database persistence.
- **Utilities:** reusable password, JWT and opaque-token functions.

Do not put SQL in services or business logic in repositories.

### User creation and profile updates

- Registration is orchestrated by `AuthenticationService.register()`.
- The service checks existing email and username, hashes the password, then calls `UserRepository.create()`.
- The repository performs the database insert and returns safe user fields.
- Profile updates will later use a separate `UserService.update_profile()` and an update method in the existing UserRepository.

### Authentication and session policy

- Access JWT lifetime: **15 minutes**.
- Opaque session/refresh token lifetime: **fixed 7 days** from session creation.
- No sliding expiry: do not extend `expires_at` during refresh.
- Store only the SHA-256 hash of the opaque session token in `chat_app.user_sessions`; never store the raw token.
- Return the raw session token in a Secure, HttpOnly cookie with suitable SameSite and HTTPS settings for deployment.
- JWT access token and opaque session token are different credentials.
- Multiple active sessions per user are allowed.

### Login flow

1. Look up the user using the submitted username (the current `LoginRequest` schema accepts `username`, not email).
2. Verify the submitted password against the stored password hash.
3. On invalid username or password, return the same authentication failure to avoid username enumeration.
4. Create a short-lived access JWT.
5. Generate a random opaque session token and hash it.
6. Calculate fixed `expires_at = now + 7 days`.
7. Create the session through SessionRepository.
8. Return the access token and set the raw session token as an HttpOnly cookie.

### Login API HTTP status codes

| Code | Meaning / condition |
|---|---|
| `200 OK` | Login successful; session created and access token returned |
| `401 Unauthorized` | Invalid username or password; use the same public response for both |
| `422 Unprocessable Entity` | Request body fails Pydantic/schema validation |
| `403 Forbidden` | Account is disabled/blocked, if this policy is implemented |
| `429 Too Many Requests` | Login rate limit exceeded; add when rate limiting is implemented |
| `503 Service Unavailable` | Required database/service is temporarily unavailable |
| `500 Internal Server Error` | Unexpected backend error |

Notes:
- FastAPI/Pydantic automatically returns 422 for request validation errors before the route handler runs.
- 403 and 429 are conditional future behavior; do not add artificial branches until account-status policy and rate limiting exist.
- Do not return different 401 messages for unknown usernames and incorrect passwords.

### Refresh flow

1. Read the opaque token from the cookie.
2. Hash it and look up the session by token hash.
3. Validate that the session exists, is ACTIVE, is not revoked and has not expired.
4. Obtain user identity from the matched database session; do not trust a client-supplied user_id.
5. Generate a new opaque token/hash and a new access JWT.
6. Call `SessionRepository.update_token()` with session_id, old hash and new hash.
7. Only if the conditional DB update succeeds, set the new cookie and return the new access token.
8. Preserve the original `expires_at`; update activity only.

### Logout flow

- Identify the session using the refresh/session cookie.
- Revoke the matching session in the database.
- Clear the session cookie using matching cookie path/domain settings.
- Decide and document whether logout is idempotent for missing/expired sessions.
- An already-issued access JWT may remain valid until its 15-minute expiry unless protected routes also check session state (or another revocation mechanism).

### SessionRepository.update_token() reviewed behavior

Previously reviewed behavior:
- Requires session_id, old_token_hash and new_token_hash.
- Updates only when session_id and old hash match, status is ACTIVE and expiry is in the future.
- Updates `last_activity_at`, but does not extend `expires_at`.
- Returns the updated row or `None` when no row matches.

Re-fetch the latest repository implementation before relying on these details during refresh implementation.

---

## 5. Authentication API plan

| Method | Endpoint | Responsibility | Current status |
|---|---|---|---|
| POST | `/auth/register` | Register a new user | Implemented; manual validation pending |
| POST | `/auth/login` | Authenticate and create a session | Route scaffold exists; implementation pending |
| POST | `/auth/refresh` | Rotate session token and issue a new access JWT | Pending |
| POST | `/auth/logout` | Revoke current session and clear cookie | Pending |

The JWT creation utility is an internal backend utility, not a separate public API endpoint.

**Agreed implementation sequence:** Finish all four APIs first, then write their API test suites. Review each API incrementally across schema, router, service, repository interactions, exceptions and cookie behavior.

---

## 6. Full Phase 1 roadmap

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

A “complete” roadmap label means planned core work is complete; it does not imply every production-hardening task is finished. Keep deferred work visible.

---

## 7. Cross-cutting foundation notes

### Logging
- Logging foundation exists in `Backend/app/core/logging_config.py`.
- `Backend/app/core/lifespan.py` initializes logging before Redis/database connections.
- Logging tests were previously reported as 7 passing.
- Revisit multi-worker logging before production deployment.
- Log unexpected server/database failures; avoid logging expected authentication failures as server exceptions.

### Application lifecycle
- Preserve the existing `LifeSpan` class and lifecycle design when making backend changes.

---

## 8. Immediate next steps

1. **Manually validate Register API** through Swagger (`/docs`): success 201, duplicate email 409, duplicate username 409, invalid preferred-language ID 422. Record actual results.
2. **Implement Login API**, starting by inspecting the latest UserRepository, SessionRepository, password utility, JWT utility, session-token utility, schemas and dependency wiring.
3. Add service-level login behavior, then complete the route's explicit exception-to-HTTP mappings and refresh-token cookie handling.
4. Implement Refresh API.
5. Implement Logout API.
6. Once all four endpoints are implemented, create and run API test suites.
7. Review protected-route authentication and authorization dependencies.

**Current focus:** Login API. Do not start refresh/logout until login's service, route, response and cookie behavior have been reviewed.

---

## 9. Review and progress-update checklist

- [ ] Confirm current roadmap step and scope.
- [ ] Inspect latest relevant code from `main`.
- [ ] Confirm API → service → repository layering.
- [ ] Check validation, security, exception mapping and transaction behavior.
- [ ] Add/update tests using existing project patterns.
- [ ] Run tests and record exact results; never claim unrun tests passed.
- [ ] Review regressions and unintended changes.
- [ ] Update this README with status, decisions, test results and next action.
- [ ] Keep deferred production-hardening work visible.
- [ ] Do not mark unverified functionality complete.

---

## 10. Change log

### 2026-11-22
- Reconciled the checkpoint with the latest reviewed authentication router, service, schemas and exception definitions on `main`.
- Updated the authentication roadmap: registration service/schema/dependencies and registration route are implemented and reviewed; registration manual validation is still pending.
- Recorded that the login route is currently a scaffold and the login service behavior is not yet implemented.
- Added the recommended Login API status-code contract, including the security rule to return the same 401 response for unknown username and incorrect password.
- Confirmed the agreed sequence: implement login, refresh and logout, then write API test suites for all four endpoints.
- Recorded the next action: manually validate registration, then implement Login API incrementally.
