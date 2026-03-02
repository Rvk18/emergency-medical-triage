-- Phase 2: triage_assessments table
-- Append-only triage records. No updated_at (rows are immutable).
-- Soft delete via deleted_at. submitted_by = rmp_id / user reference.

CREATE TABLE IF NOT EXISTS triage_assessments (
  id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  created_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
  deleted_at        TIMESTAMPTZ,

  -- Input
  symptoms          TEXT[] NOT NULL,
  vitals            JSONB DEFAULT '{}',
  age_years         INT,
  sex               VARCHAR(16),

  -- Output
  severity          VARCHAR(16) NOT NULL,
  confidence        FLOAT NOT NULL CHECK (confidence >= 0 AND confidence <= 1),
  recommendations   TEXT[] DEFAULT '{}',
  force_high_priority BOOLEAN NOT NULL DEFAULT false,
  safety_disclaimer TEXT,

  -- Audit
  request_id        UUID,
  bedrock_trace_id  VARCHAR(256),
  model_id          VARCHAR(128),

  -- Context
  submitted_by      VARCHAR(256),
  hospital_match_id UUID
);

CREATE INDEX IF NOT EXISTS idx_triage_assessments_created_at ON triage_assessments (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_triage_assessments_submitted_by ON triage_assessments (submitted_by) WHERE submitted_by IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_triage_assessments_deleted_at ON triage_assessments (deleted_at) WHERE deleted_at IS NULL;
CREATE INDEX IF NOT EXISTS idx_triage_assessments_hospital_match ON triage_assessments (hospital_match_id) WHERE hospital_match_id IS NOT NULL;
