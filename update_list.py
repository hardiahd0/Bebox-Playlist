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

# 1. قوائم الكلمات المفتاحية للتصنيف
KURD_NEWS = r"AVA|RUDAW|K24|KURDISTAN 24|NRT|KNN|WAAR|KURDSAT NEWS|GK NEWS|KURDVISION|ARK|CHANNEL 8"
KURD_ENT = r"KURDMAX|NET TV|KURDISTAN TV|ZAGROS|KURDSAT|GALI KURDISTAN|BABYLON"
KURD_KIDS = r"PEPULE|ZARO|ZAROK|NRT 3|PELISTANK|AFARIN"
KURD_RELIGION = r"AMOZHGARY|SPEDA|PAYAM|NRT 4|BANGAWAZ"
KURD_MUSIC_SPORT = r"KOREK|VIN|SPORT"

ARA_NEWS = r"AL JAZEERA|ARABIYA|AL HADATH|SKY NEWS ARABIA|RT ARABIC|EXTRANEWS"
MBC_GROUP = r"MBC"
BEIN_GROUP = r"BEIN|BEIN SPORTS"

def clean_info(line, group_name):
    """تنظيف السطر وإضافة التصنيف المناسب"""
    line = re.sub(r'group-title="[^"]*"', '', line)
    return f'{line.strip() discovery-name="" group-title="{group_name}"'

def run_bebox_advanced_sync():
    print("🚀 جاري تجميع القنوات وتنظيم التصنيفات...")
    seen_urls = set()
    
    # مصفوفات التصنيفات
    cat_kurd_news = []
    cat_kurd_general = []
    cat_kurd_kids = []
    cat_kurd_religious = []
    cat_kurd_music_sport = []
    cat_ara_news = []
    cat_mbc = []
    cat_bein = []

    for source_url in SOURCES:
        try:
            r = requests.get(source_url, timeout=15)
            if r.status_code != 200: continue
            content = r.text.splitlines()
            
            for i in range(len(content)):
                if content[i].startswith("#EXTINF"):
                    info = content[i].upper()
                    url = content[i+1].strip() if i+1 < len(content) else ""
                    
                    if not url or url in seen_urls: continue

                    # تصنيف القنوات الكردية (حسب طلبك الدقيق)
                    if any(word in info for word in ["KURD", "AVA", "RUDAW", "K24", "NRT", "KNN", "WAAR", "GK", "ZAROK", "SPEDA"]):
                        if re.search(KURD_NEWS, info):
                            cat_kurd_news.append(f"{clean_info(content[i], 'KURDISH NEWS')}\n{url}")
                        elif re.search(KURD_KIDS, info):
                            cat_kurd_kids.append(f"{clean_info(content[i], 'KURDISH KIDS')}\n{url}")
                        elif re.search(KURD_RELIGION, info):
                            cat_kurd_religious.append(f"{clean_info(content[i], 'KURDISH RELIGIOUS')}\n{url}")
                        elif re.search(KURD_MUSIC_SPORT, info):
                            cat_kurd_music_sport.append(f"{clean_info(content[i], 'KURDISH MUSIC & SPORT')}\n{url}")
                        else:
                            cat_kurd_general.append(f"{clean_info(content[i], 'KURDISH GENERAL')}\n{url}")
                        seen_urls.add(url)
                    
                    # تصنيف MBC
                    elif re.search(MBC_GROUP, info):
                        cat_mbc.append(f"{clean_info(content[i], 'MBC GROUP')}\n{url}")
                        seen_urls.add(url)
                    
                    # تصنيف beIN
                    elif re.search(BEIN_GROUP, info):
                        cat_bein.append(f"{clean_info(content[i], 'BEIN SPORTS')}\n{url}")
                        seen_urls.add(url)

                    # تصنيف الأخبار العربية
                    elif re.search(ARA_NEWS, info):
                        cat_ara_news.append(f"{clean_info(content[i], 'ARABIC NEWS')}\n{url}")
                        seen_urls.add(url)

        except: continue

    # كتابة الملف النهائي بالترتيب المطلوب
    with open("playlist.m3u", "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        
        # ترتيب الظهور في التطبيق
        groups = [
            ("KURDISH NEWS", cat_kurd_news),
            ("KURDISH GENERAL", cat_kurd_general),
            ("KURDISH KIDS", cat_kurd_kids),
            ("KURDISH RELIGIOUS", cat_kurd_religious),
            ("KURDISH MUSIC & SPORT", cat_kurd_music_sport),
            ("ARABIC NEWS", cat_ara_news),
            ("MBC GROUP", cat_mbc),
            ("BEIN SPORTS", cat_bein)
        ]

        for name, channels in groups:
            if channels:
                f.write(f"\n# --- {name} ---\n")
                f.write("\n".join(channels) + "\n")

    print(f"✅ تم الانتهاء! الملف جاهز باسم playlist.m3u")

if __name__ == "__main__":
    run_bebox_advanced_sync()
