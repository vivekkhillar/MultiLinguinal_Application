
CREATE SCHEMA CHAT_APP;

-- create this table to configure the languages which will be selected by the user for which translation as well as the chat will capture

CREATE TABLE IF NOT EXISTS language_configurations
(
    language_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    language_code VARCHAR(200) NOT NULL,
    language_name VARCHAR(200) NOT NULL,
    native_name VARCHAR(200) NOT NULL,

    script VARCHAR(50) NOT NULL,
    variant VARCHAR(50),


    is_standard_language BOOLEAN NOT NULL DEFAULT TRUE,
    is_user_selectable BOOLEAN NOT NULL DEFAULT TRUE,
    is_translation_supported BOOLEAN NOT NULL DEFAULT TRUE,
    status VARCHAR(200) NOT NULL DEFAULT 'ACTIVE',

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,


    CONSTRAINT uq_language_configuration UNIQUE (language_code, script, variant),
    CONSTRAINT chk_language_status CHECK (status IN ('ACTIVE', 'INACTIVE'))

);

-- Tis will handel all the user details and preferd language is a foreign key which connected to language_configuration table
CREATE TABLE IF NOT EXISTS users
(
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,

    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100),

    preferred_language_id UUID NOT NULL,
    FOREIGN KEY (preferred_language_id ) REFERENCES language_configurations(language_id),

    account_status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
    deactivated_at TIMESTAMPTZ ,
    deletion_scheduled_at TIMESTAMPTZ,
    last_login_at TIMESTAMPTZ,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT check_account_status CHECK (account_status IN ('ACTIVE', 'DEACTIVATED'))

);

-- create index for the better performance --
CREATE INDEX idx_users_account_status ON users(account_status);
CREATE INDEX idx_users_preferred_language ON users(preferred_language_id);


-- This will handel room type, private or group chat which have a foreign key as created_by take refference from users
CREATE TABLE IF NOT EXISTS chat_rooms
(
    room_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    room_type VARCHAR(50) NOT NULL,
    room_name VARCHAR(255),
    created_by UUID NOT NULL,
    FOREIGN KEY (created_by ) REFERENCES users(user_id),

    max_members INTEGER NOT NULL DEFAULT 50,
    room_status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT check_room_type CHECK (room_type IN ('PRIVATE', 'GROUP')),
    CONSTRAINT check_room_status CHECK (room_status IN ('ACTIVE', 'INACTIVE')),
    CONSTRAINT check_max_members CHECK (max_members > 0)

); 


