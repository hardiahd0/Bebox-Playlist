import requests
import os
import re

# المصادر - تم إضافة مصادر رياضية عالمية
SOURCES = [
    "https://iptv-org.github.io/iptv/languages/kur.m3u",
    "https://iptv-org.github.io/iptv/countries/iq.m3u",
    "https://iptv-org.github.io/iptv/categories/sports.m3u", # رياضة عالمية
    "https://raw.githubusercontent.com/iptv-org/iptv/master/streams/kur.m3u"
]

# الكلمات المفتاحية
KURD_NEWS = r"AVA media |RUDAW|K24|KURDISTAN 24|NRT|KNN|WAAR|KURDSAT NEWS|GK NEWS|ARK|CHANNEL 8"
KURD_KIDS = r"PEPULE|ZARO|ZAROK|NRT 3|PELISTANK|AFARIN"
SPORTS_GLOBAL = r"BEIN|ARENA|SKY|DAZN|ELEVEN|SUPERSPORT|EUROSPORT|CANAL\+|BT SPORT|LA LIGA|PREMIER"

def clean_channel_name(info_line):
    """تنظيف اسم القناة من الزوائد والجودة وأسماء المجموعات"""
    # استخراج الاسم الذي يأتي بعد الفاصلة في سطر EXTINF
    match = re.search(r',(.+)$', info_line)
    if not match:
        return info_line
    
    name = match.group(1).strip()
    
    # 1. إزالة الجودة والدقة
    name = re.sub(r'\(.*?\)|\[.*?\]|HD|SD|FHD|UHD|4K|1080P|720P', '', name, flags=re.IGNORECASE)
    # 2. إزالة الفواصل والرموز المزعجة
    name = re.sub(r'[:|/_-]', '', name)
    # 3. إزالة اسم المجموعة إذا كان ملتصقاً بالاسم (مثل KURD: RUDAW تصبح RUDAW)
    if " " in name:
        parts = name.split()
        if len(parts) > 1 and len(parts[0]) < 5: # تخمين أن أول كلمة هي رمز أو اختصار
            name = " ".join(parts[1:])
            
    return name.strip()

def clean_extinf(line, group_name):
    """إعادة بناء سطر المعلومات بالاسم النظيف والتصنيف الجديد"""
    clean_name = clean_channel_name(line)
    return f'#EXTINF:-1 group-title="{group_name}",{clean_name}'

def run_bebox_pro_sync():
    print("🚀 جاري معالجة القنوات وتنظيف الأسماء...")
    seen_urls = set()
    collections = {
        "KURDISH NEWS": [],
        "KURDISH GENERAL": [],
        "KURDISH KIDS": [],
        "ARABIC NEWS": [],
        "MBC GROUP": [],
        "BEIN SPORTS": [],
        "WORLD SPORTS (LIGA/PREMIER)": []
    }

    for source_url in SOURCES:
        try:
            r = requests.get(source_url, timeout=25)
            if r.status_code != 200: continue
            content = r.text.splitlines()
            
            for i in range(len(content)):
                if content[i].startswith("#EXTINF"):
                    info_line = content[i]
                    info_upper = info_line.upper()
                    url = content[i+1].strip() if i+1 < len(content) else ""
                    
                    if not url or url.startswith("#") or url in seen_urls: continue

                    # 1. تصنيف القنوات الكردية
                    if any(word in info_upper for word in ["KURD", "AVA", "RUDAW", "K24", "NRT", "GK", "ZAROK"]):
                        if re.search(KURD_NEWS, info_upper):
                            collections["KURDISH NEWS"].append(f"{clean_extinf(info_line, 'KURDISH NEWS')}\n{url}")
                        elif re.search(KURD_KIDS, info_upper):
                            collections["KURDISH KIDS"].append(f"{clean_extinf(info_line, 'KURDISH KIDS')}\n{url}")
                        else:
                            collections["KURDISH GENERAL"].append(f"{clean_extinf(info_line, 'KURDISH GENERAL')}\n{url}")
                    
                    # 2. تصنيف بي إن سبورت والرياضة العالمية
                    elif "BEIN" in info_upper:
                        collections["BEIN SPORTS"].append(f"{clean_extinf(info_line, 'BEIN SPORTS')}\n{url}")
                    elif re.search(SPORTS_GLOBAL, info_upper):
                        collections["WORLD SPORTS (LIGA/PREMIER)"].append(f"{clean_extinf(info_line, 'WORLD SPORTS')}\n{url}")
                    
                    # 3. MBC والأخبار العربية
                    elif "MBC" in info_upper:
                        collections["MBC GROUP"].append(f"{clean_extinf(info_line, 'MBC GROUP')}\n{url}")
                    elif any(news in info_upper for news in ["AL JAZEERA", "ARABIYA", "AL HADATH", "SKY NEWS"]):
                        collections["ARABIC NEWS"].append(f"{clean_extinf(info_line, 'ARABIC NEWS')}\n{url}")
                    
                    seen_urls.add(url)
        except: continue

    # حفظ الملف النهائي
    with open("playlist.m3u", "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for group, channels in collections.items():
            if channels:
                f.write(f"\n# --- {group} ---\n")
                f.write("\n".join(channels) + "\n")

    print(f"✅ تم الحفظ! إجمالي القنوات النظيفة: {len(seen_urls)}")

if __name__ == "__main__":
    run_bebox_pro_sync()
