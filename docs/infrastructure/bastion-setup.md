# Bastion Host + SSH Tunnel to Aurora

Steps to access Aurora from your laptop using a bastion host.

---

## 1. Get your public IP

```bash
curl -s ifconfig.me
# Example: 203.0.113.42 → use 203.0.113.42/32
```

---

## 2. Add bastion variables to terraform.tfvars

Edit `infrastructure/terraform.tfvars`:

```hcl
enable_bastion         = true
bastion_ssh_public_key = "ssh-rsa AAAA... your-key-content"   # from ~/.ssh/id_rsa.pub
bastion_allowed_cidr   = "YOUR_IP/32"                         # e.g. 203.0.113.42/32
```

**Get your SSH public key:**
```bash
cat ~/.ssh/id_rsa.pub
```

---

## 3. Apply Terraform

```bash
cd infrastructure
terraform apply
```

After apply, note the output:
```
bastion_public_ip = "54.x.x.x"
aurora_cluster_endpoint = "emergency-medical-triage-dev-aurora-cluster.cluster-xxx.us-east-1.rds.amazonaws.com"
```

---

## 4. Start SSH tunnel

Replace `BASTION_IP` and `AURORA_ENDPOINT` with values from `terraform output`:

```bash
ssh -i ~/.ssh/id_rsa -N -L 5432:AURORA_ENDPOINT:5432 ec2-user@BASTION_IP
```

**Example:**
```bash
ssh -i ~/.ssh/id_rsa -N -L 5432:emergency-medical-triage-dev-aurora-cluster.cluster-cub0km86ov53.us-east-1.rds.amazonaws.com:5432 ec2-user@54.123.45.67
```

Keep this terminal open. The tunnel forwards local port 5432 to Aurora.

---

## 5. Run RDS test or migrations (in another terminal)

Override the RDS config to use localhost (tunnel):

```bash
# For migrations, use the script (IAM auth + SSL). Tunnel must be running.
RDS_HOST_OVERRIDE=127.0.0.1 python3 scripts/run_rmp_learning_migration.py
# See: docs/backend/AURORA-MIGRATIONS-RUNBOOK.md and infrastructure/migrations/README.md
```

**Option A – Use psql (password auth):**
```bash
psql -h 127.0.0.1 -p 5432 -U triagemaster -d triagedb
# Password: your db_password from terraform.tfvars
```

**Option B – Run the RDS test through the tunnel:**

With the tunnel running, in another terminal:
```bash
RDS_HOST_OVERRIDE=127.0.0.1 pytest tests/test_rds.py -v
```

---

## 6. One-time: grant IAM auth (if using IAM token)

Connect with password first and run:

```sql
GRANT rds_iam TO triagemaster;
```

---

## Summary

| Step | Command |
|------|---------|
| 1. Get IP | `curl -s ifconfig.me` → `x.x.x.x/32` |
| 2. Add to tfvars | `enable_bastion`, `bastion_ssh_public_key`, `bastion_allowed_cidr` |
| 3. Apply | `terraform apply` |
| 4. Tunnel | `ssh -i ~/.ssh/id_rsa -N -L 5432:AURORA_ENDPOINT:5432 ec2-user@BASTION_IP` |
| 5. Connect / migrations | `psql -h 127.0.0.1 -p 5432 -U triagemaster -d triagedb` (password), or `RDS_HOST_OVERRIDE=127.0.0.1 python3 scripts/run_rmp_learning_migration.py` for migrations. See [AURORA-MIGRATIONS-RUNBOOK.md](../backend/AURORA-MIGRATIONS-RUNBOOK.md). |
