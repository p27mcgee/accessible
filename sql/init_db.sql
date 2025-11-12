-- Initialize Star Songs Database
-- This script creates the database and switches to it

-- Create database if it doesn't exist
IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = 'starsongs')
BEGIN
    CREATE DATABASE starsongs;
    PRINT 'Database starsongs created successfully';
END
ELSE
BEGIN
    PRINT 'Database starsongs already exists';
END
GO

-- Switch to the starsongs database
USE starsongs;
GO

PRINT 'Switched to starsongs database';
GO
