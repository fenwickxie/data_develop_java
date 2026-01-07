CREATE TABLE IF NOT EXISTS dataset (
    dataset_id      VARCHAR(64) PRIMARY KEY,
    name            VARCHAR(255),
    description     TEXT,
    status          VARCHAR(50),
    created_by      VARCHAR(100),
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS file (
    file_id         VARCHAR(64) PRIMARY KEY,
    dataset_id      VARCHAR(64) NOT NULL REFERENCES dataset(dataset_id),
    filename        VARCHAR(255),
    storage_type    VARCHAR(50),
    bucket          VARCHAR(255),
    object_key      VARCHAR(512),
    size            BIGINT,
    checksum        VARCHAR(128),
    content_type    VARCHAR(150),
    version         INT,
    encrypt_flag    BOOLEAN,
    status          VARCHAR(50),
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_file_dataset ON file(dataset_id);
