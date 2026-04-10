CREATE DATABASE IF NOT EXISTS passengers_db;
USE passengers_db;
CREATE TABLE IF NOT EXISTS records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);
INSERT INTO records (name) VALUES ('System_Init_Record');
