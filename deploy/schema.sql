-- MySQL: table for device online/offline events (state changes only)
CREATE TABLE IF NOT EXISTS status_events (
    id INT AUTO_INCREMENT PRIMARY KEY,
    device_id VARCHAR(64) NOT NULL,
    changed_at DATETIME(3) NOT NULL,
    is_online TINYINT(1) NOT NULL,
    INDEX (device_id, changed_at)
);
