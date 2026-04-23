import requests
import re
import os

# --- [ CONFIG ] ---
SOURCE_FILE = "movies.txt"
OUTPUT_M3U = "live_playlist.m3u"
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
        return re.sub(r'\b\w+\b', lambda m: dictionary.get(m.group(0), m.group(0)), p)

    match = re.search(r"}\('(.*)',\s*(\d+),\s*(\d+),\s*'(.*)'\.split\('\|'\)", packed_js)
    if match:
        p, a, c, k = match.groups()
        return decode(p, int(a), int(c), k.split('|'), 0, {})
    return None

def resolve(url):
    try:
        r = requests.get(url, headers={'User-Agent': UA, 'Referer': 'https://nanamovies.org/'}, timeout=15)
        if "eval(function(p,a,c,k,e,d)" in r.text:
            unpacked = unpack_js(r.text)
            if unpacked:
                match = re.search(r'(https?://[^\s\'"]+\.m3u8\?[^\s\'"]+)', unpacked)
                if match: return match.group(1).replace('\\', '')
    except: pass
    return None

def main():
    if not os.path.exists(SOURCE_FILE): return
    
    with open(SOURCE_FILE, "r") as f:
        urls = [line.strip() for line in f if line.strip()]

    with open(OUTPUT_M3U, "w", encoding='utf-8') as f:
        f.write("#EXTM3U\n")
        for url in urls:
            print(f"[*] Resolving: {url}")
            m3u8_url = resolve(url)
            if m3u8_url:
                title = url.split('/')[-1]
                f.write(f"#EXTINF:-1, Nana Movie {title}\n")
                f.write(f"{m3u8_url}|Referer=https://nanaplayer.com/&User-Agent={UA}\n")
                print(f"  ✅ Done!")

if __name__ == "__main__":
    main()
