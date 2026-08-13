# PHASE 1 — PROJECT ARCHITECTURE

## 1. Objective

```
The objective of this project is to build a real-time multilingual chat application where users can communicate with each other using their preferred language. A user can type a message in their own language or in a supported mixed/romanized form such as Hinglish or Odlish. The application will automatically identify the language/variant of the message and translate it into the preferred language configured by each recipient.

The translated message will then be automatically delivered to the appropriate recipient without requiring the recipient to manually request a translation.

The application will support both private conversations and group conversations, including rooms with 50 or more users having different language preferences.

The system will use an LLM-based translation workflow, Redis for caching and real-time coordination, PostgreSQL for persistent data,WebSocket for real-time communication, and LangGraph for structured AI workflow orchestration.

The architecture will also provide a foundation for specialized agents, tool calling, MCP integration, encryption, Docker-based deployment, and AWS deployment.

```

## 2. Scope

The scope of the application includes the following major areas.

### 2.1 User Management

The application will support:

- User registration and login
- JWT-based authentication
- User profile management
- Preferred language configuration
- Session management
- Automatic logout after approximately 20 minutes of inactivity
- User search and filtering
- Account deactivation
- Account reactivation
- Permanent account deletion

#### Account Deactivation

```
When a user selects "Deactivate Account":

1. The account will be marked as deactivated rather than immediately
   removed from the database.
2. The system will record the account deactivation date/time.
3. The user will not be able to use the account normally while it is
   deactivated.
4. The user will have a 30-day recovery period.
5. If the user logs in within the 30-day period, the account will be
   automatically reactivated.
6. The account will become active again and the user can continue using
   the application.
7. If the user does not log in during the 30-day recovery period, the
   account will become eligible for permanent deletion.
8. The system will permanently delete the account after the
   deactivation date + 30 days according to the application's
   deletion process.

```

#### Permanent Account Deletion

```
When the user explicitly selects "Delete Account":

1. The system will clearly distinguish this action from account
   deactivation.
2. The user will be asked for confirmation before permanent deletion.
3. The account will be permanently deleted according to the defined
   data-retention and referential-integrity rules.
4. The user will not have the 30-day reactivation period after
   explicitly choosing permanent deletion.
5. Associated user data will be handled according to the application's
   deletion policy.
```

### 2.2 Language Management

The application will support:

- Human-readable language selection for users
- Internal language codes and configurations
- Language variants
- Hinglish
- Odlish
- Romanized language input
- Mixed-language input
- Automatic language and language-variant detection
- Automatic translation into the recipient's preferred language
- Requesting a language that is not currently available
- Language validation before adding a new configuration
- Administrator-controlled language addition, modification, and deactivation

### 2.3 Chat

The application will support:

- One-to-one private chat
- Group chat
- Chat rooms with 50 or more users
- Users with different language preferences within the same room
- Real-time messaging
- Message delivery status
- Read status
- Online/offline status
- Typing indicators
- Automatic recipient-specific translation

### 2.4 AI Translation

The system will:

- Detect the language of incoming messages
- Detect supported language variants and styles
- Handle Hinglish, Odlish, Romanized and mixed-language messages
- Identify the preferred language configuration of each recipient
- Determine the unique target language/configuration requirements within a room
- Avoid unnecessary duplicate translation requests
- Translate the message into the required target configurations
- Validate translation output
- Automatically deliver the appropriate translation to each recipient

### 2.5 Performance and Scalability

The application will support:

- Redis-based translation caching
- Reuse of previously generated translations where applicable
- Multiple language configurations within a single group
- 50+ users in a chat room
- Measurement of translation latency
- Measurement of end-to-end message delivery latency
- Monitoring of LLM processing performance
- Optimization of translation workload

### 2.6 Security

The application will provide:

- Authentication
- Authorization
- Secure session management
- Encryption of chat/translation data before persistent storage
- Decryption only for authorized retrieval
- Secure encryption-key management
- Protected access to user and room data
- Secure handling of attachments and media

### 2.7 AI Architecture

