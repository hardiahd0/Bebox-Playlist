import requests

def run_bebox_mega_engine():
    # المصادر الرسمية والعالمية
    sources = [
        "https://iptv-org.github.io/iptv/languages/ara.m3u",
        "https://iptv-org.github.io/iptv/languages/kur.m3u",
        "https://iptv-org.github.io/iptv/index.m3u"
    ]
    
    # تعريف هيكلية التصنيفات لـ BeBox
    categories = {
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
        "FRANCE CHANNELS": [],
        "SPAIN & PORTUGAL": [],
        "GERMANY CHANNELS": [],
        "TURKEY CHANNELS": [],
        "IRAN CHANNELS": [],
        "ASIA (CHINA & JAPAN)": []
    }

    # القوائم البرمجية للفرز الذكي
    k_news = ["RUDAW","AVA TV", "KURDISTAN 24", "K24", "NRT NEWS", "KURDSAT NEWS", "KNN", "CHANNEL 8", "KURDISTAN TV", "GALI KURDISTAN", "ZAGROS", "SPEDA", "PAYAM", "RONAHI", "STERK", "MEDYA HABER", "NEWS 24", "KIRKUK", "TRT KURDI", "SAHAR", "TISHK", "ROJHELAT", "ARIA", "REGA", "AZADI", "BALYAZ", "AVA NEWS"]
    k_ent = ["KURDMAX", "NET TV", "AVA ENTERTAINMENT", "NRT 2", "KANAL 4", "BABYLON", "RENG", "CIHAN", "WAAR", "DUHOK", "SLEMANI", "HAWLER", "QALAT", "DELAL", "BADINAN", "ESTA", "FALCON", "BIABAN", "ACE FAMILY", "NIGA FAMILY", "ASTERA", "ASMAN", "CHARA", "DAHEN", "HETTAW", "JSN", "JUDI", "LAWAN", "MINARA", "NEWLINE", "NISHTIMANI", "UMM", "XAK", "ZOOM", "ART TV", "EFFECT", "TUESHW", "KURDINO"]
    k_kids = ["PEPULE", "ZARO", "ZAROK", "PELISTANK", "AFARIN", "NRT 3", "ACE KIDS", "IBABY", "JOJO", "NIGA KIDS", "XAK KIDS"]
    k_music = ["VIN TV", "KOREK", "ACE MUSIC", "MAX TV", "MED MUSIC", "MMC"]
    k_rel = ["BANGAWAZ", "AMOZHGARY", "SRUSHT", "NRT 4", "SOZ QURAN", "KOMALL", "EZDAN", "REBARI"]
    k_sport_doc = ["DOCUMENTARY", "KURD SPORT", "ASO SPORT", "GAMING"]

    seen_urls = set()
    print("جاري دمج القنوات الكردية مع الباقات العالمية...")

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
                        name = info.split(',')[-1].upper()

                        # 1. الأخبار العربية
                        if any(x in name for x in ["AL JAZEERA", "ARABIYA", "HADATH", "SKY NEWS ARABIA"]):
                            categories["ARABIC NEWS"].append(f'#EXTINF:-1 group-title="ARABIC NEWS",{name}\n{link}')
                        
                        # 2. باقة beIN (الرياضية، المنوعة، AFC)
                        elif any(x in name for x in ["BEIN", "AFC", "XTRA"]):
                            categories["BEIN SPORTS NETWORK"].append(f'#EXTINF:-1 group-title="beIN NETWORK",{name}\n{link}')

                        # 3. باقة OSN (بما فيها Disney و Nickelodeon)
                        elif any(x in name for x in ["OSN", "DISNEY CHANNEL", "NICKELODEON"]):
                            categories["OSN NETWORK"].append(f'#EXTINF:-1 group-title="OSN NETWORK",{name}\n{link}')

                        # 4. التصنيفات الكردية (VIP)
                        elif any(x in name for x in k_news):
                            categories["KURDISH NEWS (VIP)"].append(f'#EXTINF:-1 group-title="KURDISH NEWS",{name}\n{link}')
                        elif any(x in name for x in k_kids):
                            categories["KURDISH KIDS"].append(f'#EXTINF:-1 group-title="KURDISH KIDS",{name}\n{link}')
                        elif any(x in name for x in k_music):
                            categories["KURDISH MUSIC"].append(f'#EXTINF:-1 group-title="KURDISH MUSIC",{name}\n{link}')
                        elif any(x in name for x in k_rel):
                            categories["KURDISH RELIGION"].append(f'#EXTINF:-1 group-title="KURDISH RELIGION",{name}\n{link}')
                        elif any(x in name for x in k_sport_doc):
                            categories["KURDISH SPORT & DOC"].append(f'#EXTINF:-1 group-title="KURDISH SPORT & DOC",{name}\n{link}')
                        elif any(x in name for x in k_ent):
                            categories["KURDISH ENTERTAINMENT"].append(f'#EXTINF:-1 group-title="KURDISH ENTERTAINMENT",{name}\n{link}')

                        # 5. الدول الأجنبية والآسيوية (تصفية جغرافية)
                        elif "USA" in name or "(US)" in name or any(x in name for x in ["ABC", "NBC", "CBS", "FOX", "HBO", "ESPN"]):
                            if "MBC" not in name: categories["USA CHANNELS"].append(f'#EXTINF:-1 group-title="USA",{name}\n{link}')
                        elif "FRANCE" in name or "(FR)" in name or any(x in name for x in ["TF1", "CANAL+"]):
                            categories["FRANCE CHANNELS"].append(f'#EXTINF:-1 group-title="FRANCE",{name}\n{link}')
                        elif any(x in name for x in ["SPAIN", "(ES)", "PORTUGAL", "(PT)", "SIC", "TVI"]):
                            categories["SPAIN & PORTUGAL"].append(f'#EXTINF:-1 group-title="SPAIN & PORTUGAL",{name}\n{link}')
                        elif "GERMANY" in name or "(DE)" in name or "SKY SPORT" in name:
                            categories["GERMANY CHANNELS"].append(f'#EXTINF:-1 group-title="GERMANY",{name}\n{link}')
                        elif any(x in name for x in ["TURKEY", "(TR)", "TRT", "KANAL D", "ATV"]):
                            categories["TURKEY CHANNELS"].append(f'#EXTINF:-1 group-title="TURKEY",{name}\n{link}')
                        elif any(x in name for x in ["IRAN", "(IR)", "IRIB", "IFILM"]):
                            categories["IRAN CHANNELS"].append(f'#EXTINF:-1 group-title="IRAN",{name}\n{link}')
                        elif any(x in name for x in ["CHINA", "CCTV", "JAPAN", "NHK", "FUJI TV"]):
                            categories["ASIA (CHINA & JAPAN)"].append(f'#EXTINF:-1 group-title="ASIA (CHINA & JAPAN)",{name}\n{link}')
                        
                        seen_urls.add(link)
        except: continue

    # تجميع الملف النهائي بالترتيب المطلوب
    final_output = "#EXTM3U\n"
    for group_content in categories.values():
        if group_content:
            final_output += "\n".join(group_content) + "\n"

    with open("playlist.m3u", "w", encoding="utf-8") as f:
        f.write(final_output)
    
    print("تم التحديث! المنظومة العالمية جاهزة الآن مع قنواتك الكردية.")

if __name__ == "__main__":
    run_bebox_mega_engine()
