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

### 7.2 Redis Use-Case Identification

Redis will be introduced only for use cases where fast temporary
storage, caching, counters, coordination, or event distribution
provides a clear architectural benefit.

#### Redis MUST USE

- Translation result caching
- General application caching
- Rate limiting
- User presence
- Typing indicators
- WebSocket coordination
- Pub/Sub
- Temporary counters

#### Redis MAY USE

- Temporary agent/workflow state
- Distributed locks where required by an actual concurrency scenario

#### Redis MUST NOT USE

- Permanent user records
- Permanent messages
- Permanent chat-room data
- Permanent message translations
- Audit/compliance records
- Other authoritative business data

PostgreSQL remains the source of truth for permanent application data.
---

### 7.3 Redis Data Classification

All Redis data must belong to a defined temporary, cached, event, or
coordination category.

Redis will not contain permanent authoritative business data.

#### Redis Data Categories

##### 1. CACHE

Examples:

- Translation results
- Frequently accessed application data
- Language configuration cache

Characteristics:

- Reconstructable
- Non-authoritative
- TTL-based where appropriate
- PostgreSQL or another source remains authoritative

##### 2. TEMPORARY_STATE

Examples:

- User presence
- Typing indicators
- Temporary agent/workflow state

Characteristics:

- Short-lived
- Expirable
- Reconstructable
- Not authoritative

##### 3. COUNTER

Examples:

- API request counters
- Login attempt counters
- Translation request counters
- Rate-limit counters

Characteristics:

- Increment/decrement based
- TTL-based
- Temporary

##### 4. EVENT

Examples:

- WebSocket events
- Presence events
- Pub/Sub messages

Characteristics:

- Transient
- Not treated as permanent storage
- No assumption that historical events remain available

##### 5. COORDINATION

Examples:

- Distributed locks
- Temporary processing ownership

Characteristics:

- Short-lived
- TTL protected
- Used only when required
- Must have safe failure handling

#### Classification Rule

Redis data must always have a clearly defined purpose, lifetime, and
failure/recovery behavior.

Permanent authoritative business data must remain in PostgreSQL.
---

### 7.4 Redis Architecture

Redis is implemented as a supporting infrastructure layer between the
FastAPI application and persistent application services.

#### Architecture

React Frontend
      |
      v
FastAPI Backend
      |
      +------------------+
      |                  |
      v                  v
PostgreSQL            Redis
Source of Truth       Fast/Temporary Layer
                           |
                +----------+----------+
                |          |          |
              Cache      State      Pub/Sub
                |
            Counters
                |
          Coordination

#### PostgreSQL

PostgreSQL remains the authoritative source of truth for permanent
application data.

Redis must not be required to recover permanent business data.

#### FastAPI

FastAPI is the primary application layer that communicates with Redis.

Redis access should be centralized through a reusable connection and
service layer rather than creating independent Redis connections
throughout the application.

#### Redis

Redis is responsible for:

- Caching
- Temporary state
- Temporary counters
- Pub/Sub
- Real-time coordination
- Distributed coordination where required

#### Failure Principle

Redis is a supporting layer and must not become a single point of
failure for permanent business data.

If Redis becomes unavailable, permanent PostgreSQL-backed operations
must remain protected. Features that depend on temporary Redis state
may degrade according to their defined fallback behavior.

#### Local Docker Architecture

Docker Compose will contain the following infrastructure:

- PostgreSQL
- Redis
- FastAPI

The React frontend communicates with FastAPI, while FastAPI communicates
with PostgreSQL and Redis.
---

### 7.5 Redis Key Naming Convention

Redis keys use a consistent namespaced format:

`multilinguinal:<environment>:<domain>:<identifier>:<attribute>`

Examples:

- `multilinguinal:dev:translation:<key>`
- `multilinguinal:dev:presence:<user_id>`
- `multilinguinal:dev:typing:<room_id>:<user_id>`
- `multilinguinal:dev:rate_limit:<user_id>`
- `multilinguinal:dev:session:<session_id>`
- `multilinguinal:dev:workflow:<execution_id>`

#### Rules

- Use lowercase names.
- Use `:` as the separator.
- Use predictable domain names.
- Use UUIDs or stable identifiers where required.
- Never store secrets directly in Redis keys.
- Redis key construction should be centralized in the Redis service/key-builder layer.

#### Completed

