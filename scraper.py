import requests
from bs4 import BeautifulSoup
import os
import re

# --- [ CONFIG ] ---
BASE_URL = "https://nanamovies.org/"
OUTPUT_M3U = "nanamovies.m3u"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": BASE_URL
}

def get_movie_links():
    """กวาดรายชื่อหนังแบบเจาะจงโครงสร้าง WordPress Movie"""
    print(f"[*] กำลังกวาดรายการหนังจาก: {BASE_URL}")
    try:
        r = requests.get(BASE_URL, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(r.text, 'html.parser')
        
        movies = []
        # โดยปกติหนังในเว็บแนวนี้จะอยู่ในแท็ก article หรือ div ที่มีคลาสเกี่ยวข้อง
        for item in soup.find_all(['article', 'div'], class_=re.compile(r'post|movie|item')):
            a_tag = item.find('a', href=True)
            if not a_tag: continue
            
            href = a_tag['href']
            # กรองลิ้งค์ขยะ
            if BASE_URL in href and not any(x in href for x in ["/category/", "/tag/", "/author/", "/page/"]) and href != BASE_URL:
                # พยายามหาชื่อหนังจาก img alt หรือ text
                img = item.find('img', alt=True)
                title = img['alt'] if img else a_tag.get_text().strip()
                
                if not title:
                    # ลองหาในพวก h2, h3
                    title_tag = item.find(['h2', 'h3'])
                    if title_tag: title = title_tag.get_text().strip()
                
                if title and len(title) > 2:
                    movies.append({"title": title, "url": href})
        
        # ท่าไม้ตายสุดท้าย: ถ้ายังไม่ได้ ให้กวาดทุกลิ้งค์ที่ดูเหมือนหน้าหนัง
        if not movies:
            for a in soup.find_all('a', href=True):
                href = a['href']
                if BASE_URL in href and len(href.split('/')) == 4 and not any(x in href for x in ["/category/", "/tag/"]):
                    title = a.get_text().strip() or a.get('title')
                    if title and len(title) > 5:
                        movies.append({"title": title, "url": href})

        # ลบลิ้งค์ซ้ำ
        unique_movies = []
        seen_urls = set()
        for m in movies:
            if m['url'] not in seen_urls:
                unique_movies.append(m)
                seen_urls.add(m['url'])
        
        return unique_movies
    except Exception as e:
        print(f"❌ พังตอนดึงลิ้งค์: {e}")
        return []

def get_stream_url(movie_url):
    """มุดเข้าหน้าหนังเพื่อแงะลิ้งค์จากสคริปต์"""
    print(f"  [*] มุดเข้าส่องหนัง: {movie_url[:50]}...")
    try:
        r = requests.get(movie_url, headers=HEADERS, timeout=15)
        
        # 1. ลองหาลิ้งค์ Embed ใน iframe
        match = re.search(r'src="(https?://(filemoon|vidhide|iframely|vidsrc|player|embed)[^"]+)"', r.text)
        if match: return match.group(1)
        
        # 2. ลองหาลิ้งค์ที่ซ่อนอยู่ใน Script (Script Mining)
        # มองหาพวกพารามิเตอร์ "file": "http..." หรือ "source": "http..."
        scripts = re.findall(r'<script[^>]*>(.*?)</script>', r.text, re.DOTALL)
        for script in scripts:
            # ค้นหาลิ้งค์ .m3u8 หรือลิ้งค์วิดีโออื่นๆ
            stream_matches = re.findall(r'(https?://[^\s\'"]+\.(m3u8|mp4|ts))', script)
            if stream_matches:
                return stream_matches[0][0]
            
            # ค้นหาลิ้งค์ Embed ที่แอบใน String
            embed_matches = re.findall(r'(https?://(filemoon|vidhide|vidsrc|iframely|play)[^\s\'"]+)', script)
            if embed_matches:
                return embed_matches[0][0]
                
    except: pass
    return None

def main():
    print("=" * 65)
    print("   🍓 NANAMOVIES SCRAPER - [GITHUB ACTIONS READY]")
    print("=" * 65)
    
    movies = get_movie_links()
    print(f"✅ เจอเป้าหมายทั้งหมด {len(movies)} เรื่อง")
    
    found_count = 0
    with open(OUTPUT_M3U, "w", encoding='utf-8') as f:
        f.write("#EXTM3U\n")
        
        for movie in movies[:20]: # ทดลองกวาด 20 เรื่องแรกก่อนเพื่อนรัก
            stream_url = get_stream_url(movie['url'])
            if stream_url:
                f.write(f"#EXTINF:-1 group-title=\"Nana Movies\", {movie['title']}\n")
                f.write(f"{stream_url}\n")
                print(f"    🔥 [FOUND] {movie['title']}")
                found_count += 1
                
    print("-" * 65)
    print(f"🎉 ภารกิจสำเร็จ! ขุดมาได้ {found_count} เรื่อง")
    print(f"📁 ไฟล์อยู่ที่: {OUTPUT_M3U}")
    print("=" * 65)

if __name__ == "__main__":
    main()
