# Mobile app – Cognito auth and API access

**Audience:** Mobile app developers (Android / iOS).  
**Purpose:** How to sign in with **Amazon Cognito**, get the **user access token (Id Token)**, and send the **Authorization** header on every protected API request.

---

## 1. Get configuration from the backend

After the backend team runs `terraform apply`, you need three values. Get them from Terraform outputs (from the project root):

```bash
cd infrastructure
terraform output -raw cognito_user_pool_id      # e.g. us-east-1_yLzc69xzZ
terraform output -raw cognito_app_client_id    # e.g. 7unkvq3g553c2k7t4vrupp33bb
terraform output -raw api_gateway_url          # e.g. https://xxxx.execute-api.us-east-1.amazonaws.com/dev/
```

| Variable | Description | Use in app |
|----------|-------------|------------|
| **User Pool ID** | Cognito User Pool ID | Cognito sign-in (InitiateAuth) |
| **Client ID** | Cognito App Client ID (no secret) | Cognito sign-in |
| **API base URL** | API Gateway invoke URL (include trailing slash if your client appends paths) | Base URL for all API calls |

Store these in your app via **BuildConfig**, **local.properties**, or a config file—**never** commit secrets. The Client ID is safe to ship in the app; it is public.

---

## 2. Sign in with Cognito and get the Id Token

The backend uses **Cognito User Pools** and an **API Gateway Cognito authorizer**. The authorizer expects the **Cognito Id Token** (JWT), **not** the Access Token.

### Sign-in request (InitiateAuth)

Call AWS Cognito **InitiateAuth** with:

- **AuthFlow:** `USER_PASSWORD_AUTH` (for email + password).
- **ClientId:** from Terraform output above.
- **AuthParameters:** `USERNAME` = user's email (or username), `PASSWORD` = password.

**Endpoint:**  
`https://cognito-idp.<region>.amazonaws.com/`  
Use the same region as your API (e.g. `us-east-1`). Set header `X-Amz-Target: AWSCognitoIdentityProviderService.InitiateAuth` and `Content-Type: application/x-amz-json-1.1`.

**Response:**  
On success, `AuthenticationResult` contains:

| Field | Use |
|-------|-----|
| **IdToken** | ✅ **Use this for the API.** Send as `Authorization: Bearer <IdToken>` on every protected request. |
| AccessToken | Do **not** use for API Gateway; use Id Token only. |
| RefreshToken | Use to get a new Id Token when it expires (see §5). |
| ExpiresIn | Id token lifetime in seconds (e.g. 3600). |

**Important:** For all backend API calls (triage, hospitals, route, rmp/learning), use **only the Id Token** in the `Authorization` header. Using the Access Token will result in **401 Unauthorized**.

### Example (Android / Kotlin)

The app already has a Cognito client interface (`CognitoApi.kt`) that calls InitiateAuth. After a successful sign-in:

1. Read `AuthenticationResult.IdToken` from the response.
2. Persist it securely (e.g. encrypted preferences or DataStore) for the session.
3. On every request to a protected endpoint, add the header:  
   `Authorization: Bearer <IdToken>`.

Replace any mock or placeholder token in `AuthRepository` with this Id Token so that all API clients (Retrofit interceptors, etc.) attach the same header.

---

## 3. Which endpoints require the Auth header

| Endpoint | Method | Auth required? | Header |
|----------|--------|----------------|--------|
| **/health** | GET | No | — |
| **/config** | GET | No | — |
| **/triage** | POST | **Yes** | `Authorization: Bearer <IdToken>` |
| **/hospitals** | POST | **Yes** | Same |
| **/route** | POST | **Yes** | Same |
| **/rmp/learning** | POST | **Yes** | Same |
| **/rmp/learning/me** | GET | **Yes** | Same |
| **/rmp/learning/leaderboard** | GET | **Yes** | Same |

If you call a protected endpoint **without** a valid Id Token (or with an expired one), the API returns **401 Unauthorized**.

---

