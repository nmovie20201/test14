import requests
import json
import os
import urllib.parse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

# --- [ CONFIG ] ---
CHROMEDRIVER_PATH = "/data/data/com.termux/files/usr/bin/chromedriver"
CHROME_PATH = "/data/data/com.termux/files/usr/bin/chromium-browser"
USER_DATA_DIR = "/data/data/com.termux/files/home/.ais_chrome_profile"
OUTPUT_M3U = "/storage/emulated/0/Download/python/0mpd/nana_victory.m3u"
TARGET_URL = "https://nanamovies.org/" # เริ่มจากหน้าแรกเลย!

def main():
    print("=" * 65)
    print("   🍓 NANA ULTIMATE INTERCEPTOR - [THE FINAL HARVEST]")
    print("=" * 65)

    options = Options()
    options.binary_location = CHROME_PATH
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument(f"--user-data-dir={USER_DATA_DIR}")
    options.add_argument("--window-size=1920,1080")
    options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})

    driver = webdriver.Chrome(service=Service(CHROMEDRIVER_PATH), options=options)
    
    try:
        print("[*] กำลังบุกเข้าหน้าแรกเพื่อหาหนังตัวอย่าง...")
        driver.get(TARGET_URL)
        import time
        time.sleep(15)
        
        # 1. ค้นหาทุกลิ้งค์หนังที่น่าสนใจ
        movies = driver.execute_script("""
            let links = [];
            document.querySelectorAll('a').forEach(a => {
                if(a.href.includes('nanamovies.org') && a.href.length > 30) {
                    links.push({title: a.innerText, url: a.href});
                }
            });
            return links;
        """)
        
        print(f"✅ เจอเป้าหมาย {len(movies)} เรื่อง! เริ่มการเจาะระบบทีละเรื่อง...")
        
        with open(OUTPUT_M3U, "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")
            
            for m in movies[:10]: # ลองสุ่ม 10 เรื่องแรก
                print(f"[*] กำลังบุกส่อง: {m['title'][:30]}...")
                driver.get(m['url'])
                time.sleep(15)
                
                # ดักฟัง Network ทุกลมหายใจ!
                logs = driver.get_log('performance')
                for entry in logs:
                    msg = json.loads(entry['message'])['message']
                    if 'params' in msg and 'request' in msg['params']:
                        url = msg['params']['request']['url']
                        if ".m3u8" in url or ".mpd" in url:
                            print(f"    🔥 [BINGO!] ชิงลิ้งค์สำเร็จ: {m['title']}")
                            f.write(f"#EXTINF:-1, {m['title']}\n")
                            f.write(f"{url}|Referer=https://nanaplayer.com/&User-Agent=Mozilla/5.0\n")
                            break
                            
        print(f"\n🎉 ภารกิจเสร็จสิ้น! ไฟล์อยู่ที่: {OUTPUT_M3U}")

    except Exception as e:
        print(f"❌ พังพินาศ: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
