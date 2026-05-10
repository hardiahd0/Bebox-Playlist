import requests
import os
import re

# المصادر
SOURCES = [
    "https://iptv-org.github.io/iptv/languages/kur.m3u",
    "https://iptv-org.github.io/iptv/countries/iq.m3u",
    "https://iptv-org.github.io/iptv/languages/ara.m3u",
    "https://raw.githubusercontent.com/iptv-org/iptv/master/streams/kur.m3u"
]

# الكلمات المفتاحية
KURD_NEWS = r"AVA|RUDAW|K24|KURDISTAN 24|NRT|KNN|WAAR|KURDSAT NEWS|GK NEWS|KURDVISION|ARK|CHANNEL 8"
KURD_KIDS = r"PEPULE|ZARO|ZAROK|NRT 3|PELISTANK|AFARIN"
KURD_RELIGION = r"AMOZHGARY|SPEDA|PAYAM|NRT 4|BANGAWAZ"
KURD_MUSIC_SPORT = r"KOREK|VIN|SPORT"
ARA_NEWS = r"AL JAZEERA|ARABIYA|AL HADATH|SKY NEWS ARABIA|RT ARABIC|EXTRANEWS"
MBC_GROUP = r"MBC"
BEIN_GROUP = r"BEIN|BEIN SPORTS"

def clean_info(line, group_name):
    # إزالة group-title القديم واستبداله بالجديد
    line = re.sub(r'group-title="[^"]*"', '', line)
    return f'{line.strip()} group-title="{group_name}"'

def run_bebox_sync():
    print("🚀 Starting Sync...")
    seen_urls = set()
    
    # مصفوفات التصنيفات
    collections = {
        "KURDISH NEWS": [],
        "KURDISH GENERAL": [],
        "KURDISH KIDS": [],
        "KURDISH RELIGIOUS": [],
        "KURDISH MUSIC & SPORT": [],
        "ARABIC NEWS": [],
        "MBC GROUP": [],
        "BEIN SPORTS": []
    }

    for source_url in SOURCES:
        try:
            r = requests.get(source_url, timeout=20)
            if r.status_code != 200: continue
            content = r.text.splitlines()
            
            for i in range(len(content)):
                if content[i].startswith("#EXTINF"):
                    info_line = content[i]
                    info_upper = info_line.upper()
                    url = content[i+1].strip() if i+1 < len(content) else ""
                    
                    if not url or url.startswith("#") or url in seen_urls: continue

                    # منطق التصنيف
                    if any(word in info_upper for word in ["KURD", "AVA", "RUDAW", "K24", "NRT", "KNN", "WAAR", "GK", "ZAROK", "SPEDA"]):
                        if re.search(KURD_NEWS, info_upper):
                            collections["KURDISH NEWS"].append(f"{clean_info(info_line, 'KURDISH NEWS')}\n{url}")
                        elif re.search(KURD_KIDS, info_upper):
                            collections["KURDISH KIDS"].append(f"{clean_info(info_line, 'KURDISH KIDS')}\n{url}")
                        elif re.search(KURD_RELIGION, info_upper):
                            collections["KURDISH RELIGIOUS"].append(f"{clean_info(info_line, 'KURDISH RELIGIOUS')}\n{url}")
                        elif re.search(KURD_MUSIC_SPORT, info_upper):
                            collections["KURDISH MUSIC & SPORT"].append(f"{clean_info(info_line, 'KURDISH MUSIC & SPORT')}\n{url}")
                        else:
                            collections["KURDISH GENERAL"].append(f"{clean_info(info_line, 'KURDISH GENERAL')}\n{url}")
                    
                    elif re.search(MBC_GROUP, info_upper):
                        collections["MBC GROUP"].append(f"{clean_info(info_line, 'MBC GROUP')}\n{url}")
                    elif re.search(BEIN_GROUP, info_upper):
                        collections["BEIN SPORTS"].append(f"{clean_info(info_line, 'BEIN SPORTS')}\n{url}")
                    elif re.search(ARA_NEWS, info_upper):
                        collections["ARABIC NEWS"].append(f"{clean_info(info_line, 'ARABIC NEWS')}\n{url}")
                    
                    seen_urls.add(url)
        except Exception as e:
            print(f"Error: {e}")

    # حفظ الملف
    with open("playlist.m3u", "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for group, channels in collections.items():
            if channels:
                f.write(f"\n# --- {group} ---\n")
                f.write("\n".join(channels) + "\n")

    print(f"✅ Finished! Found {len(seen_urls)} total channels.")

if __name__ == "__main__":
    run_bebox_sync()
