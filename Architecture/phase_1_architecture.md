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

### 4.26 Profile Language Selection

The frontend dynamically loads language configurations from the backend, ensuring it relies on the database rather than hardcoded client values.

#### Selection Flow:

```text
FastAPI
   ↓ (GET supported languages)
React Frontend
   ↓
Displays "Preferred Language" dropdown
   ↓
User selects "Marathi"
   ↓
Frontend sends the selected `language_id` (e.g., 5)
   ↓
FastAPI resolves: language_id → language_configurations → Marathi → "mr"
```

*React sends the database ID, never the raw string code.*

### 4.27 Language Dropdown UI

The UI displays human-readable, native scripts to maximize user-friendliness. 

```text
Select your preferred language

┌─────────────────────────────┐
│ English                     │
│ हिन्दी                        │ 
│ मराठी                       │ 
│ ଓଡ଼ିଆ                        │
│ Hinglish                    │
│ Odlish                      │
└─────────────────────────────┘
```

### 4.28 Variant Selection

For languages where variants are relevant (like Odia vs Odlish), the UI simplifies the technical choices into natural user questions.

Instead of asking the user to select technical variants:

```text
Language: [ Odia ▼ ]
Writing style: [ Standard Odia ▼ ] / [ Odlish ▼ ]
```

The frontend uses a highly user-friendly approach:

```text
Language: [ Odia ▼ ]

How do you normally type?
 ◉ Odia script
 ◯ English letters
```

The backend then maps this seamlessly:

- `Odia` + `Odia script` → **Standard Variant**
- `Odia` + `English letters` → **Odlish Variant**

---

### 4.29 Important Frontend Rule

> ⚠️ **Architectural Boundary:** The frontend should **not** perform language detection or translation.


| React's Responsibility      | FastAPI / AI Layer's Responsibility |
| --------------------------- | ----------------------------------- |
| UI State & Display          | Language Detection                  |
| User Input & Interaction    | Language Resolution                 |
| WebSocket Connection        | Translation Processing              |
| Presenting target languages | Message Routing                     |


---

### 4.30 Chat Message Flow

The frontend acts purely as a presentation and transmission layer. 

```text
User A types: "mu aji office jibi"
      ↓
React simply sends the raw Message to FastAPI
```

*React does NOT need to determine if it is `or`, `Odlish`, or `mr`. The backend handles all detection.*

---

### 4.31 Message Display

Automatic translation presentation pipeline:

- **User B Preferred language:** Marathi
- **Backend Delivers:** `translated_message`
- **React Action:** Simply displays the text.

```text
User A sees: "mu aji office jibi"
User B sees: "मी आज ऑफिसला जाईन."
```

*The user does not need to click a "Translate" button or manually select "Marathi" for every message.*

---

### 4.32 Group Chat UI

Every user in a 50+ member group receives the message instantly translated according to their specific profile preference.

```text
┌───────────────────────────────────┐
│ Project Team                      │
│ 50 members                        │
├───────────────────────────────────┤
│                                   │
│ Vivek                             │
│ mu aji office jibi                │
│                                   │
│ Rahul                             │
│ <translated according to Rahul>   │
│                                   │
│ Priya                             │
│ <translated according to Priya>   │
│                                   │
├───────────────────────────────────┤
│ Type message...              [➤] │
└───────────────────────────────────┘
```

---

### 4.33 Frontend Architecture

The updated React application structure, routing all capabilities strictly through FastAPI:

```text
React + TypeScript
        │
        ├── Authentication & Registration
        ├── Profile & Language Selection
        ├── Chat List
        ├── Private Chat & Group Chat
        ├── Message Input & Display
        ├── Typing Indicator
        ├── Online Status & Message Status
        ├── Search & Room Creation
        ├── Language Request
        └── Account Deactivation & Deletion
                 │
                 ▼
              FastAPI
```

---

### 4.34 Updated End-to-End Architecture

The complete system architecture, reflecting the proper separation of AI orchestration, data management, and client presentation:

```text
                        React + TypeScript
                               │
                    REST API + WebSocket
                               │
                               ▼
                         FastAPI Backend
                               │
          ┌────────────────────┼────────────────────┐
          │                    │                    │
          ▼                    ▼                    ▼
     PostgreSQL              Redis              LangGraph
          │                                         │
          │                              ┌──────────┼──────────┐
          │                              ▼          ▼          ▼
          │                          Language   Translation Validation
          │                            Agent       Agent      Agent
          │                              │          │
          │                              └────┬─────┘
          │                                   ▼
          │                                  LLM
          │
          └─────────────────────────────────────────┐
                                                    │
                                                    ▼
                                             Message Routing
                                                    │
                                                    ▼
                                               WebSocket
                                                    │
                                                    ▼
                                             React Users
```

---

### 4.35 The Most Important Change: Responsibility Matrix

The system responsibilities are now completely locked and clearly separated, establishing the final blueprint before implementation.


| System Component | Core Question It Answers                           | Primary Action                                                          |
| ---------------- | -------------------------------------------------- | ----------------------------------------------------------------------- |
| **React**        | *"What did the user select?"*                      | Captures input, displays messages seamlessly.                           |
| **PostgreSQL**   | *"What is that language's configuration?"*         | Stores profiles, room states, and translation configurations.           |
| **FastAPI**      | *"What are the source and target configurations?"* | Coordinates routing, auth, database, and initiates AI workflows.        |
| **LangGraph**    | *"What AI processing is required?"*                | Orchestrates the fallback detectors and translation agents.             |
| **LLM**          | *"Translate from source → target."*                | Executes the actual natural language translation.                       |
| **Redis**        | *"Can we reuse an existing translation?"*          | Caches translations to bypass LLM latency and manages real-time states. |
| **WebSocket**    | *"Deliver the translation to the right users."*    | Pushes the finalized, personalized message to connected clients.        |


---

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

FastAPI will be responsible for:

- Authentication & Authorization
- User & Profile management
- Language configuration, preference management, and request management
- Chat room & Room member management
- Message management & Message routing
- Translation orchestration
- WebSocket, PostgreSQL, and Redis communication
- LangGraph integration & Agent orchestration
- Tool calling & MCP integration
- Encryption/decryption coordination
- Attachment & Session management
- Account deactivation, reactivation, and deletion
- Admin operations
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

> **Note:** The API layer should not contain complex business logic. Business logic must strictly remain inside the service/application layer.

---

### 5.5 WebSocket Layer

WebSocket will be responsible for real-time communication. It will support:

- Sending and receiving messages
- Translated message delivery
- Typing indicators & Online/offline status
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

The backend will implement **JWT-based authentication**. Authentication will be required for protected application operations.

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

