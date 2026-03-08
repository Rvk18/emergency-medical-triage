"""Aurora persistence for RMP Learning: scores and answer history. Uses IAM auth."""

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


def _conn():
    """Open a connection to Aurora. Caller must close."""
    import psycopg2

    config = _get_rds_config()
    host = config["host"]
    port = int(config.get("port", 5432))
    database = config["database"]
    username = config["username"]
    region = config.get("region", os.environ.get("AWS_REGION", "us-east-1"))
    token = _get_iam_token(host, port, username, region)
    return psycopg2.connect(
        host=host,
        port=port,
        dbname=database,
        user=username,
        password=token,
        connect_timeout=15,
    )


def upsert_rmp_score(rmp_id: str, add_points: int) -> int:
    """
    Add points to an RMP's total. Inserts row if not exists.
    Returns the new total_points.
    """
    import psycopg2

    conn = _conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO rmp_scores (rmp_id, total_points, updated_at)
                VALUES (%s, %s, now())
                ON CONFLICT (rmp_id) DO UPDATE SET
                  total_points = rmp_scores.total_points + EXCLUDED.total_points,
                  updated_at = now()
                RETURNING total_points
                """,
                (rmp_id, max(0, add_points)),
            )
            row = cur.fetchone()
        conn.commit()
        return row[0] if row else 0
    finally:
        conn.close()


def insert_learning_answer(
    rmp_id: str,
    question_ref: str | None,
    user_answer: str | None,
    points: int,
) -> uuid.UUID:
    """Record one quiz answer. Returns the new row id."""
    import psycopg2

    row_id = uuid.uuid4()
    conn = _conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO learning_answers (id, rmp_id, question_ref, user_answer, points)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (str(row_id), rmp_id, (question_ref or "")[:2000], (user_answer or "")[:5000], max(0, min(10, points))),
            )
        conn.commit()
    finally:
        conn.close()
    return row_id


def get_leaderboard(limit: int = 20) -> list[dict]:
    """Return top RMPs by total_points. Each item: { rmp_id, total_points, rank }."""
    import psycopg2

    conn = _conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT rmp_id, total_points,
                       ROW_NUMBER() OVER (ORDER BY total_points DESC, updated_at DESC) AS rank
                FROM rmp_scores
                ORDER BY total_points DESC, updated_at DESC
                LIMIT %s
                """,
                (max(1, min(100, limit)),),
            )
            rows = cur.fetchall()
        return [
            {"rmp_id": r[0], "total_points": r[1], "rank": r[2]}
            for r in rows
        ]
    finally:
        conn.close()


def get_my_score(rmp_id: str) -> dict | None:
    """
    Return current user's score and rank. Keys: total_points, rank.
    rank is 1-based; null if not in table.
    """
    import psycopg2

    conn = _conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT total_points FROM rmp_scores WHERE rmp_id = %s",
                (rmp_id,),
            )
            row = cur.fetchone()
        if not row:
            return {"total_points": 0, "rank": None}
        total = row[0]
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT COUNT(*) + 1 FROM rmp_scores
                WHERE total_points > %s
                """,
                (total,),
            )
            rank_row = cur.fetchone()
        rank = rank_row[0] if rank_row else None
        return {"total_points": total, "rank": rank}
    finally:
        conn.close()
