"""Aurora persistence for triage assessments. Uses IAM auth via Secrets Manager."""

import json
import logging
import os
import uuid

import boto3

logger = logging.getLogger(__name__)

RDS_CONFIG_SECRET = os.environ.get(
    "RDS_CONFIG_SECRET",
    "emergency-medical-triage-dev/rds-config",
)


def _get_rds_config() -> dict:
    """Fetch RDS connection config from Secrets Manager."""
    client = boto3.client("secretsmanager", region_name=os.environ.get("AWS_REGION", "us-east-1"))
    response = client.get_secret_value(SecretId=RDS_CONFIG_SECRET)
    return json.loads(response["SecretString"])


def _get_iam_token(host: str, port: int, username: str, region: str) -> str:
    """Generate IAM database auth token."""
    client = boto3.client("rds", region_name=region)
    return client.generate_db_auth_token(
        DBHostname=host,
        Port=port,
        DBUsername=username,
        Region=region,
    )


def insert_triage_assessment(
    *,
    symptoms: list[str],
    vitals: dict,
    age_years: int | None,
    sex: str | None,
    severity: str,
    confidence: float,
    recommendations: list[str],
    force_high_priority: bool,
    safety_disclaimer: str | None,
    request_id: uuid.UUID | None = None,
    bedrock_trace_id: str | None = None,
    model_id: str | None = None,
    submitted_by: str | None = None,
    hospital_match_id: uuid.UUID | None = None,
) -> uuid.UUID:
    """
    Insert a triage assessment into Aurora. Returns the generated id.
    Raises on DB/network errors.
    """
    import psycopg2
    from psycopg2.extras import Json

    config = _get_rds_config()
    host = config["host"]
    port = int(config.get("port", 5432))
    database = config["database"]
    username = config["username"]
    region = config.get("region", os.environ.get("AWS_REGION", "us-east-1"))

    token = _get_iam_token(host, port, username, region)
    row_id = uuid.uuid4()

    conn = psycopg2.connect(
        host=host,
        port=port,
        dbname=database,
        user=username,
        password=token,
        connect_timeout=15,
    )
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO triage_assessments (
                  id, symptoms, vitals, age_years, sex,
                  severity, confidence, recommendations, force_high_priority, safety_disclaimer,
                  request_id, bedrock_trace_id, model_id, submitted_by, hospital_match_id
                ) VALUES (
                  %s, %s, %s, %s, %s,
                  %s, %s, %s, %s, %s,
                  %s, %s, %s, %s, %s
                )
                """,
                (
                    str(row_id),
                    symptoms,
                    Json(vitals) if vitals else Json({}),
                    age_years,
                    sex,
                    severity,
                    confidence,
                    recommendations,
                    force_high_priority,
                    safety_disclaimer,
                    str(request_id) if request_id else None,
                    bedrock_trace_id,
                    model_id,
                    submitted_by,
                    str(hospital_match_id) if hospital_match_id else None,
                ),
            )
        conn.commit()
    finally:
        conn.close()

    return row_id
