# ApplyBot — IIMJobs + Naukri (Hugging Face Space + Gradio + Selenium)

## What this is
A pilot app that automates job applications on IIMJobs and Naukri using Selenium and headless Chromium. The UI is a Gradio app and is designed to be deployed as a Hugging Face Space (Docker).

## Deploy (Hugging Face Spaces)
1. Create a new Space on Hugging Face: choose **"Docker"** as the SDK.
2. Push this repo to the new Space (via GitHub or `git push` to the HF repo).
3. HF will build the Docker image and expose a public URL.

## How to use
1. Open the public URL of your Space.
2. Upload your resume (pdf/docx).
3. (Recommended) Export cookies from your browser for IIMJobs and Naukri and upload the cookie JSON files.
   - Use a browser cookie export extension (e.g., "EditThisCookie") to export cookies for `iimjobs.com` and `naukri.com`.
   - Save as JSON (array of cookie objects). Upload each file to the matching uploader.
   - Note: If cookies expire or the site invalidates them, re-export and re-upload.
4. Optionally edit preferences JSON (example):
```json
{
  "keywords": ["product manager"],
  "locations": ["Hyderabad"],
  "min_exp": 0,
  "max_exp": 5
}
