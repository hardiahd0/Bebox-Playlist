import requests

def run_bebox_pro_engine():
    # مصادر شاملة لضمان جودة الروابط وتنوعها
    sources = [
        "https://iptv-org.github.io/iptv/languages/ara.m3u",
        "https://iptv-org.github.io/iptv/languages/kur.m3u",
        "https://iptv-org.github.io/iptv/index.m3u"
    ]
    
    # القوائم البرمجية لتخزين القنوات بالترتيب المطلوب
    categories = {
        "ARABIC NEWS": [],
        "KURDISH NEWS": [],
        "KURDISH LOCAL": [],
        "BEIN SPORTS (HD/4K)": [],
        "MBC GROUP": [],
        "OSN GROUP": [],
        "MOVIES & SERIES": [],
        "USA": [],
        "UK": [],
        "FRANCE": [],
        "TURKEY": [],
        "GERMANY": [],
        "IRAN": [],
        "NORWAY": [],
        "ITALY": [],
        "SPAIN": []
    }

    seen_urls = set()
    print("جاري بناء القائمة الاحترافية لتطبيق BEBOX...")

    for url in sources:
        try:
            r = requests.get(url, timeout=25)
            if r.status_code == 200:
                lines = r.text.splitlines()
                for i in range(len(lines)):
                    if lines[i].startswith("#EXTINF"):
                        info = lines[i]
                        link = lines[i+1] if i+1 < len(lines) else ""
                        
                        if not link or link in seen_urls: continue
                        
                        name = info.split(',')[-1].upper()

                        # نظام الفرز الذكي (Smart Sorting)
                        # 1. الأخبار العربية
                        if any(x in name for x in ["AL JAZEERA", "ARABIYA", "HADATH", "SKY NEWS ARABIA"]):
                            categories["ARABIC NEWS"].append(f'#EXTINF:-1 group-title="ARABIC NEWS",{name}\n{link}')
                        
                        # 2. الأخبار الكردية
                        elif any(x in name for x in ["RUDAW", "K24", "WAAR NEWS", "KURDISTAN 24"]):
                            categories["KURDISH NEWS"].append(f'#EXTINF:-1 group-title="KURDISH NEWS",{name}\n{link}')
                        
                        # 3. القنوات الكردية المحلية (الترفيهية والعامة)
                        elif any(x in name for x in ["AVA", "NET KURD", "KURDISTAN TV", "ZAGROS", "WAAR TV", "ARK"]):
                            categories["KURDISH LOCAL"].append(f'#EXTINF:-1 group-title="KURDISH LOCAL",{name}\n{link}')

                        # 4. باقة beIN
                        elif "BEIN" in name:
                            categories["BEIN SPORTS (HD/4K)"].append(f'#EXTINF:-1 group-title="BEIN SPORTS",{name}\n{link}')

                        # 5. باقة MBC (منفصلة تماماً عن USA)
                        elif "MBC" in name:
                            categories["MBC GROUP"].append(f'#EXTINF:-1 group-title="MBC GROUP",{name}\n{link}')

                        # 6. باقة OSN
                        elif "OSN" in name:
                            categories["OSN GROUP"].append(f'#EXTINF:-1 group-title="OSN GROUP",{name}\n{link}')

                        # 7. الدول الأجنبية (تصفية صارمة لمنع التداخل)
                        elif "(US)" in name or "USA" in name:
                            if "MBC" not in name: # حماية إضافية
                                categories["USA"].append(f'#EXTINF:-1 group-title="USA",{name}\n{link}')
                        elif "(UK)" in name or "UNITED KINGDOM" in name:
                            categories["UK"].append(f'#EXTINF:-1 group-title="UNITED KINGDOM",{name}\n{link}')
                        elif "(FR)" in name or "FRANCE" in name:
                            categories["FRANCE"].append(f'#EXTINF:-1 group-title="FRANCE",{name}\n{link}')
                        elif "(TR)" in name or "TURKISH" in name:
                            categories["TURKEY"].append(f'#EXTINF:-1 group-title="TURKEY",{name}\n{link}')
                        elif "(DE)" in name or "GERMANY" in name:
                            categories["GERMANY"].append(f'#EXTINF:-1 group-title="GERMANY",{name}\n{link}')
                        
                        seen_urls.add(link)
        except:
            continue

    # دمج الملف بالترتيب الذي حددناه في القاموس (الأخبار أولاً)
    final_output = "#EXTM3U\n"
    for group in categories.values():
        if group:
            final_output += "\n".join(group) + "\n"

    with open("playlist.m3u", "w", encoding="utf-8") as f:
        f.write(final_output)
    
    print("تم التحديث! القائمة الآن مرتبة حسب الباقات والدول والأخبار.")

if __name__ == "__main__":
    run_bebox_pro_engine()