The AI layer will support:

- LLM-based language detection
- LLM-based translation
- LangGraph workflow orchestration
- Specialized agents
- Tool calling
- MCP integration
- Model abstraction so the underlying LLM can be replaced later

### 2.8 Infrastructure

The application will support:

- React frontend
- FastAPI backend
- PostgreSQL database
- Redis
- WebSocket communication
- Local/free LLM development using Ollama initially
- Docker containerization
- AWS deployment

### 2.9 Media and Attachments

The application will support:

- Photo attachments
- Video attachments
- Other supported file attachments
- Persistent attachment metadata in PostgreSQL
- Object/file storage for actual media files

### 2.10 Administration

An administrator will be able to:

- Manage supported languages
- Manage language variants
- Add language configurations
- Update language configurations
- Deactivate unsupported configurations
- Review and manage user language requests

## 3. System Architecture

### 3.1 High-Level Architecture

```text
                         MULTILINGUAL CHAT APPLICATION

                                ┌───────────┐
                                │   USER    │
                                └─────┬─────┘
                                      │
                                      ▼
                              ┌───────────────┐
                              │ React         │
                              │ Frontend      │
                              └───────┬───────┘
                                      │
                               REST / WebSocket
                                      │
                                      ▼
                              ┌───────────────┐
                              │ FastAPI       │
                              │ Backend       │
                              └───────┬───────┘
                                      │
              ┌───────────────────────┼───────────────────────┐
              │                       │                       │
              ▼                       ▼                       ▼
       ┌─────────────┐          ┌─────────────┐       ┌─────────────┐
       │ PostgreSQL  │          │    Redis    │       │  LangGraph  │
       │             │          │             │       │ AI Workflow │
       └─────────────┘          └─────────────┘       └──────┬──────┘
                                                             │
                                                             ▼
                                                      ┌─────────────┐
                                                      │   Agents    │
                                                      └──────┬──────┘
                                                             │
                                             ┌───────────────┼───────────────┐
                                             │               │               │
                                             ▼               ▼               ▼
                                          Tools            MCP          LLM/Ollama
```

### 3.2 Component Communication

```

   The main communication flow will be:

                           React
                           │
                           ├── REST API ────────────────┐
                           │                            │
                           └── WebSocket ───────────────┤
                                                         ▼
                                                      FastAPI
                                                         │
                                       ┌────────────────┼────────────────┐
                                       │                │                │
                                       ▼                ▼                ▼
                                    PostgreSQL          Redis          LangGraph
                                                                           │
                                                                           ▼
                                                                        Agents
                                                                           │
                                                               ┌─────────┴─────────┐
                                                               ▼                   ▼
                                                               Tools                MCP
                                                               │                   │
                                                               └─────────┬─────────┘
                                                                           ▼
                                                                        LLM
```

### 3.3 Core Architectural Principle

The frontend will not directly communicate with:

- PostgreSQL
- Redis
- LangGraph
- Agents
- LLM
- MCP

All communication will go through the backend.                                                                    

```
React
  ↓
FastAPI
  ↓
Internal Services
```

This provides:

- Security
- Access control
- Maintainability
- Scalability
- Separation of responsibilities

### 3.4 Message Architecture

A typical message will eventually flow like this:

```text
         User A
         ↓
         React
         ↓
         WebSocket
         ↓
         FastAPI
         ↓
         Identify Chat Room
         ↓
         Get Room Members
         ↓
         Get Preferred Languages
         ↓
         Determine Required Target Languages
         ↓
         Redis Cache Check
         ↓
         LangGraph
         ↓
         Translation Agent
         ↓
         LLM
         ↓
         Translation Validation
         ↓
         Store Result
         ↓
         Redis / WebSocket
         ↓
         Correct Translation → Each Recipient

```

### 3.5 Important Design Rule

The **LLM will not decide which user receives which translation**.

The application backend will determine:

```text
Who is in the room?
        ↓
What language does each user prefer?
        ↓
Which unique translations are required?
        ↓
Which user should receive each translation?
```

