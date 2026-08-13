# Multilingual AI Chat Platform

## Database Design

**Architect:** Vivek Khillar
**Version:** 1.0
**Status:** Phase 2 — Database Design
**Architecture:** Locked
**Primary Database:** PostgreSQL
**Cache / Pub/Sub:** Redis
**Backend:** FastAPI + Python
**AI Orchestration:** LangGraph

---

## 1. Purpose

This document defines the database architecture for the Multilingual AI Chat Platform.

The database must support:

* One-to-one chat
* Group chat
* 50+ user rooms
* Multiple preferred languages
* Automatic language detection
* Automatic translation
* Translation reuse by target language
* Message delivery and read status
* User sessions and presence
* LangGraph agent execution tracking
* Tool/MCP execution tracking
* Secure encrypted message storage
* Future AWS deployment

PostgreSQL will be the **persistent source of truth**.

Redis will be used for:

* Translation caching
* Real-time Pub/Sub
* Presence
* Typing indicators
* Temporary/high-speed state

Redis will **not** replace PostgreSQL.

---

# 2. Core Database Entities

The initial database will contain these entities:

1. `users`
2. `chat_rooms`
3. `room_members`
4. `messages`
5. `message_translations`
6. `message_status`
7. `user_sessions`
8. `attachments`
9. `agent_executions`
10. `tool_executions`

---

# 3. Entity: users

## Purpose

Stores user identity, authentication-related information, profile information, and the user's preferred display language.

## Main fields

| Field                | Purpose                                        |
| -------------------- | ---------------------------------------------- |
| `user_id`            | Unique user identifier                         |
| `name`               | User display name                              |
| `email`              | User email/login identifier                    |
| `password_hash`      | Secure password hash if authentication is used |
| `preferred_language` | User's selected preferred language             |
| `status`             | Active/inactive/blocked status                 |
| `created_at`         | Account creation timestamp                     |
| `updated_at`         | Last profile update timestamp                  |

## Primary Key

`user_id`

## Important requirement

`preferred_language` is the source of truth for the user's desired translation language.

Examples:

```text
User A → or
User B → mr
User C → hi
User D → en
```

Language codes:

```text
en → English
hi → Hindi
mr → Marathi
or → Odia
bn → Bengali
gu → Gujarati
```

---

# 4. Entity: chat_rooms

## Purpose

Represents a conversation.

A room can be:

* One-to-one
* Group

## Main fields

| Field        | Purpose                     |
| ------------ | --------------------------- |
| `room_id`    | Unique room identifier      |
| `room_type`  | `private` or `group`        |
| `room_name`  | Group name where applicable |
| `created_by` | User who created the room   |
| `created_at` | Room creation timestamp     |
| `updated_at` | Last room update timestamp  |

## Primary Key

`room_id`

## Foreign Key

`created_by` → `users.user_id`

---

# 5. Entity: room_members

## Purpose

Represents the relationship between users and chat rooms.

Many-to-many relationship:

```text
users ↔ room_members ↔ chat_rooms
```

## Main fields

| Field            | Purpose                  |
| ---------------- | ------------------------ |
| `room_member_id` | Unique membership record |
| `room_id`        | Room                     |
| `user_id`        | User                     |
| `role`           | Owner/admin/member       |
| `status`         | Active/left/removed      |
| `joined_at`      | Join timestamp           |
| `left_at`        | Leave timestamp          |

## Primary Key

`room_member_id`

## Foreign Keys

```text
room_id → chat_rooms.room_id
user_id → users.user_id
```

## Rule

Do NOT duplicate `preferred_language` here.

Source of truth:

```text
users.preferred_language
```

---

# 6. Entity: messages

## Purpose

Stores original message (single source of truth).

## Main fields

| Field               | Purpose                    |
| ------------------- | -------------------------- |
| `message_id`        | Unique message identifier  |
| `room_id`           | Room reference             |
| `sender_id`         | Sender user                |
| `encrypted_content` | Encrypted original message |
| `detected_language` | AI-detected language       |
| `created_at`        | Timestamp                  |
| `updated_at`        | Update timestamp           |

## Primary Key

`message_id`

## Foreign Keys

```text
room_id → chat_rooms.room_id
sender_id → users.user_id
```

## Security Rule

No plaintext storage.

Only:

```text
encrypted_content
```

---

# 7. Entity: message_translations

## Purpose

Stores translations per message per language.

## Main fields

| Field                          | Purpose               |
| ------------------------------ | --------------------- |
| `translation_id`               | Unique translation ID |
| `message_id`                   | Original message      |
| `target_language`              | Language code         |
| `encrypted_translated_content` | Encrypted translation |
| `model_name`                   | LLM used              |
| `latency_ms`                   | Processing time       |
| `created_at`                   | Timestamp             |