*A normal user must not be able to manage global language configurations. Only authorized administrators will have access to those operations.*

---

### 5.8 User Management Service

The User Service will manage:

- Registration & Login support
- Profile retrieval & Profile updates
- Preferred language & Language variant preferences
- User search
- Account status (deactivation, reactivation, permanent deletion)

The service will communicate with PostgreSQL through the data-access layer.

---

### 5.9 Account Deactivation and Deletion

The backend will maintain separate account states. A scheduled/background process will identify accounts whose 30-day recovery period has expired and process them.

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

- Supported languages, Language codes, Human-readable & Native language names
- Language variants, Romanized language variants, Script information
- Mixed-language configurations
- User language preferences & Language requests
- Language validation & Language activation/deactivation

The frontend shows user-friendly names, while the backend works with internal codes:


| Frontend Shows | Backend Uses           |
| -------------- | ---------------------- |
| Marathi        | `language_code = "mr"` |


Users will not be required to manually understand or enter language codes.

---

### 5.11 Language Configuration Structure

The language configuration contains information required by both the application and AI translation workflow.

```text
Language Configuration
│
├── language_id
├── language_code
├── language_name
├── native_name
├── script
├── variant
├── status
└── translation_supported
```

**Examples:**

*Standard Hindi:*

- Language: Hindi (`hi`) | Native Name: हिन्दी | Script: Devanagari | Variant: Standard

*Standard Odia:*

- Language: Odia (`or`) | Native Name: ଓଡ଼ିଆ | Script: Odia | Variant: Standard

*Odlish (Romanized Chat):*

- Language: Odia (`or`) | Script: Latin | Variant: Odlish

*The same language code may therefore have multiple supported variants or scripts.*

---

### 5.12 Language Identification Architecture

The application will use a hybrid language-identification approach. For incoming messages, the language-identification layer will attempt to determine:

- Language & Language code
- Language variant & Script
- Mixed-language characteristics
- Detection confidence

#### Example Detection:

```text
Input:      "mu aji office jibi"

Detected:   Language   = Odia
            Code       = or
            Variant    = Odlish
            Script     = Latin
            Confidence = High
```

---

### 5.13 Fast Language Detection Strategy

Language detection should not require an LLM call for every message. The application will use a fast detection layer first.

```text
Incoming Message
       ↓
Fast Language Detection
       ↓
Confidence Check
       │
       ├── High Confidence
       │       ↓
       │   Accept Detection
       │
       └── Low Confidence / Ambiguous
               ↓
            LangGraph
               ↓
          Language Agent
               ↓
              LLM
               ↓
       Confirm / Resolve Language
```

The LLM will primarily be used when the message is: Ambiguous, Mixed-language, Romanized, Hinglish, Odlish, or difficult for the fast detector to classify. This reduces unnecessary LLM calls and improves latency.

---

### 5.14 Language Code Resolution

Language codes will be used internally by the application (e.g., English → `en`, Hindi → `hi`, Marathi → `mr`). The backend will use the language code to retrieve the complete language configuration from PostgreSQL.

```text
language_code = "mr"
        ↓
PostgreSQL
        ↓
Language Configuration
        ↓
Language Name = Marathi
Script = Devanagari
Variant = Standard
```

---

### 5.15 Language Code → Language Name Workflow

Before translation, FastAPI will resolve the internal language codes into their corresponding language configurations. The Translation Agent should not be responsible for determining what a language code means.

```text
User Message
      ↓
FastAPI
      ↓
Source Language Detection
      ↓
Source Language Code
      ↓
Find Recipients
      ↓
PostgreSQL
      ↓
Fetch Each Recipient's Preferred Language Code
      ↓
Language Configuration Lookup
      ↓
Resolve Language Codes
      ↓
Source Language Name + Target Language Name + Variant / Script information
      ↓
Translation Agent → LLM
```

---

### 5.16 Complete Language Resolution and Translation Workflow

This is the final language-processing workflow for the application.

*Scenario: User A (Odlish) sends `"mu aji office jibi"`. User B prefers Marathi.*

```text
                     User A
                        │
                        ▼
              "mu aji office jibi"
                        │
                        ▼
                     FastAPI
                        │
                        ▼
             Fast Language Detection
                        │
                  Is confidence
                     sufficient?
                    /          \
                  YES           NO
                   │             │
                   │          LangGraph
                   │             │
                   │       Language Agent
                   │             │
                   │            LLM
                   │             │
                   └──────┬──────┘
                          ▼
               Source Language Result
                          │
                Code = "or"
                Language = Odia
                Variant = Odlish
                Script = Latin
                          │
                          ▼
                   Find Recipients
                          │
                          ▼
                     PostgreSQL
                          │
                          ▼
             User B Preferred Language
                          │
                     Code = "mr"
                          │
                          ▼
              Language Configuration
                          │
                          ▼
               Code "mr" → Marathi
                          │
                          ▼
                  Translation Agent
                          │
                          ▼
                         LLM
                          │
              ┌───────────┴───────────┐
              │                       │
          Source                    Target
           Odia                      Marathi
            or                         mr
          Odlish
          Latin
              │                       │
              └───────────┬───────────┘
                          ▼
                    Translation
                          │
                          ▼
                    Redis Cache
                          │
                          ▼
                     WebSocket
                          │
                          ▼
                       User B
```

This gives the model explicit information about what language it is translating from and to.

---

### 5.17 Preferred Language Resolution

The preferred language must **NOT** be determined by the LLM. The user's preferred language is stored in PostgreSQL.

```text
User B → PostgreSQL → preferred_language_code = "mr"
```

FastAPI retrieves the preference and resolves it through the Language Configuration. No LLM call is required for this operation, improving both performance and reliability.

---

### 5.18 Translation Request Construction

FastAPI / the Translation Service will prepare the translation context before invoking the Translation Agent. 

```text
Source:
Language Name = Odia
Language Code = or
Variant = Odlish
Script = Latin

Target:
Language Name = Marathi
Language Code = mr
Variant = Standard
Script = Devanagari

Message:
mu aji office jibi
```

The model is therefore not responsible for resolving internal user preferences.

---

### 5.19 Multiple Target Languages

A single message may need to be translated into multiple languages based on current room members.

```text
Room:
User B → Marathi → mr
User C → Hindi   → hi
User D → English → en
User E → Odia    → or
```

FastAPI will identify and resolve the unique target languages, and the translation workflow will process the required translations.

---

### 5.20 50+ User Group Chat Optimization

For a group with 50 or more users, the system will **NOT** automatically send 50 independent translation requests to the LLM.