The LLM's responsibility is primarily:

```
Understand language
        ↓
Translate
        ↓
Return translation
```

## 4. Frontend Architecture

### 4.1 Frontend Technology

- **The frontend will be developed using:**
  - **React**
  - **HTML & CSS**
  - **TypeScript**
  - **WebSocket Client:** For real-time communication
  - **REST API Client:** For standard backend communication

The frontend is strictly responsible for the user interface and user interactions. 

> ⚠️ **Architectural Boundary:** The frontend will **not** directly communicate with PostgreSQL, Redis, LangGraph, Agents, MCP, or the LLM. All communication must pass through FastAPI.

```text
React Frontend
      │
      ├── REST API
      │
      └── WebSocket
             │
             ▼
        FastAPI Backend
```

---

### 4.2 Frontend Responsibilities

The frontend will provide interface and state management for the following functionalities:

- **Authentication & Account Management:**
  - User Registration
  - User Login
  - Forgot Password
  - Account Deactivation
  - Account Reactivation
  - Permanent Account Deletion
  - Automatic Logout after inactivity
- **Profile & Preferences:**
  - User Profile view and updates
  - Preferred Language Selection
  - Language Variant Selection (where applicable)
- **Messaging & Communication:**
  - Chat List view
  - Private Chat interface
  - Group Chat interface
  - Message Input and typing interface
  - Message Display (Original Message information & Automatically Translated Messages)
  - Photo, Video, and File attachment interface
- **Real-Time Indicators:**
  - Online / Offline Status tracking
  - Typing Indicators
  - Message Delivery Status
  - Message Read Status
- **Administration & Room Management:**
  - Create Chat Room
  - Add or Remove Room Members (based on permissions)
  - User Search functionality
  - Admin Language Management
  - Language Request submission interface

---

### 4.3 Authentication Screens

#### Registration

Users can:

- Create a new account
- Provide required profile details
- Select a preferred primary language
- Select supported language variants (if applicable)

#### Login

Users can:

- Enter login credentials
- Authenticate against the backend
- Establish an authenticated session and enter the application

#### Forgot Password

- Provides the UI interface for initiating recovery.
- The actual password reset token generation, delivery, and verification are strictly handled by the backend.

---

### 4.4 User Profile

The profile section allows users to:

- View and update profile information
- Select preferred language and language variants
- View account status
- Deactivate or permanently delete their account

> **Note:** The preferred language selected by the user is stored on the backend and used to route and deliver appropriately translated messages to that user.

---

### 4.5 Language Selection

To ensure usability, the frontend displays human-readable language names rather than technical language codes.

#### UI Display Example

```text
Select Preferred Language
[ Marathi  ▼ ]
```

**Available Options:**

- English
- Hindi
- Marathi
- Odia
- Bengali
- Tamil
- Telugu
- Kannada
- Malayalam
- Gujarati
- Punjabi
- *Other supported languages*

#### Internal Mapping

Users select friendly names; the backend receives standard codes:


| User Interface Display | Backend Code Received |
| ---------------------- | --------------------- |
| Marathi                | `mr`                  |
| Odia                   | `or`                  |
| Hindi                  | `hi`                  |


---

### 4.6 Language Variant Selection

Where a language supports regional or written variants, the frontend provides secondary dropdown options.

- **Hindi:** `Standard Hindi`, `Hinglish`
- **Odia:** `Standard Odia`, `Odlish`

*Internal variant mappings are parsed and handled by the backend.*

---

### 4.7 Missing Language Request

If a required language or variant is not supported, users can submit a request through the system.

#### Request Execution Flow

```text
User
  ↓
React Frontend
  ↓
Language Request Form
  ↓
FastAPI Backend
  ↓
Language Validation
  ↓
Agent / LLM Validation (where required)
  ↓
Admin Review & Approval
  ↓
PostgreSQL
  ↓
Language Becomes Available System-Wide
```

---

### 4.8 Chat List

The primary chat interface displays:

