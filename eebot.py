#!/usr/bin/env python
# -*- coding:utf-8 -*-

# Author: Guy Fawkes
# LastEditors: Guy Fawkes
# Date: 2025/1/1
# LastEditTime: 2025/7/22

"""
Simplified mitmproxy logger for elearn.post.gov.tw
Removed optional addons: ElearnLogger, UserVisitsLogger, ExamLogger, Counter.
Only supports VisitDurationModifier for modifying visit_duration.
Configuration loaded from UTF-8-SIG config.txt:
  target_http, execute_file, cookies_file,
  user_name, password,
  modify_visits, silent_mitm, log_save,
  listen_host, listen_port
"""
import json
import os
import time
import asyncio
import subprocess
import base64
import sys
from datetime import datetime
from multiprocessing import Process

import requests
from mitmproxy import http
from mitmproxy.options import Options as MitmOptions
from mitmproxy.tools.dump import DumpMaster
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException

# ===========================
# Class 定義區段（完整展開）
WAIT_TIMEOUT = 40
WAIT_POLL = 0.5
# ===========================

class StealthExtractor:
    def run(self) -> None:
        try:
            os.makedirs("resource/plugins", exist_ok=True)
            subprocess.run(['npx', 'extract-stealth-evasions'], check=True)
            if os.path.exists("stealth.min.js"):
                os.replace("stealth.min.js", "resource/plugins/stealth.min.js")
            print('[StealthExtractor] completed')
        except Exception as e:
            print('[StealthExtractor] error:', e)


class VisitDurationModifier:
    def request(self, flow: http.HTTPFlow):
        if flow.request.path == "/statistics/api/user-visits":
            try:
                payload = json.loads(flow.request.get_text(strict=False) or "")
                if all(k in payload for k in ("course_code", "course_name", "visit_duration")):
                    orig = int(payload["visit_duration"])
                    payload["visit_duration"] = orig + 9000
                    flow.request.set_text(json.dumps(payload))
                    print(f"[Modifier] visit_duration {orig}->{payload['visit_duration']}")
            except Exception:
                pass


class MitmProxyManager:
    def __init__(self, host, port, modify_visits, silent=False, log_save=False):
        self.host = host
        self.port = port
        self.modify_visits = modify_visits
        self.silent = silent
        self.log_save = log_save
        self.process = None

    def _silence_stdout(self):
        sys.stdout.flush()
        sys.stderr.flush()
        if self.log_save:
            now = datetime.now().strftime("%Y%m%d%H%M%S")
            os.makedirs("log", exist_ok=True)
            log_file = os.path.join("log", f"ee{now}.log")
            f = open(log_file, 'w')
            os.dup2(f.fileno(), 1)
            os.dup2(f.fileno(), 2)
        else:
            devnull = open(os.devnull, 'w')
            os.dup2(devnull.fileno(), 1)
            os.dup2(devnull.fileno(), 2)

    async def config(self):
        opts = MitmOptions(listen_host=self.host, listen_port=self.port)
        master = DumpMaster(opts)
        if self.modify_visits:
            master.addons.add(VisitDurationModifier())
        try:
            await master.run()
        except KeyboardInterrupt:
            master.shutdown()

    def _run(self):
        if self.silent:
            self._silence_stdout()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.config())
        loop.close()

    def start(self):
        if not self.silent:
            print(f"[INFO] mitmproxy on {self.host}:{self.port}")
        elif self.log_save:
            print("silent mode logging to file...")
        else:
            print("only silent")
        self.process = Process(target=self._run)
        self.process.start()
        time.sleep(1)

    def stop(self):
        if self.process:
            self.process.terminate()
            self.process.join()