```text
50 Users:
20 → Marathi | 15 → Hindi | 10 → English | 3 → Odia | 2 → Bengali
```

The system identifies 5 unique target languages. The resulting translations can be reused for all users who have the same target language configuration.

```text
                 One Original Message
                         │
                         ▼
                  Target Languages
                         │
        ┌────────┬───────┼───────┬────────┐
        ▼        ▼       ▼       ▼        ▼
     Marathi   Hindi   English   Odia   Bengali
        │        │       │       │        │
        └────────┴───────┼───────┴────────┘
                         ▼
                  Recipient Routing
                         │
            ┌────────────┴────────────┐
            ▼                         ▼
      Same-language users       Other-language users
```

---

### 5.21 Translation Cache

Before sending a translation request to the LLM, the backend will check Redis where appropriate.

```text
Message → Source Language → Target Language → Translation Cache Key
  ↓
Redis Cache?
  │
  ├── YES → Reuse Translation
  │
  └── NO
        ↓
      LangGraph → LLM → Translation → Store in Redis
```

Caching helps reduce: LLM calls, Translation latency, Compute requirements, Resource consumption, and API costs.

---

### 5.22 Translation Orchestration

FastAPI will coordinate the translation workflow through LangGraph.

```text
Incoming Message
       ↓
FastAPI
       ↓
Message Service
       ↓
Source Language Detection
       ↓
Recipient Resolution
       ↓
Preferred Language Lookup
       ↓
Language Code Resolution
       ↓
Redis Cache Check
       ↓
Cache Hit?
       │
       ├── YES → Reuse Translation
       │
       └── NO
             ↓
          LangGraph → Translation Agent → LLM
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

### 5.23 LangGraph Integration

LangGraph coordinates specialized agents rather than putting all AI responsibilities into one large function. Potential responsibilities include: Language detection fallback, Language variant detection, Translation planning/execution/validation, and AI-related decision support.

---

### 5.24 Agent Architecture

The application will use specialized agents where they provide a clear benefit. Agents will not directly bypass application security or database authorization.

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

### 5.25 Tool Calling

Agents may use controlled tools with clearly defined inputs and outputs:

- Language configuration & User preference lookup
- Translation cache lookup & storage
- Validation services
- Application-specific operations

Tools will not have unrestricted access to the entire application.

---

### 5.26 MCP Integration

MCP provides a standardized mechanism for exposing selected tools or external capabilities to the AI workflow. It will not replace normal FastAPI business logic.

```text
LangGraph → Agent → MCP → Approved Tool / Service → Result → Agent
```

---

### 5.27 PostgreSQL Integration

FastAPI communicates with PostgreSQL to manage persistent data:

- Users, Sessions, Chat rooms, Room members
- Language configurations & Language preferences
- Messages, Translations, Message status
- Attachments, Agent/Tool execution information

---

### 5.28 Redis Integration

Redis will be used for short-lived and high-speed application data. It will **not** replace PostgreSQL as the permanent system of record.

- Translation caching
- Presence information (Online/offline, Typing state)
- WebSocket coordination & Rate limiting
- Temporary session-related data

---

### 5.29 Encryption Boundary

The backend will coordinate encryption before sensitive chat data is persisted. Encryption keys will not be stored directly alongside encrypted message data.

#### Persistence Flow:

```text
Message → FastAPI → Encryption Service → Encrypted Data → PostgreSQL
```

#### Retrieval Flow:

```text
PostgreSQL → Encrypted Data → FastAPI → Authorization Check → Decryption → React
```

---

### 5.30 Attachment Handling

FastAPI coordinates attachment uploads to object storage (e.g., AWS S3). Actual media files should not be stored directly inside PostgreSQL.

```text
React → FastAPI → Validate User/Room Permission → Validate Attachment
        ↓
Object Storage (S3) → Attachment Metadata → PostgreSQL
```

---

### 5.31 Error Handling

The backend will provide consistent error handling (and standardized frontend responses) for:

- Authentication & Authorization errors
- Invalid requests & language configurations
- Room access & Message processing errors
- Translation, LLM, WebSocket, Database, & Redis failures
- Attachment & External service failures

---

### 5.32 Retry and Failure Handling

The backend will provide controlled retry mechanisms for temporary failures.

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

### 5.33 Logging

FastAPI will provide structured application logging. **Sensitive message content and credentials should not be unnecessarily written into application logs.**

- Authentication events & Authorization failures
- Message & Translation processing metadata
- LLM latency & WebSocket connection events
- Database/Redis errors & Agent/Tool/MCP operations
- Attachment & Account operations

---

### 5.34 Performance Monitoring

The backend will record timing information to determine the actual end-to-end latency of a translated message.

```text
Message received
        ↓
Language detection time → Recipient language resolution → Language code → name resolution
        ↓
Redis lookup time → LLM processing time → Translation validation & storage time
        ↓
Message routing time → WebSocket delivery time
```

---

### 5.35 Initial Free / Local LLM

The initial development environment will use a locally hosted, freely downloadable LLM through Ollama. 

- **Initial model candidate:** `Qwen3 4B`

The architecture will use an LLM abstraction layer so that the model can be replaced later without redesigning the application.

```text
FastAPI → LangGraph → LLM Abstraction Layer → Qwen3 4B / Ollama
```

*Qwen3 4B is an initial model candidate, not a permanently locked production model.*

---

### 5.36 Model Selection Strategy

The final model will be selected based on actual benchmarking. The evaluation will include:

- Translation & Language detection accuracy
- Hinglish, Odlish, Romanized, and Mixed-language handling
- Odi↔Mar, Hin↔Mar, Eng↔Indian language translations
- Response latency, Memory, and CPU/GPU requirements
- Concurrent request performance, Tool-calling & Structured output capabilities

---

### 5.37 Speed and Latency as a Core Requirement

Fast message delivery is a primary architectural requirement. The system will minimize unnecessary LLM calls.

#### Initial Engineering Targets:

- **Language Detection:** `< 100 ms target`
- **Language Resolution:** `< 20 ms target`
- **Redis Cache Lookup:** `< 20 ms target`
- **Translation Processing:** `< 1–2 seconds target`
- **WebSocket Delivery:** `Near real-time target`

*(Actual performance will depend on hardware, model size, message length, concurrency, and network conditions.)*

---

### 5.38 Backend Responsibility Boundary

The AI layer will **not** replace normal backend business logic.


| FastAPI Responsibilities              | AI Layer (LangGraph/LLM) Responsibilities |
| ------------------------------------- | ----------------------------------------- |
| Authentication & Authorization        | Language Understanding                    |
| Business Logic & User/Room Management | Language Detection Fallback               |
| Message Management & Routing          | Language Variant Detection                |
| Recipient & Language Code Resolution  | Translation Processing                    |
| WebSocket & Redis Coordination        | Translation Validation                    |
| Database Access & Attachments         | AI Workflow Processing                    |
| Encryption Coordination & Logging     |                                           |


---

### 5.39 Final Language Translation Responsibility

The following responsibility boundary is locked for the current architecture:

```text
                     PostgreSQL
                          │
              Language Configuration
                          │
                          ▼
                       FastAPI
                          │
          ┌───────────────┴────────────────┐
          │                                │
          ▼                                ▼
 Source Language                     Recipient Preference
 Detection                           Lookup
          │                                │
          ▼                                ▼
     Source Code                       Target Code
       "or"                              "mr"
          │                                │
          └───────────────┬────────────────┘
                          ▼
                 Language Resolution
                          │
                 ┌────────┴────────┐
                 ▼                 ▼
              Odia              Marathi
                or                 mr
              Odlish
              Latin
                 │                 │
                 └────────┬────────┘
                          ▼
                  Translation Agent
                          │
                          ▼
                         LLM
                          │
                          ▼
                    Translation
