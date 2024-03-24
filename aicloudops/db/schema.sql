CREATE TABLE code_files (
    file_id SERIAL PRIMARY KEY,
    file_path VARCHAR(255) NOT NULL UNIQUE,
    file_hash CHAR(64) NOT NULL UNIQUE
);
CREATE TABLE execution_logs (
    execution_id SERIAL PRIMARY KEY,
    file_id INT NOT NULL,
    execution_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    exit_code INT NOT NULL,
    execution_output TEXT DEFAULT '',
    FOREIGN KEY (file_id) REFERENCES files(file_id)
);