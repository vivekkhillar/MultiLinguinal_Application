# Phase 1 Implementation Roadmap

**Repository:** MultiLinguinal Application  
**Branch:** `main`  
**Purpose:** Track Phase 1 implementation progress and the current next action. Update this document whenever a roadmap step is completed or the next action changes.

## Status legend

- **Complete** — implementation/review work is complete for the current Phase 1 scope.
- **In progress** — currently being implemented.
- **Pending** — not started yet.
- **Deferred** — intentionally postponed; not a blocker for current development.

## Master roadmap

| # | Phase 1 area | Status | Notes |
|---:|---|---|---|
| 1 | Overall Project Architecture | Complete | Architecture approved. |
| 2 | Technology Stack & Project Structure | Complete | Stack and repository structure established. |
| 3 | Frontend Architecture (React + TypeScript) | Complete | Architecture defined. |
| 4 | Backend Architecture (FastAPI) | Complete | Architecture defined; implementation proceeds incrementally. |
| 5 | AI / Language / Translation Architecture | Complete | Architecture approved/locked for Phase 1. |
| 6 | PostgreSQL Database Design & Implementation | Complete | Core schema, constraints, and seed data designed; schema changes should use migrations. |
| 7 | Redis Architecture & Implementation | Complete (core) | Core implementation and local tests completed. Production hardening and monitoring are deferred. |
| 8 | Authentication & Authorization | **In progress** | Password hashing implemented and four local pytest tests passed. Continue with token configuration, token utilities, registration, login, and authorization. |
| 9 | User Profile & Language Preference | Pending | Build on the existing users and language configuration schema. |
| 10 | Language Configuration & Management | Pending | Implement supported-language retrieval and management rules. |
| 11 | Chat Room & Group Chat Foundation | Pending | Use existing chat-room and membership schema. |
| 12 | Message Management | Pending | Build message creation and retrieval around the existing schema. |
| 13 | WebSocket / Real-Time Communication | Pending | Integrate after the relevant identity, room, and message flows exist. |
| 14 | Local File / Media Storage | Pending | Implement attachment handling using the existing metadata design. |
| 15 | Encryption Architecture | Pending | Implement according to the approved security design. |
| 16 | Session Management & Account Lifecycle | Pending | Include revocation, inactivity policy, deactivation, and deletion workflows. Coordinate with authentication work. |
| 17 | Basic LangGraph Integration | Pending | Establish a minimal workflow integration. |
| 18 | Basic Agent / Tool / MCP Foundation | Pending | Add the foundation needed by Phase 1 workflows. |
| 19 | Dockerization — Local Development | Pending | Complete the local development container setup. |
| 20 | Frontend + Backend Integration | Pending | Connect frontend flows to backend APIs. |
| 21 | Phase 1 Testing & Validation | Pending | Validate the integrated Phase 1 behavior. |
| 22 | Phase 1 Final Review & Lock | Pending | Review scope, known limitations, and completion evidence. |

## Current focus: Step 8 — Authentication & Authorization

### Completed

- [x] Reviewed the existing `users` and `user_sessions` database schema.
- [x] Created `Backend/app/security/password.py` using `pwdlib` with Argon2.
- [x] Created `Backend/app/tests/security/test_password.py`.
- [x] Ran the password tests locally: **4 passed, 0 failed** (reported by the developer on 2026-10-27).

### Next tasks

1. [ ] Add authentication settings to `Backend/app/core/config.py`:
   - Access-token lifetime: 15 minutes.
   - Refresh/session-token lifetime: 7 days.
   - JWT algorithm: HS256.
   - JWT signing secret loaded from local environment configuration; never commit the secret.
2. [ ] Add and test JWT access-token creation and verification utilities.
3. [ ] Define refresh/session-token generation and store only the token hash in the existing `user_sessions.token_hash` column.
4. [ ] Implement registration using the existing asynchronous `DBConnectionManager.get_session()` pattern and `users.password_hash`.
5. [ ] Implement login with password verification and active-account checks.
6. [ ] Implement logout/session revocation and token/session validation.
7. [ ] Add authorization dependencies for protected routes.
8. [ ] Add tests for token expiry, invalid tokens, registration/login outcomes, and session revocation.

### Existing implementation references

- `Backend/app/core/config.py` — Pydantic Settings; currently includes Redis and database settings.
- `Backend/app/infrastructure/database/connection.py` — asynchronous SQLAlchemy session manager with commit/rollback handling.
- `Backend/app/security/password.py` — Argon2 password hashing and verification.
- `Backend/app/tests/security/test_password.py` — four password tests currently passing in the developer's local environment.

### Implementation rules

- Keep PostgreSQL as the source of truth for persistent users and sessions.
- Reuse the existing database connection/session manager; do not introduce a duplicate connection manager.
- Never store plain-text passwords or plain refresh/session tokens in the database.
- Keep signing secrets out of Git; use local environment configuration and provide safe example variable names only.
- Do not change the existing database schema unless implementation reveals a real requirement; use a migration for any required schema change.
- The assistant reviews code and guides implementation; repository code changes are made by the developer unless direct GitHub edits are explicitly requested.
- A locally reported test result is evidence for that local run only; do not describe unrun tests as passing.

## Deferred work

- Redis production-readiness hardening, monitoring implementation, and final production review are deferred until the appropriate later stage.