## 4. Sending the Auth header on every protected request

For **every** request to the endpoints marked "Yes" above:

1. Obtain the current Id Token (from session storage or refresh flow).
2. Add the header:  
   `Authorization: Bearer <IdToken>`
3. Also set `Content-Type: application/json` for POST requests.

**Example (generic):**

```http
POST /triage HTTP/1.1
Host: xxxx.execute-api.us-east-1.amazonaws.com
Content-Type: application/json
Authorization: Bearer eyJraWQiOiJ...

{"symptoms":["chest pain"],"age_years":50,"sex":"M"}
```

**Implementation tips:**

- Use a **single HTTP client** (e.g. OkHttp or Retrofit) and an **interceptor** that adds `Authorization: Bearer <token>` to every request to the API base URL. Read the token from your auth repository/session store.
- Do **not** add the header for `/health` or `/config` if you call them from the same client; or configure the interceptor to skip those paths.

---

## 5. Token expiry and refresh

- Id Tokens typically expire in **about 1 hour** (check `ExpiresIn` in the sign-in response).
- When the API returns **401**, treat the token as invalid or expired. Either:
  - **Refresh:** Use Cognito **InitiateAuth** with `AuthFlow: REFRESH_TOKEN_AUTH` and `AuthParameters: REFRESH_TOKEN = <RefreshToken>` to get a new `AuthenticationResult` (with a new `IdToken`), then retry the request with the new Id Token.
  - Or **re-prompt sign-in** if you don't have a refresh token or refresh fails.

After refreshing, persist the new Id Token (and optionally RefreshToken) and use it for all subsequent requests.

---

## 6. Creating a test user

RMP users must exist in the Cognito User Pool. Options:

1. **AWS Console:** Cognito → User Pools → your pool → Users → Create user (email + temporary password).
2. **AWS CLI:**
   ```bash
   aws cognito-idp admin-create-user \
     --user-pool-id <USER_POOL_ID> \
     --username user@example.com \
     --user-attributes Name=email,Value=user@example.com Name=email_verified,Value=true \
     --temporary-password "TempPass123!"
   ```
3. **Script:** The repo has `scripts/create_cognito_test_user.py`; the backend team can use it to create a test user and (if configured) store credentials in Secrets Manager for automation.

The mobile app only needs to call InitiateAuth with the user's email and password; no extra backend call for "login" is required.

---

## 7. Summary checklist for mobile

- [ ] Get **User Pool ID**, **Client ID**, and **API base URL** from Terraform (or backend team).
- [ ] Implement **sign-in** with Cognito InitiateAuth (`USER_PASSWORD_AUTH`); read **IdToken** from `AuthenticationResult`.
- [ ] Store the Id Token (and RefreshToken) securely for the session.
- [ ] Add **`Authorization: Bearer <IdToken>`** to every request to **POST /triage**, **POST /hospitals**, **POST /route**, **POST /rmp/learning**, **GET /rmp/learning/me**, **GET /rmp/learning/leaderboard**.
- [ ] Do **not** send the Authorization header for **GET /health** and **GET /config** (they are public).
- [ ] On **401**, refresh the token (REFRESH_TOKEN_AUTH) or redirect to sign-in.
- [ ] Use **Id Token** only for the API; do not use the Access Token for API Gateway.

---

## References

- [RMP-AUTH.md](./RMP-AUTH.md) – Web/frontend Cognito integration (Amplify, curl).
- [API-Integration-Guide.md](./API-Integration-Guide.md) – All endpoints, request/response shapes, triage → hospitals → route flow.
- [RMP-LEARNING-API.md](./RMP-LEARNING-API.md) – RMP Learning endpoints and contract.
- [AWS Cognito InitiateAuth](https://docs.aws.amazon.com/cognito-user-identity-pools/latest/APIReference/API_InitiateAuth.html)
- [API Gateway Cognito authorizer](https://docs.aws.amazon.com/apigateway/latest/developerguide/apigateway-integrate-with-cognito.html)
