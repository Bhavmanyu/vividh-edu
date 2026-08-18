-- ============================================================
-- IndiaLens Production Database Schema v1.0
-- PostgreSQL 15+
-- ============================================================

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- ============================================================
-- ENUM TYPES
-- ============================================================

CREATE TYPE college_tier AS ENUM ('1', '2', '3');
CREATE TYPE college_type AS ENUM ('IIT', 'NIT', 'private', 'deemed', 'central', 'autonomous', 'state');
CREATE TYPE degree_level AS ENUM ('UG', 'PG', 'PhD', 'Diploma');
CREATE TYPE degree_field AS ENUM (
  'engineering-cs',
  'engineering-non-cs',
  'medicine',
  'management',
  'commerce',
  'design',
  'law',
  'pure-sciences',
  'social-sciences',
  'arts'
);
CREATE TYPE scrape_status AS ENUM ('running', 'success', 'partial', 'failed');
CREATE TYPE anomaly_status AS ENUM ('pending', 'accepted', 'rejected', 'auto_accepted');
CREATE TYPE confidence_level AS ENUM ('High', 'Medium', 'Low');
CREATE TYPE feedback_status AS ENUM ('pending', 'accepted', 'rejected', 'merged');

-- ============================================================
-- COLLEGES
-- ============================================================

