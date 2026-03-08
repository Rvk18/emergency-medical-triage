# RMP Learning (Group C) — Complete runbook

**Purpose:** Finish the first slice of RMP Learning: deploy RMP Quiz agent, wire Gateway (Eka), apply Terraform, and test POST /rmp/learning.

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
   This builds the RMP Learning Lambda and creates POST /rmp/learning.

5. **Test**
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

Expect **200** and JSON with `question`/`reference_answer` (get_question) or `points`/`feedback` (score_answer).

---

## References

- [NEW-MODULE-RMP-AUGMENTATION.md](./NEW-MODULE-RMP-AUGMENTATION.md) §4–6  
- [API-TEST-RESULTS.md](./API-TEST-RESULTS.md) § RMP Learning test  
- [IAM-AGENTCORE-DEPLOY-PERMISSIONS.md](./IAM-AGENTCORE-DEPLOY-PERMISSIONS.md)
