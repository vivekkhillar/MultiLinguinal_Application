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