- Private conversations & Group conversations
- Chat name & Profile/Group avatars
- Latest message preview & timestamp
- Unread message counter
- Live online status indicators

*All chat list metadata is fetched via FastAPI REST endpoints.*

---

### 4.9 Private Chat

Enables direct 1-on-1 communication with seamless, automatic translation.

#### Scenario Example

- **User A** (Preferred Language: **Odia**)
- **User B** (Preferred Language: **Marathi**)

1. **User A types:** `"Mu aji office jibi"`
2. **Backend Processing:** Detects source dialect, processes message, translates to Marathi.
3. **User B receives:** `"मी आज ऑफिसला जाईन."`

> **Key Design:** User B receives the translated text automatically without having to manually click a "Translate" button.

---

### 4.10 Group Chat

The frontend supports scaling group rooms (50+ users) with mixed language preferences.

```text
Room Members:
 ├── User A (Odia)
 ├── User B (Marathi)
 ├── User C (Hindi)
 ├── User D (English)
 └── User E (Hinglish)
```

- **Frontend Role:** Displays the specific translated payload meant for the currently logged-in user.
- **Backend Role:** Determines recipient target languages, requests/generates necessary translations, and fans out localized payloads via WebSocket.

---

### 4.11 Message Display

Automatic translation presentation pipeline:

```text
Incoming Message
       ↓
Backend determines recipient preference
       ↓
Translation generated
       ↓
WebSocket Payload Transmitted
       ↓
React Client Receives Payload
       ↓
Display Translated Message
```

*Optionally, the UI can offer a toggle/accordion to reveal the original source message based on UI/UX requirements.*

---

### 4.12 Real-Time Communication

The frontend maintains a persistent **WebSocket connection** for real-time events, including:

- New incoming messages & completed translations
- Message delivery & read receipts
- Typing indicators
- User online/offline status updates
- Room dynamic events (member added/removed)
- Connection state changes (connect/reconnect/disconnect)

---

### 4.13 Online / Offline Status

Displays dynamic user availability across chat views:

- Vivek **● Online**
- Vivek **○ Offline**

> **Implementation:** Status states are continuously tracked by the backend using **Redis**. React purely presents the state received over WebSocket.

---

### 4.14 Typing Indicator

- Displays real-time status: `User A is typing...`
- Transmitted purely via lightweight WebSocket events.
- *Typing events are ephemeral and never persisted in PostgreSQL.*

---

### 4.15 Message Status

Messages render real-time state flags:

1. **Sent** (Single checkmark / status)
2. **Delivered** (Double checkmark / status)
3. **Read** (Highlighted / colored double checkmark)

The backend acts as the single source of truth for message states.

---

### 4.16 User Search

Provides a search interface for finding users to initiate chats:

```text
Search users...
[ Vivek      ]
[ Rahul      ]
[ Priya      ]
```

*Search queries call FastAPI endpoints; direct database lookups from the UI are strictly prohibited.*

---

### 4.17 Chat Room Creation

Interface allows users to:

1. Select target (Private vs. Group Chat)
2. Assign a Group Name and Avatar
3. Search, select, and review added members
4. Dispatch creation request

*The backend validates creation permissions before persisting room data.*

---

### 4.18 Account Deactivation

Provides a flow to temporarily disable accounts with explicit warnings.

```text
Account
   ↓
Deactivated
   ↓
30-Day Recovery Period

- **Logging in within 30 days:** Instantly reactivates the account.
- **Inactivity exceeding 30 days:** Account becomes permanently eligible for backend deletion jobs.
```

---

### 4.19 Permanent Account Deletion

A dedicated flow distinct from deactivation.

- Requires explicit, multi-step user confirmation.
- **No recovery window:** Bypasses the 30-day grace period.
- Triggers hard/soft compliance wipe on the backend.

---

### 4.20 Session Timeout

- **Client-side Inactivity:** The frontend monitors mouse/keyboard activity. Inactivity reaching ~20 minutes automatically triggers a local logout.
- **Server-side Security:** FastAPI enforces JWT/Session invalidation to prevent client-side bypasses.

