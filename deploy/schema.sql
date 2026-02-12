-- MySQL: table for device online/offline events (state changes only)
CREATE TABLE IF NOT EXISTS status_events (
    id INT AUTO_INCREMENT PRIMARY KEY,
    device_id VARCHAR(64) NOT NULL,
    changed_at DATETIME(3) NOT NULL,
    is_online TINYINT(1) NOT NULL,
    INDEX (device_id, changed_at)
);

-- Displayboard: reviews count from helgamade.com.ua (reviews_parser.py)
CREATE TABLE IF NOT EXISTS displayboard_reviews (
    id TINYINT PRIMARY KEY DEFAULT 1,
    reviews_count INT NOT NULL DEFAULT 0,
    updated_at DATETIME NOT NULL
);
INSERT IGNORE INTO displayboard_reviews (id, reviews_count, updated_at) VALUES (1, 0, NOW());
