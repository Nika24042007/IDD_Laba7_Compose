CREATE TABLE IF NOT EXISTS gifts (
    id SERIAL PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    description TEXT,
    recipient VARCHAR(50),
    price FLOAT DEFAULT 0,
    completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_gifts_completed ON gifts(completed);
CREATE INDEX IF NOT EXISTS idx_gifts_created_at ON gifts(created_at DESC);