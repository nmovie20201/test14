from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import time
import json
import os

# --- [ CONFIG ] ---
CHROMEDRIVER_PATH = "/data/data/com.termux/files/usr/bin/chromedriver"
CHROME_PATH = "/data/data/com.termux/files/usr/bin/chromium-browser"
TARGET_URL = "https://embed.nana2play.com/e/688667688667"

def main():
    print("=" * 65)
    print("   🍓 NANA2PLAY REAPER - [BYPASSING BOT DETECTION]")
    print("=" * 65)

    options = Options()
    options.binary_location = CHROME_PATH
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    # เปิด Performance Log เพื่อดักฟัง m3u8
    options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})

    driver = webdriver.Chrome(service=Service(CHROMEDRIVER_PATH), options=options)
    
    try:
        print(f"[*] กำลังบุกไปที่: {TARGET_URL}")
        driver.get(TARGET_URL)
        
        # รอมันรัน JavaScript และโหลดวิดีโอ (30 วินาที)
        print("[*] กำลังรอกระบวนการดีดลิ้งค์ m3u8 (30 วินาที)...")
        time.sleep(30)
        
        print("\n--- [ ผลการสแกนทราฟฟิก ] ---")
        logs = driver.get_log('performance')
        
        found_links = set()
        for entry in logs:
            msg = json.loads(entry['message'])['message']
            if 'params' in msg and 'request' in msg['params']:
                url = msg['params']['request']['url']
                # ค้นหาลิ้งค์สตรีม
                if ".m3u8" in url or ".mpd" in url or "get_sources" in url:
                    found_links.add(url)

        if found_links:
            for link in found_links:
                print(f"🔥 [FOUND] {link}")
        else:
            print("❌ ไม่เจอลิ้งค์สตรีมในทราฟฟิกเลยว่ะเพื่อน")
            # ถ่ายรูปดูหน่อยว่าหน้าตามันเป็นยังไง
            driver.save_screenshot("nana_fail.png")
            print("[!] ถ่ายรูปหน้าจอไว้ให้แล้วที่ nana_fail.png")

    except Exception as e:
        print(f"❌ พังพินาศ: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
