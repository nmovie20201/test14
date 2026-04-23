import requests
import re
import json
import os
from urllib.parse import quote as url_quote

# --- [ CONFIG ] ---
TARGET_URL = "https://embed.nana2play.com/e/688667688667"
REFERER = "https://nanamovies.org/"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

def get_p2p_m3u8(url):
    print("=" * 65)
    print("   🍓 NANA P2P RESOLVER - [THE M3U8 SNIPER]")
    print("=" * 65)
    
    session = requests.Session()
    headers = {'User-Agent': UA, 'Referer': REFERER}
    
    try:
        # 1. บุกหน้า Embed เพื่อเอา ID และ Token
        print(f"[*] กำลังบุกไปที่: {url}")
        r = session.get(url, headers=headers, timeout=15)
        
        # ค้นหาค่า ID และ Token ในฟังก์ชัน JavaScript
        # ตัวอย่าง: loadMovie('123', 'abc...') หรือ loadSerieEpisode(...)
        match = re.search(r"(?:loadMovie|loadSerieEpisode|loadMovieServer)\s*\(\s*['\"]?(\d+)['\"]?\s*(?:,\s*['\"]?(\d+)['\"]?\s*)?,\s*['\"]?([a-z0-9]+)['\"]?\s*\)", r.text)
        
        if not match:
            print("❌ ไม่เจอรหัสลับในหน้าเว็บว่ะเพื่อน!")
            # ลองใช้ไม้ตายสำรอง: หา ID จาก URL
            mid = url.split('/')[-1]
            print(f"[!] ลองใช้ ID จาก URL แทน: {mid}")
            # ถ้าไม่มี Token จริงๆ เราต้องมุดหาให้เจอ
            return None

        # แกะรหัส
        if match.lastindex == 3:
            mid, epid, token = match.group(1), match.group(2), match.group(3)
            ajax_url = f"https://embed.nana2play.com/ajax/serie/get_sources/{mid}/{epid}/{token}"
        else:
            mid, token = match.group(1), match.group(3)
            ajax_url = f"https://embed.nana2play.com/ajax/movie/get_sources/{mid}/{token}"

        print(f"✅ เจอรหัสลับ! ID={mid}, TOKEN={token[:10]}...")
        print(f"[*] กำลังเบิกทางลิ้งค์ m3u8 จาก API ลับ...")
        
        # 2. เรียก AJAX ชิงลิ้งค์มหาเทพ
        headers['X-Requested-With'] = 'XMLHttpRequest'
        r_ajax = session.get(ajax_url, headers=headers, timeout=10)
        
        if r_ajax.status_code == 200:
            data = r_ajax.json()
            source = data.get('sources')
            if source:
                # แก้ลิ้งค์ให้เป็นมหาเทพสไตล์ (ลบ /e/ ออกถ้ามี)
                m3u8_final = source.replace("/e/", "/")
                print("\n" + "="*50)
                print("💎 [BINGO!] ลิ้งค์ m3u8 ตัวจบของมึงมาแล้ว!")
                print(f"📌 URL: {m3u8_final}")
                print("="*50)
                return m3u8_final
            else:
                print("❌ API ตอบกลับมาแต่ไม่มีลิ้งค์สตรีมว่ะเพื่อน!")
        else:
            print(f"❌ API พัง! Status: {r_ajax.status_code}")

    except Exception as e:
        print(f"❌ พังพินาศ: {e}")
    return None

if __name__ == "__main__":
    link = get_p2p_m3u8(TARGET_URL)
    if link:
        # เจนไฟล์ M3U เล็กๆ ให้ลองรันใน OTT
        with open("test14/nana_test.m3u", "w") as f:
            f.write("#EXTM3U\n")
            f.write(f"#EXTINF:-1, Nana P2P Stream\n")
            f.write(f"{link}|Referer={REFERER}&User-Agent={UA}\n")
        print(f"\n📁 ไฟล์ทดสอบอยู่ที่: test14/nana_test.m3u")