class Eel:
    def __init__(self, url, driver_path, cookie_path, proxy_host, proxy_port):
        self.url = url
        self.cookie_path = cookie_path
        self.proxy_host = proxy_host
        self.proxy_port = proxy_port
        self.driver = self._init_driver(driver_path)

    def _init_driver(self, path):
        opts = ChromeOptions()
        svc = Service(path)
        opts.add_argument(f"--proxy-server={self.proxy_host}:{self.proxy_port}")
        opts.add_argument("--ignore-certificate-errors")
        opts.add_experimental_option('useAutomationExtension', False)
        opts.add_experimental_option('excludeSwitches', ['enable-automation'])
        opts.add_experimental_option('prefs', {
            'credentials_enable_service': False,
            'profile.password_manager_enabled': False,
            'intl.accept_languages': 'zh-TW'
        })
        opts.add_argument('user-agent=Mozilla/5.0')
        driver = webdriver.Chrome(service=svc, options=opts)
        driver.maximize_window()
        try:
            js_path = os.path.join("resource", "plugins", "stealth.min.js")
            if not os.path.isfile(js_path):
                print('[Warn] stealth missing, attempting to extract again...')
                os.makedirs("resource/plugins", exist_ok=True)
                subprocess.run(['npx', 'extract-stealth-evasions', '-o', js_path], check=True)
            js = open(js_path, 'r', encoding='utf-8').read()
            driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {'source': js})
        except FileNotFoundError:
            print('[Warn] stealth missing')
        return driver

    def click_lesson_link(self):
        try:
            elem = WebDriverWait(self.driver, WAIT_TIMEOUT, WAIT_POLL).until(
                EC.element_to_be_clickable((By.XPATH, "//div[@class='clickable-area']"))
            )
            try:
                elem.click()
            except ElementClickInterceptedException:
                driver.execute_script("arguments[0].click();", elem)
            print("[INFO] 成功點擊 clickable-area")
        except Exception as e:
            print("[ERROR] clickable-area click failed:", e)

    def click_go_back(self):
        try:
            back_link = WebDriverWait(self.driver, WAIT_TIMEOUT, WAIT_POLL).until(
                EC.element_to_be_clickable((By.XPATH, "//a[span[text()='返回課程']]"))
            )
            try:
                back_link.click()
            except ElementClickInterceptedException:
                driver.execute_script("arguments[0].click();", back_link)
            print("[INFO] 點擊返回課程成功")
        except Exception as e:
            print("[WARN] 返回課程點擊失敗:", e)

    def click_go_back_to_course_list(self):
        try:
            link = WebDriverWait(self.driver, WAIT_TIMEOUT, WAIT_POLL).until(
                EC.element_to_be_clickable((By.XPATH, "//a[@class='go-back-link' and span[text()='返回']]"))
            )
            try:
                link.click()
            except ElementClickInterceptedException:
                driver.execute_script("arguments[0].click();", link)
            print("[INFO] 點擊返回成功")
        except Exception as e:
            print("[WARN] 返回課程列表點擊失敗:", e)

    def load_cookies(self):
        path = os.path.join("resource", "cookies", self.cookie_path)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        if os.path.isfile(path):
            with open(path, 'r', encoding='utf-8-sig') as f:
                return json.load(f)
        return []

    def save_cookies(self, cookies):
        path = os.path.join("resource", "cookies", self.cookie_path)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8-sig') as f:
            json.dump(cookies, f, ensure_ascii=False)

    def save_captcha_image(self):
        img = self.driver.execute_script(
            """
            let e = arguments[0], c = document.createElement('canvas');
            c.width = e.width; c.height = e.height;
            c.getContext('2d').drawImage(e, 0, 0);
            return c.toDataURL('image/png').split(',')[1];
            """,
            self.driver.find_element(By.XPATH, "//form//img[contains(@src,'captcha')]")
        )
        with open('captcha.png', 'wb') as f:
            f.write(base64.b64decode(img))

    def handle_login(self, username, password):
        self.driver.get(self.url)
        self.driver.find_element(By.ID, 'user_name').send_keys(username)
        self.driver.find_element(By.ID, 'password').send_keys(password)
        self.save_captcha_image()
        code = input('captcha: ')
        self.driver.find_element(By.NAME, 'captcha_code').send_keys(code)
        self.driver.find_element(By.ID, 'submit').click()
        time.sleep(3)
        self.save_cookies(self.driver.get_cookies())

    def autologin(self, username=None, password=None):
        self.driver.get(self.url)
        if username is None:
            username = cfg.get('user_name', '')
        if password is None:
            password = cfg.get('password', '')
        time.sleep(2)
        try:
            self.driver.find_element(By.CSS_SELECTOR, 'div.login-content.ng-scope')
            cookies = self.load_cookies()
            if cookies:
                self.driver.delete_all_cookies()
                for ck in cookies:
                    self.driver.add_cookie(ck)
                self.driver.refresh()
                time.sleep(5)
                if not self.driver.find_elements(By.CSS_SELECTOR, 'div.login-content.ng-scope'):
                    print('[SUCCESS] via cookies')
                    return
            print('[INFO] manual login required')
            self.handle_login(username, password)
            if not self.driver.find_elements(By.CSS_SELECTOR, 'div.login-content.ng-scope'):
                print('[SUCCESS] manual login')
            else:
                print('[ERROR] login failed')
        except:
            print('[INFO] already logged in')

    def quit(self):
        self.driver.quit()