---

### 4.21 Admin Interface

An isolated, role-restricted dashboard for managing system languages:

- View supported languages and active variants
- Add/Update/Deactivate language configurations
- Queue review, approval, or rejection for user-submitted Language Requests

---

### 4.22 Media and Attachments

- Handles user uploads for photos, videos, and general attachments.
- **Storage Pipeline:** Attachments upload through FastAPI to Cloud Object Storage (e.g., AWS S3). 
- Metadata (file size, S3 URL, file type) is stored in PostgreSQL via the API.

---

### 4.23 Frontend-to-Backend Communication Summary

The client communicates with FastAPI through two unified pathways:

#### 1. REST API

- Authentication (Login / Register / Password Reset)
- Profile Management & Language Preferences
- User Search & Chat Room Creation
- Account Lifecycles (Deactivation / Deletion)
- Admin Management
- File Attachment Uploads

#### 2. WebSocket

- Real-time message sending & localized payload delivery
- Typing indicators & status updates
- Message status receipts (Sent / Delivered / Read)
- Room events & member state changes

---

### 4.24 Frontend Architectural Boundary

To maintain separation of concerns, the frontend is bound strictly to specific operational domains:


| Allowed Frontend Responsibilities | Prohibited (Backend / AI Responsibilities) |
| --------------------------------- | ------------------------------------------ |
| User Interface & Interaction      | Direct PostgreSQL or Redis access          |
| Form Validation & Local State     | Direct LLM / MCP / LangGraph calls         |
| Displaying Data & Translations    | Source Language Detection decisions        |
| Client-side Session Handling      | Target Recipient Translation Routing       |
| REST API & WebSocket handling     | Encryption Key & Permission Authorization  |


---

### 4.25 Frontend Architecture Diagram

```text
                         React Frontend
                                │
              ┌─────────────────┴─────────────────┐
              │                                   │
              ▼                                   ▼
          REST API                             WebSocket
              │                                   │
              └─────────────────┬─────────────────┘
                                ▼
                         FastAPI Backend
```

## 5. Backend Architecture

### 5.1 Backend Technology

The backend will be developed using:

- **Python**
- **FastAPI**
- **REST API & WebSocket**
- **PostgreSQL & Redis**
- **LangGraph & LLM integration**
- **JWT authentication & Encryption services**
- **Tool calling & MCP integration**

> ⚠️ **Architectural Concept:** FastAPI will act as the **central application coordinator**. The React frontend will communicate with FastAPI through REST APIs and WebSocket connections.

```text
React + TypeScript
        │
        ├── REST API
        │
        └── WebSocket
                │
                ▼
        FastAPI Backend
```

---

### 5.2 Backend Responsibilities

FastAPI will be responsible for managing the following domains:

- **Identity & Security:**
  - Authentication & Authorization
  - Session management
  - Encryption/decryption coordination
  - Account deactivation, reactivation, and permanent deletion
- **User & Room Management:**
  - User and Profile management
  - Chat room and Room member management
  - Admin operations
- **Messaging & Communication:**
  - Message management and Routing
  - WebSocket communication
  - Attachment management
- **Language & AI Orchestration:**
  - Language configuration, preferences, and request management
  - Translation orchestration
  - LangGraph integration and Agent orchestration
  - Tool calling and MCP integration
- **Data & Operations:**
  - PostgreSQL and Redis communication
  - Logging, Error handling, and Performance monitoring

---

### 5.3 Backend Architectural Layers

The backend will follow a strictly layered architecture.