- [x] Redis key namespace defined
- [x] Environment separation defined
- [x] Domain naming defined
- [x] Key construction centralization defined
---

### 7.6 Redis TTL Strategy

TTL (Time To Live) defines how long Redis data remains before it is
automatically removed.

#### Initial TTL

| Data | TTL |
|---|---:|
| Translation cache | 24 hours |
| General application cache | 1 hour |
| Presence | 60 seconds |
| Typing indicator | 5 seconds |
| Rate-limit counters | Rate-limit window |
| Temporary workflow state | 30 minutes |
| WebSocket temporary state | 60 seconds |
| Distributed locks | 30 seconds |
| Temporary counters | Use-case dependent |

#### Rules

- TTL must be set when temporary Redis data is created.
- Redis handles expiration automatically.
- TTL must not be used for permanent business data.
- PostgreSQL remains the source of truth.
- Expired cache/state must be safely recreatable.
- TTL values should be configurable rather than scattered as hardcoded
  values throughout the application.

#### Completed

- [x] TTL strategy defined
- [x] Initial TTL values defined
- [x] Expiration responsibility defined
- [x] PostgreSQL fallback principle defined
- [x] Configurable TTL requirement defined
---

### 7.7 Redis Cache Strategy

Redis uses a cache-aside strategy.

#### Cache Flow

FastAPI Request
      |
      v
Redis GET
      |
   +--+--+
   |     |
  HIT   MISS
   |     |
Return  Fetch from source
          |
       Store in Redis
          |
        Return

#### Cached Data

Phase 1 cache candidates:

- Translation results
- Language configuration
- Frequently accessed read-heavy application data

Redis must not be used as the source of truth for permanent business
data.

#### Cache Invalidation

When cached data changes:

1. Update PostgreSQL.
2. Remove or refresh the related Redis key.
3. Future requests rebuild the cache when required.

#### Rules

- Use cache-aside for application caching.
- Every cache entry must have an appropriate TTL.
- Cache misses must safely fetch data from the source.
- Redis failure must not cause permanent data loss.
- Cache keys must use the centralized key-building convention.

#### Completed

- [x] Cache-aside strategy defined
- [x] Cache candidates defined
- [x] Cache invalidation defined
- [x] Redis failure behavior defined
- [x] PostgreSQL source-of-truth rule maintained

---
### 7.8 Translation Cache Strategy

Translation results are cached in Redis to reduce repeated calls to
the translation service.

#### Cache Key

The cache identifier is generated from:

- Source language
- Target language
- Source text
- Translation model/version
- Relevant translation options

A deterministic hash is generated from these values.

Key format:

`multilinguinal:<environment>:translation:<hash>`

#### Translation Flow

Translation Request
      |
      v
Generate Cache Key
      |
      v
Redis GET
   |       |
  HIT     MISS
   |       |
Return   Translation Service
            |
      Save required DB record
            |
      Save Redis + TTL
            |
          Return

#### Rules

- Redis stores translation results as a cache only.
- PostgreSQL `message_translations` remains the persistent record.
- Different languages, models, versions, or options must generate
  different cache keys.
- Translation cache TTL is 24 hours.
- Cache misses must safely continue to the translation service.
- Redis failure must not cause permanent data loss.

#### Completed

- [x] Translation cache key strategy defined
- [x] Deterministic cache identifier defined
- [x] Cache HIT/MISS flow defined
- [x] PostgreSQL relationship defined
- [x] Model/version isolation defined
- [x] Translation cache TTL defined
- [x] Redis failure behavior defined
---

### 7.9 Session / Temporary Authentication Data

PostgreSQL remains the authoritative session store through the
`user_sessions` table.

Redis is used only for temporary or fast-access authentication data.

#### Redis Usage

- Short-lived session lookup/cache
- Login attempt counters
- Temporary authentication state
- Temporary verification/challenge data when required

#### Rules

- Redis must not replace `user_sessions`.
- PostgreSQL remains the source of truth for sessions.
- Sensitive authentication data should not be unnecessarily stored in Redis.
- Temporary authentication data must have TTL.
- Redis failure must not cause permanent session-data loss.

#### Completed

- [x] PostgreSQL session ownership defined
- [x] Redis temporary authentication role defined
- [x] Session cache approach defined
- [x] Sensitive-data rule defined
- [x] TTL requirement defined
---

### 7.10 — Rate Limiting
### 7.10 Rate Limiting

Redis is used for temporary API request counters.

