# RMP Learning (Group C) — Complete runbook

**Purpose:** Deploy and operate RMP Learning: RMP Quiz agent, Gateway (Eka), Terraform (Lambda + Aurora), POST /rmp/learning (get_question, score_answer), GET /rmp/learning/me, GET /rmp/learning/leaderboard. Frontend contract: [RMP-LEARNING-API.md](../frontend/RMP-LEARNING-API.md).

---

## Blocker: IAM

Deploy fails with:
```text
User arn:aws:iam::ACCOUNT:user/YOUR_USER is not authorized to perform: bedrock-agentcore:UpdateAgentRuntime
```

**Fix:** Attach **BedrockAgentCoreFullAccess** (or a custom policy with `bedrock-agentcore:UpdateAgentRuntime` and `bedrock-agentcore:CreateAgentRuntime`) to the **IAM user or role** used when running `agentcore deploy`. Verify with:

```bash
aws sts get-caller-identity
```

Then attach the policy to that principal in IAM Console. If you just attached it, try a new terminal or `aws configure` / refresh credentials and run deploy again.

### If the policy is attached but UpdateAgentRuntime still returns AccessDenied

1. **Run deploy outside Cursor**  
   In a normal terminal (not Cursor’s): `aws sts get-caller-identity` then `cd agentcore/agent && agentcore deploy --agent rmp_quiz_agent`. This rules out Cursor/sandbox using different credentials.

2. **IAM Policy Simulator**  
   IAM Console → **Policy simulator** → run as user **Tamerofgamers**, action `bedrock-agentcore:UpdateAgentRuntime`, resource `*`. Check whether the result is “allowed” or “implicitDeny”/“explicitDeny”.

3. **Organization SCPs**  
   If the account is in AWS Organizations, check **Service Control Policies** on the account or OU; an SCP can deny `bedrock-agentcore:*` even when the user has the managed policy.

4. **Explicit allow**  
   Add an **inline policy** on user Tamerofgamers with:
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [{
       "Effect": "Allow",
       "Action": [
         "bedrock-agentcore:CreateAgentRuntime",
         "bedrock-agentcore:UpdateAgentRuntime"
       ],
       "Resource": "*"
     }]
   }
   ```
   Then run deploy again. If it still fails, the deny is likely from an SCP or permission boundary.

---

## Steps (after IAM is fixed)

1. **Deploy RMP Quiz agent**
   ```bash
   cd agentcore/agent && agentcore deploy --agent rmp_quiz_agent
   ```
   Copy the **runtime ARN** from the output (e.g. `arn:aws:bedrock-agentcore:us-east-1:ACCOUNT:runtime/rmp_quiz_agent-xxxxx`).

2. **Set ARN in Terraform**
   Edit `infrastructure/terraform.tfvars`: uncomment and set:
   ```hcl
   rmp_quiz_agent_runtime_arn = "arn:aws:bedrock-agentcore:us-east-1:ACCOUNT:runtime/rmp_quiz_agent-xxxxx"
   ```
   (Use the ARN from step 1.)

3. **Enable Eka on quiz runtime**
   From project root:
   ```bash
   python3 scripts/enable_gateway_on_rmp_quiz_runtime.py
   ```

4. **Apply Terraform**
   ```bash
   cd infrastructure && terraform apply
   ```
   This builds the RMP Learning Lambda (with VPC and RDS access), creates POST /rmp/learning, GET /rmp/learning/me, GET /rmp/learning/leaderboard.

5. **Run Aurora migration 003** (for leaderboard and “my score”)

   With an **SSH tunnel** to Aurora running (see [AURORA-MIGRATIONS-RUNBOOK.md](./AURORA-MIGRATIONS-RUNBOOK.md)):
   ```bash
   RDS_HOST_OVERRIDE=127.0.0.1 python3 scripts/run_rmp_learning_migration.py
   ```
   Without this, GET /rmp/learning/me and GET /rmp/learning/leaderboard return 500. For full migration steps (tunnel, IAM token, SSL), see [AURORA-MIGRATIONS-RUNBOOK.md](./AURORA-MIGRATIONS-RUNBOOK.md) and [infrastructure/migrations/README.md](../../infrastructure/migrations/README.md).

6. **Test**
   ```bash
   eval $(python3 scripts/load_api_config.py --exports)
   export RMP_TOKEN=$(python3 scripts/get_rmp_token.py)
   ```
   - Get question:
     ```bash
     curl -s -X POST "$API_URL/rmp/learning" -H "Content-Type: application/json" -H "Authorization: Bearer $RMP_TOKEN" -d '{"action":"get_question","topic":"fever protocol"}'
     ```
   - Score answer (use `question` and `reference_answer` from the get_question response):
     ```bash
     curl -s -X POST "$API_URL/rmp/learning" -H "Content-Type: application/json" -H "Authorization: Bearer $RMP_TOKEN" -d '{"action":"score_answer","question":"...","reference_answer":"...","user_answer":"Monitor temperature and give paracetamol"}'
     ```
   - My score:
     ```bash
     curl -s "$API_URL/rmp/learning/me" -H "Authorization: Bearer $RMP_TOKEN"
     ```
   - Leaderboard:
     ```bash
     curl -s "$API_URL/rmp/learning/leaderboard?limit=10" -H "Authorization: Bearer $RMP_TOKEN"
     ```

Expect **200** and JSON: get_question → `question`/`reference_answer`; score_answer → `points`/`feedback`; me → `total_points`/`rank`; leaderboard → `leaderboard` array.

---

## References

- [NEW-MODULE-RMP-AUGMENTATION.md](./NEW-MODULE-RMP-AUGMENTATION.md) §4–6  
- [API-TEST-RESULTS.md](./API-TEST-RESULTS.md) § RMP Learning test  
- [RMP-LEARNING-API.md](../frontend/RMP-LEARNING-API.md) – Frontend integration contract  
- [IAM-AGENTCORE-DEPLOY-PERMISSIONS.md](./IAM-AGENTCORE-DEPLOY-PERMISSIONS.md)  
- [AURORA-MIGRATIONS-RUNBOOK.md](./AURORA-MIGRATIONS-RUNBOOK.md) – Run any Aurora migration (tunnel, script, IAM + SSL)
- [infrastructure/migrations/README.md](../../infrastructure/migrations/README.md) – Aurora migration 003
