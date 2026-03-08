# MVP Deploy Runbook — Working MVP Link (#3)

How to get a **Working MVP link** for the hackathon: deploy the web app on AWS (public) and options for making the mobile app available to evaluators.

---

## 1. Web app — deploy on AWS and make public

**Goal:** A public URL (e.g. `https://your-app.cloudfront.net` or `https://xxx.amplifyapp.com`) that evaluators can open to use the MVP.

### Option A: AWS Amplify (recommended for speed)

1. **Connect repo:** AWS Amplify Console → New app → Host web app → GitHub → select `Rvk18/emergency-medical-triage`, branch `main`.
2. **Root and build:** Set root to `frontend/web`. Build: `npm ci && npm run build` (or whatever `frontend/web/package.json` scripts use). Output directory: `dist` or `out` (match your framework).
3. **Env vars:** Add `VITE_API_URL` or `NEXT_PUBLIC_API_URL` (your API Gateway URL from Terraform / api_config). So the frontend knows where to call the backend.
4. **Deploy:** Amplify builds and deploys. You get a URL like `https://main.xxxx.amplifyapp.com`. Use that as your **Working MVP link**.
5. **CORS:** Ensure your API Gateway allows the Amplify origin. If you get CORS errors, add the Amplify URL to the API’s CORS allowed origins (Terraform or API Gateway console).

### Option B: S3 + CloudFront

1. **Build:** From `frontend/web`: `npm run build` → static output in `dist/` or `out/`.
2. **S3 bucket:** Create a bucket, enable static website hosting, upload the build output. Or use `aws s3 sync dist/ s3://your-bucket-name --delete`.
3. **CloudFront:** Create a distribution with origin = S3 bucket (or S3 website endpoint). Use the CloudFront URL (e.g. `https://d1234.cloudfront.net`) as your **Working MVP link**.
4. **Env:** Build with the correct API URL (e.g. at build time via env var) so the deployed app points to your live API.
5. **CORS:** Same as Option A — allow the CloudFront (or custom) origin in API Gateway.

### Option C: Vercel / Netlify

If you prefer Vercel or Netlify: connect the repo, set root to `frontend/web`, set API URL env var, deploy. Use the provided URL as your **Working MVP link**. Ensure CORS on API Gateway allows that origin.

---

## 2. Mobile app — how to make it “available” to evaluators

You don’t need a full Play Store release. Pick one of these:

### Option A: APK on Google Drive (simplest)

1. **Build release APK:** From `frontend/mobile-android`: `./gradlew assembleRelease`. APK is in `app/build/outputs/apk/release/`.
2. **Upload:** Upload the APK to Google Drive. Set sharing to “Anyone with the link can view” (or “can download”).
3. **Link:** In your PROJECT-SUMMARY and PPT, add: “Android APK (download): [Drive link]”. Evaluators download and install (they may need to allow “Install from unknown sources” on their device).

### Option B: Internal testing track (Google Play)

1. Create an app in Google Play Console (one-time).  
2. Upload the AAB/APK to **Internal testing**.  
3. Add evaluators’ email addresses as testers; they get an opt-in link and can install from Play Store.  
4. Use that opt-in link as your “mobile app” link in the submission.

### Option C: Firebase App Distribution

1. Build APK/AAB, upload to Firebase App Distribution.  
2. Invite testers by email; they get a link to download and install.  
3. Share that invite link as your mobile MVP link.

### Option D: “Source only” fallback

If you can’t distribute the APK in time: in PROJECT-SUMMARY and PPT, write: “Android app: build from source — see `frontend/mobile-android/README.md`. Clone repo, open in Android Studio, set API URL, run on device/emulator.” Provide the **web MVP link** as the primary Working MVP link.

---

## 3. What to put in the submission form

- **Working MVP link:** Prefer the **web app URL** (Amplify/CloudFront/Vercel). It’s the one click that works for everyone.  
- **Optional second link / note:** “Android APK: [Drive link]” or “Mobile: see PROJECT-SUMMARY.md for APK / build instructions.”

---

## 4. Quick reference

| Item | Where |
|------|--------|
| API base URL | `eval $(python3 scripts/load_api_config.py --exports)` → `API_URL`; or Terraform output `api_gateway_url` |
| Web app code | `frontend/web/` |
| Android app code | `frontend/mobile-android/` |
| Frontend integration | [docs/frontend/API-Integration-Guide.md](frontend/API-Integration-Guide.md) |
| CORS (API Gateway) | Infrastructure Terraform or API Gateway console — add your web app origin to allowed origins |
