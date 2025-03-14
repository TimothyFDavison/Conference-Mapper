BEGIN;

CREATE TABLE IF NOT EXISTS conference_categories (
    id SERIAL PRIMARY KEY,
    category TEXT UNIQUE NOT NULL
);

INSERT INTO conference_categories (category) VALUES
    ('artificial intelligence'),
    ('machine learning'),
    ('communications'),
    ('image processing'),
    ('computer science'),
    ('medicine'),
    ('medical')
ON CONFLICT (category) DO NOTHING;
COMMIT;

SELECT 'Finished initialization' AS status;
SELECT pg_sleep(5);
