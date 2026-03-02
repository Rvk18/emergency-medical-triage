# Aurora migrations

Run in order: 001 → 002.

```bash
psql -h HOST -p PORT -U triagemaster -d triagedb -f 001_create_triage_assessments.sql
psql -h HOST -p PORT -U triagemaster -d triagedb -f 002_create_hospital_matches.sql
```

Or use RDS Data API (see implementation-history.md).

One-time: `GRANT rds_iam TO triagemaster;`
