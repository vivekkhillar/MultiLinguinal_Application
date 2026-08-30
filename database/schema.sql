CREATE SCHEMA IF NOT EXISTS chat_app;

SET search_path TO chat_app;
-- ============================================================
-- 1. LANGUAGE CONFIGURATIONS
-- ============================================================

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

    CONSTRAINT uq_language_configuration
        UNIQUE (language_code, script, variant),

    CONSTRAINT chk_language_status
        CHECK (status IN ('ACTIVE', 'INACTIVE')),

    CONSTRAINT chk_language_code_not_empty
        CHECK (length(trim(language_code)) > 0),

    CONSTRAINT chk_language_name_not_empty
        CHECK (length(trim(language_name)) > 0),

    CONSTRAINT chk_language_native_name_not_empty
        CHECK (length(trim(native_name)) > 0),

    CONSTRAINT chk_language_script_not_empty
        CHECK (length(trim(script)) > 0)
);


-- ============================================================
-- 2. USERS
-- ============================================================

CREATE TABLE IF NOT EXISTS users
(
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,

    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100),

    preferred_language_id UUID NOT NULL,

    account_status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
    deactivated_at TIMESTAMPTZ,
    deletion_scheduled_at TIMESTAMPTZ,
    last_login_at TIMESTAMPTZ,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_users_preferred_language
        FOREIGN KEY (preferred_language_id)
        REFERENCES language_configurations(language_id),

    CONSTRAINT chk_account_status
        CHECK (account_status IN ('ACTIVE', 'DEACTIVATED')),

    CONSTRAINT chk_users_username_not_empty
        CHECK (length(trim(username)) > 0),

    CONSTRAINT chk_users_email_not_empty
        CHECK (length(trim(email)) > 0),

    CONSTRAINT chk_users_deactivation_timestamp
        CHECK (
            (account_status = 'ACTIVE' AND deactivated_at IS NULL)
            OR
            (account_status = 'DEACTIVATED' AND deactivated_at IS NOT NULL)
        ),
    CONSTRAINT chk_users_deletion_schedule
        CHECK (
            deletion_scheduled_at IS NULL
            OR
            (
                account_status = 'DEACTIVATED'
                AND deactivated_at IS NOT NULL
                AND deletion_scheduled_at >= deactivated_at
            )
        )

);

CREATE INDEX idx_users_account_status
    ON users(account_status);

CREATE INDEX idx_users_preferred_language
    ON users(preferred_language_id);

CREATE INDEX idx_users_deletion_scheduler
    ON users(deletion_scheduled_at)
    WHERE account_status = 'DEACTIVATED'
    AND deletion_scheduled_at IS NOT NULL;


-- ============================================================
-- 3. CHAT ROOMS
-- ============================================================

CREATE TABLE IF NOT EXISTS chat_rooms
(
    room_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    room_type VARCHAR(50) NOT NULL,
    room_name VARCHAR(255),

    created_by UUID NOT NULL,

    max_members INTEGER NOT NULL DEFAULT 50,

    room_status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_chat_rooms_created_by
        FOREIGN KEY (created_by)
        REFERENCES users(user_id),

    CONSTRAINT chk_room_type
        CHECK (room_type IN ('PRIVATE', 'GROUP')),

    CONSTRAINT chk_room_status
        CHECK (room_status IN ('ACTIVE', 'INACTIVE')),

    CONSTRAINT chk_max_members
        CHECK (max_members > 0),

    CONSTRAINT chk_chat_rooms_group_name
        CHECK (
            room_type = 'PRIVATE'
            OR length(trim(room_name)) > 0
        )
);




-- ============================================================
-- 4. ROOM MEMBERS
-- ============================================================

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

    CONSTRAINT chk_room_members_left_at
        CHECK (
            (member_status = 'ACTIVE' AND left_at IS NULL)
            OR
            (member_status IN ('LEFT', 'REMOVED') AND left_at IS NOT NULL)
        ),

    CONSTRAINT chk_room_members_role
        CHECK (member_role IN ('OWNER', 'ADMIN', 'MEMBER')),

    CONSTRAINT chk_room_members_status
        CHECK (member_status IN ('ACTIVE', 'LEFT', 'REMOVED'))
);

