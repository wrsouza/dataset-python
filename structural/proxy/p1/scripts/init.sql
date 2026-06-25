-- Schema + demo data for the Lazy DB Proxy example.

CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username VARCHAR(64) NOT NULL,
    email VARCHAR(128) NOT NULL,
    full_name VARCHAR(128) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS user_avatars (
    user_id INTEGER PRIMARY KEY REFERENCES users(user_id),
    content_type VARCHAR(32) NOT NULL DEFAULT 'image/png',
    data BYTEA NOT NULL DEFAULT '',
    size_bytes INTEGER NOT NULL DEFAULT 0,
    updated_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS user_documents (
    document_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(user_id),
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    file_size_kb NUMERIC(10, 2) NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS activity_log (
    event_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(user_id),
    event_type VARCHAR(32) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

INSERT INTO users (user_id, username, email, full_name) VALUES
    (1, 'alice', 'alice@example.com', 'Alice Anderson'),
    (2, 'bob', 'bob@example.com', 'Bob Brown')
ON CONFLICT (user_id) DO NOTHING;

INSERT INTO user_avatars (user_id, content_type, data, size_bytes) VALUES
    (1, 'image/png', E'\\x89504e470d0a1a0a', 8)
ON CONFLICT (user_id) DO NOTHING;

INSERT INTO user_documents (user_id, title, content, file_size_kb) VALUES
    (1, 'Resume', 'Lorem ipsum...', 12.5),
    (1, 'Cover Letter', 'Dear hiring manager...', 4.2)
ON CONFLICT DO NOTHING;

INSERT INTO activity_log (user_id, event_type) VALUES
    (1, 'login'),
    (1, 'login')
ON CONFLICT DO NOTHING;
