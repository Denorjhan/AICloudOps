CREATE TABLE code_files (
    file_id SERIAL PRIMARY KEY,
    file_path VARCHAR(255) NOT NULL UNIQUE,
    -- maps to code_file (str)
    file_hash CHAR(64) NOT NULL UNIQUE
);
CREATE TABLE execution_logs (
    execution_id SERIAL PRIMARY KEY,
    file_id INT NOT NULL,
    execution_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    exit_code INT NOT NULL,
    -- mpas to exit_code (int)
    execution_output TEXT DEFAULT '',
    -- maps to output (str)
    FOREIGN KEY (file_id) REFERENCES files(file_id)
);