CREATE INDEX idx_room_members_user_id
    ON room_members(user_id);


CREATE INDEX IF NOT EXISTS idx_room_members_user_active
ON room_members(user_id, room_id)
WHERE member_status = 'ACTIVE';

CREATE INDEX IF NOT EXISTS idx_room_members_room_active
ON room_members(room_id, user_id)
WHERE member_status = 'ACTIVE';


-- ============================================================
-- 5. MESSAGES
-- ============================================================

CREATE TABLE IF NOT EXISTS messages
(
    message_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    room_id UUID NOT NULL,
    sender_id UUID,

    encrypted_content TEXT NOT NULL,
    source_language_id UUID NOT NULL,

    source_variant VARCHAR(50),
    message_type VARCHAR(20) NOT NULL DEFAULT 'TEXT',

    reply_to_message_id UUID,

    is_edited BOOLEAN NOT NULL DEFAULT FALSE,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,

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

    CONSTRAINT uq_messages_message_room
        UNIQUE (message_id, room_id),

    CONSTRAINT fk_messages_reply_to
        FOREIGN KEY (reply_to_message_id, room_id)
        REFERENCES messages(message_id, room_id)
        ON DELETE SET NULL,

    CONSTRAINT fk_messages_source_language
        FOREIGN KEY (source_language_id)
        REFERENCES language_configurations(language_id)
        ON DELETE RESTRICT,

    CONSTRAINT chk_messages_type
        CHECK (message_type IN ('TEXT', 'IMAGE', 'VIDEO', 'FILE', 'AUDIO'))
);

CREATE INDEX idx_messages_sender_id
    ON messages(sender_id);

CREATE INDEX idx_messages_room_created_at
    ON messages(room_id, created_at);


-- ============================================================
-- 6. MESSAGE TRANSLATIONS
-- ============================================================

