-- Phase 4: hospital_matches table (matches triage_assessments.hospital_match_id)

CREATE TABLE IF NOT EXISTS hospital_matches (
  id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
  triage_assessment_id UUID REFERENCES triage_assessments(id),
  hospitals           JSONB NOT NULL DEFAULT '[]',
  safety_disclaimer   TEXT
);

CREATE INDEX IF NOT EXISTS idx_hospital_matches_triage ON hospital_matches (triage_assessment_id);
