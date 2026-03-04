# Observability (AC-1, AC-2)

Triage and Hospital Matcher Lambdas emit structured logs for **trace review** and **medical audit**. Use CloudWatch Logs Insights to query by source and duration.

---

## Log fields

| Lambda        | Log message pattern | Use |
|---------------|---------------------|-----|
| **Triage**    | `Triage source=agentcore \| converse \| bedrock_agent duration_ms=...` | Which path ran; latency |
| **Triage**    | `Triage success request_id=... aws_request_id=...` | Correlate assessment with Lambda request |
| **Triage**   | `Persisted triage assessment id=...` | DB row for audit |
| **Hospital Matcher** | `HospitalMatcher source=agentcore \| converse \| bedrock_agent duration_ms=...` | Which path ran; latency |

---

## CloudWatch Logs Insights

**Triage – count by source (last 24h):**
```text
fields @timestamp, @message
| filter @message like /Triage source=/
| parse @message "Triage source=* duration_ms=*" as source, duration_ms
| stats count() by source
```

**Triage – p99 duration (last 24h):**
```text
fields @timestamp, @message
| filter @message like /Triage source=/
| parse @message "Triage source=* duration_ms=*" as source, duration_ms
| stats pct(duration_ms, 99) by source
```

**Trace review (medical audit):** Use `request_id` (UUID) or `aws_request_id` (Lambda request ID) from the success log line to find the same request in other log lines or in Aurora (`triage_assessments.request_id`).

---

## Dashboards

You can create a CloudWatch dashboard with widgets that run the above queries, or use the default Lambda metrics (Invocations, Duration, Errors). For full AgentCore tracing (Runtime spans), use the Bedrock AgentCore console when available.

---

## AC-2 Triage on AgentCore

When `USE_AGENTCORE_TRIAGE=true` and `TRIAGE_AGENT_RUNTIME_ARN` is set, POST /triage uses the AgentCore Runtime triage agent. Logs show `Triage source=agentcore`. Persistence to Aurora is unchanged; `request_id` and assessment `id` remain the primary keys for audit.