#### Initial Limits

| Category | Limit | Window |
|---|---:|---:|
| General API | 60 requests | 1 minute |
| Authentication | 10 requests | 1 minute |
| Translation | 30 requests | 1 minute |

Limits must be configurable.

#### Key Format

`multilinguinal:<environment>:rate_limit:<identifier>:<endpoint>`

The identifier is normally the authenticated user ID. For
unauthenticated requests, the client IP may be used.

#### Flow

Request
   |
   v
Redis Counter
   |
Within limit?
  |       |
 Yes      No
  |       |
Allow   HTTP 429

#### Implementation

Use a Redis atomic counter with a TTL-based rate-limit window.

#### Phase 2 — Parked

Advanced enterprise-scale rate limiting is deferred to Phase 2,
including Redis Cluster, distributed rate limiting, multi-region
support, and advanced capacity planning.

#### Rules

- Rate-limit configuration must be configurable.
- Counters are temporary Redis data.
- Counters use TTL-based windows.
- PostgreSQL is not used for request counters.
- Rate limiting should be implemented through a reusable FastAPI
  service/dependency.

#### Completed

- [x] Rate-limit categories defined
- [x] Initial limits defined
- [x] Key structure defined
- [x] Redis counter strategy defined
- [x] TTL window defined
- [x] Configurable limits defined
- [x] Enterprise scaling parked for Phase 2

---

### 7.11 Presence / Online Status

Redis stores temporary user presence information.

#### Key Format

`multilinguinal:<environment>:presence:<user_id>`

#### Presence Flow

User connects
      |
      v
Set Redis presence
      |
    ONLINE
      |
Heartbeat/activity
      |
Refresh TTL
      |
No heartbeat
      |
TTL expires
      |
   OFFLINE

#### TTL

Presence keys use a 60-second TTL.

The TTL is refreshed when the user sends a valid heartbeat or
activity update.

#### Rules

- Live presence is stored in Redis.
- Presence data is temporary.
- Presence keys must have a TTL.
- PostgreSQL is not used for continuous presence updates.
- Expired presence means the user is considered offline.
- Only the minimum required presence data should be stored.

#### Completed

- [x] Presence ownership defined
- [x] Redis key structure defined
- [x] Online/offline flow defined
- [x] Presence TTL defined
- [x] Heartbeat refresh defined
- [x] PostgreSQL write avoidance defined
---

### 7.12 WebSocket / Real-Time Redis Support

Redis provides temporary coordination between FastAPI instances for real-time WebSocket communication.

#### Architecture

Client
  |
  v
FastAPI / WebSocket
  |
  v
Redis
  |
  v
Other FastAPI / WebSocket instances
  |
  v
Connected Clients

#### Redis Responsibilities

Redis may distribute temporary real-time events such as:

- New message notifications
- Presence updates
- Typing indicators
- Message status updates
- Room events

The actual message and permanent business data remain in PostgreSQL.

#### Event Flow

User sends message
      |
      v
FastAPI
      |
      v
PostgreSQL
      |
      v
Publish event
      |
      v
Redis
      |
      v
Subscribed FastAPI instances
      |
      v
WebSocket clients

Permanent data must be persisted before publishing the real-time
event.

#### Channel Format

`multilinguinal:<environment>:room:<room_id>`

#### Rules

- Redis is used for real-time event distribution.
- Redis is not the permanent message store.
- PostgreSQL remains the source of truth.
- Real-time events are temporary.
- WebSocket logic should be separated from Redis connection logic.

#### Completed

- [x] WebSocket/Redis relationship defined
- [x] Real-time event types defined
- [x] Event flow defined
- [x] Channel naming defined
- [x] PostgreSQL persistence rule defined

---

### 7.13 Redis Pub/Sub Strategy

Redis Pub/Sub is used for temporary real-time event distribution
between FastAPI instances.

#### Publisher / Subscriber

FastAPI instance
      |
   PUBLISH
      |
    Redis
      |
  SUBSCRIBE
   /      \
FastAPI  FastAPI
   |        |
WebSocket WebSocket

#### Phase 1 Events

- New message notifications
- Presence changes
- Typing indicators
- Message status changes
- Room events

#### Channel Format

`multilinguinal:<environment>:room:<room_id>`

#### Important Rules

