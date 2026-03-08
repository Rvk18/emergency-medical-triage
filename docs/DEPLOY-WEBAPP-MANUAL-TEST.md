# Deploy Webapp and Manual Test

**Purpose:** One path to deploy the webapp (S3 + CloudFront) and run a manual test with real login (Cognito) and API (triage, hospitals).

---

## How login and Cognito are handled

| Item | How it's handled |
|------|------------------|
| **User Pool + App Client** | Created by Terraform (`infrastructure/cognito.tf`). After `terraform apply` you get `cognito_user_pool_id` and `cognito_app_client_id` from outputs (and in `api_config` secret). |
| **Test user (email + password)** | **Not** created by Terraform. You create it once via script or AWS Console. Use that email/password in the webapp login form. |
| **Webapp config** | At **build time**, Vite reads `VITE_COGNITO_USER_POOL_ID`, `VITE_COGNITO_CLIENT_ID`, `VITE_COGNITO_REGION` and `VITE_API_URL` from `.env` and bakes them into the app. So you need a `.env` (or env vars) when running `npm run build`. |
| **Optional: get_rmp_token.py** | If you set `rmp_test_email` and `rmp_test_password` in `terraform.tfvars`, Terraform stores them in Secrets Manager. That same user can be used for web login; create the user in Cognito first (script below), then add those vars and apply so scripts can get a token. |

So: **Cognito pool and client exist after Terraform. You add one test user (script or Console), put pool/client IDs and API URL in `.env`, build, deploy, then log in with that user.**

---

## Prerequisites

- AWS CLI configured (`aws sts get-caller-identity` works).
- Terraform and Node/npm installed.
- From repo root.

---

## Step 1: Terraform apply

```bash
cd infrastructure
terraform init   # if not already
terraform apply  # accept prompts, or use -var-file=terraform.tfvars
```

Then get outputs (use these in the next steps):

```bash
terraform output api_gateway_url
terraform output cognito_user_pool_id
terraform output cognito_app_client_id
terraform output web_app_bucket_name
terraform output web_app_url
```

If `web_app_bucket_name` or `web_app_url` are missing, ensure `web_hosting.tf` is present and run `terraform apply` again.

---

## Step 2: Create a Cognito test user

**Option A – Script (recommended)**

From repo root:

```bash
python3 scripts/create_cognito_test_user.py \
  --email your-test@example.com \
  --password 'YourSecurePass1!'
```

Use an email you control and a password that meets the pool policy (10+ chars, upper, lower, number, symbol). The script creates the user and sets the password so you can log in immediately (no “change password” step).

**Option B – AWS Console**

1. AWS Console → Cognito → User Pools → your pool (`emergency-medical-triage-dev-rmp-users` or similar).
2. Users → Create user.
3. Username: email (e.g. `test@example.com`).
4. Temporary password: set one that meets the policy.
5. Send email invitation or leave unchecked. Create.
6. For a permanent password without “change on first login,” use CLI:  
   `aws cognito-idp admin-set-user-password --user-pool-id <POOL_ID> --username test@example.com --password 'YourSecurePass1!' --permanent`

**Option C – CLI only**

```bash
POOL_ID=$(terraform -chdir=infrastructure output -raw cognito_user_pool_id)
aws cognito-idp admin-create-user \
  --user-pool-id "$POOL_ID" \
  --username test@example.com \
  --user-attributes Name=email,Value=test@example.com Name=email_verified,Value=true \
  --temporary-password 'TempPass1!ChangeMe' \
  --message-action SUPPRESS
aws cognito-idp admin-set-user-password \
  --user-pool-id "$POOL_ID" \
  --username test@example.com \
  --password 'YourSecurePass1!' \
  --permanent
```

Use the same **email** and **password** in the webapp login form when you do the manual test.

---

## Step 3: Configure webapp .env

From repo root:

```bash
cp frontend/web/.env.example frontend/web/.env
```

Edit `frontend/web/.env` and set:

```bash
# From terraform output api_gateway_url (include trailing slash or not per your API)
VITE_API_URL=https://xxxx.execute-api.us-east-1.amazonaws.com/dev

# From terraform output cognito_user_pool_id and cognito_app_client_id
VITE_COGNITO_USER_POOL_ID=us-east-1_xxxxxxxxx
VITE_COGNITO_CLIENT_ID=xxxxxxxxxxxxxxxxxxxxxxxxxx
VITE_COGNITO_REGION=us-east-1

# Optional: or rely on GET /config for Maps key
# VITE_GOOGLE_MAPS_API_KEY=...
```

Do **not** put the test user’s password in `.env`; you type it in the browser at login.

---

## Step 4: Build webapp

```bash
cd frontend/web
npm ci
npm run build
```

Output is in `dist/`. If build fails, check that `.env` has no typos and that `VITE_API_URL` has no trailing slash if your API expects none (or add it if it expects one).

---

## Step 5: Upload to S3 and use CloudFront URL

From repo root:

```bash
BUCKET=$(terraform -chdir=infrastructure output -raw web_app_bucket_name)
aws s3 sync frontend/web/dist/ "s3://$BUCKET" --delete
```

Then open the web app:

```bash
terraform -chdir=infrastructure output -raw web_app_url
```

Open that URL in a browser (e.g. `https://xxxx.cloudfront.net`).  
If you see old content, invalidate CloudFront cache:

```bash
DIST_ID=$(aws cloudfront list-distributions --query "Items[?Origins.Items[0].DomainName=='$BUCKET.s3.us-east-1.amazonaws.com'].Id" --output text)
aws cloudfront create-invalidation --distribution-id "$DIST_ID" --paths "/*"
```

---

## Step 6: Manual test

1. **Open** the CloudFront URL (from Step 5).
2. **Login:** Use the test user email and password from Step 2.
3. **Triage:** Go to the triage flow, enter symptoms/vitals, submit. You should see severity and recommendations from the real API (or mock if `VITE_USE_MOCK_API=true` was set at build).
4. **Hospitals:** From the same flow or hospital match, request hospitals. You should see a list from the API.
5. **Route:** If the UI has a “Get directions” or route step, use it; it should call `POST /route` with auth.

If login fails: double-check Cognito pool ID and client ID in `.env` and that they match Terraform outputs. If triage/hospitals return 401: ensure you’re logged in and that the app was built with the same `VITE_API_URL` as the API you’re calling.

---

## Optional: Use the same user for get_rmp_token.py

If you want `scripts/get_rmp_token.py` to work with the same test user:

1. Create the user (Step 2) and choose a password.
2. In `infrastructure/terraform.tfvars` (create if needed), set:
   - `rmp_test_email` = that email
   - `rmp_test_password` = that password
3. Run `terraform apply` so the `rmp-test-credentials` secret is created/updated.
4. Then: `TOKEN=$(python3 scripts/get_rmp_token.py)` and use `Authorization: Bearer $TOKEN` for curl/Postman.

---

## Quick reference

| What | Command / Where |
|------|------------------|
| Cognito pool ID | `terraform -chdir=infrastructure output -raw cognito_user_pool_id` |
| Cognito client ID | `terraform -chdir=infrastructure output -raw cognito_app_client_id` |
| API URL | `terraform -chdir=infrastructure output -raw api_gateway_url` |
| Create test user | `python3 scripts/create_cognito_test_user.py --email X --password 'Y'` |
| Web bucket | `terraform -chdir=infrastructure output -raw web_app_bucket_name` |
| Web URL | `terraform -chdir=infrastructure output -raw web_app_url` |
| Upload build | `aws s3 sync frontend/web/dist/ s3://$BUCKET --delete` |
