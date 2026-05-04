import requests
import os

def run_bebox_hybrid_engine():
    # مصادر البحث الآلي
    sources = [
        "https://iptv-org.github.io/iptv/languages/ara.m3u",
        "https://iptv-org.github.io/iptv/languages/kur.m3u",
        "https://iptv-org.github.io/iptv/index.m3u"
    ]
    
    categories = {
        "KURDISH LOCAL (MANUAL)": [], # القنوات التي ستضيفها يدوياً
        "ARABIC NEWS": [],
        "KURDISH NEWS (VIP)": [],
        "KURDISH ENTERTAINMENT": [],
        "KURDISH KIDS": [],
        "BEIN SPORTS NETWORK": [],
        "OSN NETWORK": [],
        "USA CHANNELS": [],
        "TURKEY CHANNELS": [],
        "EUROPE & ASIA": []
    }

    seen_urls = set()

    # 1. جلب القنوات اليدوية أولاً (الأولوية القصوى)
    if os.path.exists("manual_channels.m3u"):
        with open("manual_channels.m3u", "r", encoding="utf-8") as f:
            manual_content = f.read().splitlines()
            for i in range(len(manual_content)):
                if manual_content[i].startswith("#EXTINF"):
                    categories["KURDISH LOCAL (MANUAL)"].append(manual_content[i] + "\n" + manual_content[i+1])
                    if i+1 < len(manual_content): seen_urls.add(manual_content[i+1])

    # 2. جلب القنوات الآلية وتصنيفها
    for url in sources:
        try:
            r = requests.get(url, timeout=30)
            if r.status_code == 200:
                lines = r.text.splitlines()
                for i in range(len(lines)):
                    if lines[i].startswith("#EXTINF"):
                        info = lines[i]
                        link = lines[i+1] if i+1 < len(lines) else ""
                        if not link or link in seen_urls: continue
                        name = info.upper()

                        # فرز ذكي ومرن (Flexible Matching)
                        if any(x in name for x in ["AL JAZEERA", "ARABIYA", "HADATH", "SKY NEWS"]):
                            categories["ARABIC NEWS"].append(f'{info} group-title="ARABIC NEWS"\n{link}')
                        elif any(x in name for x in ["RUDAW", "K24", "KURDISTAN 24", "WAAR", "NRT"]):
                            categories["KURDISH NEWS (VIP)"].append(f'{info} group-title="KURDISH NEWS"\n{link}')
                        elif "BEIN" in name:
                            categories["BEIN SPORTS NETWORK"].append(f'{info} group-title="beIN NETWORK"\n{link}')
                        elif "OSN" in name:
                            categories["OSN NETWORK"].append(f'{info} group-title="OSN NETWORK"\n{link}')
                        elif "USA" in name or "(US)" in name:
                            if "MBC" not in name: categories["USA CHANNELS"].append(f'{info} group-title="USA"\n{link}')
                        elif "TURKEY" in name or "(TR)" in name or "TRT" in name:
                            categories["TURKEY CHANNELS"].append(f'{info} group-title="TURKEY"\n{link}')
                        
                        seen_urls.add(link)
        except: continue

    # بناء الملف النهائي playlist.m3u
    final_output = "#EXTM3U\n"
    for group in categories.values():
        if group: final_output += "\n".join(group) + "\n"

    with open("playlist.m3u", "w", encoding="utf-8") as f:
        f.write(final_output)
    
    print("تم دمج القنوات اليدوية مع التحديث الآلي بنجاح!")

if __name__ == "__main__":
    run_bebox_hybrid_engine()
