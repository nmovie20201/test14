import requests
import re
import json
import os
import urllib3

# ปิด Warning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- [ CONFIG ] ---
# ใช้ลิ้งค์ตรงๆ ตามที่มึงบอกเป๊ะ!
TARGET_URL = "https://nanaplayer.com/99gsmeiw4dul"
REFERER = "https://nanamovies.org/"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

def unpack_js(packed_js):
    """ฟังก์ชันถอดรหัส JS Packer (p,a,c,k,e,d)"""
    def decode(p, a, c, k, e, d):
        def e_func(c):
            return ('' if c < a else e_func(int(c / a))) + \
                   (chr(c % a + 161) if c % a > 35 else "0123456789abcdefghijklmnopqrstuvwxyz"[c % a])
        
        dictionary = {}
        while c > 0:
            c -= 1
            dictionary[e_func(c)] = k[c] if k[c] else e_func(c)
        
        result = re.sub(r'\b\w+\b', lambda m: dictionary.get(m.group(0), m.group(0)), p)
        return result

    match = re.search(r"}\('(.*)',\s*(\d+),\s*(\d+),\s*'(.*)'\.split\('\|'\)", packed_js)
    if match:
        p, a, c, k = match.groups()
        return decode(p, int(a), int(c), k.split('|'), 0, {})
    return None

def main():
    print("=" * 65)
    print("   🍓 NANAPLAYER DIRECT SNIPER - [NO MAPPING ERROR]")
    print("=" * 65)
    
    headers = {'User-Agent': UA, 'Referer': REFERER}
    
    try:
        print(f"[*] กำลังบุกเข้าลิ้งค์ตรง: {TARGET_URL}")
        r = requests.get(TARGET_URL, headers=headers, timeout=15)
        
        # ค้นหาโค้ดที่ถูก Pack
        if "eval(function(p,a,c,k,e,d)" in r.text:
            print("[*] เจอโค้ด JS Packer! กำลังปลดล็อครหัสลับ...")
            unpacked = unpack_js(r.text)
            
            if unpacked:
                # สแกนหาลิ้งค์ .m3u8 พร้อมพารามิเตอร์ (tt, tuid, ฯลฯ)
                match = re.search(r'(https?://[^\s\'"]+\.m3u8\?[^\s\'"]+)', unpacked)
                if match:
                    m3u8_url = match.group(1).replace('\\', '')
                    print("\n" + "="*50)
                    print("💎 [BINGO!] ลิ้งค์ m3u8 ตัวจบหลุดออกมาแล้ว!")
                    print(f"📌 URL: {m3u8_url}")
                    print("="*50)
                    
                    # เจนไฟล์ M3U ให้พร้อมใช้
                    with open("test14/nana_direct_victory.m3u", "w") as f:
                        f.write("#EXTM3U\n")
                        f.write("#EXTINF:-1, Nana Direct Victory\n")
                        f.write(f"{m3u8_url}|Referer=https://nanaplayer.com/&User-Agent={UA}\n")
                    print(f"\n📁 ไฟล์ตัวจบอยู่ที่: test14/nana_direct_victory.m3u")
                else:
                    print("❌ ถอดรหัสได้แต่หาลิ้งค์ m3u8 ไม่เจอว่ะเพื่อน!")
            else:
                print("❌ ถอดรหัส JS Packer ล้มเหลว!")
        else:
            print("❌ ไม่เจอโค้ดลับในหน้านี้ว่ะ หรือมันบล็อกกูแล้ว?")
            
    except Exception as e:
        print(f"❌ พังพินาศ: {e}")

if __name__ == "__main__":
    main()
