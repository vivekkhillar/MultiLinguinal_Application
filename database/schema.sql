CREATE SCHEMA CHAT_APP;

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
        ON DELETE CASCADE,


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
    