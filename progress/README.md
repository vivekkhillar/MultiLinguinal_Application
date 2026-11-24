# MultiLinguinal Application — Project Progress & Handoff

> **Purpose:** Shared project checkpoint for continuing development across conversations.
>
> **Repository:** `vivekkhillar/MultiLinguinal_Application`  
> **Branch:** `main`  
> **Last updated:** 2026--11-25

---

## 1. How to use this checkpoint

At the beginning of each project discussion:
1. Read this file first.
2. Verify the current task against the latest repository code.
3. Continue from **Immediate next step**; do not repeat completed work without a reason.
4. Keep implementation status separate from test status.

After each meaningful milestone:
1. Update this roadmap and the decisions.
2. Record only tests actually run and their reported results.
3. Update blockers and the immediate next step.
4. Commit the updated checkpoint.

**Working style:** Work one logical step at a time. The user implements code and asks for review. Fetch the latest GitHub files before every code review. Do not modify application code unless explicitly asked. Never inspect or expose `.env` secrets.

---

## 2. Current project status

**Current phase:** Phase 1 — Core Application Foundation  
**Current roadmap step:** Step 8 — Authentication & Authorization  
**Current substep:** Step 8.9 — Four authentication API routes implemented; correction review complete; manual validation is next.

### Authentication progress

| Substep | Work | Status |
|---|---|---|
| 8.1 | Password utility | Complete — 6 tests previously reported passing |
| 8.2 | Authentication configuration | Complete |
| 8.3 | JWT utility | Complete — 6 tests previously reported passing |
| 8.4 | Session-token utility | Complete — 18 tests previously reported passing |
| 8.5.1 | UserRepository read methods and create | Complete — 10 tests previously reported passing |
| 8.5.2 | SessionRepository | Implemented/reviewed — 14 tests previously reported passing |
| 8.6 | AuthenticationService.register() | Implemented and reviewed |
| 8.7 | Authentication request/response schemas | Implemented and reviewed |
| 8.8 | API dependencies | Implemented and reviewed |
| 8.9.1 | Register API | Implemented and reviewed; manual validation pending |
| 8.9.2 | Login API | Implemented and reviewed; manual validation pending |
| 8.9.3 | Refresh API | Implemented and reviewed; manual validation pending |
| 8.9.4 | Logout API | Implemented and reviewed; manual validation pending |
| 8.10 | Centralized router registration | Implemented |
| 8.11 | Authentication API test suites | Pending — agreed to write after all four APIs are implemented |

**Important test-status note:** The test counts above are results previously reported by the user. The latest GitHub review inspected source code only; it did not execute tests or validate the APIs at runtime. Do not mark manual/API tests as passed until actual results are shared or executed.

### Latest code review checkpoint (2026-11-25)

Reviewed latest `main` versions of:
- `Backend/app/api/routers/authentication.py` — blob SHA `ece1d05ebffd61740df6c55bd30c078bae77a31f`
- `Backend/app/services/authentication_service.py` — blob SHA `65192dfd0526ffd1fa895853284a1addc78ea067`
- `Backend/app/core/exception.py` — blob SHA `a1c3eb97534940c8029783a3e569377b9295672b`
- `Backend/app/security/session_token.py` — blob SHA `834a30b827b0cc515a2992d637ee2c29014be90c`
- `Backend/app/api/dependencies.py` — blob SHA `4d400b3579cd22aa212cd7375d43cc1c68aebe52`

Corrections confirmed in latest code:
- Refresh API's unexpected database error message now correctly refers to refreshing the session.
- Refresh invalid-token attempts are logged as warnings rather than exception stack traces.
- Login's raw refresh token variable is now named `raw_refresh_token`.
- `Any` is imported for the refresh service return annotation.
- Router imports `SessionCreationError` before using it in the Login exception handler.
- The duplicate `SessionTokenError` definition was removed from `core/exception.py`; the token utility's `SessionTokenError` remains in `security/session_token.py`.
- Login raises `SessionCreationError` if session creation returns no row, and the router maps it to HTTP 500.
- Refresh normalizes a naive database expiry datetime to UTC before comparison.
- Logout checks the result of the revoke operation and logs if it was already revoked or no longer found.

