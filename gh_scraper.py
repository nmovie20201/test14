import requests
import re
import json
import os
from datetime import datetime

# --- [ CONFIG ] ---
INPUT_JSON = "nanamovie_Movie___Thai_Sub.json"
OUTPUT_M3U = "live_playlist.m3u"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
REFERER = "https://nanamovies.org/"

def unpack_js(packed_js):
    """ถอดรหัส JS Packer (สูตรสำเร็จ)"""
    try:
        match = re.search(r"}\('(.*)',\s*(\d+),\s*(\d+),\s*'(.*)'\.split\('\|'\)", packed_js)
        if not match: return None
        p, a, c, k = match.groups()
        a, c, k = int(a), int(c), k.split('|')
        def e_func(c):
            return ('' if c < a else e_func(int(c / a))) + (chr(c % a + 161) if c % a > 35 else "0123456789abcdefghijklmnopqrstuvwxyz"[c % a])
        dictionary = {e_func(i): k[i] or e_func(i) for i in range(c)}
        return re.sub(r'\b\w+\b', lambda m: dictionary.get(m.group(0), m.group(0)), p)
    except: return None

def get_real_m3u8(url):
    """แปลง nanaplayer.com -> .m3u8"""
    try:
        r = requests.get(url, headers={'User-Agent': UA, 'Referer': REFERER}, timeout=10)
        unpacked = unpack_js(r.text)
        if unpacked:
            match = re.search(r'(https?://[^\s\'"]+\.m3u8\?[^\s\'"]+)', unpacked)
            if match: return match.group(1).replace('\\', '')
    except: pass
    return url # ถ้าแปลงไม่ได้ คืนค่าเดิม

def main():
    print(f"[*] เริ่มปฏิบัติการ: {datetime.now()}")
    playlist = ["#EXTM3U\n"]

    # 1. จัดการจากไฟล์ JSON (หนังไทยซับ)
    if os.path.exists(INPUT_JSON):
        print(f"[*] กำลังแงะ {INPUT_JSON}...")
        with open(INPUT_JSON, "r", encoding="utf-8") as f:
            data = json.load(f)
        for item in data.get("groups", []):
            name = item.get("name", "Unknown")
            stations = item.get("stations", [])
            if stations:
                raw_url = stations[0].get("url", "")
                if "nanaplayer.com" in raw_url:
                    print(f"  > กำลังปั๊มลิ้งค์สด: {name}")
                    final_url = get_real_m3u8(raw_url)
                else:
                    final_url = raw_url
                
                playlist.append(f'#EXTINF:-1 tvg-logo="{item.get("image","")}" group-title="Thai Sub", {name}\n')
                playlist.append(f"{final_url}|Referer=https://nanaplayer.com/&User-Agent={UA}\n")

    # บันทึกไฟล์ตัวจบ
    with open(OUTPUT_M3U, "w", encoding="utf-8") as f:
        f.writelines(playlist)
    
    print(f"✅ ภารกิจสำเร็จ! ได้ไฟล์ {OUTPUT_M3U}")

if __name__ == "__main__":
    main()
