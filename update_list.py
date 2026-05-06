import requests
import os

def run_bebox_ultimate_engine():
    # 1. المصادر العالمية (Fluxus و IPTV-org) لضمان الاستقرار
    sources = {
        "ARABIC NEWS": "https://raw.githubusercontent.com/fluxustv/IPTV/main/news.m3u",
        "MOVIES & CINEMA": "https://raw.githubusercontent.com/fluxustv/IPTV/main/cinema.m3u",
        "KIDS & FAMILY": "https://raw.githubusercontent.com/fluxustv/IPTV/main/kids.m3u",
        "WORLD LIST": "https://raw.githubusercontent.com/fluxustv/IPTV/main/list.m3u",
        "KURDISH_BASE": "https://iptv-org.github.io/iptv/languages/kur.m3u"
    }
    
    # 2. هيكلية التصنيفات الخاصة بتطبيق BeBox
    categories = {
        "KURDISH LOCAL (MANUAL)": [], # قنواتك اليدوية
        "ARABIC NEWS": [],
        "KURDISH NEWS (VIP)": [],
        "KURDISH ENTERTAINMENT": [],
        "KURDISH KIDS": [],
        "KURDISH MUSIC": [],
        "KURDISH RELIGION": [],
        "KURDISH SPORT & DOC": [],
        "BEIN SPORTS NETWORK": [],
        "OSN NETWORK": [],
        "USA CHANNELS": [],
        "TURKEY CHANNELS": [],
        "EUROPE & ASIA": []
    }

    # القوائم الكردية التي زودتني بها للفرز الدقيق
    k_news = ["RUDAW", "K24", "KURDISTAN 24", "NRT NEWS", "KURDSAT NEWS", "KNN", "CHANNEL 8", "KURDISTAN TV", "GALI KURDISTAN", "ZAGROS", "SPEDA", "PAYAM", "RONAHI", "STERK", "MEDYA HABER", "NEWS 24", "KIRKUK", "TRT KURDI", "SAHAR", "TISHK", "ROJHELAT", "ARIA", "REGA", "AZADI", "BALYAZ", "AVA NEWS"]
    k_kids = ["PEPULE", "ZARO", "ZAROK", "PELISTANK", "AFARIN", "NRT 3", "ACE KIDS", "IBABY", "JOJO", "NIGA KIDS", "XAK KIDS", "ASTERA BABY"]
    k_music = ["VIN TV", "KOREK", "ACE MUSIC", "BIABAN MUSIC", "MAX TV", "MED MUSIC", "MMC"]
    k_rel = ["BANGAWAZ", "AMOZHGARY", "SRUSHT", "NRT 4", "SOZ QURAN", "KOMALL", "EZDAN", "REBARI"]
    k_sport_doc = ["DOCUMENTARY", "KURD SPORT", "ASO SPORT", "GAMING", "WAAR SPORT"]

    seen_urls = set()

    # 3. جلب القنوات اليدوية أولاً (إذا كان الملف موجوداً)
    if os.path.exists("manual_channels.m3u"):
        try:
            with open("manual_channels.m3u", "r", encoding="utf-8") as f:
                content = f.read().splitlines()
                for i in range(len(content)):
                    if content[i].startswith("#EXTINF"):
                        link = content[i+1] if i+1 < len(content) else ""
                        if link:
                            categories["KURDISH LOCAL (MANUAL)"].append(content[i] + "\n" + link)
                            seen_urls.add(link)
        except: pass

    # 4. جلب وفرز القنوات من المصادر العالمية
    for cat_key, url in sources.items():
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

                        # نظام الفرز الذكي لـ BeBox
                        if any(x in name for x in ["AL JAZEERA", "ARABIYA", "HADATH", "SKY NEWS"]):
                            categories["ARABIC NEWS"].append(f'{info} group-title="ARABIC NEWS"\n{link}')
                        elif any(x in name for x in k_news):
                            categories["KURDISH NEWS (VIP)"].append(f'{info} group-title="KURDISH NEWS"\n{link}')
                        elif any(x in name for x in k_kids):
                            categories["KURDISH KIDS"].append(f'{info} group-title="KURDISH KIDS"\n{link}')
                        elif any(x in name for x in k_music):
                            categories["KURDISH MUSIC"].append(f'{info} group-title="KURDISH MUSIC"\n{link}')
                        elif any(x in name for x in k_rel):
                            categories["KURDISH RELIGION"].append(f'{info} group-title="KURDISH RELIGION"\n{link}')
                        elif any(x in name for x in k_sport_doc):
                            categories["KURDISH SPORT & DOC"].append(f'{info} group-title="KURDISH SPORT & DOC"\n{link}')
                        elif "BEIN" in name or "AFC" in name:
                            categories["BEIN SPORTS NETWORK"].append(f'{info} group-title="beIN NETWORK"\n{link}')
                        elif "OSN" in name or "DISNEY" in name or "NICKELODEON" in name:
                            categories["OSN NETWORK"].append(f'{info} group-title="OSN NETWORK"\n{link}')
                        elif "USA" in name or "(US)" in name:
                            if "MBC" not in name: categories["USA CHANNELS"].append(f'{info} group-title="USA"\n{link}')
                        elif "TURKEY" in name or "(TR)" in name or "TRT" in name:
                            categories["TURKEY CHANNELS"].append(f'{info} group-title="TURKEY"\n{link}')
                        
                        seen_urls.add(link)
        except: continue

    # 5. تصدير ملف playlist.m3u النهائي
    final_data = "#EXTM3U\n"
    for group_list in categories.values():
        if group_list:
            final_data += "\n".join(group_list) + "\n"

    with open("playlist.m3u", "w", encoding="utf-8") as f:
        f.write(final_data)
    
    print(f"تم بنجاح! إجمالي القنوات المستخرجة: {len(seen_urls)}")

if __name__ == "__main__":
    run_bebox_ultimate_engine()
