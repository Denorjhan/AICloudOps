



-- Create contexts table
CREATE TABLE IF NOT EXISTS contexts (
    context_id SERIAL PRIMARY KEY,
    context_vector BYTEA,  -- Change data type to BYTEA for binary data
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create operations table
CREATE TABLE IF NOT EXISTS operations (
    operation_id SERIAL PRIMARY KEY,
    context_id INT REFERENCES contexts(context_id),
    operation_type VARCHAR(255),
    description TEXT,
    file_reference VARCHAR(255),
    agent_id INT,
    status VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create agents table
CREATE TABLE IF NOT EXISTS agents (
    agent_id SERIAL PRIMARY KEY,
    agent_name VARCHAR(255),
    agent_type VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