- Pub/Sub is used only for temporary event delivery.
- Pub/Sub is not the permanent message store.
- Pub/Sub is not used as the source of truth.
- Permanent data must be stored in PostgreSQL.
- Subscribers may miss events while disconnected.
- Missed events must be recoverable from authoritative application
  state when required.
- Pub/Sub logic should be isolated from business logic.

#### Completed

- [x] Publisher/subscriber model defined
- [x] Event types defined
- [x] Channel structure defined
- [x] Temporary-event rule defined
- [x] PostgreSQL source-of-truth rule defined
- [x] Missed-event behavior defined

---

### 7.14 Distributed Locking

Redis distributed locks are used only for short-lived application-level coordination when multiple processes may perform the same operation
concurrently.

#### Key Format

`multilinguinal:<environment>:lock:<resource>`

#### Flow

Process A ──┐
            ↓
        Redis Lock
            ↑
Process B ──┘

Only the process that acquires the lock performs the protected operation.

#### Phase 1 Use Cases

- Prevent duplicate processing
- Protect short critical sections
- Coordinate temporary resource ownership
- Prevent duplicate translation/workflow execution when required

#### Rules

- Use locks only when an actual concurrency requirement exists.
- Every lock must have a TTL.
- Default lock TTL is 30 seconds.
- Locks must be released after successful completion.
- Lock expiry must safely handle process failure.
- Redis locks must not replace PostgreSQL transactions or constraints.
- Lock acquisition must be atomic.

#### Completed

- [x] Distributed locking purpose defined
- [x] Lock key structure defined
- [x] Initial use cases defined
- [x] Lock TTL defined
- [x] Failure behavior defined
- [x] PostgreSQL integrity rule defined
---

### 7.15 Agent / Workflow Temporary State

Redis may store temporary state required while an agent or workflow is executing.

#### Key Format

`multilinguinal:<environment>:workflow:<execution_id>`

#### Temporary Data

- Current workflow step
- Temporary agent context
- Temporary tool results
- Retry information
- Execution progress
- Short-lived coordination state

#### Flow

Agent starts
    |
    v
Create Redis state
    |
    v
Update during execution
    |
    v
Workflow completes
    |
    v
Persist required permanent data
    |
    v
Remove temporary Redis state

#### TTL

Temporary workflow state uses a 30-minute TTL.

#### Rules

- Redis stores temporary workflow state only.
- Permanent execution records remain in PostgreSQL.
- Redis state must have a TTL.
- Workflow recovery must not depend exclusively on Redis.
- Expired state must be handled safely.
- Only required temporary data should be stored.

#### Completed

- [x] Workflow state responsibility defined
- [x] Temporary data defined
- [x] Key structure defined
- [x] TTL defined
- [x] PostgreSQL persistence boundary defined
---

### 7.16 Redis Persistence

Redis persistence is used only to improve recovery and restart behavior. It is not used as a durability mechanism for permanent application data.

#### Phase 1 Strategy

Redis will use **RDB snapshots**.

PostgreSQL remains the authoritative source of truth for all permanent business data.

#### Persistence Responsibilities

RDB persistence may preserve:

- Translation cache
- General application cache
- Temporary workflow state
- Temporary counters
- Other reconstructable Redis state

The application must remain functional when Redis data is lost and rebuildable.

#### Important Rules

- Redis persistence must not replace PostgreSQL persistence.
- Redis data must always be treated as temporary or reconstructable.
- Redis loss must not cause permanent business-data loss.
- Redis locks must not rely on persistence for correctness.
- Pub/Sub messages are not persisted.
- TTL-based expiration remains active after Redis restart.

#### Phase 2

AOF persistence and other Redis durability optimizations may be evaluated later based on actual workload and reliability requirements.

#### Completed

- [x] Redis persistence responsibility defined
- [x] RDB selected for Phase 1
- [x] PostgreSQL source-of-truth rule confirmed
- [x] Redis data recovery principle defined
- [x] Pub/Sub persistence limitation defined
- [x] AOF deferred to Phase 2File (AOF) is disabled.

---

### 7.17 Redis Failure Strategy

Redis is a supporting infrastructure layer. Redis failure must not cause permanent business-data loss.

#### Failure Principle

PostgreSQL remains the source of truth.

If Redis becomes unavailable, the application should bypass Redis
where possible and continue using the authoritative source.

#### Failure Behavior

