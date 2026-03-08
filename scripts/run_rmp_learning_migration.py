#!/usr/bin/env python3
"""
Run an Aurora PostgreSQL migration (IAM auth). Use for 001, 002, 003, or any new migration.

Aurora is in a private VPC, so from your machine you must use an SSH tunnel, then connect
to 127.0.0.1. The IAM token must be generated for the real cluster hostname (from Secrets
Manager), not 127.0.0.1. Connection requires SSL (sslmode=require).

Usage:
  1. Start tunnel (leave running):
       cd infrastructure
       AURORA=$(terraform output -raw aurora_cluster_endpoint)
       BASTION=$(terraform output -raw bastion_public_ip)
       ssh -i ~/.ssh/id_ed25519 -N -L 5432:${AURORA}:5432 ec2-user@${BASTION}
  2. In another terminal:
       RDS_HOST_OVERRIDE=127.0.0.1 python3 scripts/run_aurora_migration.py [path/to/migration.sql]
     Default migration: infrastructure/migrations/003_rmp_learning.sql

See: infrastructure/migrations/README.md and docs/backend/AURORA-MIGRATIONS-RUNBOOK.md
"""
from __future__ import annotations

import json
import os
import sys

import boto3

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
DEFAULT_MIGRATION = os.path.join(REPO_ROOT, "infrastructure", "migrations", "003_rmp_learning.sql")

RDS_CONFIG_SECRET = os.environ.get("RDS_CONFIG_SECRET", "emergency-medical-triage-dev/rds-config")
REGION = os.environ.get("AWS_REGION", "us-east-1")


def get_rds_config() -> dict:
    client = boto3.client("secretsmanager", region_name=REGION)
    resp = client.get_secret_value(SecretId=RDS_CONFIG_SECRET)
    return json.loads(resp["SecretString"])


def get_iam_token(host: str, port: int, username: str) -> str:
    client = boto3.client("rds", region_name=REGION)
    return client.generate_db_auth_token(
        DBHostname=host,
        Port=port,
        DBUsername=username,
        Region=REGION,
    )


def main() -> int:
    if len(sys.argv) > 1:
        migration_sql = os.path.abspath(sys.argv[1].strip())
    else:
        migration_sql = DEFAULT_MIGRATION

    override = os.environ.get("RDS_HOST_OVERRIDE", "").strip()
    config = get_rds_config()
    connect_host = override or config["host"]
    aurora_host = config["host"]  # Token must be for the real cluster endpoint, not 127.0.0.1
    port = int(config.get("port", 5432))
    database = config["database"]
    username = config["username"]

    if not os.path.isfile(migration_sql):
        print(f"Migration file not found: {migration_sql}", file=sys.stderr)
        return 1

    sql = open(migration_sql).read()
    token = get_iam_token(aurora_host, port, username)

    try:
        import psycopg2
    except ImportError:
        print("Install psycopg2-binary: pip install psycopg2-binary", file=sys.stderr)
        return 1

    try:
        conn = psycopg2.connect(
            host=connect_host,
            port=port,
            dbname=database,
            user=username,
            password=token,
            connect_timeout=15,
            sslmode="require",
        )
    except Exception as e:
        print(f"Connection failed to {connect_host}:{port}. If Aurora is in a VPC, start an SSH tunnel and set RDS_HOST_OVERRIDE=127.0.0.1", file=sys.stderr)
        print(f"Error: {e}", file=sys.stderr)
        return 1

    try:
        with conn.cursor() as cur:
            cur.execute(sql)
        conn.commit()
        print(f"Migration applied: {os.path.basename(migration_sql)}")
    except Exception as e:
        print(f"Migration failed: {e}", file=sys.stderr)
        conn.rollback()
        return 1
    finally:
        conn.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