CREATE TABLE colleges (
  id                UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  short_name        VARCHAR(64) NOT NULL,
  full_name         VARCHAR(256) NOT NULL,
  state             VARCHAR(64) NOT NULL,
  city              VARCHAR(64) NOT NULL,
  tier              college_tier NOT NULL,
  college_type      college_type NOT NULL,
  naac_grade        VARCHAR(4),
  nirf_rank         INTEGER,
  established_year  INTEGER,
  website_url       VARCHAR(512),
  is_active         BOOLEAN NOT NULL DEFAULT TRUE,
  created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_colleges_state ON colleges(state);
CREATE INDEX idx_colleges_tier ON colleges(tier);
CREATE INDEX idx_colleges_nirf_rank ON colleges(nirf_rank);
CREATE INDEX idx_colleges_name_trgm ON colleges USING gin(full_name gin_trgm_ops);

-- ============================================================
-- DEGREES
-- ============================================================

CREATE TABLE degrees (
  id                UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  short_name        VARCHAR(64) NOT NULL,
  full_name         VARCHAR(256) NOT NULL,
  field             degree_field NOT NULL,
  level             degree_level NOT NULL,
  duration_years    DECIMAL(3,1) NOT NULL,
  created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_degrees_field ON degrees(field);
CREATE INDEX idx_degrees_level ON degrees(level);

-- ============================================================
-- PROGRAMS (college × degree combinations)
-- ============================================================

CREATE TABLE programs (
  id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  college_id          UUID NOT NULL REFERENCES colleges(id) ON DELETE CASCADE,
  degree_id           UUID NOT NULL REFERENCES degrees(id) ON DELETE CASCADE,
  annual_tuition_inr  BIGINT,
  total_seats         INTEGER,
  cutoff_rank_low     INTEGER,   -- JEE/NEET/CAT lower bound
  cutoff_rank_high    INTEGER,
  is_active           BOOLEAN NOT NULL DEFAULT TRUE,
  created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE(college_id, degree_id)
);

CREATE INDEX idx_programs_college ON programs(college_id);
CREATE INDEX idx_programs_degree ON programs(degree_id);

-- ============================================================
-- SCRAPE RUNS
-- ============================================================

CREATE TABLE scrape_runs (
  id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  source_name     VARCHAR(64) NOT NULL,   -- 'nirf', 'ambitionbox', 'naukri', 'reddit', 'plfs', 'worldbank'
  started_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  completed_at    TIMESTAMPTZ,
  status          scrape_status NOT NULL DEFAULT 'running',
  records_scraped INTEGER DEFAULT 0,
  records_updated INTEGER DEFAULT 0,
  records_flagged INTEGER DEFAULT 0,
  error_message   TEXT,
  metadata        JSONB DEFAULT '{}'
);

CREATE INDEX idx_scrape_runs_source ON scrape_runs(source_name);
CREATE INDEX idx_scrape_runs_started ON scrape_runs(started_at DESC);

-- ============================================================
-- SCRAPED DATA POINTS
-- ============================================================

CREATE TABLE data_points (
  id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  program_id      UUID NOT NULL REFERENCES programs(id) ON DELETE CASCADE,
  scrape_run_id   UUID NOT NULL REFERENCES scrape_runs(id),
  field_name      VARCHAR(64) NOT NULL,
  raw_value       TEXT NOT NULL,
  parsed_value    DECIMAL(20, 4),
  unit            VARCHAR(32),   -- 'INR', 'PCT', 'RANK', 'COUNT'
  source_url      VARCHAR(1024),
  scraped_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  is_current      BOOLEAN NOT NULL DEFAULT TRUE
);

-- Only one current value per (program, field) at a time
CREATE UNIQUE INDEX idx_data_points_current ON data_points(program_id, field_name) WHERE is_current = TRUE;
CREATE INDEX idx_data_points_program ON data_points(program_id);
CREATE INDEX idx_data_points_field ON data_points(field_name);
CREATE INDEX idx_data_points_scraped ON data_points(scraped_at DESC);

-- ============================================================
-- ROI SCORES (computed, versioned)
-- ============================================================

CREATE TABLE roi_scores (
  id                        UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  program_id                UUID NOT NULL REFERENCES programs(id) ON DELETE CASCADE,
  model_version             VARCHAR(32) NOT NULL,
  composite_score           DECIMAL(5,2) NOT NULL CHECK (composite_score BETWEEN 0 AND 100),
  financial_roi_pct         DECIMAL(10,2),
  risk_score                DECIMAL(5,4) CHECK (risk_score BETWEEN 0 AND 1),
  optionality_score         DECIMAL(5,4) CHECK (optionality_score BETWEEN 0 AND 1),
  mobility_score            DECIMAL(5,4) CHECK (mobility_score BETWEEN 0 AND 1),
  satisfaction_score        DECIMAL(5,4) CHECK (satisfaction_score BETWEEN 0 AND 1),
  network_score             DECIMAL(5,4) CHECK (network_score BETWEEN 0 AND 1),
  ci_low                    DECIMAL(5,2),
  ci_high                   DECIMAL(5,2),
  confidence_level          confidence_level NOT NULL DEFAULT 'Medium',
  ppp_factor                DECIMAL(8,4) DEFAULT 23.1,  -- INR per USD PPP
  computed_at               TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  is_current                BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE UNIQUE INDEX idx_roi_scores_current ON roi_scores(program_id) WHERE is_current = TRUE;
CREATE INDEX idx_roi_scores_composite ON roi_scores(composite_score DESC);
CREATE INDEX idx_roi_scores_model ON roi_scores(model_version);

-- ============================================================
-- SALARY TRAJECTORIES
-- ============================================================

CREATE TABLE salary_trajectories (
  id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  program_id      UUID NOT NULL REFERENCES programs(id) ON DELETE CASCADE,
  model_version   VARCHAR(32) NOT NULL,
  year_number     INTEGER NOT NULL CHECK (year_number IN (1, 2, 3, 5, 7, 10, 15, 20)),
  p10_inr         BIGINT,
  p25_inr         BIGINT NOT NULL,
  p50_inr         BIGINT NOT NULL,
  p75_inr         BIGINT NOT NULL,
  p90_inr         BIGINT,
  ppp_usd_p50     DECIMAL(10,2),
  data_source     VARCHAR(128),
  sample_size     INTEGER,
  computed_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  is_current      BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE UNIQUE INDEX idx_salary_traj_current ON salary_trajectories(program_id, year_number) WHERE is_current = TRUE;
CREATE INDEX idx_salary_traj_program ON salary_trajectories(program_id);

-- ============================================================
-- RISK INDICATORS
-- ============================================================

CREATE TABLE risk_indicators (
  id                        UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  program_id                UUID NOT NULL REFERENCES programs(id) ON DELETE CASCADE,
  model_version             VARCHAR(32) NOT NULL,
  ai_automation_prob        DECIMAL(5,4) CHECK (ai_automation_prob BETWEEN 0 AND 1),
  salary_volatility         DECIMAL(5,4),
  industry_cyclicality      DECIMAL(5,4),
  credential_inflation      DECIMAL(5,4),
  geographic_concentration  DECIMAL(5,4),
  regulatory_risk           DECIMAL(5,4),
  physical_health_risk      DECIMAL(5,4),
  work_life_quality         DECIMAL(5,4),
  ai_risk_label             VARCHAR(16),   -- 'Low' | 'Medium' | 'High' | 'Very High'
  computed_at               TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  is_current                BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE UNIQUE INDEX idx_risk_current ON risk_indicators(program_id) WHERE is_current = TRUE;

-- ============================================================
-- PLACEMENT DATA
-- ============================================================

CREATE TABLE placement_data (
  id                    UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  program_id            UUID NOT NULL REFERENCES programs(id) ON DELETE CASCADE,
  academic_year         VARCHAR(16) NOT NULL,   -- '2023-24'
  placement_rate_pct    DECIMAL(5,2),
  highest_salary_inr    BIGINT,
  median_salary_inr     BIGINT,
  average_salary_inr    BIGINT,
  companies_visited     INTEGER,
  ppo_count             INTEGER,
  source                VARCHAR(128),
  scraped_at            TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  is_current            BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE UNIQUE INDEX idx_placement_current ON placement_data(program_id) WHERE is_current = TRUE;
CREATE INDEX idx_placement_program ON placement_data(program_id);
CREATE INDEX idx_placement_year ON placement_data(academic_year);

-- ============================================================
-- COST DATA
-- ============================================================

CREATE TABLE cost_data (
  id                      UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  program_id              UUID NOT NULL REFERENCES programs(id) ON DELETE CASCADE,
  total_tuition_inr       BIGINT,
  hostel_living_inr       BIGINT,
  exam_prep_costs_inr     BIGINT,
  opportunity_cost_inr    BIGINT,
  total_cost_of_degree    BIGINT,
  source_year             INTEGER,
  scraped_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  is_current              BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE UNIQUE INDEX idx_cost_current ON cost_data(program_id) WHERE is_current = TRUE;

-- ============================================================
-- ANOMALY QUEUE
-- ============================================================

CREATE TABLE anomalies (
  id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  program_id          UUID NOT NULL REFERENCES programs(id),
  scrape_run_id       UUID NOT NULL REFERENCES scrape_runs(id),
  field_name          VARCHAR(64) NOT NULL,
  prior_value         TEXT,
  new_value           TEXT NOT NULL,
  delta_pct           DECIMAL(8,2),
  status              anomaly_status NOT NULL DEFAULT 'pending',
  auto_accepted       BOOLEAN NOT NULL DEFAULT FALSE,
  reviewed_by         VARCHAR(128),   -- admin email
  reviewed_at         TIMESTAMPTZ,
  review_notes        TEXT,
  created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_anomalies_status ON anomalies(status);
CREATE INDEX idx_anomalies_program ON anomalies(program_id);
CREATE INDEX idx_anomalies_created ON anomalies(created_at DESC);

-- ============================================================
-- EDUCATOR FEEDBACK
-- ============================================================

CREATE TABLE educator_feedback (
  id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  program_id          UUID REFERENCES programs(id),
  submitter_email     VARCHAR(256),
  submitter_org       VARCHAR(256),
  field_name          VARCHAR(64) NOT NULL,
  old_value           TEXT,
  new_value           TEXT NOT NULL,
  source_url          VARCHAR(1024),
  submitter_confidence VARCHAR(16),  -- 'high' | 'medium' | 'low'
  notes               TEXT,
  status              feedback_status NOT NULL DEFAULT 'pending',
  reviewed_by         VARCHAR(128),
  reviewed_at         TIMESTAMPTZ,
  created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_feedback_status ON educator_feedback(status);
CREATE INDEX idx_feedback_created ON educator_feedback(created_at DESC);

-- ============================================================
-- STUDENT REPORTS (intake wizard results)
-- ============================================================

CREATE TABLE student_reports (
  id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  token           VARCHAR(32) UNIQUE NOT NULL,
  profile_data    JSONB NOT NULL,
  results_data    JSONB,
  model_version   VARCHAR(32),
  generated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  viewed_count    INTEGER DEFAULT 0,
  expires_at      TIMESTAMPTZ DEFAULT NOW() + INTERVAL '90 days'
);

CREATE INDEX idx_student_reports_token ON student_reports(token);
CREATE INDEX idx_student_reports_generated ON student_reports(generated_at DESC);

-- ============================================================
-- MODEL VERSIONS
-- ============================================================

CREATE TABLE model_versions (
  id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  version_tag     VARCHAR(32) UNIQUE NOT NULL,
  is_live         BOOLEAN NOT NULL DEFAULT FALSE,
  trained_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  trigger_type    VARCHAR(64),   -- 'weekly_scrape' | 'manual' | 'feedback_threshold'
  training_records INTEGER,
  mse             DECIMAL(8,4),
  r2_score        DECIMAL(6,4),
  mape_salary     DECIMAL(6,4),
  recall_at_5     DECIMAL(6,4),
  changelog       TEXT,
  model_artifact_path VARCHAR(512)
);

CREATE INDEX idx_model_versions_live ON model_versions(is_live);

-- ============================================================
-- JOB POSTINGS (Naukri scrape)
-- ============================================================

CREATE TABLE job_postings (
  id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  scrape_run_id   UUID NOT NULL REFERENCES scrape_runs(id),
  title           VARCHAR(512) NOT NULL,
  company         VARCHAR(256),
  city            VARCHAR(128),
  state           VARCHAR(64),
  experience_min  INTEGER,
  experience_max  INTEGER,
  salary_min_inr  BIGINT,
  salary_max_inr  BIGINT,
  skills_required TEXT[],
  job_function    VARCHAR(128),
  degree_field    degree_field,
  posted_at       TIMESTAMPTZ,
  scraped_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_job_postings_field ON job_postings(degree_field);
CREATE INDEX idx_job_postings_state ON job_postings(state);
CREATE INDEX idx_job_postings_scraped ON job_postings(scraped_at DESC);

-- ============================================================
-- REDDIT NLP EXTRACTIONS
-- ============================================================

CREATE TABLE reddit_extractions (
  id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  scrape_run_id   UUID NOT NULL REFERENCES scrape_runs(id),
  post_id         VARCHAR(32) UNIQUE NOT NULL,
  subreddit       VARCHAR(64),
  title           TEXT,
  body_snippet    TEXT,
  extracted_salary BIGINT,
  extracted_company VARCHAR(256),
  extracted_role   VARCHAR(256),
  extracted_yoe    INTEGER,   -- years of experience
  degree_field    degree_field,
  nlp_confidence  DECIMAL(4,3),
  post_date       TIMESTAMPTZ,
  scraped_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_reddit_field ON reddit_extractions(degree_field);
CREATE INDEX idx_reddit_scraped ON reddit_extractions(scraped_at DESC);

-- ============================================================
-- TRIGGERS: auto-update updated_at
-- ============================================================

CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER colleges_updated_at BEFORE UPDATE ON colleges
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER programs_updated_at BEFORE UPDATE ON programs
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- ============================================================
-- VIEWS
-- ============================================================

-- Master program view (used by API)
CREATE VIEW v_programs_full AS
SELECT
  p.id AS program_id,
  c.id AS college_id,
  c.short_name AS college_short_name,
  c.full_name AS college_full_name,
  c.state,
  c.city,
  c.tier,
  c.college_type,
  c.nirf_rank,
  d.id AS degree_id,
  d.short_name AS degree_short_name,
  d.full_name AS degree_full_name,
  d.field AS degree_field,
  d.level AS degree_level,
  d.duration_years,
  p.annual_tuition_inr,
  r.composite_score,
  r.financial_roi_pct,
  r.risk_score,
  r.ci_low,
  r.ci_high,
  r.confidence_level,
  r.model_version,
  ri.ai_automation_prob,
  ri.ai_risk_label,
  pl.placement_rate_pct,
  pl.median_salary_inr,
  pl.highest_salary_inr,
  cd.total_cost_of_degree
FROM programs p
JOIN colleges c ON c.id = p.college_id
JOIN degrees d ON d.id = p.degree_id
LEFT JOIN roi_scores r ON r.program_id = p.id AND r.is_current = TRUE
LEFT JOIN risk_indicators ri ON ri.program_id = p.id AND ri.is_current = TRUE
LEFT JOIN placement_data pl ON pl.program_id = p.id AND pl.is_current = TRUE
LEFT JOIN cost_data cd ON cd.program_id = p.id AND cd.is_current = TRUE
WHERE p.is_active = TRUE;

-- Anomaly queue view
CREATE VIEW v_anomaly_queue AS
SELECT
  a.*,
  c.short_name AS college_name,
  d.short_name AS degree_name
FROM anomalies a
JOIN programs p ON p.id = a.program_id
JOIN colleges c ON c.id = p.college_id
JOIN degrees d ON d.id = p.degree_id
WHERE a.status = 'pending'
ORDER BY a.created_at DESC;

-- ============================================================
-- COMMENTS
-- ============================================================

COMMENT ON TABLE data_points IS 'Raw scraped values. Immutable — new scrape creates new row and flips is_current.';
COMMENT ON TABLE anomalies IS 'Auto-flagged when delta > 25% from prior current value. Requires human review before applying.';
COMMENT ON COLUMN roi_scores.ppp_factor IS 'World Bank ICP India-US PPP conversion factor at time of computation.';
