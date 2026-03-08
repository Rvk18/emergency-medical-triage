# MVP Deploy Runbook — Working MVP Link (#3)

How to get a **Working MVP link** for the hackathon: deploy the web app on AWS (public) and options for making the mobile app available to evaluators.

**Chosen approach:** Web app is hosted via **Terraform S3 + CloudFront** (`infrastructure/web_hosting.tf`). After `terraform apply`, build the frontend and upload: `aws s3 sync frontend/web/dist s3://$(terraform -chdir=infrastructure output -raw web_app_bucket_name) --delete`. Web URL: `terraform -chdir=infrastructure output -raw web_app_url`. Android: provide APK (e.g. Google Drive link) as well. See [WEB-BACKEND-INTEGRATION-PLAN.md](WEB-BACKEND-INTEGRATION-PLAN.md) and [SECURITY-PUBLIC-VS-PRIVATE.md](SECURITY-PUBLIC-VS-PRIVATE.md).

---

## 1. Web app — deploy on AWS and make public

**Goal:** A public URL (e.g. `https://your-app.cloudfront.net` or `https://xxx.amplifyapp.com`) that evaluators can open to use the MVP.

### Option A: AWS Amplify (recommended for speed)

1. **Connect repo:** AWS Amplify Console → New app → Host web app → GitHub → select `Rvk18/emergency-medical-triage`, branch `main`.
2. **Root and build:** Set root to `frontend/web`. Build: `npm ci && npm run build` (or whatever `frontend/web/package.json` scripts use). Output directory: `dist` or `out` (match your framework).
3. **Env vars:** Add `VITE_API_URL` or `NEXT_PUBLIC_API_URL` (your API Gateway URL from Terraform / api_config). So the frontend knows where to call the backend.
4. **Deploy:** Amplify builds and deploys. You get a URL like `https://main.xxxx.amplifyapp.com`. Use that as your **Working MVP link**.
5. **CORS:** Ensure your API Gateway allows the Amplify origin. If you get CORS errors, add the Amplify URL to the API’s CORS allowed origins (Terraform or API Gateway console).

### Option B: S3 + CloudFront (Terraform — chosen)

1. **Terraform:** `infrastructure/web_hosting.tf` creates the web bucket and CloudFront. Run `terraform apply`; get bucket name and URL: `terraform -chdir=infrastructure output web_app_bucket_name web_app_url`.
2. **Build:** From `frontend/web`: set `VITE_API_URL`, `VITE_COGNITO_*` (and optional `VITE_GOOGLE_MAPS_API_KEY`), then `npm run build` → `dist/`.
3. **Upload:** `aws s3 sync dist/ s3://$(terraform -chdir=infrastructure output -raw web_app_bucket_name) --delete`.
4. **Optional:** Invalidate cache: `aws cloudfront create-invalidation --distribution-id <ID> --paths "/*"`. Use `web_app_url` as your **Working MVP link**.
5. **CORS:** API Gateway allows all origins (`*`); see `infrastructure/api_gateway_cors.tf`.

### Option C: Vercel / Netlify

If you prefer Vercel or Netlify: connect the repo, set root to `frontend/web`, set API URL env var, deploy. Use the provided URL as your **Working MVP link**. Ensure CORS on API Gateway allows that origin.

---

## 2. Mobile app — how to make it “available” to evaluators

You don’t need a full Play Store release. Pick one of these:

### Option A: APK on S3 (same bucket as web app + CloudFront)

Uses the existing Terraform web bucket and CloudFront so the APK is served at a stable HTTPS URL. **Requires JDK 17+ and Android SDK on your machine** (the APK cannot be built in CI without Java).

1. **Build debug APK** (from repo root):
   ```bash
   cd frontend/mobile-android && ./gradlew assembleDebug
   cd ../..
   ```
   APK output: `frontend/mobile-android/app/build/outputs/apk/debug/app-debug.apk`

2. **Upload to S3** (bucket from Terraform, correct content type so devices install correctly):
   ```bash
   cd infrastructure && terraform init && cd ..   # if you see "Required plugins are not installed"
   BUCKET=$(terraform -chdir=infrastructure output -raw web_app_bucket_name)
   aws s3 cp frontend/mobile-android/app/build/outputs/apk/debug/app-debug.apk \
     s3://$BUCKET/apk/MedTriage.apk \
     --content-type "application/vnd.android.package-archive"
   ```
   **If `BUCKET` is empty:** run `terraform apply` in `infrastructure/` first to create the bucket (or use an existing bucket name from AWS Console). Then re-run the `aws s3 cp` command with that bucket name.

3. **Download URL** (after upload):
   ```
   https://d2x5u793glu2eu.cloudfront.net/apk/MedTriage.apk
   ```
   (Uses the same CloudFront distribution as the web app; distribution ID from `terraform -chdir=infrastructure output -raw web_app_cloudfront_distribution_id` if needed.)

