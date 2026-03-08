-- RMP Learning: scores and answer history for Eka quiz gamification.
-- rmp_id = Cognito sub (submitted_by / RMP identifier).

CREATE TABLE IF NOT EXISTS rmp_scores (
  rmp_id       VARCHAR(256) PRIMARY KEY,
  total_points INT NOT NULL DEFAULT 0 CHECK (total_points >= 0),
  updated_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS learning_answers (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  rmp_id      VARCHAR(256) NOT NULL,
  question_ref TEXT,
  user_answer TEXT,
  points      INT NOT NULL CHECK (points >= 0 AND points <= 10),
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_learning_answers_rmp_id ON learning_answers (rmp_id);
CREATE INDEX IF NOT EXISTS idx_learning_answers_created_at ON learning_answers (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_rmp_scores_total_points ON rmp_scores (total_points DESC, updated_at DESC);