**Review outcome:** The two missing imports identified in the previous review are fixed. The four API implementations are now source-reviewed, but not yet runtime-validated.

### Remaining review notes / risks

1. Cookie creation currently uses `secure=False` in Login and Refresh, and deletion uses matching flags in Logout. This is acceptable only for local HTTP development. Before HTTPS production deployment, make the Secure flag environment/configuration-driven and true in production.
2. Confirm that the database session context commits successful writes and rolls back failed transactions. This is especially important for Register, Login session creation, Refresh token rotation and Logout revocation. The latest review has not yet verified the database manager's transaction lifecycle.
3. The refresh service handles timezone-naive expiry values by assuming UTC. Confirm the actual database column type and driver behavior; prefer timezone-aware UTC timestamps end-to-end.
4. Logout revokes the refresh session, but an already-issued access JWT can remain usable until its 15-minute expiry unless protected endpoints check session validity or an access-token revocation mechanism is added.
5. Rate limiting and failed-login tracking are not yet confirmed as integrated into these API flows.

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

### Authentication and session policy

- Access JWT lifetime: **15 minutes**.
- Opaque session/refresh token lifetime: **fixed 7 days** from session creation.
- No sliding expiry: do not extend `expires_at` during refresh.
- Store only the SHA-256 hash of the opaque session token in `chat_app.user_sessions`; never store the raw token.
- Return the raw session token in an HttpOnly cookie with suitable SameSite and HTTPS settings for deployment.
- JWT access token and opaque session token are different credentials.
- Multiple active sessions per user are allowed.
- Login currently authenticates by username, not email.

### Login flow

1. Look up the user using the submitted username.
2. Verify the submitted password against the stored password hash.
3. Return the same public 401 response for unknown username and incorrect password.
4. Check account status.
5. Create a short-lived access JWT.
6. Generate a random opaque session token and hash it.
7. Calculate fixed `expires_at = now + 7 days`.
8. Create the session through SessionRepository.
9. Return the access token and set the raw session token as an HttpOnly cookie.

### Refresh flow

1. Read the opaque token from the cookie.
2. Hash it and look up the session by token hash.
3. Validate that the session exists, is ACTIVE and has not expired.
4. Obtain user identity from the matched database session; do not trust a client-supplied user_id.
5. Generate a new opaque token/hash and a new access JWT.
6. Call `SessionRepository.update_token()` with session_id, old hash and new hash.
7. Only if the conditional DB update succeeds, set the new cookie and return the new access token.
8. Preserve the original `expires_at`; update activity only.
9. Missing, malformed, unknown, revoked, expired or concurrently rotated refresh tokens should all result in the same public 401 response.

### Logout flow

- Identify the session using the refresh/session cookie.
- Revoke the matching session in the database.
- Clear the session cookie using matching cookie path/domain settings.
- Current behavior is intentionally idempotent for missing, malformed or unknown refresh cookies.
- An already-issued access JWT may remain valid until its 15-minute expiry unless protected routes also check session state or another revocation mechanism.

### SessionRepository.update_token() reviewed behavior

- Requires session_id, old_token_hash and new_token_hash.
- Updates only when session_id and old hash match, status is ACTIVE and expiry is in the future.
- Updates `last_activity_at`, but does not extend `expires_at`.
- Returns the updated row or `None` when no row matches.
- The conditional update prevents two concurrent refresh requests from both successfully rotating the same old token.

---

## 5. Authentication API contract and status

| Method | Endpoint | Responsibility | Implementation |
|---|---|---|---|
| POST | `/auth/register` | Register a new user | Implemented |
| POST | `/auth/login` | Authenticate and create a session | Implemented |
| POST | `/auth/refresh` | Rotate session token and issue a new access JWT | Implemented |
| POST | `/auth/logout` | Revoke current session and clear cookie | Implemented |

The JWT creation utility is an internal backend utility, not a separate public API endpoint.

### Expected HTTP behavior to validate

