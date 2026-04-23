import requests
import re
import os

# --- [ CONFIG ] ---
TARGET_URL = "https://nanaplayer.com/99gsmeiw4dul"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

def unpack_js(packed_js):
    """ฟังก์ชันถอดรหัส JS Packer (p,a,c,k,e,d)"""
    def decode(p, a, c, k, e, d):
        def e_func(c):
            return ('' if c < a else e_func(int(c / a))) + \
                   (chr(c % a + 161) if c % a > 35 else "0123456789abcdefghijklmnopqrstuvwxyz"[c % a])
        
        # สร้าง Dict สำหรับ Mapping
        dictionary = {}
        while c > 0:
            c -= 1
            dictionary[e_func(c)] = k[c] if k[c] else e_func(c)
        
        # แทนที่คำใน P
        result = re.sub(r'\b\w+\b', lambda m: dictionary.get(m.group(0), m.group(0)), p)
        return result

    # แกะพารามิเตอร์จากสตริง eval
    match = re.search(r"}\('(.*)',\s*(\d+),\s*(\d+),\s*'(.*)'\.split\('\|'\)", packed_js)
    if match:
        p, a, c, k = match.groups()
        return decode(p, int(a), int(c), k.split('|'), 0, {})
    return None

def get_nanaplayer_m3u8(url):
    print("=" * 65)
    print("   🍓 NANAPLAYER UNPACKER - [THE M3U8 REAPER]")
    print("=" * 65)
    
    headers = {'User-Agent': UA, 'Referer': 'https://nanamovies.org/'}
    
    try:
        print(f"[*] กำลังบุกไปที่: {url}")
        r = requests.get(url, headers=headers, timeout=15)
        
        # ค้นหาโค้ดที่ถูก Pack
        if "eval(function(p,a,c,k,e,d)" in r.text:
            print("[*] เจอโค้ด JS Packer! กำลังเริ่มถอดรหัส...")
            unpacked = unpack_js(r.text)
            
            if unpacked:
                # ค้นหาลิ้งค์ m3u8 ในโค้ดที่ถอดรหัสแล้ว
                # รูปแบบ: file:"https://...master.m3u8?..."
                match = re.search(r'file:"(https?://[^"]+\.m3u8[^"]*)"', unpacked)
                if not match:
                    # ลองหาแบบกว้างๆ
                    match = re.search(r'(https?://[^"]+\.m3u8[^"]*)', unpacked)

                if match:
                    m3u8_url = match.group(1).replace('\\', '')
                    print("\n" + "="*50)
                    print("💎 [BINGO!] ลิ้งค์ m3u8 ตัวจบของมึงมาแล้ว!")
                    print(f"📌 URL: {m3u8_url}")
                    print("="*50)
                    return m3u8_url
                else:
                    print("❌ ถอดรหัสได้แต่หาลิ้งค์ m3u8 ไม่เจอว่ะเพื่อน!")
            else:
                print("❌ ถอดรหัส JS Packer ล้มเหลว!")
        else:
            print("❌ ไม่เจอโค้ด JS Packer ในหน้านี้ว่ะ")
            
    except Exception as e:
        print(f"❌ พังพินาศ: {e}")
    return None

if __name__ == "__main__":
    link = get_nanaplayer_m3u8(TARGET_URL)
    if link:
        # เจนไฟล์ M3U เล็กๆ ให้ลองรันใน OTT
        with open("test14/nanaplayer_test.m3u", "w") as f:
            f.write("#EXTM3U\n")
            f.write(f"#EXTINF:-1, Nanaplayer Stream\n")
            f.write(f"{link}|Referer=https://nanaplayer.com/&User-Agent={UA}\n")
        print(f"\n📁 ไฟล์ทดสอบอยู่ที่: test14/nanaplayer_test.m3u")
