# IAM permissions for AgentCore deploy (e.g. RMP Quiz agent)

When `agentcore deploy --agent rmp_quiz_agent` fails with:

```text
AccessDeniedException: User: arn:aws:iam::ACCOUNT:user/USERNAME is not authorized to perform: bedrock-agentcore:UpdateAgentRuntime
```

the IAM user or role you use for the CLI is missing Bedrock AgentCore **Control Plane** permissions.

---

## Option 1: Attach the AWS managed policy (simplest)

Attach the managed policy **BedrockAgentCoreFullAccess** to the IAM user (e.g. `Tamerofgamers`) or role you use when running `agentcore deploy`:

- **Policy ARN:** `arn:aws:iam::aws:policy/BedrockAgentCoreFullAccess`
- **Scope:** Full access to Bedrock AgentCore (Control Plane, runtimes, gateways, etc.). Suitable for development; for production consider Option 2.

**In AWS Console:**

1. IAM → Users → select your user (e.g. Tamerofgamers) → **Add permissions** → **Attach policies directly**.
2. Search for **BedrockAgentCoreFullAccess**, select it, then **Add permissions**.

**AWS CLI:**

```bash
aws iam attach-user-policy \
  --user-name Tamerofgamers \
  --policy-arn arn:aws:iam::aws:policy/BedrockAgentCoreFullAccess
```

Replace `Tamerofgamers` with your IAM user name. If you use an IAM role instead of a user, use `aws iam attach-role-policy --role-name ROLE_NAME --policy-arn arn:aws:iam::aws:policy/BedrockAgentCoreFullAccess`.

---

## Option 2: Minimal custom policy (least privilege for deploy)

If you prefer to grant only the actions needed for `agentcore deploy` (create/update runtime and memory), attach an inline or customer-managed policy with the following. The deploy flow uses the **Control Plane** API (service name `bedrock-agentcore-control`); actions are in the `bedrock-agentcore` namespace.

**Minimal policy for deploy (create/update runtimes and memory):**

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AgentCoreControlPlaneDeploy",
      "Effect": "Allow",
      "Action": [
        "bedrock-agentcore:CreateAgentRuntime",
        "bedrock-agentcore:UpdateAgentRuntime",
        "bedrock-agentcore:GetAgentRuntime",
        "bedrock-agentcore:CreateMemory",
        "bedrock-agentcore:GetMemory",
        "bedrock-agentcore:UpdateMemory"
      ],
      "Resource": "arn:aws:bedrock-agentcore:*:*:*"
    }
  ]
}
```

- **CreateAgentRuntime / UpdateAgentRuntime:** Required to create or update the RMP Quiz runtime (the call that failed was **UpdateAgentRuntime**).
- **GetAgentRuntime:** Used by the CLI to read current runtime config before update.
- **CreateMemory / GetMemory / UpdateMemory:** Used when the toolkit creates or uses an STM-only memory for the agent.

**Important:** The starter toolkit also needs IAM, CodeBuild, S3, ECR, and related permissions to build and upload the deployment package. If your user already deploys other AgentCore agents (e.g. hospital_matcher_agent, triage_agent), you likely have those; the only missing permission was **UpdateAgentRuntime**. In that case, a **minimal add-on** is:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AgentCoreUpdateRuntime",
      "Effect": "Allow",
      "Action": [
        "bedrock-agentcore:UpdateAgentRuntime",
        "bedrock-agentcore:GetAgentRuntime"
      ],
      "Resource": "arn:aws:bedrock-agentcore:*:*:*"
    }
  ]
}
```

Add this as an inline policy on the user, or create a customer-managed policy and attach it.

**Console:** IAM → Users → your user → **Add permissions** → **Create inline policy** → JSON → paste one of the JSON policies above → **Review policy** → name it (e.g. `AgentCoreDeploy`) → **Create policy**.

---

## After adding permissions

1. Run again: `cd agentcore/agent && agentcore deploy --agent rmp_quiz_agent`.
2. Copy the runtime ARN from the output into `infrastructure/terraform.tfvars`:  
   `rmp_quiz_agent_runtime_arn = "arn:aws:bedrock-agentcore:us-east-1:ACCOUNT:runtime/rmp_quiz_agent-xxx"`.
3. Run `python3 scripts/enable_gateway_on_rmp_quiz_runtime.py`, then `cd infrastructure && terraform apply`.
4. Test POST /rmp/learning (see [API-TEST-RESULTS.md](./API-TEST-RESULTS.md) § RMP Learning).

---

## References

- [IAM permissions for AgentCore Runtime](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-permissions.html) — starter toolkit and execution role
- [BedrockAgentCoreFullAccess](https://docs.aws.amazon.com/aws-managed-policy/latest/reference/BedrockAgentCoreFullAccess.html) — AWS managed policy
- [UpdateAgentRuntime](https://docs.aws.amazon.com/bedrock-agentcore-control/latest/APIReference/API_UpdateAgentRuntime.html) — Control Plane API