```

#### Responsibility Rules

1. PostgreSQL stores the language configuration and the user's preferred language code.
2. FastAPI fetches the preferred code and resolves it using the configuration.
3. FastAPI provides the Translation Agent with the resolved language information.
4. The Translation Agent prepares the AI translation request.
5. The LLM receives both human-readable language names and language codes, performs the translation.
6. Redis stores/reuses eligible translations.
7. FastAPI routes the translated message; WebSocket delivers it in real time.
8. The user sees only the translated message and does not need to understand internal codes.

---

### 5.40 Backend Architecture Summary

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

---

### 5.41 Initial Technology Decisions


| Area                          | Initial Decision                        |
| ----------------------------- | --------------------------------------- |
| **Backend**                   | FastAPI                                 |
| **Language**                  | Python                                  |
| **Database**                  | PostgreSQL                              |
| **Cache**                     | Redis                                   |
| **Real-time communication**   | WebSocket                               |
| **AI orchestration**          | LangGraph                               |
| **Initial local LLM runtime** | Ollama                                  |
| **Initial LLM candidate**     | Qwen3 4B                                |
| **Language detection**        | Fast detection layer + LLM fallback     |
| **Language configuration**    | PostgreSQL                              |
| **Language code handling**    | FastAPI                                 |
| **Translation context**       | Language name + language code + variant |
| **Translation cache**         | Redis                                   |
| **Authentication**            | JWT                                     |
| **File storage**              | Object storage / AWS S3 for production  |
| **AI integration**            | Agents + Tool Calling + MCP             |
| **Deployment**                | Docker + AWS                            |


*The model selection remains subject to benchmarking before production deployment.*

---

### 5.42 Backend Performance Principle

The backend will follow a **fast-path first** architecture. The system should always avoid expensive AI processing when the required result can be safely obtained through deterministic or cached operations.

#### FAST PATH

```text
Message → Fast Language Detection → Resolve Recipient Languages → Resolve Language Codes → Redis Cache → Reuse Translation → WebSocket
```

#### AI PATH

```text
Message → Ambiguous Detection / Cache Miss → LangGraph → Agent → Qwen3 4B → Translation → Cache → WebSocket
```

This approach is intended to: Reduce latency, unnecessary LLM calls, and compute requirements, while improving scalability and 50+ user group-chat performance.

---

**The newly added key workflow is:**

```text
User Message
     ↓
FastAPI
     ↓
Detect Source Language
     ↓
Source Code = "or"
     ↓
Find Recipients
     ↓
PostgreSQL
     ↓
Preferred Code = "mr"
     ↓
FastAPI resolves:
"or" → Odia
"mr" → Marathi
     ↓
Translation Agent
     ↓
LLM receives:
Odia (or) → Marathi (mr)
     ↓
Translation
     ↓
Redis
     ↓
WebSocket
     ↓
User B
```

*This keeps language-code management in the application, while the LLM receives clear language names plus codes for accurate translation.*

## 6. Database Design & Implementation

### 6.1 Objective

PostgreSQL will be the **permanent source of truth** for the application. Redis will not replace PostgreSQL. 

**PostgreSQL will store:**
Users, Authentication-related information, Language configurations, User language preferences, Language requests, Chat rooms, Room members, Messages, Message translations, Message status, Sessions, Attachments metadata, Agent execution information, Tool execution information, and Account deactivation information.

```text
PostgreSQL
    ↓
Permanent application data

Redis
    ↓
Cache / temporary / real-time data
```

---

### 6.2 Database Design

The initial database will contain these 12 major tables. We will implement them in this order:

1. `users`
2. `language_configurations`
3. `language_requests`
4. `chat_rooms`
5. `room_members`
6. `messages`
7. `message_translations`
8. `message_status`
9. `user_sessions`
10. `attachments`
11. `agent_executions`
12. `tool_executions`

---

### 6.3 `language_configurations`

This should be implemented first, because other tables depend on it.

**Purpose:** This is the master configuration for all supported languages. It solves our requirement that users should see "Marathi" instead of "mr".

**Important Fields:**

- `language_id`
- `language_code`
- `language_name`
- `native_name`
- `display_name`
- `script`
- `variant`
- `is_standard_language`
- `is_user_selectable`
- `is_translation_supported`
- `status`
- `created_at`
- `updated_at`

**Examples:**

- **Language Name:** Marathi | **Code:** mr | **Native Name:** मराठी | **Script:** Devanagari | **Variant:** Standard
- **Language Name:** Odia | **Code:** or | **Native Name:** ଓଡ଼ିଆ | **Script:** Latin | **Variant:** Odlish

> ⚠️ **Important Decision:** Do not create separate root language codes such as "odlish". Instead: `language_code = or`, `variant = Odlish`, `script = Latin`. This keeps the system standardized.

---

### 6.4 `users`

This stores the user's account and profile information.

**Important Fields:**

- `user_id`
- `name`
- `email`
- `password_hash`
- `preferred_language_id`
- `account_status`
- `deactivated_at`
- `deletion_scheduled_at`
- `created_at`
- `updated_at`

**Relationship:**

```text
users.preferred_language_id
             ↓
language_configurations.language_id
```

So the user selects **Marathi**, but the database knows: `language_id → Marathi → mr`. The user does not manually enter `mr`.

---

### 6.5 Account Status

The `users` table needs to support the locked account lifecycle (`ACTIVE` / `DEACTIVATED`). Permanent deletion means the user record is removed according to the final deletion policy.

#### Deactivation Flow:

```text
ACTIVE
   ↓ (User chooses Deactivate)
