SET search_path TO chat_app;

-- ============================================================
-- SEED DATA
-- ============================================================


-- ============================================================
-- 1. LANGUAGE CONFIGURATIONS
-- ============================================================

INSERT INTO chat_app.language_configurations
(
    language_code,
    language_name,
    native_name,
    script,
    variant,
    is_standard_language,
    is_user_selectable,
    is_translation_supported,
    status
)
VALUES

    -- ========================================================
    -- Standard scripts
    -- ========================================================

    ('en', 'English', 'English', 'Latin', 'Standard',
        TRUE, TRUE, TRUE, 'ACTIVE'),

    ('hi', 'Hindi', 'हिन्दी', 'Devanagari', 'Standard',
        TRUE, TRUE, TRUE, 'ACTIVE'),

    ('bn', 'Bengali', 'বাংলা', 'Bengali', 'Standard',
        TRUE, TRUE, TRUE, 'ACTIVE'),

    ('te', 'Telugu', 'తెలుగు', 'Telugu', 'Standard',
        TRUE, TRUE, TRUE, 'ACTIVE'),

    ('mr', 'Marathi', 'मराठी', 'Devanagari', 'Standard',
        TRUE, TRUE, TRUE, 'ACTIVE'),

    ('ta', 'Tamil', 'தமிழ்', 'Tamil', 'Standard',
        TRUE, TRUE, TRUE, 'ACTIVE'),

    ('ur', 'Urdu', 'اردو', 'Arabic', 'Standard',
        TRUE, TRUE, TRUE, 'ACTIVE'),

    ('gu', 'Gujarati', 'ગુજરાતી', 'Gujarati', 'Standard',
        TRUE, TRUE, TRUE, 'ACTIVE'),

    ('kn', 'Kannada', 'ಕನ್ನಡ', 'Kannada', 'Standard',
        TRUE, TRUE, TRUE, 'ACTIVE'),

    ('ml', 'Malayalam', 'മലയാളം', 'Malayalam', 'Standard',
        TRUE, TRUE, TRUE, 'ACTIVE'),

    ('or', 'Odia', 'ଓଡ଼ିଆ', 'Odia', 'Standard',
        TRUE, TRUE, TRUE, 'ACTIVE'),

    ('pa', 'Punjabi', 'ਪੰਜਾਬੀ', 'Gurmukhi', 'Standard',
        TRUE, TRUE, TRUE, 'ACTIVE'),

    ('as', 'Assamese', 'অসমীয়া', 'Assamese', 'Standard',
        TRUE, TRUE, TRUE, 'ACTIVE'),

    ('mai', 'Maithili', 'मैथिली', 'Devanagari', 'Standard',
        TRUE, TRUE, TRUE, 'ACTIVE'),

    ('sat', 'Santali', 'ᱥᱟᱱᱛᱟᱲᱤ', 'Ol Chiki', 'Standard',
        TRUE, TRUE, TRUE, 'ACTIVE'),

    ('ks', 'Kashmiri', 'कॉशुर', 'Devanagari', 'Standard',
        TRUE, TRUE, TRUE, 'ACTIVE'),

    ('sd', 'Sindhi', 'सिन्धी', 'Devanagari', 'Standard',
        TRUE, TRUE, TRUE, 'ACTIVE'),

    ('doi', 'Dogri', 'डोगरी', 'Devanagari', 'Standard',
        TRUE, TRUE, TRUE, 'ACTIVE'),

    ('brx', 'Bodo', 'बड़ो', 'Devanagari', 'Standard',
        TRUE, TRUE, TRUE, 'ACTIVE'),

    ('mni', 'Manipuri', 'মৈতৈলোন্', 'Bengali', 'Standard',
        TRUE, TRUE, TRUE, 'ACTIVE'),

    ('ne', 'Nepali', 'नेपाली', 'Devanagari', 'Standard',
        TRUE, TRUE, TRUE, 'ACTIVE'),

    ('kok', 'Konkani', 'कोंकणी', 'Devanagari', 'Standard',
        TRUE, TRUE, TRUE, 'ACTIVE'),

    ('sa', 'Sanskrit', 'संस्कृतम्', 'Devanagari', 'Standard',
        TRUE, TRUE, TRUE, 'ACTIVE'),


    -- ========================================================
    -- Latin script variants
    -- ========================================================

    ('hi-Latn', 'Hindi', 'हिन्दी', 'Latin', 'Hinglish',
        FALSE, TRUE, TRUE, 'ACTIVE'),

    ('bn-Latn', 'Bengali', 'বাংলা', 'Latin', 'Banglish',
        FALSE, TRUE, TRUE, 'ACTIVE'),

    ('te-Latn', 'Telugu', 'తెలుగు', 'Latin', 'Tenglish',
        FALSE, TRUE, TRUE, 'ACTIVE'),

    ('mr-Latn', 'Marathi', 'मराठी', 'Latin', 'Marlish',
        FALSE, TRUE, TRUE, 'ACTIVE'),

    ('ta-Latn', 'Tamil', 'தமிழ்', 'Latin', 'Tanglish',
        FALSE, TRUE, TRUE, 'ACTIVE'),

    ('ur-Latn', 'Urdu', 'اردو', 'Latin', 'Roman Urdu',
        FALSE, TRUE, TRUE, 'ACTIVE'),

    ('gu-Latn', 'Gujarati', 'ગુજરાતી', 'Latin', 'Guglish',
        FALSE, TRUE, TRUE, 'ACTIVE'),

    ('kn-Latn', 'Kannada', 'ಕನ್ನಡ', 'Latin', 'Kanglish',
        FALSE, TRUE, TRUE, 'ACTIVE'),

    ('ml-Latn', 'Malayalam', 'മലയാളം', 'Latin', 'Manglish',
        FALSE, TRUE, TRUE, 'ACTIVE'),

    ('or-Latn', 'Odia', 'ଓଡ଼ିଆ', 'Latin', 'Odlish',
        FALSE, TRUE, TRUE, 'ACTIVE'),

    ('pa-Latn', 'Punjabi', 'ਪੰਜਾਬੀ', 'Latin', 'Roman Punjabi',
        FALSE, TRUE, TRUE, 'ACTIVE'),

    ('kok-Latn', 'Konkani', 'Konkani', 'Latin', 'Roman Konkani',
        FALSE, TRUE, TRUE, 'ACTIVE'),


    -- ========================================================
    -- Arabic script variants
    -- ========================================================

    ('ks-Arab', 'Kashmiri', 'کٲشُر', 'Arabic', 'Standard',
        FALSE, TRUE, TRUE, 'ACTIVE'),

    ('sd-Arab', 'Sindhi', 'سنڌي', 'Arabic', 'Standard',
        FALSE, TRUE, TRUE, 'ACTIVE'),


    -- ========================================================
    -- Meitei Mayek
    -- ========================================================

    ('mni-Mtei', 'Manipuri', 'ꯃꯤꯇꯩ ꯂꯣꯟ', 'Meitei Mayek', 'Standard',
        FALSE, TRUE, TRUE, 'ACTIVE')

