CREATE EXTENSION IF NOT EXISTS vector;


CREATE TABLE scripts (
    script_id SERIAL PRIMARY KEY,
    script_name VARCHAR(127) NOT NULL UNIQUE,
    script_content TEXT NOT NULL UNIQUE CHECK (length(script_content) > 0),  -- check datatype
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    executed_at TIMESTAMP WITH TIME ZONE DEFAULT NULL,
    CHECK (created_at <= CURRENT_TIMESTAMP), -- Preventing future 'created_at' dates
    CHECK (executed_at IS NULL OR executed_at <= CURRENT_TIMESTAMP)
);


CREATE TABLE vectors (
    vector_id INTEGER PRIMARY KEY REFERENCES scripts(script_id) ON DELETE CASCADE,
    vector VECTOR(1536) NOT NULL
);
