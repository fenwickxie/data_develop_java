CREATE TABLE IF NOT EXISTS metric_result (
    id                  BIGSERIAL PRIMARY KEY,
    dataset_id          VARCHAR(64) NOT NULL,
    file_id             VARCHAR(64) NOT NULL,
    metric_name         VARCHAR(255),
    metric_value        JSONB,
    metric_type         VARCHAR(100),
    calculated_at       TIMESTAMPTZ DEFAULT NOW(),
    source_tool_version VARCHAR(100)
);

CREATE INDEX IF NOT EXISTS idx_metric_dataset ON metric_result(dataset_id);
CREATE INDEX IF NOT EXISTS idx_metric_file ON metric_result(file_id);

CREATE TABLE IF NOT EXISTS report (
    id              BIGSERIAL PRIMARY KEY,
    dataset_id      VARCHAR(64) NOT NULL,
    file_id         VARCHAR(64) NOT NULL,
    report_type     VARCHAR(100),
    storage_type    VARCHAR(50),
    bucket          VARCHAR(255),
    object_key      VARCHAR(512),
    generated_at    TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_report_dataset ON report(dataset_id);
CREATE INDEX IF NOT EXISTS idx_report_file ON report(file_id);