```text
                         FastAPI Backend
                                │
        ┌───────────────────────┼───────────────────────┐
        │                       │                       │
        ▼                       ▼                       ▼
   API Layer              WebSocket Layer         Admin API
        │                       │                       │
        └───────────────────────┼───────────────────────┘
                                ▼
                       Application / Service Layer
                                │
             ┌──────────────────┼──────────────────┐
             │                  │                  │
             ▼                  ▼                  ▼
       User Services      Chat Services      Language Services
             │                  │                  │
             └──────────────────┼──────────────────┘
                                ▼
                         AI Orchestration
                                │
                           LangGraph
                                │
                    ┌───────────┼───────────┐
                    ▼           ▼           ▼
                 Agents       Tools        MCP
                    │           │           │
                    └───────────┼───────────┘
                                ▼
                               LLM
                                │
        Data / Infrastructure Layer
                    │
          ┌─────────┴─────────┐
          ▼                   ▼
      PostgreSQL            Redis
```

---

### 5.4 API Layer

The API layer will expose REST endpoints for operations that do not require continuous real-time communication. It will handle:

- Request validation
- Authentication & Authorization
- Request/response handling
- Calling application services
- Returning standardized responses
- Error handling

> **Note:** The API layer should not contain complex business logic. Business logic must strictly remain inside the Application/Service layer.

---

### 5.5 WebSocket Layer

WebSocket will be responsible for real-time communication. It will support:

- Sending and receiving messages
- Translated message delivery
- Typing indicators
- Online/offline status updates
- Message delivery and read statuses
- Real-time room events
- Connection management, disconnection handling, and reconnection support

The WebSocket layer will communicate with the application/service layer instead of directly implementing translation or database logic.

```text
React
  │
  │ WebSocket
  ▼
FastAPI WebSocket Layer
  │
  ▼
Chat Service
  │
  ├── Message Service
  ├── Translation Service
  └── Routing Service
```

---

### 5.6 Authentication

The backend will implement **JWT-based authentication**. Authentication will be required for protected application operations. The backend will validate the authentication token before allowing access to protected resources.

#### Authentication Flow:

```text
User
  ↓
React Login
  ↓
FastAPI
  ↓
Validate Credentials
  ↓
Generate Authentication Token
  ↓
React
  ↓
Authenticated Requests
```

---

### 5.7 Authorization

While Authentication answers *"Who is this user?"*, Authorization answers *"What is this user allowed to do?"*

FastAPI will enforce authorization for:

- User resources
- Private conversations & Group rooms
- Room membership & Room administration
- Language management
- Account & Administrative operations
- Attachments & Message access

*Example: A normal user cannot manage global language configurations. Only authorized administrators will have access to those operations.*

---

### 5.8 User Management Service

The User Service will communicate with PostgreSQL through the data-access layer to manage:

- Registration & Login support
- Profile retrieval & Profile update
- Preferred language & Language variant preference
- User search
- Account status (deactivation, reactivation, permanent deletion)

---

### 5.9 Account Deactivation and Deletion

The backend will maintain separate account states. A scheduled/background process will eventually identify accounts whose recovery period has expired and process them.

#### Deactivation Flow:

```text
ACTIVE
   │
   │ User chooses deactivate
   ▼
DEACTIVATED
   │
   ├── Login within 30 days
   │        ↓
   │     ACTIVE
   │
   └── No login for 30 days
            ↓
      Eligible for deletion
```

#### Permanent Deletion Flow (Separate Action):

```text
ACTIVE
   │
   │ User chooses permanent delete
   ▼
PERMANENT DELETION
```

---

### 5.10 Language Management Service

The Language Service will manage:

- Supported languages & Language codes
- Human-readable language names
- Language variants & Romanized language variants
- Mixed-language configurations
- User language preferences
- Language requests, validation, and activation/deactivation

The frontend displays user-friendly names, while the backend utilizes internal codes:


| Frontend Shows | Backend Processes      |
| -------------- | ---------------------- |
| Marathi        | `language_code = "mr"` |


---

### 5.11 Language Request Flow

When a user requests a language or variant that is not available, the LLM/Agent will **not** directly insert an unverified language into production. It must follow this flow:

```text
User
  ↓
React
  ↓
FastAPI
  ↓
Language Request Service
  ↓
Validation / AI-assisted verification where required
  ↓
Admin Review
  ↓
Approved
  ↓
Language Configuration
  ↓
PostgreSQL
```

---

### 5.12 Chat Room Service