ON CONFLICT (language_code, script, variant)
DO NOTHING;


-- ============================================================
-- 2. TEST USER
-- ============================================================

INSERT INTO chat_app.users
(
    username,
    email,
    password_hash,
    first_name,
    last_name,
    preferred_language_id
)
SELECT
    'testuser001',
    'testuser001@example.com',
    'test-hash',
    'Test',
    'User',
    lc.language_id
FROM chat_app.language_configurations lc
WHERE lc.language_code = 'mr'
  AND lc.script = 'Devanagari'
  AND lc.variant = 'Standard'
ON CONFLICT (username)
DO NOTHING;


-- ============================================================
-- 3. TEST USER SESSION
-- ============================================================


INSERT INTO user_sessions
(
    user_id,
    token_hash,
    device_info,
    user_agent,
    ip_address,
    expires_at,
    session_status
)
SELECT
    user_id,
    'test-session-token-001',
    'Test Device',
    'Test Browser',
    '127.0.0.1',
    CURRENT_TIMESTAMP + INTERVAL '1 hour',
    'ACTIVE'
FROM users
WHERE username = 'testuser001';

-- ============================================================
-- 4. TEST USER CHATROOM
-- ============================================================


INSERT INTO chat_rooms
(
    room_type,
    room_name,
    created_by
)
SELECT
    'PRIVATE',
    NULL,
    user_id
FROM users
WHERE username = 'testuser001';

-- ============================================================
-- 5. TEST USER CHATROOM MEMBER ADD
-- ============================================================
INSERT INTO room_members
(
    room_id,
    user_id,
    member_role,
    member_status
)
SELECT
    cr.room_id,
    u.user_id,
    'OWNER',
    'ACTIVE'
FROM chat_rooms cr
JOIN users u
    ON cr.created_by = u.user_id
WHERE u.username = 'testuser001'
ORDER BY cr.created_at DESC
LIMIT 1
RETURNING
    room_member_id,
    room_id,
    user_id,
    member_role,
    member_status,
    joined_at;


-- ============================================================
-- 6. TEST MESSAGE
-- ============================================================

INSERT INTO messages
(
    room_id,
    sender_id,
    encrypted_content,
    source_language_id,
    source_variant,
    message_type
)
SELECT
    cr.room_id,
    u.user_id,
    'encrypted-test-message',
    lc.language_id,
    lc.variant,
    'TEXT'
FROM chat_rooms cr
JOIN users u
    ON cr.created_by = u.user_id
JOIN language_configurations lc
    ON lc.language_code = 'mr'
   AND lc.script = 'Devanagari'
   AND lc.variant = 'Standard'
WHERE u.username = 'testuser001'
ORDER BY cr.created_at DESC
LIMIT 1
RETURNING
    message_id,
    room_id,
    sender_id,
    source_language_id,
    message_type,
    created_at;

-- ============================================================
-- 7. TEST MESSAGE STATUS
-- ============================================================

INSERT INTO message_status
(
    message_id,
    user_id,
    status
)
SELECT
    m.message_id,
    u.user_id,
    'SENT'
FROM messages m
JOIN users u
    ON m.sender_id = u.user_id
WHERE u.username = 'testuser001'
ORDER BY m.created_at DESC
LIMIT 1
RETURNING
    message_status_id,
    message_id,
    user_id,
    status,
    sent_at,
    delivered_at,
    read_at,
    created_at,
    updated_at;