## Primary Key

`translation_id`

## Foreign Key

```text
message_id → messages.message_id
```

## Constraint

Unique:

```text
(message_id, target_language)
```

---

# 8. Entity: message_status

## Purpose

Tracks delivery/read per user.

## Main fields

| Field               | Purpose             |
| ------------------- | ------------------- |
| `message_status_id` | Unique ID           |
| `message_id`        | Message             |
| `user_id`           | Recipient           |
| `status`            | sent/delivered/read |
| `delivered_at`      | Timestamp           |
| `read_at`           | Timestamp           |
| `updated_at`        | Update time         |

## Primary Key

`message_status_id`

## Foreign Keys

```text
message_id → messages.message_id
user_id → users.user_id
```

---

# 9. Entity: user_sessions

## Purpose

Tracks online presence and devices.

## Main fields

| Field           | Purpose         |
| --------------- | --------------- |
| `session_id`    | Session ID      |
| `user_id`       | User            |
| `connection_id` | WebSocket ID    |
| `device_info`   | Device metadata |
| `status`        | online/offline  |
| `last_seen`     | Activity        |
| `created_at`    | Start           |
| `expires_at`    | Expiry          |

## Primary Key

`session_id`

## Foreign Key

```text
user_id → users.user_id
```

---

# 10. Entity: attachments

## Purpose

Stores file metadata (S3 later).

## Main fields

| Field              | Purpose   |
| ------------------ | --------- |
| `attachment_id`    | ID        |
| `message_id`       | Message   |
| `file_name`        | Name      |
| `file_type`        | MIME      |
| `storage_location` | S3 path   |
| `file_size`        | Size      |
| `created_at`       | Timestamp |

## Primary Key

`attachment_id`

## Foreign Key

```text
message_id → messages.message_id
```

---

# 11. Entity: agent_executions

## Purpose

Tracks LangGraph execution lifecycle.

## Main fields

| Field           | Purpose              |
| --------------- | -------------------- |
| `execution_id`  | ID                   |
| `message_id`    | Message              |
| `agent_name`    | Agent                |
| `status`        | running/success/fail |
| `started_at`    | Start                |
| `completed_at`  | End                  |
| `latency_ms`    | Time                 |
| `error_message` | Error                |

## Primary Key

`execution_id`

## Foreign Key

```text
message_id → messages.message_id
```

---

# 12. Entity: tool_executions

## Purpose

Tracks tool / MCP calls.

## Main fields

| Field           | Purpose |
| --------------- | ------- |
| `execution_id`  | ID      |
| `message_id`    | Message |
| `tool_name`     | Tool    |
| `mcp_server`    | MCP     |
| `status`        | state   |
| `started_at`    | Start   |
| `completed_at`  | End     |
| `latency_ms`    | Time    |
| `error_message` | Error   |

## Primary Key

`execution_id`

## Foreign Key

```text
message_id → messages.message_id
```

---

# 13. 50+ User Translation Strategy

System optimizes by language, not users.

Example:

```text
50 users → 4 languages → 4 translations only
```

---

# 14. Language Routing

```text
language → users
```

Backend controls mapping.

---

# 15. Dynamic Room Language

Languages recalculated on:

* join
* leave
* preference change

---

# 16. Sender Optimization

No translation if sender language matches target.

---

# 17. Encryption

Use:

```text
AES-256-GCM
```

Store:

* messages encrypted
* translations encrypted

Keys stored in AWS KMS / Secrets Manager.

---

# 18. Encryption Flow

Write:

User → API → Encrypt → PostgreSQL

Read:

PostgreSQL → API → Decrypt → User

---

# 19. Redis Cache

Key:

```text
translation:{message_id}:{lang}
```

---

# 20. Message Flow

User → Auth → Encrypt → DB → Translate → Cache → WebSocket → Users

---

# 21. Relationships

```text
users → room_members → chat_rooms → messages → translations/status/attachments/executions
users → sessions
```

---

# 22. Summary

| Relation            | Type |
| ------------------- | ---- |
| User–Room           | M    |
| Room–Message        | 1    |
| Message–Translation | 1    |
| Message–Status      | 1    |

---

# 23. Rules

* PostgreSQL = source of truth
* Redis = cache only
* No plaintext storage
* One translation per language
* Language-based optimization required

---

# 24. Scalability

Supports:

* 10K+ users
* horizontal scaling
* read replicas
* partitioning later

---

# 25. Phase Scope

Focus:

* schema
* relationships
* encryption
* translation logic

---

# 26. Next Step

ER Diagram creation and validation.