The Chat Room Service determines which users belong to a room and manages:

- Private & Group conversations
- Room creation & Room updates
- Room members & Member permissions
- Room status & Room metadata

---

### 5.13 Message Service

The message service will **not** allow the frontend to directly insert records into PostgreSQL. It is strictly responsible for managing:

- Incoming messages & Message validation
- Message persistence & Message retrieval
- Message status & Message metadata
- Attachment & Translation association

---

### 5.14 Message Routing Service

The Message Routing Service is responsible for determining where a message should go. 

> ⚠️ **Boundary Rule:** The LLM will **not** be responsible for recipient routing. This separation is vital for security, correctness, and scalability.

#### Routing Determination Flow:

```text
Who sent it?
        ↓
Which room?
        ↓
Who are the recipients?
        ↓
What is each recipient's preferred language?
        ↓
Which unique target languages are required?
        ↓
Which translated message should be delivered to which recipient?
```

---

### 5.15 Translation Orchestration

FastAPI will coordinate the translation workflow through LangGraph. 

```text
Incoming Message
       ↓
FastAPI
       ↓
Message Service
       ↓
Recipient Resolution
       ↓
Language Requirements
       ↓
Redis Cache Check
       ↓
LangGraph
       ↓
AI Agents
       ↓
LLM
       ↓
Translation Result
       ↓
Validation
       ↓
Store / Cache
       ↓
Message Routing
       ↓
WebSocket
       ↓
Recipients
```

---

### 5.16 LangGraph Integration

LangGraph will provide structured orchestration for AI-related processing. FastAPI will invoke the LangGraph workflow when AI processing is required. LangGraph will coordinate specialized agents rather than putting all AI responsibilities into one large function. 

Potential responsibilities include:

- Language & Language variant detection
- Translation planning & execution
- Translation validation
- AI-related decision support

---

### 5.17 Agent Architecture

The application will use specialized agents where they provide clear benefits. Agents will **not** directly bypass application security or database authorization.

```text
                       LangGraph
                           │
             ┌─────────────┼─────────────┐
             │             │             │
             ▼             ▼             ▼
       Language Agent  Translation   Validation
                         Agent         Agent
             │             │             │
             └─────────────┼─────────────┘
                           ▼
                          LLM
```

---

### 5.18 Tool Calling

Agents may use controlled tools when required. Tools will have clearly defined inputs and outputs and will **not** be allowed unrestricted access to the entire application.

Examples include:

- Language configuration & User preference lookup
- Translation cache lookup & storage
- Validation services
- Application-specific operations

---

### 5.19 MCP Integration

MCP will provide a standardized mechanism for exposing selected tools or external capabilities to the AI workflow. It will be introduced only where it provides real architectural benefit and will **not** replace normal FastAPI business logic.

```text
LangGraph
    ↓
Agent
    ↓
MCP
    ↓
Approved Tool / Service
    ↓
Result
    ↓
Agent
```

---

### 5.20 PostgreSQL Integration

FastAPI will communicate with PostgreSQL through the application's data-access/repository layer to manage persistent information:

- Users & Sessions
- Language configurations & Language preferences
- Chat rooms & Room members
- Messages, Translations, & Message statuses
- Attachments
- Agent & Tool execution information

---

### 5.21 Redis Integration

Redis will be used for short-lived and high-speed application data. It will **not** replace PostgreSQL as the permanent system of record. Uses include:

- Translation caching
- Presence information (Online/offline state, Typing state)
- WebSocket coordination
- Temporary session-related data & frequently accessed temporary data
- Rate limiting

---

### 5.22 Translation Cache

Before sending a translation request to the LLM, the backend will check Redis. This reduces LLM calls, translation latency, compute requirements, and API costs.

```text
Message
  ↓
Target Language
  ↓
Redis Cache?
  │
  ├── YES → Reuse Translation
  │
  └── NO
        ↓
      LangGraph
        ↓
       LLM
        ↓
    Translation
        ↓
   Store in Redis
```

---

