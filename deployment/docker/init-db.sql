-- Database initialization script for PostgreSQL
-- This runs automatically when the PostgreSQL container starts for the first time

-- Create database (this is redundant since POSTGRES_DB already creates it, but kept for clarity)
-- CREATE DATABASE france_chomage;

-- Set encoding and locale
ALTER DATABASE france_chomage SET timezone TO 'Europe/Paris';

-- Create user if needed (postgres user already exists and has all permissions)
-- The application will create tables automatically via SQLAlchemy

-- Grant necessary permissions (already granted to postgres user)
-- GRANT ALL PRIVILEGES ON DATABASE france_chomage TO postgres;

-- Log successful initialization
SELECT 'Database france_chomage initialized successfully' AS status;
