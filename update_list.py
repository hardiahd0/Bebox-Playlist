import requests
import os

def run_bebox_final_repair():
    # مصادر البحث الآلي العالمية
    sources = [
        "https://iptv-org.github.io/iptv/languages/ara.m3u",
        "https://iptv-org.github.io/iptv/languages/kur.m3u",
        "https://iptv-org.github.io/iptv/index.m3u"
    ]
    
    categories = {
        "KURDISH LOCAL (MANUAL)": [],
        "ARABIC NEWS": [],
        "KURDISH NEWS (VIP)": [],
        "BEIN SPORTS NETWORK": [],
        "OSN NETWORK": [],
        "USA CHANNELS": [],
        "FRANCE CHANNELS": [],
        "TURKEY CHANNELS": [],
        "EUROPE & ASIA": []
    }

    seen_urls = set()

    # 1. محاولة جلب القنوات اليدوية (إن وجدت)
    if os.path.exists("manual_channels.m3u"):
        try:
            with open("manual_channels.m3u", "r", encoding="utf-8") as f:
                lines = f.read().splitlines()
                for i in range(len(lines)):
                    if lines[i].startswith("#EXTINF"):
                        link = lines[i+1] if i+1 < len(lines) else ""
                        if link:
                            categories["KURDISH LOCAL (MANUAL)"].append(lines[i] + "\n" + link)
                            seen_urls.add(link)
        except Exception as e:
            print(f"لا يوجد ملف يدوياً حالياً: {e}")

    # 2. البحث الآلي المكثف عن القنوات العالمية
    for url in sources:
        try:
            r = requests.get(url, timeout=30)
            if r.status_code == 200:
                content = r.text.splitlines()
                for i in range(len(content)):
                    if content[i].startswith("#EXTINF"):
                        info = content[i]
                        link = content[i+1] if i+1 < len(content) else ""
                        
                        if not link or link in seen_urls: continue
                        
                        name = info.upper()

                        # فرز beIN و OSN والقنوات الدولية
                        if any(x in name for x in ["BEIN", "AFC", "XTRA"]):
                            categories["BEIN SPORTS NETWORK"].append(f'{info} group-title="beIN NETWORK"\n{link}')
                        elif any(x in name for x in ["OSN", "DISNEY", "NICKELODEON"]):
                            categories["OSN NETWORK"].append(f'{info} group-title="OSN NETWORK"\n{link}')
                        elif any(x in name for x in ["AL JAZEERA", "ARABIYA", "HADATH", "SKY NEWS"]):
                            categories["ARABIC NEWS"].append(f'{info} group-title="ARABIC NEWS"\n{link}')
                        elif any(x in name for x in ["RUDAW", "K24", "WAAR", "NRT", "KURDISTAN"]):
                            categories["KURDISH NEWS (VIP)"].append(f'{info} group-title="KURDISH NEWS"\n{link}')
                        elif "USA" in name or "(US)" in name:
                            if "MBC" not in name: categories["USA CHANNELS"].append(f'{info} group-title="USA"\n{link}')
                        elif "FRANCE" in name or "(FR)" in name:
                            categories["FRANCE CHANNELS"].append(f'{info} group-title="FRANCE"\n{link}')
                        elif "TURKEY" in name or "(TR)" in name:
                            categories["TURKEY CHANNELS"].append(f'{info} group-title="TURKEY"\n{link}')
                        
                        seen_urls.add(link)
        except:
            continue

    # 3. بناء الملف النهائي
    final_output = "#EXTM3U\n"
    for group in categories.values():
        if group:
            final_output += "\n".join(group) + "\n"

    with open("playlist.m3u", "w", encoding="utf-8") as f:
        f.write(final_output)
    
    print("تمت إعادة كافة القنوات العالمية واليدوية بنجاح!")

if __name__ == "__main__":
    run_bebox_final_repair()
