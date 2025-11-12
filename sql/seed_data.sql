-- Sample data for Star Songs database
-- Based on the star-songs project theme

-- Insert Artists (one at a time for sqlcmd compatibility)
INSERT INTO dbo.Artist (name) VALUES ('David Bowie');
INSERT INTO dbo.Artist (name) VALUES ('The Beatles');
INSERT INTO dbo.Artist (name) VALUES ('Elton John');
INSERT INTO dbo.Artist (name) VALUES ('Queen');
INSERT INTO dbo.Artist (name) VALUES ('Pink Floyd');

-- Insert Songs (one at a time for sqlcmd compatibility)
INSERT INTO dbo.Song (title, artistID, released, URL, distance) VALUES ('Space Oddity', 1, CAST('1969-07-11' AS DATE), 'https://www.youtube.com/watch?v=iYYRH4apXDo', 238900.0);
INSERT INTO dbo.Song (title, artistID, released, URL, distance) VALUES ('Starman', 1, CAST('1972-04-28' AS DATE), 'https://www.youtube.com/watch?v=tRcPA7Fzebw', 384400.0);
INSERT INTO dbo.Song (title, artistID, released, URL, distance) VALUES ('Across the Universe', 2, CAST('1970-02-06' AS DATE), 'https://www.youtube.com/watch?v=90M60PzmxEE', 40000000.0);
INSERT INTO dbo.Song (title, artistID, released, URL, distance) VALUES ('Rocket Man', 3, CAST('1972-04-17' AS DATE), 'https://www.youtube.com/watch?v=DtVBCG6ThDk', 384400.0);
INSERT INTO dbo.Song (title, artistID, released, URL, distance) VALUES ('''39', 4, CAST('1975-11-21' AS DATE), 'https://www.youtube.com/watch?v=BjuyXR5by2s', 9460730472580.8);
INSERT INTO dbo.Song (title, artistID, released, URL, distance) VALUES ('Astronomy Domine', 5, CAST('1967-08-05' AS DATE), 'https://www.youtube.com/watch?v=pJh9OLlXenM', 4000000.0);

-- Verify the data
PRINT 'Artists loaded successfully';
PRINT 'Songs loaded successfully';