# ⏩ 省略 class StealthExtractor, VisitDurationModifier, MitmProxyManager, Eel 等定義（保持與上傳版本一致）

# 🧩 Main 區段補齊並整合點擊流程：
if __name__ == '__main__':
    cfg = {}
    fn = os.path.join("config", "eebot.cfg")
    if os.path.isfile(fn):
        with open(fn, 'r', encoding='utf-8-sig') as f:
            for ln in f:
                ln = ln.strip()
                if not ln or ln.startswith('#') or '=' not in ln:
                    continue
                k, v = ln.split('=', 1)
                cfg[k.strip()] = v.strip().strip('"').strip("'")

    T = cfg['target_http']
    D = cfg['execute_file']
    C = cfg['cookies_file']
    U = cfg['user_name']
    P = cfg['password']
    m = cfg.get('modify_visits', 'n').lower() == 'y'
    s = cfg.get('silent_mitm', 'n').lower() == 'y'
    l = cfg.get('log_save', 'n').lower() == 'y'
    h = cfg.get('listen_host', '127.0.0.1')
    pn = int(cfg.get('listen_port', '8080'))

    StealthExtractor().run()
    mitm = MitmProxyManager(h, pn, m, silent=s, log_save=l)
    bot = None
    try:
        mitm.start()
        bot = Eel(T, D, C, h, pn)
        bot.autologin()
        WebDriverWait(bot.driver, WAIT_TIMEOUT, WAIT_POLL).until(
            EC.presence_of_element_located((By.LINK_TEXT, "我的課程"))
        )

        try:
            elem = WebDriverWait(bot.driver, WAIT_TIMEOUT, WAIT_POLL).until(
                EC.element_to_be_clickable((By.LINK_TEXT, "我的課程"))
            )
            try:
                elem.click()
            except ElementClickInterceptedException:
                driver.execute_script("arguments[0].click();", elem)

            def safe_click(link_text, desc, delay_after=7.0):
                try:
                    elem = WebDriverWait(bot.driver, WAIT_TIMEOUT, WAIT_POLL).until(
                        EC.element_to_be_clickable((By.LINK_TEXT, link_text))
                    )
                    bot.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", elem)
                    time.sleep(delay_after)
                    try:
                        elem.click()
                        print(f"[INFO] {desc} 點擊成功")
                    except Exception as e:
                        print(f"[WARN] {desc} 點擊失敗，改用 JS click: {e}")
                        try:
                            js_elem = bot.driver.find_element(By.LINK_TEXT, link_text)
                            bot.driver.execute_script("arguments[0].click();", js_elem)
                            print(f"[INFO] {desc} JS click 成功")
                        except Exception as err:
                            print(f"[ERROR] {desc} JS click 仍然失敗: {err}")
                except Exception as e:
                    print(f"[ERROR] 找不到 {desc}: {e}")
                    
            # 🔰 新增：點擊「預防執行職務遭受不法侵害(員工)(114年度)」                            
            safe_click("預防執行職務遭受不法侵害(員工)(114年度)", "預防執行職務遭受不法侵害(員工)(114年度)")
            safe_click("預防執行職務遭受不法侵害(員工)(上)", "預防執行職務遭受不法侵害(員工)(上)")
            # 點擊返回課程（goBackCourse(369)）
            try:
                back_course = WebDriverWait(bot.driver, WAIT_TIMEOUT, WAIT_POLL).until(
                    EC.element_to_be_clickable((By.XPATH, "//a[@ng-click='goBackCourse(369)']"))
                )
                try:
                    back_course.click()
                except ElementClickInterceptedException:
                    driver.execute_script("arguments[0].click();", back_course)
                print('[INFO] 返回課程 369 成功')
            except Exception as e:
                print('[ERROR] 返回課程 369 點擊失敗:', e)
            bot.click_go_back_to_course_list()
            
            # 🔰 新增：點擊「資通安全學程課程(114年度)」            
            safe_click("資通安全學程課程(114年度)", "資通安全學程課程(114年度)")
            safe_click("個資保護認知宣導與案例分享教育訓練", "個資保護認知宣導與案例分享教育訓練")
            # 點擊返回課程（goBackCourse(365)）
            try:
                back_course = WebDriverWait(bot.driver, WAIT_TIMEOUT, WAIT_POLL).until(
                    EC.element_to_be_clickable((By.XPATH, "//a[@ng-click='goBackCourse(365)']"))
                )
                try:
                    back_course.click()
                except ElementClickInterceptedException:
                    driver.execute_script("arguments[0].click();", back_course)
                print('[INFO] 返回課程 365 成功')
            except Exception as e:
                print('[ERROR] 返回課程 365 點擊失敗:', e)
            bot.click_go_back_to_course_list()

            # 🔰 新增：點擊「環境教育學程課程(綠色金融)(114年度)」
            safe_click("環境教育學程課程(綠色金融)(114年度)", "環境教育學程課程(綠色金融)(114年度)")
            safe_click("永續金融與環境教育", "永續金融與環境教育")

            # 點擊返回課程（goBackCourse(367)）
            try:
                back_course = WebDriverWait(bot.driver, WAIT_TIMEOUT, WAIT_POLL).until(
                    EC.element_to_be_clickable((By.XPATH, "//a[@ng-click='goBackCourse(367)']"))
                )
                try:
                    back_course.click()
                except ElementClickInterceptedException:
                    driver.execute_script("arguments[0].click();", back_course)
                print('[INFO] 返回課程 367 成功')
            except Exception as e:
                print('[ERROR] 返回課程 367 點擊失敗:', e)
            bot.click_go_back_to_course_list()

            # 新增課程：高齡客戶投保權益保障
            safe_click("高齡客戶投保權益保障(114年度)", "高齡客戶投保權益保障(114年度)")
            safe_click("高齡客戶投保權益保障", "高齡客戶投保權益保障")
            try:
                back_course = WebDriverWait(bot.driver, WAIT_TIMEOUT, WAIT_POLL).until(
                    EC.element_to_be_clickable((By.XPATH, "//a[@ng-click='goBackCourse(452)']"))
                )
                try:
                    back_course.click()
                except ElementClickInterceptedException:
                    driver.execute_script("arguments[0].click();", back_course)
                print('[INFO] 返回課程 452 成功')
            except Exception as e:
                print('[ERROR] 返回課程 452 點擊失敗:', e)
            bot.click_go_back_to_course_list()

            # 新增課程：性別平等工作法...
            safe_click("性別平等工作法、性騷擾防治法及相關子法修法重點與實務案例(114年度)", "性別平等工作法、性騷擾防治法及相關子法修法重點與實務案例(114年度)")
            safe_click("性別平等工作法及相關子法修法重點與實務案例", "性別平等工作法及相關子法修法重點與實務案例")
            try:
                back_course = WebDriverWait(bot.driver, WAIT_TIMEOUT, WAIT_POLL).until(
                    EC.element_to_be_clickable((By.XPATH, "//a[@ng-click='goBackCourse(465)']"))
                )
                try:
                    back_course.click()
                except ElementClickInterceptedException:
                    driver.execute_script("arguments[0].click();", back_course)
                print('[INFO] 返回課程 465 成功')
            except Exception as e:
                print('[ERROR] 返回課程 465 點擊失敗:', e)
            bot.click_go_back_to_course_list()

            # 新增課程：壽險業務員在職訓練學程
            safe_click("壽險業務員在職訓練學程課程及測驗(114年度)", "壽險業務員在職訓練學程課程及測驗(114年度)")
            safe_click("一、壽險商品介紹", "一、壽險商品介紹")
            try:
                back_course = WebDriverWait(bot.driver, WAIT_TIMEOUT, WAIT_POLL).until(
                    EC.element_to_be_clickable((By.XPATH, "//a[@ng-click='goBackCourse(454)']"))
                )
                try:
                    back_course.click()
                except ElementClickInterceptedException:
                    driver.execute_script("arguments[0].click();", back_course)
                print('[INFO] 返回課程 454 成功')
            except Exception as e:
                print('[ERROR] 返回課程 454 點擊失敗:', e)
            bot.click_go_back_to_course_list()

            # 新增課程：公平待客與洗錢防制
            safe_click("金融服務業公平待客原則＆洗錢防制及打擊資恐教育訓練(114年度)", "金融服務業公平待客原則＆洗錢防制及打擊資恐教育訓練(114年度)")
            safe_click("防制洗錢及打擊資助恐怖主義", "防制洗錢及打擊資助恐怖主義")
            try:
                back_course = WebDriverWait(bot.driver, WAIT_TIMEOUT, WAIT_POLL).until(
                    EC.element_to_be_clickable((By.XPATH, "//a[@ng-click='goBackCourse(450)']"))
                )
                try:
                    back_course.click()
                except ElementClickInterceptedException:
                    driver.execute_script("arguments[0].click();", back_course)
                print('[INFO] 返回課程 450 成功')
            except Exception as e:
                print('[ERROR] 返回課程 450 點擊失敗:', e)
            bot.click_go_back_to_course_list()

            # 新增課程：性騷擾勿擾：談機關防治責任與案件處理實務(114年度)
            safe_click("性騷擾勿擾：談機關防治責任與案件處理實務(114年度)", "性騷擾勿擾：談機關防治責任與案件處理實務(114年度)")
            safe_click("性騷擾勿擾：談機關防治責任與案件處理實務", "性騷擾勿擾：談機關防治責任與案件處理實務")
            try:
                back_course = WebDriverWait(bot.driver, WAIT_TIMEOUT, WAIT_POLL).until(
                    EC.element_to_be_clickable((By.XPATH, "//a[@ng-click='goBackCourse(466)']"))
                )
                try:
                    back_course.click()
                except ElementClickInterceptedException:
                    driver.execute_script("arguments[0].click();", back_course)
                print('[INFO] 返回課程 466 成功')
            except Exception as e:
                print('[ERROR] 返回課程 466 點擊失敗:', e)
            bot.click_go_back_to_course_list()

            # 新增課程：預防執行職務遭受不法侵害(主管)(114年度)
            safe_click("預防執行職務遭受不法侵害(主管)(114年度)", "預防執行職務遭受不法侵害(主管)(114年度)")
            safe_click("預防執行職務遭受不法侵害(主管)(上)", "預防執行職務遭受不法侵害(主管)(上)")
            try:
                back_course = WebDriverWait(bot.driver, WAIT_TIMEOUT, WAIT_POLL).until(
                    EC.element_to_be_clickable((By.XPATH, "//a[@ng-click='goBackCourse(368)']"))
                )
                try:
                    back_course.click()
                except ElementClickInterceptedException:
                    driver.execute_script("arguments[0].click();", back_course)
                print('[INFO] 返回課程 368 成功')
            except Exception as e:
                print('[ERROR] 返回課程 368 點擊失敗:', e)
            bot.click_go_back_to_course_list()

            # ⏹ 結束擴充課程流程區塊


        except Exception as e:
            print('[WARN] 主流程點擊失敗:', e)
        try:
            WebDriverWait(bot.driver, WAIT_TIMEOUT, WAIT_POLL).until(lambda d: False)
        except:
            pass
        bot.quit()
    except Exception as err:
        print('[ERROR]', err)
    finally:
        mitm.stop()