| API | Scenario | Expected result |
|---|---|---|
| Register | Successful registration | 201 |
| Register | Duplicate email or username | 409 |
| Register | Invalid preferred-language ID | 422 |
| Login | Valid credentials | 200 and refresh cookie |
| Login | Invalid username/password | 401 |
| Login | Inactive account | 403 |
| Login | Database unavailable | 503 |
| Refresh | Valid refresh cookie | 200, new access token and rotated cookie |
| Refresh | Missing/invalid/expired/revoked/old token | 401 |
| Refresh | Database unavailable | 503 |
| Logout | Valid refresh cookie | 200, session revoked and cookie cleared |
| Logout | Missing/unknown/malformed refresh cookie | 200, idempotent response |
| Any API | Request schema validation fails | 422 from FastAPI |

429 is not expected until rate limiting is implemented.

---

## 6. Redis decision

- PostgreSQL remains the source of truth for users and persistent sessions.
- Redis complements PostgreSQL for rate limiting, failed-login attempt tracking, optional access-token denylist and temporary security state.
- Do not move persistent session records from PostgreSQL to Redis.
- User previously reported Redis core implementation/testing as complete; verify actual integration before marking authentication rate limiting or failed-login tracking complete.
- Add HTTP 429 only when rate limiting is actually implemented.

---

## 7. Full Phase 1 roadmap

| # | Area | Status |
|---|---|---|
| 1 | Overall Project Architecture | Complete |
| 2 | Technology Stack & Project Structure | Complete |
| 3 | Frontend Architecture — React + TypeScript | Complete |
| 4 | Backend Architecture — FastAPI | Complete |
| 5 | AI / Language / Translation Architecture | Approved / locked |
| 6 | PostgreSQL Database Design & Implementation | Complete |
| 7 | Redis Architecture & Implementation | Core implementation/testing reported complete; auth integration/hardening to verify |
| 8 | Authentication & Authorization | **In progress — APIs implemented; validation and tests pending** |
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

## 8. Immediate next steps

**Current focus: manual Swagger validation of the four authentication endpoints.**

Proceed one endpoint at a time:

1. Start the backend and open `/docs`.
2. Validate Register: successful registration, duplicate email, duplicate username and invalid preferred-language ID.
3. Validate Login: valid credentials, invalid credentials and inactive account (if test data exists). Confirm the refresh cookie is set and the raw refresh token is not included in the JSON response.
4. Validate Refresh: use the cookie from Login; confirm a new access token and cookie are returned, the stored hash rotates, the old token no longer works, and the original expiry is unchanged.
5. Validate Logout: confirm the session becomes REVOKED and the cookie is cleared; also check missing-cookie behavior.
6. Record actual response codes and database observations. Do not claim tests passed without evidence.

After manual validation:
7. Verify database transaction commit/rollback behavior.
8. Integrate/verify Redis authentication protections (rate limiting and failed-login tracking) before final API test suites, consistent with the agreed plan.
9. Write and run API test suites for all four endpoints.
10. Build protected-route authentication/authorization dependencies and decide the access-token revocation strategy.

---

## 9. Review and progress-update checklist

- [ ] Confirm current roadmap step and scope.
- [ ] Inspect latest relevant code from `main`.
- [ ] Confirm API → service → repository layering.
- [ ] Check validation, security, exception mapping and transaction behavior.
- [ ] Manually validate the API behavior.
- [ ] Add/update tests using existing project patterns.
- [ ] Run tests and record exact results; never claim unrun tests passed.
- [ ] Review regressions and unintended changes.
- [ ] Update this README with status, decisions, test results and next action.
- [ ] Keep deferred production-hardening work visible.
- [ ] Do not mark unverified functionality complete.

---

## 10. Change log

### 2026-11-25
- Reconciled the checkpoint with the latest authentication router, service, exception, token utility and dependency files on `main`.
- Confirmed that Register, Login, Refresh and Logout routes and their corresponding service flows are implemented.
- Confirmed fixes for the missing `Any` import and missing `SessionCreationError` router import.
- Confirmed removal of the duplicate `SessionTokenError` from core exceptions.
- Confirmed Refresh error wording/logging, UTC handling for naive expiry values, Login session-creation error handling, and Logout revoke-result logging.
- Marked all four APIs as implemented and source-reviewed, but manual API validation and API test suites remain pending.
- Recorded cookie Secure configuration, transaction lifecycle, and access-token behavior after logout as items to verify or harden.
- Set the immediate next task to manual Swagger validation of the four endpoints, beginning with Register.
