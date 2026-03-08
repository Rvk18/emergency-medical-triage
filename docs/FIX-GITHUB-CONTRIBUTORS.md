# Fix GitHub contributors to show your name

GitHub links commits to your profile using the **author email**. If commits used a different email (e.g. hostname-based or Cursor), you won't appear as contributor.

## 1. Use your GitHub email in Git (for future commits)

Replace with the **same email** you use on GitHub (Settings → Emails):

```bash
git config --global user.name "VickramKarthick R"
git config --global user.email "YOUR-GITHUB-EMAIL@example.com"
```

Then in **GitHub → Settings → Emails**, add and verify that email if it's not already there.

---

## 2. Rewrite recent commits so you appear as author (optional)

This changes the **author** of the last 10 commits to your name and GitHub email, then updates the remote.  
**Replace `YOUR-GITHUB-EMAIL@example.com`** with your real GitHub email.

```bash
cd /path/to/AI_Hackathon_Triage

# Rewrite last 10 commits with you as author (use angle brackets around email)
git rebase -i HEAD~10 --exec 'git commit --amend --author="VickramKarthick R <YOUR-GITHUB-EMAIL@example.com>" --no-edit'

# Force push (rewrites history on main)
git push origin main --force
```

**Warning:** `--force` rewrites history. If anyone else has cloned the repo, they’ll need to re-clone or `git pull --rebase`. For a solo hackathon repo this is usually fine.

---

## 3. Verify

- Open https://github.com/Rvk18/emergency-medical-triage  
- Check the **Contributors** section (right sidebar or Insights → Contributors).  
- Your profile should appear once the email matches and the rewritten commits are pushed.

---

## If you prefer not to rewrite history

Just do **step 1**. All **new** commits will then count toward your profile. Old commits will still show the previous author until you do step 2.