DEACTIVATED
   ↓
30-day recovery period
```

**If the user logs in within 30 days:**

```text
DEACTIVATED → Login → ACTIVE
```

**If the user does not return within 30 days:**

```text
DEACTIVATED → 30 days expired → Deletion process
```

*(We will later decide whether deletion is immediate or handled through a scheduled cleanup process.)*

---

### 6.6 `language_requests`

This supports the requirement: *User doesn't find their language → request it → system validates it → admin can approve it.*

**Important Fields:**

- `request_id`
- `requested_by`
- `language_name`
- `native_name`
- `requested_variant`
- `requested_script`
- `status`
- `validated_by`
- `validation_result`
- `created_at` / `updated_at`

#### Flow:

```text
User → Language not available → Submit request → language_requests
 ↓
Validation → Admin review if required → Approved → language_configurations
```

*This should not directly modify the master language table from the frontend.*

---

### 6.7 `chat_rooms`

This represents a conversation. 

**Important Fields:**

- `room_id`
- `room_type` (`PRIVATE` or `GROUP`)
- `room_name`
- `created_by`
- `status`
- `created_at` / `updated_at`

**Examples:**

- User A + User B → `PRIVATE ROOM`
- User A + User B + User C ... User 50 → `GROUP ROOM`

---

### 6.8 `room_members`

This table establishes the relationship between users and chat rooms.

**Important Fields:**

- `room_member_id`
- `room_id`
- `user_id`
- `joined_at`
- `left_at`
- `member_status`

**Relationship:**

```text
chat_rooms → room_members → users
```

> ⚠️ **Important Decision:** Do not store the preferred language in `room_members`. The preferred language belongs to the user profile (`users.preferred_language_id`). The room member table only answers: *"Which users belong to this room?"*

---

### 6.9 `messages`

This stores the original message.

**Important Fields:**

- `message_id`
- `room_id`
- `sender_id`
- `original_content`
- `detected_language_id`
- `detected_language_code`
- `detected_variant`
- `detected_script`
- `detection_confidence`
- `created_at` / `updated_at`

**Example:**

- Original message: `"mu aji office jibi"`
- Detected: Language = `Odia`, Code = `or`, Variant = `Odlish`, Script = `Latin`, Confidence = `0.92`

**Why store detection information?**
Later we need to know: What language did the system identify? Was it Odia or Hindi? Was it Odlish? What script was used? How confident was the detector? This helps with debugging and model evaluation.

---

### 6.10 Encryption of Messages

We previously locked the requirement that messages will eventually be stored securely. The database design supports encrypted content.

**Storage Flow:**

```text
User message → FastAPI → Encryption Service → Encrypted content → PostgreSQL
```

**Retrieval Flow:**

```text
PostgreSQL → Encrypted content → Authorization → Decryption Service → Plain message → User
```

> ⚠️ **Important:** Do not store encryption keys in the same database row as the encrypted message. The actual key-management design will be handled in the security implementation stage.

---

### 6.11 `message_translations`

This is one of the most important tables in our application. It stores AI translations of an original message.

**Important Fields:**

- `translation_id`
- `message_id`
- `target_language_id`
- `target_language_code`
- `translated_content`
- `translation_status`
- `translation_model`
- `translation_time_ms`
- `created_at` / `updated_at`

---

### 6.12 Why Translation Should Be Stored Separately

Consider a group of 50 people: 20 → Marathi, 15 → Hindi, 10 → English, 5 → Odia. 
We should **not** translate the original message 50 times. Instead:

```text
Original Message
       │
       ├── Marathi translation
       ├── Hindi translation
       ├── English translation
       └── Odia translation
```

Users sharing the same preferred language receive the same translation. This is a major performance optimization.

---

### 6.13 Unique Translation Constraint

There should logically be only one translation for a given message + target language configuration.

**Constraint:**

```text
UNIQUE (message_id, target_language_id)
```

*So: `Message 100 + Marathi` should not accidentally create Translation A, Translation B, and Translation C (unless intentionally supporting multiple translation versions later).*

---

### 6.14 `message_status`

This handles delivery and read status per user, necessary for group chats.

**Important Fields:**

- `message_status_id`
- `message_id`
- `user_id`
- `delivery_status`
- `delivered_at`
- `read_at`

**Example:**

```text
Message 100
   │
   ├── User B → delivered
   ├── User C → read
   ├── User D → delivered
   └── User E → read
```

---

### 6.15 `user_sessions`

This supports the automatic logout requirement.

**Important Fields:**

- `session_id`, `user_id`, `token/session identifier`, `last_activity_at`, `expires_at`, `created_at`, `revoked_at`, `status`

**Requirement Flow:**

```text
15–20 minutes inactive → Session expires → User logged out
```

Make the actual timeout configurable (e.g., `SESSION_IDLE_TIMEOUT_MINUTES`). The frontend may detect inactivity for UX, but the backend must enforce the session/security rule.

---

### 6.16 `attachments`

The database will store metadata, **not** the actual image/video/file.

**Important Fields:**

- `attachment_id`, `message_id`, `uploaded_by`, `file_name`, `file_type`, `file_size`, `storage_provider`, `storage_key`, `created_at`

**Final Architecture:**

- **LOCAL:** `FastAPI` → `LocalStorage` → `Docker Volume`
- **AWS:** `FastAPI` → `S3Storage` → `AWS S3`

---

### 6.17 `agent_executions`

Since we have LangGraph and agents, we track AI workflow execution.

**Important Fields:**

- `execution_id`, `message_id`, `agent_name`, `workflow_name`, `status`, `started_at`, `completed_at`, `execution_time_ms`, `error_message`, `created_at`

**Example Flow:** `Message 100` → `Language Agent` → `Translation Agent` → `Validation Agent`.
*This allows us to answer: "Why did this translation take 2.8 seconds?" or "Which agent failed?"*

---

### 6.18 `tool_executions`

Because we have Tool Calling and MCP, we track tool usage separately.

**Important Fields:**

- `tool_execution_id`, `agent_execution_id`, `tool_name`, `tool_type`, `status`, `started_at`, `completed_at`, `execution_time_ms`, `error_message`, `created_at`

**Relationship:** `agent_executions → tool_executions`

---

### 6.19 Final Database Relationship

The overall entity relationship design:

```text
                    ┌─────────────────────────┐
                    │ LANGUAGE_CONFIGURATIONS │
                    └────────────┬────────────┘
                                 │
                  ┌──────────────┴──────────────┐
                  │                             │
                  ▼                             ▼
               USERS                    LANGUAGE_REQUESTS
                  │
                  │ (preferred_language_id)
                  ▼
             CHAT_ROOMS
                  │
                  ▼
             ROOM_MEMBERS
                  │
                  ▼
               MESSAGES
                  │
       ┌──────────┼──────────┐
       │          │          │
       ▼          ▼          ▼
