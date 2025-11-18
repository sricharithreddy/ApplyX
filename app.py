# app.py
import gradio as gr
import json, os, threading, time
from applybot.db import init_db
from applybot.iimjobs import IIMJobsBot
from applybot.naukri import NaukriBot

CFG_DIR = "workspace"
os.makedirs(CFG_DIR, exist_ok=True)

LOG_BUF = []

def _log(msg):
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    LOG_BUF.append(f"[{ts}] {msg}")

def save_file(file, dest_dir=CFG_DIR):
    if file is None:
        return None
    os.makedirs(dest_dir, exist_ok=True)
    path = os.path.join(dest_dir, file.name)
    with open(path, "wb") as f:
        f.write(file.read())
    return path

def run_apply(resume_file, prefs_json, cookies_iim_file, cookies_naukri_file, run_iim, run_naukri):
    LOG_BUF.clear()
    _log("Starting run...")

    # Save uploaded files
    resume_path = save_file(resume_file) if resume_file else None
    cookies_iim = save_file(cookies_iim_file) if cookies_iim_file else None
    cookies_naukri = save_file(cookies_naukri_file) if cookies_naukri_file else None

    # Parse preferences
    try:
        prefs = json.loads(prefs_json) if prefs_json else {}
    except Exception as e:
        prefs = {}
        _log("Invalid preferences JSON, ignoring.")

    init_db()

    # Create bots
    if run_iim:
        _log("Launching IIMJobs bot...")
        try:
            bot = IIMJobsBot(headless=True, resume_path=resume_path, preferences=prefs)
            if cookies_iim:
                bot.cookie_file = cookies_iim
            bot.run(log_fn=_log)
            _log("IIMJobs run completed.")
        except Exception as e:
            _log(f"IIMJobs error: {e}")

    if run_naukri:
        _log("Launching Naukri bot...")
        try:
            bot = NaukriBot(headless=True, resume_path=resume_path, preferences=prefs)
            if cookies_naukri:
                bot.cookie_file = cookies_naukri
            bot.run(log_fn=_log)
            _log("Naukri run completed.")
        except Exception as e:
            _log(f"Naukri error: {e}")

    _log("Run finished.")
    return "\n".join(LOG_BUF)

def run_background(resume_file, prefs_json, cookies_iim_file, cookies_naukri_file, run_iim, run_naukri):
    # run in thread so Gradio remains responsive
    thread = threading.Thread(target=run_apply, args=(resume_file, prefs_json, cookies_iim_file, cookies_naukri_file, run_iim, run_naukri), daemon=True)
    thread.start()
    return "Started background run. Logs will appear below once available."

with gr.Blocks() as demo:
    gr.Markdown("# ApplyBot — IIMJobs + Naukri (HF Space pilot)")
    with gr.Row():
        with gr.Column(scale=1):
            resume = gr.File(label="Upload resume (pdf/docx)")
            cookies_iim = gr.File(label="Upload iimjobs cookies JSON (optional)")
            cookies_naukri = gr.File(label="Upload naukri cookies JSON (optional)")
            prefs = gr.Textbox(label="Preferences (JSON). Example: {\"keywords\":[\"product manager\"], \"locations\":[\"Hyderabad\"]}", lines=4)
            run_iim = gr.Checkbox(label="Run IIMJobs bot", value=True)
            run_naukri = gr.Checkbox(label="Run Naukri bot", value=True)
            run_btn = gr.Button("Start ApplyBot (background)")

        with gr.Column(scale=1):
            logs = gr.Textbox(label="Logs (live after run starts)", lines=20)

    run_btn.click(fn=run_background, inputs=[resume, prefs, cookies_iim, cookies_naukri, run_iim, run_naukri], outputs=[logs])

    gr.Markdown("""
    **Important notes**
    - This Space runs Selenium + headless Chromium in the container.
    - Many job sites require login and anti-bot protections. For stability upload `cookies_*.json` exported from your browser (instructions in README).
    - Keep runs short (demo/pilot). Long-running jobs may be killed by HF.
    """)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
