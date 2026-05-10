import requests
import re

# مصادر ضخمة (تغطي العالم بالكامل والرياضة)
SOURCES = [
    "https://iptv-org.github.io/iptv/index.m3u", # الفهرس العالمي الشامل (أكثر من 30 ألف قناة)
    "https://raw.githubusercontent.com/iptv-org/iptv/master/streams/kur.m3u",
    "https://raw.githubusercontent.com/iptv-org/iptv/master/streams/iq.m3u",
    "https://raw.githubusercontent.com/iptv-org/iptv/master/streams/spts.m3u" # الرياضة العالمية
]

# كلمات مفتاحية للتصنيف
KURD_KEYWORDS = r"KURD|RUDAW|K24|NRT|AVA|WAAR|ZAROK|SPEDA|KNN|GK|ARK|PELISTANK"
GLOBAL_SPORTS = r"BEIN|ARENA|SKY|DAZN|ELEVEN|SUPERSPORT|EUROSPORT|CANAL\+|BT SPORT|LALIGA|PREMIER|M+ LIGA"

def clean_name(info):
    """تنظيف الاسم ليظهر بشكل احترافي في التطبيق"""
    name = info.split(',')[-1]
    name = re.sub(r'\(.*?\)|\[.*?\]|HD|SD|FHD|4K|1080p|720p|ARABIC|KURDISH|IRAQ', '', name, flags=re.IGNORECASE)
    return name.strip()

def run_deep_sync():
    print("🔍 جاري البدء بالزحف العميق... قد يستغرق هذا وقتاً بسبب ضخامة المصادر")
    seen_urls = set()
    collections = {
        "KURDISH CHANNELS": [],
        "BEIN SPORTS": [],
        "WORLD SPORTS (LIGA/CL)": [],
        "ARABIC NEWS": [],
        "MBC GROUP": []
    }

    for source in SOURCES:
        try:
            print(f"📡 فحص المصدر: {source}")
            r = requests.get(source, timeout=30)
            if r.status_code != 200: continue
            
            lines = r.text.splitlines()
            for i in range(len(lines)):
                if lines[i].startswith("#EXTINF"):
                    info = lines[i].upper()
                    url = lines[i+1].strip() if i+1 < len(lines) else ""
                    
                    if not url or not url.startswith("http") or url in seen_urls:
                        continue

                    display_name = clean_name(lines[i])

                    # 1. القنوات الكردية (أي قناة كردية في العالم)
                    if re.search(KURD_KEYWORDS, info):
                        collections["KURDISH CHANNELS"].append(f'#EXTINF:-1 group-title="KURDISH",{display_name}\n{url}')
                        seen_urls.add(url)
                    
                    # 2. بي إن سبورت
                    elif "BEIN" in info:
                        collections["BEIN SPORTS"].append(f'#EXTINF:-1 group-title="BEIN SPORTS",{display_name}\n{url}')
                        seen_urls.add(url)

                    # 3. الرياضة العالمية (الدوريات الكبرى)
                    elif re.search(GLOBAL_SPORTS, info):
                        collections["WORLD SPORTS (LIGA/CL)"].append(f'#EXTINF:-1 group-title="WORLD SPORTS",{display_name}\n{url}')
                        seen_urls.add(url)

                    # 4. مجموعات MBC
                    elif "MBC" in info:
                        collections["MBC GROUP"].append(f'#EXTINF:-1 group-title="MBC GROUP",{display_name}\n{url}')
                        seen_urls.add(url)

                    # 5. الأخبار
                    elif any(x in info for x in ["AL JAZEERA", "ARABIYA", "AL HADATH"]):
                        collections["ARABIC NEWS"].append(f'#EXTINF:-1 group-title="NEWS",{display_name}\n{url}')
                        seen_urls.add(url)
                        
        except Exception as e:
            print(f"⚠️ خطأ في مصدر: {e}")

    # كتابة الملف
    with open("playlist.m3u", "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for group, channels in collections.items():
            if channels:
                f.write(f"\n# --- {group} ({len(channels)} Channels) ---\n")
                f.write("\n".join(channels) + "\n")

    print(f"✅ تم الانتهاء! تم العثور على {len(seen_urls)} قناة مفلترة ونظيفة.")

if __name__ == "__main__":
    run_deep_sync()
