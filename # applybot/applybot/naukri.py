# applybot/naukri.py
import os, time, json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from .db import has_applied, save_application

class NaukriBot:
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
        log_fn("NaukriBot: starting driver")
        self._start_driver()
        self.driver.get("https://www.naukri.com/mnjuser/recommendedjobs")
        time.sleep(2)
        try:
            self._load_cookies()
            self.driver.refresh()
            time.sleep(1)
            log_fn("Naukri: cookies loaded (if provided)")
        except Exception:
            pass

        job_cards = self.driver.find_elements(By.XPATH, ".//article[contains(@class,'jobTuple')]")
        log_fn(f"Naukri: found {len(job_cards)} cards")
        for card in job_cards:
            try:
                try:
                    link_el = card.find_element(By.XPATH, ".//a[contains(@href, '/job-detail/')]")
                except Exception:
                    link_el = card.find_element(By.TAG_NAME, "a")
                url = link_el.get_attribute("href")
                title = card.text.split("\n")[0]
                job_id = (url.split("/")[-1] or url.split("/")[-2]).split("?")[0]
                if has_applied("naukri", job_id):
                    continue
                self.driver.execute_script("window.open(arguments[0]);", url)
                self.driver.switch_to.window(self.driver.window_handles[-1])
                time.sleep(1.5)
                try:
                    apply_btn = WebDriverWait(self.driver, 6).until(
                        EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Apply') or contains(., 'APPLY')]"))
                    )
                    apply_btn.click()
                    time.sleep(2)
                    save_application("naukri", job_id, title, "", url)
                    log_fn(f"Naukri: applied (heuristic) to {title}")
                except Exception as e:
                    log_fn(f"Naukri: no apply / error {e}")
                self.driver.close()
                self.driver.switch_to.window(self.driver.window_handles[0])
            except Exception as e:
                log_fn(f"Naukri: error with card {e}")
        try:
            self.driver.quit()
        except Exception:
            pass
        log_fn("Naukri: finished")
