# Aurora migrations

Run in order: **001 → 002 → 003** (and any future 004, 005, …). Use the **migration script** so IAM auth and SSL are correct; see [AURORA-MIGRATIONS-RUNBOOK.md](../../docs/backend/AURORA-MIGRATIONS-RUNBOOK.md) for full details.

## Quick run (recommended)

1. **Start SSH tunnel** to Aurora (in one terminal, leave open):
   ```bash
   cd infrastructure
   AURORA=$(terraform output -raw aurora_cluster_endpoint)
   BASTION=$(terraform output -raw bastion_public_ip)
   ssh -i ~/.ssh/id_ed25519 -N -L 5432:${AURORA}:5432 ec2-user@${BASTION}
   ```
   Use your actual key path (e.g. `~/.ssh/id_rsa` if that's what's in tfvars).

2. **Run migration(s)** in another terminal:
   ```bash
   cd /path/to/AI_Hackathon_Triage
   RDS_HOST_OVERRIDE=127.0.0.1 python3 scripts/run_rmp_learning_migration.py
   ```
   That runs **003** by default. To run a specific file:
   ```bash
   RDS_HOST_OVERRIDE=127.0.0.1 python3 scripts/run_rmp_learning_migration.py infrastructure/migrations/004_my_feature.sql
   ```

**Requirements:** `psycopg2-binary`, AWS credentials with access to Secrets Manager (and RDS for IAM token). The script reads RDS config from Secrets Manager, generates an IAM token for the **real** Aurora host, and connects to `127.0.0.1` (tunnel) with **SSL**.

## Migration files

| File | Purpose |
|------|---------|
| 001_create_triage_assessments.sql | triage_assessments table |
| 002_create_hospital_matches.sql | hospital_matches table |
| 003_rmp_learning.sql | rmp_scores, learning_answers (RMP Learning) |

## Adding a new migration

1. Add `004_description.sql` (or next number) in this directory.
2. Run it with the same script:
   ```bash
   RDS_HOST_OVERRIDE=127.0.0.1 python3 scripts/run_rmp_learning_migration.py infrastructure/migrations/004_description.sql
   ```
3. Update this README and [AURORA-MIGRATIONS-RUNBOOK.md](../../docs/backend/AURORA-MIGRATIONS-RUNBOOK.md) if needed.

## One-time: IAM auth

If the DB user doesn't have IAM auth yet, connect once with **password** (from tfvars) and run:

```sql
GRANT rds_iam TO triagemaster;
```

After that, the migration script (IAM token) works. See [bastion-setup.md](../../docs/infrastructure/bastion-setup.md) for tunnel and psql.
