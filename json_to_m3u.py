import json
import os

# --- [ CONFIG ] ---
INPUT_JSON = "nanamovie_Movie___Thai_Sub.json"
OUTPUT_M3U = "thai_sub_movies.m3u"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

def convert():
    if not os.path.exists(INPUT_JSON):
        print(f"❌ ไม่เจอไฟล์ {INPUT_JSON} ว่ะเพื่อน!")
        return

    print(f"[*] กำลังแปลง {INPUT_JSON} เป็น M3U...")
    try:
        with open(INPUT_JSON, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        items = data.get("groups", [])
        with open(OUTPUT_M3U, "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")
            for item in items:
                name = item.get("name", "Unknown")
                stations = item.get("stations", [])
                if stations:
                    url = stations[0].get("url", "")
                    image = item.get("image", "")
                    if url:
                        f.write(f'#EXTINF:-1 tvg-logo="{image}" group-title="Thai Sub Movies", {name}\n')
                        # พ่วง Referer มาตรฐานของ Nana
                        if "nanaplayer" in url or "nana2play" in url:
                            f.write(f"{url}|Referer=https://nanaplayer.com/&User-Agent={UA}\n")
                        else:
                            f.write(f"{url}\n")
        
        print(f"✅ แปลงสำเร็จ! ได้ไฟล์ {OUTPUT_M3U} (ทั้งหมด {len(items)} เรื่อง)")
    except Exception as e:
        print(f"❌ พังพินาศ: {e}")

if __name__ == "__main__":
    convert()
