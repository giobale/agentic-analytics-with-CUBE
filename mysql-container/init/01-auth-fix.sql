-- ABOUTME: MySQL authentication plugin fix for CUBE compatibility
-- ABOUTME: Ensures organiser user uses mysql_native_password for proper CUBE connection

-- Fix authentication plugin for existing organiser user
ALTER USER 'organiser'@'%' IDENTIFIED WITH mysql_native_password BY 'amatriciana';

-- Create organiser user with correct authentication plugin if it doesn't exist
CREATE USER IF NOT EXISTS 'organiser'@'%' IDENTIFIED WITH mysql_native_password BY 'amatriciana';

-- Grant necessary privileges on the ticketshopdb database
GRANT ALL PRIVILEGES ON ticketshopdb.* TO 'organiser'@'%';

-- Ensure organiser can create, read, update, delete on all tables
GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, DROP, ALTER, INDEX ON ticketshopdb.* TO 'organiser'@'%';

-- Allow LOAD DATA INFILE for CSV imports
GRANT FILE ON *.* TO 'organiser'@'%';

-- Flush privileges to apply changes immediately
FLUSH PRIVILEGES;

-- Log successful authentication setup
SELECT 'Authentication setup completed for organiser user' as Status;