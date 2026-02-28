"""
RDS Aurora connectivity test using IAM auth and Secrets Manager.

- Connection config from Secrets Manager (host, port, database, username) — no password stored.
- Auth via boto3 generate_db_auth_token (managed identity / IAM credentials).
- Run from project root: pytest tests/test_rds.py -v

Requires:
- Terraform applied with rds-config secret and IAM DB auth enabled.
- One-time: connect with password and run: GRANT rds_iam TO triagemaster;
- Network access to Aurora (VPC/bastion) — test will skip if unreachable.
"""

import json
import os

import boto3
import pytest

RDS_CONFIG_SECRET = os.environ.get(
    "RDS_CONFIG_SECRET",
    "emergency-medical-triage-dev/rds-config",
)


def _get_rds_config() -> dict:
    """Fetch RDS connection config from Secrets Manager. No password."""
    client = boto3.client("secretsmanager")
    try:
        response = client.get_secret_value(SecretId=RDS_CONFIG_SECRET)
    except client.exceptions.ResourceNotFoundException:
        pytest.skip(
            f"Secret {RDS_CONFIG_SECRET} not found. Run: cd infrastructure && terraform apply"
        )
    return json.loads(response["SecretString"])


def _get_iam_token(host: str, port: int, username: str, region: str) -> str:
    """Generate IAM database auth token using default credentials (managed identity)."""
    client = boto3.client("rds", region_name=region)
    return client.generate_db_auth_token(
        DBHostname=host,
        Port=port,
        DBUsername=username,
        Region=region,
    )


def test_rds_iam_connect():
    """Connect to Aurora via IAM auth using config from Secrets Manager."""
    config = _get_rds_config()
    # Use 127.0.0.1 when SSH tunnel is active: ssh -L LOCAL_PORT:AURORA_ENDPOINT:5432 ec2-user@BASTION_IP
    host = os.environ.get("RDS_HOST_OVERRIDE", config["host"])
    port = int(os.environ.get("RDS_PORT_OVERRIDE", config["port"]))
    database = config["database"]
    username = config["username"]
    region = config["region"]
    # Token must be generated for real Aurora host, not 127.0.0.1
    token = _get_iam_token(config["host"], port, username, region)

    try:
        import psycopg2

        conn = psycopg2.connect(
            host=host,
            port=port,
            dbname=database,
            user=username,
            password=token,
            connect_timeout=15,
        )
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute("SELECT 1")
        row = cur.fetchone()
        cur.close()
        conn.close()
        assert row == (1,)
    except ImportError:
        pytest.skip("psycopg2 not installed")
    except Exception as e:
        err = str(e).lower()
        if "could not connect" in err or "timeout" in err or "connection refused" in err:
            pytest.skip(
                f"Aurora unreachable (host={host}). "
                "Ensure SSH tunnel is running and RDS_HOST_OVERRIDE=127.0.0.1. Error: " + str(e)
            )
        if "password authentication failed" in err or "rds_iam" in err:
            pytest.fail(
                "IAM auth failed. Run once with password: GRANT rds_iam TO triagemaster;"
            )
        raise