-- This will handel the in which chat rooms how many room members are there there is 2 foreign key user_id and room_id take refference from users and chat_rooms
CREATE TABLE IF NOT EXISTS room_members
(
    room_member_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    room_id UUID NOT NULL,
    user_id UUID NOT NULL,

    member_role VARCHAR(20) NOT NULL,
    member_status VARCHAR(20) NOT NULL,

    joined_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    left_at TIMESTAMPTZ,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_room_members_room
        FOREIGN KEY (room_id)
        REFERENCES chat_rooms(room_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_room_members_user
        FOREIGN KEY (user_id)
        REFERENCES users(user_id)
        ON DELETE CASCADE,

    CONSTRAINT uq_room_members_room_user
        UNIQUE (room_id, user_id),

    CONSTRAINT check_member_role
        CHECK (member_role IN ('OWNER', 'ADMIN', 'MEMBER')),

    CONSTRAINT check_member_status
        CHECK (member_status IN ('ACTIVE', 'LEFT', 'REMOVED'))
); 

-- This will handel all th messages which are encrypted having foreign key room_id, source_language_id, sender_id take refferece from the chat_rooms,language_configuration and users
-- Also there is foreign key replay_to_message_id which take refference from the messages table it self
-- Also messages are encrypted and photo, videos are encrypted with meta data
CREATE TABLE IF NOT EXISTS messages
(
    message_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    room_id UUID NOT NULL,
    sender_id UUID NOT NULL,

    encrypted_content TEXT NOT NULL,
    source_language_id UUID NOT NULL,

    source_variant VARCHAR(50),
    message_type VARCHAR(20) NOT NULL DEFAULT 'TEXT',

    reply_to_message_id UUID,
    is_edited BOOLEAN NOT NULL DEFAULT FALSE ,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE ,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_messages_room
        FOREIGN KEY (room_id)
        REFERENCES chat_rooms(room_id)
        ON DELETE CASCADE,


    CONSTRAINT fk_messages_sender
        FOREIGN KEY (sender_id)
        REFERENCES users(user_id)
        ON DELETE SET NULL,


    CONSTRAINT fk_messages_source_language
        FOREIGN KEY (source_language_id)
        REFERENCES language_configurations(language_id)
        ON DELETE RESTRICT,

    
    CONSTRAINT fk_messages_reply_to
        FOREIGN KEY (reply_to_message_id)
        REFERENCES messages(message_id)
        ON DELETE SET NULL,

    CONSTRAINT chk_messages_type
        CHECK (message_type IN ('TEXT', 'IMAGE', 'VIDEO', 'FILE', 'AUDIO'))

); 

    CREATE INDEX idx_messages_sender_id ON messages(sender_id);
    CREATE INDEX idx_messages_created_at ON messages(created_at);


-- This will handel which messages are translated by which model and store the messages into encrypted only
-- Having 2 foreign key message_id, target_language_id take refference from messages and language_configurations

CREATE TABLE IF NOT EXISTS message_translations(

    translation_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    message_id UUID NOT NULL,
    target_language_id UUID NOT NULL,

    encrypted_content TEXT NOT NULL,
    translation_status VARCHAR(20) NOT NULL ,
    translation_model VARCHAR(200),


    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_translation_target_language
    FOREIGN KEY (target_language_id) REFERENCES language_configurations(language_id) ON DELETE RESTRICT,

    CONSTRAINT fk_message_id
    FOREIGN KEY (message_id) REFERENCES messages(message_id) ON DELETE CASCADE,

    CONSTRAINT uq_message_target_language UNIQUE(message_id,target_language_id),

    CONSTRAINT chk_translation_status CHECK (translation_status in ('PENDING','PROCESSING','COMPLETED','FAILED'))
);

-- This will handel the message_status which will have READ, DELIVERED and SENT when to deliver and if user read the messages
-- this table has 2 foreign ket message_id and user_id take refferences from the messages and users table

CREATE TABLE IF NOT EXISTS message_status(
    
    message_status_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    message_id UUID NOT NULL,
    user_id UUID NOT NULL,
    
    status VARCHAR(20) NOT NULL DEFAULT('SENT'),

    sent_at TIMESTAMPTZ NOT NULL,
    delivered_at TIMESTAMPTZ,
    read_at TIMESTAMPTZ, 

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,


    CONSTRAINT fk_message_id FOREIGN KEY (message_id) REFERENCES messages(message_id),
    CONSTRAINT fk_user_id FOREIGN KEY (user_id) REFERENCES users(user_id),
    CONSTRAINT check_status CHECK (status in ('SENT','DELIVERED','READ')),
    CONSTRAINT uq_message_user UNIQUE (message_id, user_id)

);

-- Creating a user_session table which handel the user when active and read the message everything

CREATE TABLE IF NOT EXISTS user_sessions(

    session_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    token_hash TEXT NOT NULL,
    device_info TEXT,
    user_agent TEXT,
    ip_address INET,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_activity_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMPTZ NOT NULL,
    revoked_at TIMESTAMPTZ,
    session_status VARCHAR(20) NOT NULL,

    CONSTRAINT fk_user_id FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    CONSTRAINT check_is_active CHECK(session_status in ('ACTIVE','EXPIRED','REVOKED')),
    CONSTRAINT unique_token UNIQUE (token_hash)

);

CREATE INDEX idx_user_sessions_user_id
    ON user_sessions(user_id);

CREATE INDEX idx_user_sessions_status
    ON user_sessions(session_status);

CREATE INDEX idx_user_sessions_expires_at
    ON user_sessions(expires_at);

CREATE INDEX idx_user_sessions_last_activity
    ON user_sessions(last_activity_at);

-- Creating the message_attachement which have two fk message_id and user_id take refference from the message and user table 
-- here the attachement status will be uploading,available, failed, deleted

CREATE TABLE IF NOT EXISTS message_attachments(

    attachment_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    message_id UUID NOT NULL,
    uploaded_by UUID NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_type VARCHAR(50) NOT NULL,
    mime_type VARCHAR(100) NOT NULL,
    file_size BIGINT NOT NULL,
    storage_path TEXT NOT NULL,
    attachment_status VARCHAR(20) NOT NULL DEFAULT 'UPLOADING',

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,


    CONSTRAINT fk_message_id FOREIGN KEY (message_id) REFERENCES messages(message_id) ON DELETE CASCADE,
    CONSTRAINT fk_uploaded_by FOREIGN KEY (uploaded_by) REFERENCES users(user_id) ON DELETE CASCADE,
    CONSTRAINT check_file_type CHECK(file_type in ('IMAGE','DOCUMENT','AUDIO','VIDEO','OTHER')),
    CONSTRAINT check_attachment_status CHECK(attachment_status in ('UPLOADING','AVAILABLE','FAILED','DELETED')),
    CONSTRAINT check_file_size CHECK(file_size > 0)
);

CREATE INDEX idx_message_attachments_message_id
    ON message_attachments(message_id);

CREATE INDEX idx_message_attachments_uploaded_by
    ON message_attachments(uploaded_by);

CREATE INDEX idx_message_attachments_status
    ON message_attachments(attachment_status);



-- Creating the agent table which handel which message is invoked by which agent and all details 
-- An agent execution represents a workflow/agent run.
CREATE TABLE IF NOT EXISTS agent_executions(

    agent_execution_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    message_id UUID NOT NULL,
    user_id UUID NOT NULL,

    agent_name VARCHAR(100) NOT NULL,
    workflow_name VARCHAR(100) NOT NULL,
    execution_status VARCHAR(20) NOT NULL,

    started_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP, 
    completed_at TIMESTAMPTZ,
    error_message TEXT,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_message_id Foreign Key (message_id) REFERENCES messages(message_id),
    CONSTRAINT fk_user_id Foreign Key (user_id) REFERENCES users(user_id),
    CONSTRAINT check_execution_status CHECK (execution_status in ('STARTED', 'RUNNING', 'COMPLETED', 'FAILED'))
    
);

-- The purpose is to record each individual tool/MCP call that happens inside an AGENT_EXECUTIONS record.

CREATE TABLE IF NOT EXISTS tool_executions(

    tool_execution_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_execution_id UUID NOT NULL,
    tool_name VARCHAR(100) NOT NULL,
    tool_type VARCHAR(50) NOT NULL,

    execution_status VARCHAR(20) NOT NULL,
    input_payload TEXT,
    output_payload TEXT,

    started_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMPTZ,

    error_message TEXT,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_agent_execution_id FOREIGN KEY (agent_execution_id) REFERENCES agent_executions(agent_execution_id),
    CONSTRAINT check_tool_type CHECK (tool_type in ('INTERNAL','EXTERNAL','LLM','MCP')),
    CONSTRAINT check_execution_status CHECK (execution_status in ('STARTED','RUNNING','COMPLETED','FAILED'))

);