| Redis Feature | Failure Behavior |
|---|---|
| General cache | Bypass cache |
| Translation cache | Perform translation normally |
| Presence | Presence may temporarily degrade |
| Typing indicators | Typing state may temporarily degrade |
| Pub/Sub | Real-time event delivery may temporarily degrade |
| Temporary workflow state | Workflow must protect required permanent state |
| Distributed locks | Operation must safely handle lock failure |
| Rate limiting | Apply endpoint-specific failure policy |

#### Cache Failure Flow

Request
   |
   v
Redis unavailable
   |
   v
Bypass Redis
   |
   v
Source Service / PostgreSQL
   |
   v
Return response

#### Rules

- Redis failure must not cause permanent data loss.
- Cache failures should normally fail open.
- Translation requests must continue without the translation cache.
- Redis operations should use short connection/operation timeouts.
- Redis errors must be logged.
- Redis failure must not crash unrelated application requests.
- Temporary Redis state must never be treated as the only copy of
  required permanent business data.
- Real-time features may temporarily degrade when Redis is unavailable.

#### Rate Limiting

Rate-limit failure behavior will be finalized together with the
authentication and authorization implementation.

Security-sensitive endpoints may use stricter failure handling than
general application caching.

#### Completed

- [x] Redis failure principle defined
- [x] Cache fallback defined
- [x] Translation-cache fallback defined
- [x] Real-time degradation behavior defined
- [x] Temporary-state protection defined
- [x] Timeout requirement defined
- [x] Error logging requirement defined
---

### 7.18 Redis Docker Setup

Redis is included in the local Docker development environment.

#### Redis Image

Use the official:

`redis:7-alpine`

#### Container

Container name:

`chat_application_REDIS`

#### Docker Service

The Redis service is named:

`redis`

FastAPI should connect to Redis using the Docker service name rather
than `localhost` when running inside Docker.

Example:

`redis://redis:6379`

#### Persistence

Redis RDB persistence is enabled for Phase 1.

Redis data is stored using a Docker volume so that container recreation
does not automatically remove the Redis persistence files.

Example volume:

`redis_data:/data`

#### Docker Architecture

Docker Compose

    |
    +------------------+
    |                  |
    v                  v
PostgreSQL            Redis
    |                  |
    +--------+---------+
             |
             v
          FastAPI

#### Phase 1 Rules

- Use `redis:7-alpine`.
- Use a dedicated Redis Docker service.
- Use a Docker volume for Redis persistence.
- FastAPI connects through the Docker service name.
- Redis Cluster is not required in Phase 1.
- Redis security configuration is handled separately.
- Redis configuration values are centralized and configurable.
- Redis must remain a supporting infrastructure service.

#### Completed

- [x] Redis Docker image selected
- [x] Redis service defined
- [x] Container naming defined
- [x] Docker networking approach defined
- [x] Redis persistence volume defined
- [x] Phase 1 Docker scope defined

---

### 7.19 Redis Configuration

Redis configuration is centralized and loaded through environment variables.

#### Configuration

The application should support the following Redis configuration:

| Setting | Purpose | Phase 1 |
|---|---|---|
| REDIS_HOST | Redis hostname | `redis` in Docker |
| REDIS_PORT | Redis port | `6379` |
| REDIS_DB | Redis database number | `0` |
| REDIS_TIMEOUT | Connection/operation timeout | Configurable |
| REDIS_URL | Complete Redis connection URL | Configurable |

#### Docker

When FastAPI runs inside Docker:

`REDIS_HOST=redis`

Example connection:

`redis://redis:6379/0`

When FastAPI runs directly on the host during local development:

`REDIS_HOST=localhost`

#### Configuration Rules

- Redis configuration must come from environment variables.
- Redis connection details must not be hardcoded in business logic.
- Redis settings should be represented by a centralized application
  configuration object.
- Redis timeouts must be configurable.
- Redis database `0` is used for Phase 1.
- Environment-specific configuration should be supported.
- Redis credentials will be handled separately by the security design.

#### Phase 1 Scope

The initial Redis configuration does not include:

- Redis Cluster configuration
- Sentinel configuration
- Multi-region configuration
- Advanced Redis topology settings

These remain deferred to Phase 2 if required.

#### Completed

- [x] Redis configuration parameters defined
- [x] Environment-variable strategy defined
- [x] Docker hostname defined
- [x] Local development hostname defined
- [x] Redis database defined
- [x] Timeout configuration defined
- [x] Centralized configuration requirement defined
- [x] Advanced Redis topology deferred

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