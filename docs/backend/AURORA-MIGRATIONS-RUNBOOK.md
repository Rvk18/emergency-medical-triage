# Aurora migrations runbook

**Purpose:** Run schema migrations on Aurora PostgreSQL (triagedb) without wasting time on connection/auth issues. Use this whenever you add or change tables.

**Script:** `scripts/run_rmp_learning_migration.py` — works for **any** migration (001, 002, 003, or a new 004_xxx.sql). Uses IAM auth and SSL.

---

## Why the script (and not raw psql)

- **Aurora is in a private VPC.** From your laptop you must connect via an **SSH tunnel** (bastion → Aurora). You connect to `127.0.0.1:5432`; the tunnel forwards to the cluster.
- **IAM token must be for the real host.** `generate_db_auth_token(DBHostname=...)` must use the **Aurora cluster endpoint** (e.g. `xxx.cluster-xxx.rds.amazonaws.com`), not `127.0.0.1`. The script reads the real host from Secrets Manager and generates the token for it, then connects to `RDS_HOST_OVERRIDE` (127.0.0.1 when using the tunnel).
- **Aurora requires SSL.** Connections without encryption are rejected (`pg_hba.conf rejects connection ... no encryption`). The script uses `sslmode="require"`.

If you use raw `psql` with a tunnel, you must still use the IAM token (generated for the real host) and SSL; the script does that for you.

---

## Step 1: Start the SSH tunnel

In a terminal, leave this running:

```bash
cd infrastructure
AURORA=$(terraform output -raw aurora_cluster_endpoint)
BASTION=$(terraform output -raw bastion_public_ip)
ssh -i ~/.ssh/id_ed25519 -N -L 5432:${AURORA}:5432 ec2-user@${BASTION}
```

- Use the key that matches `bastion_ssh_public_key` in your tfvars (e.g. `~/.ssh/id_ed25519` or `~/.ssh/id_rsa`).
- No output is normal; the session is just holding the tunnel open.

---

## Step 2: Run the migration

In **another** terminal:

```bash
cd /path/to/AI_Hackathon_Triage
RDS_HOST_OVERRIDE=127.0.0.1 python3 scripts/run_rmp_learning_migration.py
```

That runs the **default** migration (003_rmp_learning.sql). To run a specific file:

```bash
RDS_HOST_OVERRIDE=127.0.0.1 python3 scripts/run_rmp_learning_migration.py infrastructure/migrations/004_my_new_tables.sql
```

You should see: `Migration applied: 003_rmp_learning.sql` (or the file you passed).

**Requirements:**

- `pip install psycopg2-binary`
- AWS credentials that can read the RDS config secret and call `rds:GenerateDBAuthToken`
- Tunnel from step 1 must be up

---

## Adding a new migration (new tables / schema change)

1. **Create the SQL file** in `infrastructure/migrations/`:
   - Name: `004_short_description.sql` (next number, descriptive suffix).
   - Use `CREATE TABLE IF NOT EXISTS`, `CREATE INDEX IF NOT EXISTS`, etc., so re-running is safe.

2. **Run it** (with tunnel up):
   ```bash
   RDS_HOST_OVERRIDE=127.0.0.1 python3 scripts/run_rmp_learning_migration.py infrastructure/migrations/004_short_description.sql
   ```

3. **Update docs:** Add the file to the table in [infrastructure/migrations/README.md](../../infrastructure/migrations/README.md). Optionally note it here or in the feature doc.

No need to change the script for a new migration; it accepts any `.sql` path as the first argument.

---

## Troubleshooting

| Error | Cause | Fix |
|-------|--------|-----|
| `Connection refused` to 127.0.0.1:5432 | Tunnel not running or wrong port | Start the SSH tunnel (step 1); leave that terminal open. |
| `pg_hba.conf rejects connection ... no encryption` | Client connected without SSL | Script uses `sslmode="require"`; ensure you’re using the script, not raw psql without SSL. |
| `PAM authentication failed` | IAM token was generated for 127.0.0.1 | Script must generate the token for the **real** Aurora host (from Secrets Manager). Fixed in current script. |
| `Identity file ... not accessible` | Wrong SSH key path | Use `-i ~/.ssh/id_ed25519` (or the key that matches your tfvars). |
| `Migration file not found` | Wrong path or cwd | Pass absolute path or path relative to repo root; or run from repo root without args for default 003. |

---

## References

- [infrastructure/migrations/README.md](../../infrastructure/migrations/README.md) – Migration list and quick commands
- [docs/infrastructure/bastion-setup.md](../infrastructure/bastion-setup.md) – Bastion and tunnel setup
- [implementation-history.md](./implementation-history.md) – RDS Data API, IAM auth notes
