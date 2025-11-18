# applybot/iimjobs.py
import os, time, json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from .db import has_applied, save_application

class IIMJobsBot:
    def __init__(self, headless=True, resume_path=None, preferences=None):
        self.headless = headless
        self.resume_path = resume_path
        self.preferences = preferences or {}
        self.driver = None
        self.cookie_file = None

    def _start_driver(self):
        options = Options()
        if self.headless:
            options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-infobars")
        # Accept insecure certs if any
        options.add_argument('--ignore-certificate-errors')
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        self.driver.implicitly_wait(5)

    def _load_cookies(self):
        if self.cookie_file and os.path.exists(self.cookie_file):
            try:
                with open(self.cookie_file, "r") as f:
                    cookies = json.load(f)
                for cookie in cookies:
                    cookie.pop("sameSite", None)
                    try:
                        self.driver.add_cookie(cookie)
                    except Exception:
                        pass
            except Exception:
                pass

    def run(self, log_fn=print):
        log_fn("IIMJobsBot: starting driver")
        self._start_driver()
        self.driver.get("https://www.iimjobs.com/recommended-jobs")
        time.sleep(2)
        # load cookies if provided, then refresh
        try:
            self._load_cookies()
            self.driver.refresh()
            time.sleep(1)
            log_fn("IIMJobs: cookies loaded (if provided)")
        except Exception:
            pass

        # scroll to load
        last_h = self.driver.execute_script("return document.body.scrollHeight")
        for _ in range(10):
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)
            new_h = self.driver.execute_script("return document.body.scrollHeight")
            if new_h == last_h:
                break
            last_h = new_h

        job_links = self.driver.find_elements(By.XPATH, './/a[contains(@href, "/j/")]')
        unique = {}
        for el in job_links:
            href = el.get_attribute("href")
            title = el.text.strip()
            if href:
                unique[href] = title or href

        log_fn(f"IIMJobs: found {len(unique)} job links")

        for url, title in unique.items():
            try:
                job_id = url.rstrip("/").split("/")[-1]
                if has_applied("iimjobs", job_id):
                    log_fn(f"IIMJobs: already applied {job_id}")
                    continue
                log_fn(f"IIMJobs: opening {url}")
                self.driver.get(url)
                time.sleep(1.5)
                try:
                    apply_btn = WebDriverWait(self.driver, 6).until(
                        EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Apply') or contains(., 'APPLY')]"))
                    )
                    apply_btn.click()
                    time.sleep(1.5)
                    try:
                        rev = WebDriverWait(self.driver, 4).until(
                            EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Review') or contains(., 'Submit') or contains(., 'Review & Submit')]"))
                        )
                        rev.click()
                        time.sleep(1)
                    except Exception:
                        pass
                    company = ""
                    try:
                        company = self.driver.find_element(By.XPATH, "//h1").text
                    except Exception:
                        pass
                    save_application("iimjobs", job_id, title, company, url)
                    log_fn(f"IIMJobs: applied to {title}")
                except Exception as e:
                    log_fn(f"IIMJobs: no apply button / error {e}")
            except Exception as e:
                log_fn(f"IIMJobs: error processing job {e}")
        try:
            self.driver.quit()
        except Exception:
            pass
        log_fn("IIMJobs: finished")