CREATE TABLE IF NOT EXISTS message_translations
(
    translation_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    message_id UUID NOT NULL,
    target_language_id UUID NOT NULL,

    encrypted_content TEXT NOT NULL,
    translation_status VARCHAR(20) NOT NULL,
    translation_model VARCHAR(200),

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_message_translations_message
        FOREIGN KEY (message_id)
        REFERENCES messages(message_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_message_translations_target_language
        FOREIGN KEY (target_language_id)
        REFERENCES language_configurations(language_id)
        ON DELETE RESTRICT,

    CONSTRAINT uq_message_target_language
        UNIQUE (message_id, target_language_id),

    CONSTRAINT chk_translation_status
        CHECK (
            translation_status IN (
                'PENDING',
                'PROCESSING',
                'COMPLETED',
                'FAILED'
            )
        )
);


-- ============================================================
-- 7. MESSAGE STATUS
-- ============================================================

CREATE TABLE IF NOT EXISTS message_status
(
    message_status_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    message_id UUID NOT NULL,
    user_id UUID NOT NULL,

    status VARCHAR(20) NOT NULL DEFAULT 'SENT',

    sent_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    delivered_at TIMESTAMPTZ,
    read_at TIMESTAMPTZ,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_message_status_message
        FOREIGN KEY (message_id)
        REFERENCES messages(message_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_message_status_user
        FOREIGN KEY (user_id)
        REFERENCES users(user_id)
        ON DELETE CASCADE,

    CONSTRAINT chk_message_status
        CHECK (status IN ('SENT', 'DELIVERED', 'READ')),

    CONSTRAINT uq_message_user
        UNIQUE (message_id, user_id),

    CONSTRAINT chk_message_status_timestamps
        CHECK (
            (delivered_at IS NULL OR delivered_at >= sent_at)
            AND
            (read_at IS NULL OR read_at >= COALESCE(delivered_at, sent_at))
        )
);

CREATE INDEX idx_message_status_user_id
    ON message_status(user_id);


-- ============================================================
-- 8. USER SESSIONS
-- ============================================================

CREATE TABLE IF NOT EXISTS user_sessions
(
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

    CONSTRAINT fk_user_sessions_user
        FOREIGN KEY (user_id)
        REFERENCES users(user_id)
        ON DELETE CASCADE,

    CONSTRAINT chk_user_sessions_status
        CHECK (session_status IN ('ACTIVE', 'EXPIRED', 'REVOKED')),

    CONSTRAINT uq_user_sessions_token
        UNIQUE (token_hash),

    CONSTRAINT chk_user_sessions_expiry
        CHECK (expires_at > created_at),

    CONSTRAINT chk_user_sessions_revoked_at
        CHECK (
            (session_status = 'REVOKED' AND revoked_at IS NOT NULL)
            OR
            (session_status IN ('ACTIVE', 'EXPIRED') AND revoked_at IS NULL)
        )
);

CREATE INDEX idx_user_sessions_user_id
    ON user_sessions(user_id);

CREATE INDEX idx_user_sessions_expires_at
    ON user_sessions(expires_at);

CREATE INDEX IF NOT EXISTS idx_user_sessions_active_expiry
ON user_sessions(expires_at)
WHERE session_status = 'ACTIVE';


-- ============================================================
-- 9. MESSAGE ATTACHMENTS
-- ============================================================

CREATE TABLE IF NOT EXISTS message_attachments
(
    attachment_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    message_id UUID NOT NULL,
    uploaded_by UUID,

    file_name VARCHAR(255) NOT NULL,
    file_type VARCHAR(50) NOT NULL,
    mime_type VARCHAR(100) NOT NULL,

    file_size BIGINT NOT NULL,
    storage_path TEXT NOT NULL,

    attachment_status VARCHAR(20) NOT NULL DEFAULT 'UPLOADING',

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_message_attachments_message
        FOREIGN KEY (message_id)
        REFERENCES messages(message_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_message_attachments_uploaded_by
        FOREIGN KEY (uploaded_by)
        REFERENCES users(user_id)
        ON DELETE SET NULL,

    CONSTRAINT chk_attachment_file_type
        CHECK (
            file_type IN (
                'IMAGE',
                'DOCUMENT',
                'AUDIO',
                'VIDEO',
                'OTHER'
            )
        ),

    CONSTRAINT chk_attachment_status
        CHECK (
            attachment_status IN (
                'UPLOADING',
                'AVAILABLE',
                'FAILED',
                'DELETED'
            )
        ),

    CONSTRAINT chk_attachment_file_size
        CHECK (file_size > 0),

    CONSTRAINT chk_attachment_file_name_not_empty
        CHECK (length(trim(file_name)) > 0),

    CONSTRAINT chk_attachment_mime_type_not_empty
        CHECK (length(trim(mime_type)) > 0),

    CONSTRAINT chk_attachment_storage_path_not_empty
        CHECK (length(trim(storage_path)) > 0)
);

CREATE INDEX idx_message_attachments_message_id
    ON message_attachments(message_id);

CREATE INDEX idx_message_attachments_uploaded_by
    ON message_attachments(uploaded_by);


-- ============================================================
-- 10. AGENT EXECUTIONS
-- ============================================================

CREATE TABLE IF NOT EXISTS agent_executions
(
    agent_execution_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    message_id UUID NOT NULL,
    user_id UUID,

    agent_name VARCHAR(100) NOT NULL,
    workflow_name VARCHAR(100) NOT NULL,
    execution_status VARCHAR(20) NOT NULL,

    started_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMPTZ,
    error_message TEXT,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_agent_executions_message
        FOREIGN KEY (message_id)
        REFERENCES messages(message_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_agent_executions_user
        FOREIGN KEY (user_id)
        REFERENCES users(user_id)
        ON DELETE SET NULL,

    CONSTRAINT chk_agent_execution_status
        CHECK (
            execution_status IN (
                'STARTED',
                'RUNNING',
                'COMPLETED',
                'FAILED'
            )
        ),

    CONSTRAINT chk_agent_execution_times
        CHECK (
            completed_at IS NULL
            OR completed_at >= started_at
        )
);

CREATE INDEX idx_agent_execution_message_id
    ON agent_executions(message_id);

CREATE INDEX idx_agent_execution_user_id
    ON agent_executions(user_id);


-- ============================================================
-- 11. TOOL EXECUTIONS
-- ============================================================

CREATE TABLE IF NOT EXISTS tool_executions
(
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

    CONSTRAINT fk_tool_executions_agent_execution
        FOREIGN KEY (agent_execution_id)
        REFERENCES agent_executions(agent_execution_id)
        ON DELETE CASCADE,

    CONSTRAINT chk_tool_execution_type
        CHECK (
            tool_type IN (
                'INTERNAL',
                'EXTERNAL',
                'LLM',
                'MCP'
            )
        ),

    CONSTRAINT chk_tool_execution_status
        CHECK (
            execution_status IN (
                'STARTED',
                'RUNNING',
                'COMPLETED',
                'FAILED'
            )
        ),

    CONSTRAINT chk_tool_execution_times
        CHECK (
            completed_at IS NULL
            OR completed_at >= started_at
        )
);

CREATE INDEX idx_tool_executions_agent_execution_id
    ON tool_executions(agent_execution_id);


-- ============================================================
-- 12. AUDIT & COMPLIANCE
-- ============================================================

CREATE TABLE IF NOT EXISTS audit_logs
(
    audit_log_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    user_id UUID,

    event_type VARCHAR(100) NOT NULL,
    event_category VARCHAR(50) NOT NULL,

    entity_type VARCHAR(50),
    entity_id UUID,

    ip_address INET,
    user_agent TEXT,

    event_details JSONB,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_audit_logs_user
        FOREIGN KEY (user_id)
        REFERENCES users(user_id)
        ON DELETE SET NULL,

    CONSTRAINT chk_audit_event_category
        CHECK (
            event_category IN (
                'AUTHENTICATION',
                'ACCOUNT',
                'SECURITY',
                'ROOM',
                'MESSAGE',
                'ATTACHMENT',
                'AGENT',
                'TOOL',
                'ADMIN'
            )
        ),

    CONSTRAINT chk_audit_event_type_not_empty
        CHECK (length(trim(event_type)) > 0)
);

CREATE INDEX idx_audit_logs_user_id
    ON audit_logs(user_id);

CREATE INDEX idx_audit_logs_event_type
    ON audit_logs(event_type);

CREATE INDEX idx_audit_logs_created_at
    ON audit_logs(created_at);

CREATE INDEX idx_audit_logs_entity
    ON audit_logs(entity_type, entity_id);

CREATE INDEX IF NOT EXISTS idx_audit_logs_category_created
ON audit_logs(event_category, created_at DESC);

-- 1. Create OR REPLACE FUNCTION for updated_at trigger
CREATE OR REPLACE FUNCTION set_updated_at() RETURNS TRIGGER AS $$
    BEGIN
        NEW.updated_at = CURRENT_TIMESTAMP;
        RETURN NEW;
    END; 
    $$ LANGUAGE plpgsql;

-- ============================================================
-- 6.16.2 — UPDATED_AT TRIGGERS
-- ============================================================

CREATE TRIGGER trg_language_configurations_updated_at
BEFORE UPDATE ON language_configurations
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();


CREATE TRIGGER trg_users_updated_at
BEFORE UPDATE ON users
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();


CREATE TRIGGER trg_chat_rooms_updated_at
BEFORE UPDATE ON chat_rooms
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();


CREATE TRIGGER trg_room_members_updated_at
BEFORE UPDATE ON room_members
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();


CREATE TRIGGER trg_messages_updated_at
BEFORE UPDATE ON messages
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();


CREATE TRIGGER trg_message_translations_updated_at
BEFORE UPDATE ON message_translations
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();


CREATE TRIGGER trg_message_status_updated_at
BEFORE UPDATE ON message_status
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();


CREATE TRIGGER trg_message_attachments_updated_at
BEFORE UPDATE ON message_attachments
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();


CREATE TRIGGER trg_agent_executions_updated_at
BEFORE UPDATE ON agent_executions
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();


CREATE TRIGGER trg_tool_executions_updated_at
BEFORE UPDATE ON tool_executions
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