TRANSLATIONS   STATUS   ATTACHMENTS
       │
       ▼
LANGUAGE_CONFIGURATIONS

MESSAGES → AGENT_EXECUTIONS → TOOL_EXECUTIONS

USERS → USER_SESSIONS
```

---

### 6.20 Foreign Key Relationships


| Table                  | Foreign Key             | References                            |
| ---------------------- | ----------------------- | ------------------------------------- |
| `users`                | `preferred_language_id` | `language_configurations.language_id` |
| `language_requests`    | `requested_by`          | `users.user_id`                       |
| `language_requests`    | `validated_by`          | `users.user_id`                       |
| `room_members`         | `room_id`               | `chat_rooms.room_id`                  |
| `room_members`         | `user_id`               | `users.user_id`                       |
| `messages`             | `room_id`               | `chat_rooms.room_id`                  |
| `messages`             | `sender_id`             | `users.user_id`                       |
| `messages`             | `detected_language_id`  | `language_configurations.language_id` |
| `message_translations` | `message_id`            | `messages.message_id`                 |
| `message_translations` | `target_language_id`    | `language_configurations.language_id` |
| `message_status`       | `message_id`            | `messages.message_id`                 |
| `message_status`       | `user_id`               | `users.user_id`                       |
| `user_sessions`        | `user_id`               | `users.user_id`                       |
| `attachments`          | `message_id`            | `messages.message_id`                 |
| `attachments`          | `uploaded_by`           | `users.user_id`                       |
| `agent_executions`     | `message_id`            | `messages.message_id`                 |
| `tool_executions`      | `agent_execution_id`    | `agent_executions.execution_id`       |


---

### 6.21 Important Indexes

Plan indexes around actual application queries:

- **Users:** `email`, `account_status`, `preferred_language_id`
- **Language configuration:** `language_code`, `status`, `is_user_selectable`, and potentially `(language_code, variant, script)`
- **Room members:** `room_id`, `user_id`
- **Messages:** `room_id`, `sender_id`, `created_at`
- **Translations:** `message_id`, `target_language_id`
  - *Unique constraint:* `UNIQUE(message_id, target_language_id)`
- **Status:** `message_id`, `user_id`
- **Sessions:** `user_id`, `expires_at`, `status`

---

### 6.22 Important Database Rules

1. **PostgreSQL is the source of truth.**
2. **Redis is not permanent storage.**
3. **Users select language names, not language codes.**
4. **Database stores language configuration and IDs.**
5. **Backend resolves language IDs/codes to language configuration.**
6. **Translation records are separated from original messages.**
7. **Same message + same target language should reuse the translation.**
8. **Room membership does not contain language preference.** User preference belongs to the user profile.
9. **Attachments are stored outside PostgreSQL.** (Local: Docker Volume | Production: AWS S3).
10. **Database stores attachment metadata only.**
11. **Sensitive message data will support encryption.**
12. **LLM/Agent execution information is tracked separately.**

---

### 6.23 Your Actual Task for Step 6

Don't create all tables at once. Follow this sequence:

1. **Step 6.1 — Set up PostgreSQL:** For local development: `PostgreSQL → Docker` (Do not install directly on your machine unless required).
2. **Step 6.2 — Create the database:** Conceptually: `multilingual_chat`
3. **Step 6.3 — Create the initial schema:** Start with `language_configurations`, then `users`, then `language_requests`. Next, create `chat_rooms` and `room_members`. Then `messages`, `message_translations`, and `message_status`. Then `user_sessions` and `attachments`. Finally, `agent_executions` and `tool_executions`.

---

### 6.24 Recommended Implementation Order

Your actual work pipeline should be:

```text
[STEP 6.1]  PostgreSQL Docker setup
        ↓
[STEP 6.2]  Database creation
        ↓
[STEP 6.3]  Language configuration table
        ↓
[STEP 6.4]  Users table
        ↓
[STEP 6.5]  Language request table
        ↓
[STEP 6.6]  Chat room tables
        ↓
[STEP 6.7]  Message tables
        ↓
[STEP 6.8]  Translation tables
        ↓
[STEP 6.9]  Status/session tables
        ↓
[STEP 6.10] Attachment metadata
        ↓
[STEP 6.11] Agent/tool execution tables
        ↓
[STEP 6.12] Foreign keys
        ↓
[STEP 6.13] Indexes
        ↓
[STEP 6.14] Constraints
        ↓
[STEP 6.15] Seed language configurations
```
```
DB Structure:

language_configurations
        │
        ├────────── users
        │              │
        │              ├── room_members
        │              │       │
        │              │       └── chat_rooms
        │              │
        │              ├── messages
        │              │       │
        │              │       ├── message_translations
        │              │       ├── message_status
        │              │       └── message_attachments
        │              │
        │              └── user_sessions
        │
        └────────── messages
