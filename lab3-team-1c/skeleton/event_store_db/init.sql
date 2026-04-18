CREATE DATABASE IF NOT EXISTS event_store_db;
USE event_store_db;
CREATE TABLE IF NOT EXISTS events (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    event_type VARCHAR(100) NOT NULL,
    aggregate_id VARCHAR(100) NOT NULL,
    payload JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_aggregate (aggregate_id),
    INDEX idx_type (event_type)
);
INSERT INTO events (event_type, aggregate_id, payload)
VALUES ('SYSTEM_INIT', 'ERTMS', '{"source": "MDE_Generator"}');
