# Submission Checklist — The Big 5

Use this checklist to ensure your hackathon submission is complete.

---

## The Big 5

| # | Item | Owner | Status | Notes |
|---|------|--------|--------|-------|
| **1** | **Project PPT** | You | ⬜ | Step 1 filter — crucial. |
| **2** | **Demo video** | You | ⬜ | YouTube or Google Drive link. |
| **3** | **Working MVP link** | You | ✅ | **Web:** Hosted (S3 + CloudFront). **Android:** Upload APK to S3 — see [MVP deploy runbook](docs/MVP-DEPLOY-RUNBOOK.md) §2 Option A; fill APK URL in PROJECT-SUMMARY after upload. |
| **4** | **GitHub repository** | You | ⬜ | **Ensure it is Public.** Repo: https://github.com/Rvk18/emergency-medical-triage |
| **5** | **Project summary** | Done | ✅ | [PROJECT-SUMMARY.md](PROJECT-SUMMARY.md) — one-pager; fill in MVP/video/PPT links before submit. |

---

## Completed (for reference)

- **Backend:** All planned APIs (triage, hospitals, route, RMP Learning, Eka, Cognito auth) implemented and deployed.
- **Web app:** Built and hosted on S3 + CloudFront; public URL in PROJECT-SUMMARY.
- **Android app:** Completed; build APK and upload to S3 for download link (runbook §2 Option A).

---

## #4 — GitHub: ensure repo is public

1. Open https://github.com/Rvk18/emergency-medical-triage  
2. Go to **Settings** → **General**  
3. Under **Danger Zone** or **Visibility**, confirm the repository is **Public**.  
4. If it was private, change to Public and save.  
5. Verify: open the repo in an incognito window (or logged out) — you should see the code without logging in.

---

## #3 — Working MVP (runbook for later)

- **Web app:** ✅ Deployed `frontend/web/` to AWS (S3 + CloudFront). URL: see PROJECT-SUMMARY.md.
- **Mobile app:** Build APK (`./gradlew assembleDebug` in `frontend/mobile-android/`), then upload to S3 for download — **[docs/MVP-DEPLOY-RUNBOOK.md](docs/MVP-DEPLOY-RUNBOOK.md)** §2 Option A (APK on S3). Use the CloudFront URL `/apk/MedTriage.apk` as the download link. Alternatives: Google Drive, internal testing track, or “build from source” — see runbook.

---

## Before you submit

- [ ] All five items above are done or linked.  
- [ ] PROJECT-SUMMARY.md has MVP link, demo video link, and PPT link filled in (or “see submission form”).  
- [ ] README.md is up to date (overview, structure, quick start, link to HACKATHON.md and this checklist).