```



## Step 7 — Redis Architecture & Implementation

### 7.0 Objective

Redis is used as a fast, temporary, and distributed data layer for caching,
rate limiting, real-time coordination, temporary state, and other
performance-sensitive operations.

PostgreSQL remains the authoritative source of truth for permanent
application data. Redis must not be treated as the primary persistent
database.

#### Core Principle

PostgreSQL = Permanent / Authoritative Data

Redis = Temporary / Cached / Fast-access / Coordination Data

#### Primary Redis Responsibilities

- Caching
- Translation result caching
- Rate limiting
- Presence and temporary state
- WebSocket coordination
- Pub/Sub
- Distributed locking where required

#### PostgreSQL Responsibilities

- Users
- Messages
- Chat rooms
- Room members
- Message translations
- Sessions
- Attachments metadata
- Agent executions
- Tool executions
- Audit and compliance data

#### Redis Failure Principle

If Redis becomes unavailable, permanent business data must remain safe
because PostgreSQL is the authoritative source of truth.

#### 7.0 Completion Criteria

- Redis responsibilities defined
- PostgreSQL vs Redis responsibilities defined
- Redis use cases identified
- Redis failure principle defined
- Redis implementation planned

---

### 7.1 Redis Role & Responsibility

Redis acts as a high-speed, temporary, caching, and coordination layer
for the MultiLinguinal Application.

Redis does not replace PostgreSQL and must not be treated as the
authoritative source of truth for permanent business data.

#### Redis Responsibilities

Redis will be used for:

- Translation result caching
- General application caching
- Rate limiting
- User presence
- Typing indicators
- WebSocket coordination
- Pub/Sub
- Temporary agent/workflow state
- Temporary counters
- Distributed locks where required

#### PostgreSQL Responsibilities

PostgreSQL remains the authoritative source for:

- Users
- Messages
- Chat rooms
- Room members
- Message translations
- User sessions
- Attachment metadata
- Agent executions
- Tool executions
- Audit and compliance data

#### Core Principle

PostgreSQL = Permanent / Authoritative Data

Redis = Cache / Temporary State / Fast Access / Coordination

#### Redis Failure Principle

Redis failure must not result in permanent business-data loss.

If Redis becomes unavailable, the application should fall back to
PostgreSQL wherever possible. Temporary features such as caching,
presence, typing indicators, rate limiting, and real-time coordination
may temporarily degrade.

#### Translation Cache

Translation requests should first check Redis.

If a matching translation is found in Redis, the cached result can be
returned without calling the translation API or LLM again.

If no cached result exists, the application calls the translation
service, stores the reusable result in Redis, persists the required
business result in PostgreSQL, and returns the response.

---

### 7.2 — Redis Use-Case Identification

| Use Case | Status | Justification |
| :--- | :--- | :--- |
| **1. Cache** | **YES** | Reduces PostgreSQL load for frequently accessed, slow-changing data. |
| **2. Session / Temp Auth** | **YES** | Fast token blacklisting and temporary OAuth/reset state verification. |
| **3. Rate Limiting** | **YES** | Fast, atomic counters required to protect API endpoints. |
| **4. WebSocket Coordination** | **YES** | Essential for multi-instance horizontal scaling and broadcasting. |
| **5. Pub/Sub** | **YES** | Core mechanism for real-time chat message delivery across clients. |
| **6. Temp Agent/Workflow State** | **YES** | LangGraph temporary execution state before final persistence. |
| **7. Translation Caching** | **YES** | Saves external API costs and reduces latency for duplicate translations. |
| **8. Presence/Online Status** | **YES** | Ephemeral data; perfect for Redis TTLs. Does not belong in Postgres. |
| **9. Temporary Locks** | **YES** | Prevents duplicate agent executions or race conditions in async tasks. |

---

### 7.3 — Redis Data Classification
All Redis data is classified into one of the following categories to dictate its lifecycle and importance:

*   **Persistent Business Data:** `NONE`. Redis will not hold authoritative business data.
*   **Temporary Data:** Data with a strict lifecycle that is not needed after completion (e.g., session blacklists, presence, temporary agent state, rate limit counters).
*   **Derived Data:** Data that can be perfectly reconstructed from PostgreSQL or external APIs (e.g., translation cache, database query caches).
*   **Coordination Data:** Transitory messages and locks used for system synchronization (e.g., Pub/Sub messages, distributed locks).

---

### 7.4 — Redis Architecture
**Logical Architecture:**

```text
                    FastAPI
                       │
              ┌────────┴────────┐
              │                 │
              ▼                 ▼
         PostgreSQL           Redis
      (Source of Truth)  (Supporting Layer)
```

*   **Connection:** FastAPI communicates with Redis via an asynchronous client (`redis.asyncio`).
*   **Connection Pooling:** A global connection pool is initialized on application startup to prevent connection overhead per request.
*   **Logical Databases:** Use a single DB (DB `0`) to simplify infrastructure and cluster compatibility. Logical separation is handled via key prefixes.
*   **Access Layer:** Application code never calls Redis directly. A dedicated repository/service layer abstracts Redis operations.
*   **Failure Handling:** Redis calls are wrapped in try-except blocks. Timeouts are kept short (e.g., 50ms for cache gets) to prevent cascading failures.

---

### 7.5 — Redis Key Naming Convention
**Standard:** `chat_app:{domain}:{identifier}:{attribute}`

**Examples:**
*   `chat_app:user:123:profile` (Cache)
*   `chat_app:room:456:members` (Cache/State)
*   `chat_app:session:blacklist:789` (Auth)
*   `chat_app:rate_limit:user:123:api` (Rate Limiting)
*   `chat_app:presence:user:123:status` (Presence)
*   `chat_app:translation:en:es:v1:hash123` (Translation Cache)

---

### 7.6 — TTL Strategy
Every key written to Redis **must** have a Time-To-Live (TTL).

| Data Type | TTL Duration | Expiry Behavior | Recreation |
| :--- | :--- | :--- | :--- |
| **Rate Limit** | 1 min - 1 hour | Auto-deletes | Counter resets on next request |
| **Presence** | 60 seconds | User marked offline | Refreshed via client heartbeat |
| **App Cache** | 15 min - 24 hours | Cache Miss | Re-fetched from PostgreSQL |
| **Translations** | 30 - 90 days | Cache Miss | Re-fetched from LLM/Translation API |
| **Temp Locks** | 5 - 30 seconds | Lock released | Re-acquired if task retries |

---

### 7.7 — Cache Strategy
*   **Workflow:** Cache Miss → Fetch from PostgreSQL → Write to Redis (with TTL) → Return Result
*   **Cache Invalidation:** Event-driven. When a record is updated in PostgreSQL, the corresponding Redis key is explicitly deleted.
*   **Stale Data:** Prefer cache invalidation (deletion) over cache updates to prevent race conditions.
*   **Cache Stampede Prevention:** For heavy queries, use a short-lived distributed lock to ensure only one worker fetches from Postgres and populates the cache.

---

### 7.8 — Translation Cache Strategy
Translations are highly repetitive and costly.

*   **Cache Identity (Key):** `chat_app:translation:{source_language}:{target_language}:{model_version}:{md5_hash_of_source_text}`
*   **TTL:** Long-lived (e.g., 30 days).
*   **Invalidation:** Automatic via TTL. If the underlying translation model is swapped (e.g., moving from v1 to v2), the model version in the key changes, inherently starting a fresh cache.

---

### 7.9 — Session / Temporary Authentication Data
*   **PostgreSQL:** Stores permanent user credentials and long-lived refresh tokens.
*   **Redis:** Stores blacklisted JWT tokens (on logout) and fast temporary session states (e.g., OAuth flow states, password reset temporary codes).
*   **Rule:** We do not duplicate the entire user session in Redis. JWTs remain stateless; Redis is only queried to check if a valid JWT has been prematurely revoked.

---

### 7.10 — Rate Limiting
Rate limiting protects the application from abuse and controls API costs using sliding or fixed window counters (`INCR` + `EXPIRE`).

| Action | Limit | Window | Exceeded Response |
| :--- | :--- | :--- | :--- |
| **Login Attempts** | 5 | 15 mins | `429 Too Many Requests` |
| **Message Sending** | 60 | 1 min | `429 Too Many Requests` |
| **Translations** | 100 | 1 min | `429 Too Many Requests` |
| **File Uploads** | 10 | 1 hour | `429 Too Many Requests` |
| **Agent Execution** | 20 | 1 min | `429 Too Many Requests` |

---

### 7.11 — Presence / Online Status
Maintains the real-time status of users.

*   **Status Types:** `ONLINE`, `OFFLINE`, `TYPING`.
*   **Flow:**
    1. WebSocket connects → Sets `chat_app:presence:user:{id}` to `ONLINE` (TTL: 60s).
    2. Client sends heartbeat every 30s → Updates TTL.
    3. Client disconnects normally → Explicitly deletes key (`OFFLINE`).
    4. Client drops connection abruptly → TTL expires automatically (`OFFLINE`).

---

### 7.12 — WebSocket / Real-Time Redis Support
To support multiple FastAPI instances, WebSockets cannot hold state strictly in local memory.

**Architecture:**
```text
Client 1 
  ↓ (WebSocket)