4. **Optional — invalidate CloudFront cache** (so users get the latest APK immediately):
   ```bash
   aws cloudfront create-invalidation \
     --distribution-id $(terraform -chdir=infrastructure output -raw web_app_cloudfront_distribution_id) \
     --paths "/apk/*"
   ```

Use the download URL as your **Android APK (download)** link in PROJECT-SUMMARY and submission.

### Option A2: APK on dedicated public S3 bucket

A separate **public-read** S3 bucket is available so anyone can download the APK without CloudFront. Terraform creates it in `infrastructure/apk_bucket.tf`.

1. **Apply Terraform** (if not already): `cd infrastructure && terraform apply`
2. **Get bucket name:** `terraform -chdir=infrastructure output -raw apk_bucket_name`
3. **Upload the APK** (you or your team uploads the built APK; key `apk/MedTriage.apk` recommended):
   ```bash
   BUCKET=$(terraform -chdir=infrastructure output -raw apk_bucket_name)
   aws s3 cp path/to/your-app.apk s3://$BUCKET/apk/MedTriage.apk \
     --content-type "application/vnd.android.package-archive"
   ```
   Or upload via **AWS Console**: S3 → bucket → Upload → choose the APK file; create folder `apk` and upload as `apk/MedTriage.apk`.
   **If you see "Access Denied" when opening the download URL:** the object likely doesn't exist yet — S3 returns 403 for missing objects. Upload the APK to the key `apk/MedTriage.apk` first, then use the URL from step 4.
4. **Download URL** (after upload):  
   `terraform -chdir=infrastructure output -raw apk_download_url`  
   This is a **CloudFront** URL (e.g. `https://d123.cloudfront.net/apk/MedTriage.apk`). Use this link in PROJECT-SUMMARY; no auth required.

### Option B: APK on Google Drive (simplest)

1. **Build release APK:** From `frontend/mobile-android`: `./gradlew assembleRelease`. APK is in `app/build/outputs/apk/release/`.
2. **Upload:** Upload the APK to Google Drive. Set sharing to “Anyone with the link can view” (or “can download”).
3. **Link:** In your PROJECT-SUMMARY and PPT, add: “Android APK (download): [Drive link]”. Evaluators download and install (they may need to allow “Install from unknown sources” on their device).

### Option C: Internal testing track (Google Play)

1. Create an app in Google Play Console (one-time).  
2. Upload the AAB/APK to **Internal testing**.  
3. Add evaluators’ email addresses as testers; they get an opt-in link and can install from Play Store.  
4. Use that opt-in link as your “mobile app” link in the submission.

### Option D: Firebase App Distribution

1. Build APK/AAB, upload to Firebase App Distribution.  
2. Invite testers by email; they get a link to download and install.  
3. Share that invite link as your mobile MVP link.

### Option E: “Source only” fallback

If you can’t distribute the APK in time: in PROJECT-SUMMARY and PPT, write: “Android app: build from source — see `frontend/mobile-android/README.md`. Clone repo, open in Android Studio, set API URL, run on device/emulator.” Provide the **web MVP link** as the primary Working MVP link.

---

## 3. What to put in the submission form

- **Working MVP link:** Prefer the **web app URL** (CloudFront from Terraform, or Amplify/Vercel). It’s the one click that works for everyone.
- **Android:** Provide **Android APK** link (e.g. Google Drive: “Anyone with the link can download”) in PROJECT-SUMMARY and submission: “Android APK (download): [Drive link].”

---

## 4. Quick reference

| Item | Where |
|------|--------|
| API base URL | `eval $(python3 scripts/load_api_config.py --exports)` → `API_URL`; or Terraform output `api_gateway_url` |
| Web app code | `frontend/web/` |
| Android app code | `frontend/mobile-android/` |
| Frontend integration | [docs/frontend/API-Integration-Guide.md](frontend/API-Integration-Guide.md) |
| Web app URL (after deploy) | `terraform -chdir=infrastructure output -raw web_app_url` |
| Web app bucket | `terraform -chdir=infrastructure output -raw web_app_bucket_name` |
| APK bucket (public) | `terraform -chdir=infrastructure output -raw apk_bucket_name` |
| APK download URL (after upload to apk bucket) | `terraform -chdir=infrastructure output -raw apk_download_url` |
| Android APK URL (Option A: S3) | `https://d2x5u793glu2eu.cloudfront.net/apk/MedTriage.apk` (after uploading APK to bucket) |
| CORS (API Gateway) | Allow all origins (`*`); see `infrastructure/api_gateway_cors.tf` and [SECURITY-PUBLIC-VS-PRIVATE.md](SECURITY-PUBLIC-VS-PRIVATE.md) |