### 5.23 50+ User Group Chat (Target Optimization)

For large groups, the system will **not** automatically make 50 separate LLM translation requests. Instead, it aggregates unique translation requirements and generates them once.

```text
50 Users
   │
   ├── 20 → Marathi
   ├── 15 → Hindi
   ├── 10 → English
   ├── 3  → Odia
   └── 2  → Bengali
```

*Result: The system only requests 5 unique translations, caches them in Redis, and routes them to the appropriate recipients.*

---

### 5.24 Encryption Boundary

The backend will coordinate encryption before sensitive chat data is persisted. Encryption keys will **not** be stored directly alongside the encrypted message data.

#### Persistence Flow:

```text
Message
   ↓
FastAPI
   ↓
Encryption Service
   ↓
Encrypted Data
   ↓
PostgreSQL
```

#### Retrieval Flow:

```text
PostgreSQL
   ↓
Encrypted Data
   ↓
FastAPI
   ↓
Authorization Check
   ↓
Decryption
   ↓
React
```

---

### 5.25 Attachment Handling

Actual media files should not be stored directly inside PostgreSQL. FastAPI will coordinate attachment uploads to object storage (e.g., AWS S3).

```text
React
  ↓
FastAPI
  ↓
Validate User / Room Permission
  ↓
Validate Attachment
  ↓
Object Storage (S3)
  ↓
Attachment Metadata
  ↓
PostgreSQL
```

---

### 5.26 Error Handling

The backend will provide consistent, standardized error responses to the frontend for:

- Authentication & Authorization errors
- Invalid requests & Invalid language configurations
- Room access & Message processing errors
- Translation & LLM failures
- WebSocket, Database, & Redis failures
- Attachment & External service failures

---

### 5.27 Retry and Failure Handling

The backend will provide controlled retry mechanisms to avoid overloading the LLM or backend during temporary failures.

```text
LLM temporary failure
        ↓
Retry according to policy
        ↓
Still failing?
        ↓
Mark translation as failed / pending
        ↓
Notify or recover according to application policy
```

---

### 5.28 Logging

FastAPI will provide structured application logging. **Sensitive message content and credentials will strictly NOT be written into application logs.** 

Logged events include:

- Authentication events & Authorization failures
- Message & Translation processing
- LLM latency
- WebSocket connection events
- Database & Redis errors
- Agent, Tool, & MCP execution operations
- Attachment & Account operations

---

### 5.29 Performance Monitoring

The backend will measure important timings to determine the actual end-to-end latency of a translated message.

```text
Message received
        ↓
Language detection time
        ↓
Translation processing time
        ↓
Translation validation time
        ↓
Message routing time
        ↓
WebSocket delivery time
```

---

### 5.30 Backend Responsibility Boundary

The AI layer will **not** replace normal backend business logic. Responsibilities are strictly divided:


| FastAPI Core Responsibilities                  | AI / LangGraph Responsibilities |
| ---------------------------------------------- | ------------------------------- |
| Authentication & Authorization                 | Language Understanding          |
| Business Logic & User/Room Management          | Language & Variant Detection    |
| Message Management & Routing                   | Translation Processing          |
| WebSocket & Redis Coordination                 | Translation Validation          |
| Database Access & Attachments                  | AI Workflow Processing          |
| Encryption Coordination, Logging, & Monitoring |                                 |


---

### 5.31 Backend Architecture Summary

```text
                       React + TypeScript
                              │
                    REST API / WebSocket
                              │
                              ▼
                     ┌─────────────────┐
                     │     FastAPI     │
                     │     Backend     │
                     └────────┬────────┘
                              │
       ┌──────────────────────┼──────────────────────┐
       │                      │                      │
       ▼                      ▼                      ▼
  PostgreSQL                Redis               LangGraph
                                                    │
                                             ┌──────┴──────┐
                                             │             │
                                          Agents         Tools
                                             │             │
                                             └──────┬──────┘
                                                    │
                                                   MCP
                                                    │
                                                    ▼
                                                   LLM
```