FastAPI Instance A
  ↓ (Publish)
Redis Pub/Sub 
  ↓ (Subscribe)
FastAPI Instance B
  ↓ (WebSocket)
Client 2
```

---

### 7.13 — Redis Pub/Sub Strategy
*   **Channels:**
    *   `chat_app:room:{room_id}:messages` (New chat messages)
    *   `chat_app:user:{user_id}:notifications` (Direct user alerts)
*   **Message Format:** JSON payloads containing `event_type`, `payload`, and `timestamp`.
*   **Failure Behavior:** Pub/Sub is "fire and forget". Messages must also be saved to PostgreSQL first. Redis Pub/Sub is strictly for UI updates, not guaranteed delivery.

---

### 7.14 — Distributed Locking
Redis locks will be used sparingly to prevent race conditions in asynchronous environments.

*   **Use Cases:** Preventing duplicate LangGraph agent executions triggered by the same event; deduplicating heavy external API calls.
*   **Implementation:** Redis `SET resource_name my_random_value NX PX 30000`.
*   **Rule:** If a PostgreSQL unique constraint or transaction can easily solve the problem, prefer PostgreSQL over Redis locks.

---

### 7.15 — Agent / Workflow Temporary State
For LangGraph/Agent execution:

*   **Temporary Execution State:** Short-lived memory for an agent currently running a thought-loop will be stored in Redis.
*   **Permanent Execution Record:** Once the agent concludes a workflow step or outputs a final decision, the result is written to PostgreSQL. Redis is then cleared of that workflow state.

---

### 7.16 — Redis Persistence
*   **Decision:** **RDB (Redis Database) Snapshots Enabled.**
*   **Reasoning:** While Redis does not hold authoritative data, losing rate limit counters, translation caches, and workflow locks abruptly can cause a massive traffic spike to PostgreSQL and external APIs upon restart.
*   **Configuration:** Save snapshot every 5 minutes if at least 100 keys changed (`save 300 100`). Append-Only File (AOF) is disabled.

---

### 7.17 — Redis Failure Strategy

| Feature | Action if Redis Fails |
| :--- | :--- |
| **Database Cache** | **Bypass** - Fetch directly from PostgreSQL. |
| **Translation Cache** | **Bypass** - Call external API directly. |
| **Rate Limiting** | **Fail Open** - Allow request (prioritize availability). |
| **WebSockets** | **Degrade** - Broadcasts only work within the local FastAPI instance. |
| **Agent Locks** | **Fail Closed** - Halt agent execution to prevent duplicate corruptions. |

---

### 7.18 — Redis Docker Setup
`docker-compose.yml` snippet:

```yaml
services:
  redis:
    image: redis:7.2-alpine
    container_name: chat_app_redis
    restart: unless-stopped
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --save 300 100 --requirepass ${REDIS_PASSWORD}
    healthcheck:
      test: ["CMD", "redis-cli", "-a", "${REDIS_PASSWORD}", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - app_network

volumes:
  redis_data:
```

---

### 7.19 — Redis Configuration
Application environment variables required for Redis:

```env
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=your_secure_password
REDIS_DB=0
REDIS_TIMEOUT_MS=500
```

---

### 7.20 — FastAPI Redis Integration
*   **Architecture:** Abstract Redis behind a Service/Repository pattern (e.g., `CacheService`, `RateLimitService`).
*   **Rule:** No raw Redis commands scattered in API routers.
*   **Connection:** Utilize a global connection pool initialized on FastAPI lifespan startup.

---

### 7.21 — Redis Security
*   **Authentication:** Redis requires a password (configured via `REDIS_PASSWORD`).
*   **Network Exposure:** Resides strictly within the internal Docker/VPC network. No public IP exposure.
*   **Protected Configuration:** Dangerous commands (`FLUSHALL`, `FLUSHDB`, `KEYS`) will be disabled or renamed via `redis.conf` in production.

---

### 7.22 — Redis Testing
**Test Checklist:**
- [ ] Connection pool establishes on application startup.
- [ ] Read/write operations succeed.
- [ ] TTL expires data automatically.
- [ ] Cache invalidation triggers correctly on PostgreSQL updates.
- [ ] Rate limiting blocks requests after threshold is met.
- [ ] WebSocket Pub/Sub successfully delivers cross-instance messages.
- [ ] Application starts and functions normally (bypassing cache) when Redis is deliberately stopped.

---

### 7.23 — Redis Performance & Monitoring
**Monitoring Baseline:**
*   **Memory Usage:** Ensure eviction policies trigger before OOM.
*   **Cache Hit Rate:** Target > 80% for read-heavy endpoints.
*   **Connected Clients:** Monitor for connection leaks from FastAPI.
*   **Latency:** Ensure average Redis response time is < 5ms.
*   **Evictions:** Track keys evicted due to max-memory limits.

---

### 7.24 — Redis Production Readiness Review
**Review Checklist:**
- [ ] Architecture aligns with "Postgres=Permanent, Redis=Temporary" principle.
- [ ] `redis.conf` secured (password applied, public access blocked).
- [ ] RDB snapshots configured appropriately.
- [ ] Fallback mechanisms (failure strategy) implemented in application code.
- [ ] Max memory limit and eviction policy (`allkeys-lru`) configured.
- [ ] Standardized key naming convention enforced.

---

### 7.25 — Redis Finalization
**Status:** The initial Redis architecture is **FROZEN**.

Future modifications to core Redis usage patterns, key structures, or infrastructure responsibilities must be documented here and implemented deliberately.