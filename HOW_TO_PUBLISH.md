# Publish this project (free, manual — about 20 minutes)

No GitHub connection is needed. Everything below is done by you in the browser.

## 1. Create the repo
1. Go to github.com/new, name it `healthcare-disease-analysis`, set it to
   **Public** (GitHub Actions and Streamlit Cloud free tiers work best on
   public repos), and create it empty.
2. Upload the files from this project (drag and drop the whole folder, or use
   GitHub's "uploading an existing file" flow). Skip the `.venv` folder and
   the `.duckdb` file — they are local only.

## 2. Turn on the daily pipeline
1. In the repo, open the **Actions** tab and enable workflows if asked.
2. The workflow in `.github/workflows/daily-refresh.yml` runs every day at
   08:00 UTC and commits refreshed data. You can also run it once manually
   from Actions → "Daily healthcare data refresh" → Run workflow.

## 3. Put the dashboard online (free)
1. Go to share.streamlit.io and sign in with GitHub.
2. New app → pick your repo, branch `main`, main file
   `dashboard/app.py` → Deploy.
3. The dashboard URL is your live demo link — put it in the repo README and
   on your portfolio site.

## 4. Add it to your portfolio and resume
- Portfolio: link the repo and the live dashboard URL.
- Resume: use a bullet from `docs/RESUME_BULLETS.md`.
- Interviews: `docs/INTERVIEW_TALKING_POINTS.md` has the architecture story.
