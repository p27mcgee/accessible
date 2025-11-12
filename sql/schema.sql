-- Star Songs Database Schema for SQL Server
-- Based on JPA entities from star-songs project

-- Drop tables if they exist (for clean recreation)
IF OBJECT_ID('dbo.Song', 'U') IS NOT NULL DROP TABLE dbo.Song;
IF OBJECT_ID('dbo.Artist', 'U') IS NOT NULL DROP TABLE dbo.Artist;

-- Create Artist table
CREATE TABLE dbo.Artist (
    id INT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(64) NOT NULL
);

-- Create Song table
CREATE TABLE dbo.Song (
    id INT IDENTITY(1,1) PRIMARY KEY,
    title NVARCHAR(64) NOT NULL,
    artistID INT NULL,
    released DATE NULL,
    URL NVARCHAR(1024) NULL,
    distance FLOAT(53) NULL,  -- FLOAT(53) is equivalent to Double precision
    CONSTRAINT FK_Song_Artist FOREIGN KEY (artistID) REFERENCES dbo.Artist(id)
);

-- Create indexes for better query performance
CREATE INDEX IX_Song_ArtistID ON dbo.Song(artistID);
CREATE INDEX IX_Artist_Name ON dbo.Artist(name);
CREATE INDEX IX_Song_Title ON dbo.Song(title);
