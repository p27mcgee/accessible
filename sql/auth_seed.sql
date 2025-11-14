-- Seed data for authentication database
-- Creates initial admin user

-- Connect to auth_db
-- \c auth_db;

-- Insert default admin user
-- Password: Admin123! (This should be changed immediately after first login)
-- Password hash generated with bcrypt rounds=12
INSERT INTO users (id, username, email, password_hash, role, is_active)
VALUES (
    uuid_generate_v4(),
    'admin',
    'admin@example.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzNW8J6tKe',  -- Admin123!
    'admin',
    true
)
ON CONFLICT (username) DO NOTHING;

-- Insert a test regular user (optional - for testing)
-- Password: User123!
INSERT INTO users (id, username, email, password_hash, role, is_active)
VALUES (
    uuid_generate_v4(),
    'testuser',
    'testuser@example.com',
    '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW',  -- User123!
    'user',
    true
)
ON CONFLICT (username) DO NOTHING;

-- Verify inserted users
SELECT id, username, email, role, is_active, created_at FROM users;
