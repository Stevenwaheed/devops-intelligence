-- Initialize TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Create hypertables for time-series data
-- Note: This should be run after the initial migration

-- API Requests hypertable
SELECT create_hypertable('api_requests', 'timestamp', if_not_exists => TRUE);

-- Create continuous aggregates for API requests (hourly)
CREATE MATERIALIZED VIEW IF NOT EXISTS api_requests_hourly
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 hour', timestamp) AS bucket,
    project_id,
    provider_id,
    COUNT(*) AS request_count,
    AVG(latency_ms) AS avg_latency,
    SUM(cost_usd) AS total_cost,
    SUM((tokens_used->>'prompt')::int) AS total_prompt_tokens,
    SUM((tokens_used->>'completion')::int) AS total_completion_tokens
FROM api_requests
GROUP BY bucket, project_id, provider_id;

-- Create continuous aggregates for API requests (daily)
CREATE MATERIALIZED VIEW IF NOT EXISTS api_requests_daily
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 day', timestamp) AS bucket,
    project_id,
    provider_id,
    COUNT(*) AS request_count,
    AVG(latency_ms) AS avg_latency,
    SUM(cost_usd) AS total_cost
FROM api_requests
GROUP BY bucket, project_id, provider_id;

-- Query Patterns hypertable
SELECT create_hypertable('query_patterns', 'timestamp', if_not_exists => TRUE);

-- Create continuous aggregates for query patterns (hourly)
CREATE MATERIALIZED VIEW IF NOT EXISTS query_patterns_hourly
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 hour', timestamp) AS bucket,
    connection_id,
    query_fingerprint,
    COUNT(*) AS execution_count,
    AVG(execution_time_ms) AS avg_execution_time,
    MAX(execution_time_ms) AS max_execution_time,
    SUM(rows_examined) AS total_rows_examined
FROM query_patterns
GROUP BY bucket, connection_id, query_fingerprint;

-- Database Metrics hypertable
SELECT create_hypertable('database_metrics', 'timestamp', if_not_exists => TRUE);

-- Create continuous aggregates for database metrics (hourly)
CREATE MATERIALIZED VIEW IF NOT EXISTS database_metrics_hourly
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 hour', timestamp) AS bucket,
    connection_id,
    AVG(cpu_usage_pct) AS avg_cpu_usage,
    AVG(memory_usage_pct) AS avg_memory_usage,
    AVG(connection_count) AS avg_connection_count,
    SUM(slow_query_count) AS total_slow_queries,
    AVG(cache_hit_rate) AS avg_cache_hit_rate
FROM database_metrics
GROUP BY bucket, connection_id;

-- Add retention policies (optional - adjust as needed)
-- Keep raw data for 90 days
SELECT add_retention_policy('api_requests', INTERVAL '90 days', if_not_exists => TRUE);
SELECT add_retention_policy('query_patterns', INTERVAL '90 days', if_not_exists => TRUE);
SELECT add_retention_policy('database_metrics', INTERVAL '90 days', if_not_exists => TRUE);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_api_requests_project_provider ON api_requests(project_id, provider_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_query_patterns_connection_fingerprint ON query_patterns(connection_id, query_fingerprint, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_database_metrics_connection ON database_metrics(connection_id, timestamp DESC);
